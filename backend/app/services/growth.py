"""Growth engine — the "evolving Student Graph" layer.

This module keeps two deliberately separate axes:

* **Profile confidence** — how sure Novi is about a dimension/label. Stored as an
  append-only event log and folded with an exponential moving average so a single
  answer can never swing a score (enforces the "don't label from one answer" rule
  in code, not just policy).
* **Growth** — whether the student's real state is changing and whether they act on
  it. Computed from behaviour (app events), milestone completion and snapshot diffs.

Nothing here is destructive: every function is additive and the recording helpers
are written to be called best-effort from existing flows (wrapped in try/except by
the caller) so a growth failure can never break a core feature.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import pvariance

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.growth import AppEvent, DimensionSignal, GraphSnapshot, GrowthMilestone
from app.models.user import User

# --------------------------------------------------------------------------- tuning

DNA_FIELD_TO_DIMENSION = {
    "interests": "interest",
    "strengths": "strength",
    "skills": "skill",
    "career_zones": "zone",
    "goals": "goal",
    "motivations": "motivation",
    "values": "value",
    "traits": "trait",
}

# Presence in the DNA is strong evidence, but the EMA starts from a neutral prior so
# one signal is never enough to "declare" a label (confidence stays < 70 after 1-2).
INITIAL_BASELINE = 55.0
DNA_SIGNAL_STRENGTH = 88.0
DECAY_SIGNAL_STRENGTH = 25.0

# Lower alpha for high-stakes dimensions (career interest), higher for low-stakes ones.
ALPHA_BY_DIMENSION = {
    "goal": 0.18,
    "interest": 0.20,
    "zone": 0.20,
    "motivation": 0.22,
    "value": 0.25,
    "strength": 0.30,
    "skill": 0.30,
    "trait": 0.35,
}
DEFAULT_ALPHA = 0.30
DECLARED_THRESHOLD = 70.0  # confidence at/above which a label counts as "self-declared"

COMPOSITE_WEIGHTS = {
    "confidence_velocity": 0.20,
    "signal_stability": 0.15,
    "say_do_alignment": 0.30,
    "milestone_completion": 0.25,
    "engagement_recency": 0.10,
}

_WORD_RE = re.compile(r"[a-z0-9+#]+")


# --------------------------------------------------------------------------- core math

def update_confidence(prev_confidence: float, new_signal: float, alpha: float = DEFAULT_ALPHA) -> float:
    """Exponential moving average: recent, repeated signals beat a single outlier."""
    alpha = max(0.0, min(1.0, alpha))
    return round(prev_confidence + alpha * (new_signal - prev_confidence), 2)


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _normalize_label(label: str) -> str:
    return " ".join(str(label or "").strip().lower().split())[:191]


def _normalize_dimension(dimension: str) -> str:
    return str(dimension or "").strip().lower()[:64]


# --------------------------------------------------------------------------- signals

def _latest_confidence(db: Session, user_id: int, dimension: str, label: str) -> float | None:
    value = db.scalar(
        select(DimensionSignal.confidence_after)
        .where(
            DimensionSignal.user_id == user_id,
            DimensionSignal.dimension == dimension,
            DimensionSignal.label == label,
        )
        .order_by(DimensionSignal.id.desc())
        .limit(1)
    )
    return float(value) if value is not None else None


def record_signal(
    db: Session,
    user: User,
    dimension: str,
    label: str,
    signal_value: float,
    source: str = "manual",
    source_ref: str | None = None,
    alpha: float | None = None,
    created_at: datetime | None = None,
) -> DimensionSignal | None:
    """Append one signal and fold it into the running confidence (never overwrite)."""
    dimension = _normalize_dimension(dimension)
    label = _normalize_label(label)
    if not dimension or not label:
        return None

    prev = _latest_confidence(db, user.id, dimension, label)
    before = INITIAL_BASELINE if prev is None else prev
    value = float(signal_value)
    after = update_confidence(before, value, alpha if alpha is not None else ALPHA_BY_DIMENSION.get(dimension, DEFAULT_ALPHA))

    kwargs: dict = {}
    if created_at is not None:
        kwargs["created_at"] = created_at
    row = DimensionSignal(
        user_id=user.id,
        dimension=dimension,
        label=label,
        signal_value=round(value, 2),
        confidence_before=round(before, 2),
        confidence_after=after,
        delta=round(after - before, 2),
        source=(source or "manual")[:64],
        source_ref=(source_ref[:191] if source_ref else None),
        **kwargs,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def current_scores(db: Session, user: User) -> dict[str, dict[str, float]]:
    """Latest confidence per ``dimension -> label`` (the current Student Graph)."""
    rows = db.scalars(
        select(DimensionSignal)
        .where(DimensionSignal.user_id == user.id)
        .order_by(DimensionSignal.id.asc())
    )
    scores: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        scores[row.dimension][row.label] = float(row.confidence_after)
    return {dim: dict(labels) for dim, labels in scores.items()}


def _dna_labels(dna) -> set[str]:
    labels: set[str] = set()
    if dna is None:
        return labels
    for field in DNA_FIELD_TO_DIMENSION:
        for label in (getattr(dna, field, None) or []):
            clean = _normalize_label(label)
            if clean:
                labels.add(clean)
    return labels


def _labels_from_text(text: str, dna) -> list[str]:
    """Which known DNA labels are present in a free-text blob (behaviour tagging)."""
    low = (text or "").lower()
    if not low:
        return []
    found = [label for label in _dna_labels(dna) if label in low]
    tokens = set(_WORD_RE.findall(low))
    for label in _dna_labels(dna):
        if label not in found and set(_WORD_RE.findall(label)) & tokens:
            found.append(label)
    return found


def record_signals_from_dna(db: Session, user: User, dna, source: str = "dna") -> int:
    """Turn the current DNA into signals, and decay labels that have disappeared.

    Called on every DNA update: repeated corroboration raises confidence, a removed
    label decays it — both are captured as rows so the trend is preserved.
    """
    present: dict[str, set[str]] = defaultdict(set)
    for field, dimension in DNA_FIELD_TO_DIMENSION.items():
        for label in (getattr(dna, field, None) or []):
            clean = _normalize_label(label)
            if clean:
                present[dimension].add(clean)

    written = 0
    for dimension, labels in present.items():
        for label in labels:
            record_signal(
                db, user, dimension, label, DNA_SIGNAL_STRENGTH, source=source, source_ref="dna"
            )
            written += 1

    known = current_scores(db, user)
    for dimension, labels in known.items():
        for label in labels:
            if label in present.get(dimension, set()):
                continue
            record_signal(
                db, user, dimension, label, DECAY_SIGNAL_STRENGTH,
                source=f"{source}_decay", source_ref="dna_removed",
            )
            written += 1
    return written


def event_tags(user: User, db: Session, text: str, extra: list | None = None) -> list[str]:
    """Tags for a behavioural event: known DNA labels found in the text + explicit extras."""
    from app.services.career_dna import get_dna  # local import avoids a cycle

    try:
        dna = get_dna(user, db)
    except Exception:
        dna = None

    tags = _labels_from_text(text, dna)
    for item in (extra or []):
        clean = _normalize_label(item)
        if clean:
            tags.append(clean)
    return list(dict.fromkeys(tags))


def record_event(
    db: Session,
    user: User,
    event_type: str,
    title: str = "",
    tags: list | None = None,
    created_at: datetime | None = None,
) -> AppEvent:
    """Log what the student actually did. Deduped tags, never fails the caller."""
    clean: list[str] = []
    for tag in (tags or []):
        value = _normalize_label(tag)
        if value and value not in clean:
            clean.append(value)

    kwargs: dict = {}
    if created_at is not None:
        kwargs["created_at"] = created_at
    event = AppEvent(
        user_id=user.id,
        event_type=(event_type or "generic")[:64],
        title=(title or "")[:255],
        tags=clean or None,
        **kwargs,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# --------------------------------------------------------------------------- say-do alignment

def say_do_alignment(
    db: Session,
    user: User,
    window_days: int = 90,
    threshold: float = DECLARED_THRESHOLD,
) -> dict:
    """Of the labels a student self-reports, how many have behavioural evidence?"""
    scores = current_scores(db, user)
    declared = sorted({label for labels in scores.values() for label, c in labels.items() if c >= threshold})

    since = datetime.now() - timedelta(days=window_days)
    events = db.scalars(
        select(AppEvent).where(AppEvent.user_id == user.id, AppEvent.created_at >= since)
    )
    acted: set[str] = set()
    for event in events:
        for tag in (event.tags or []):
            acted.add(_normalize_label(tag))

    matched = [label for label in declared if label in acted]
    unproven = [label for label in declared if label not in acted]
    ratio = (len(matched) / len(declared)) if declared else 0.0
    return {
        "alignment": round(ratio * 100, 1),
        "ratio": round(ratio, 3),
        "declared": declared,
        "matched": matched,
        "unproven": unproven,
        "window_days": window_days,
        "threshold": threshold,
    }


# --------------------------------------------------------------------------- milestones

def _ensure_milestone(
    db: Session,
    user: User,
    source_type: str,
    source_id: int | None,
    title: str,
    done: bool,
    completed_at: datetime | None,
) -> GrowthMilestone:
    milestone = db.scalar(
        select(GrowthMilestone).where(
            GrowthMilestone.user_id == user.id,
            GrowthMilestone.source_type == source_type,
            GrowthMilestone.source_id == source_id,
        )
    )
    status = "done" if done else "pending"
    if milestone is None:
        milestone = GrowthMilestone(
            user_id=user.id,
            source_type=source_type,
            source_id=source_id,
            title=(title or "Untitled")[:255],
            status=status,
            completed_at=completed_at if done else None,
        )
        db.add(milestone)
    elif milestone.status != "skipped":
        milestone.title = (title or milestone.title)[:255]
        milestone.status = status
        milestone.completed_at = completed_at if done else None
    return milestone


def sync_milestones_from_roadmap(db: Session, user: User) -> int:
    """Mirror roadmap steps, weekly priorities and tasks into the milestone ground truth."""
    from app.models.roadmap import RoadmapItem, Task, WeeklyPriority
    from app.models.enums import TaskStatus

    count = 0
    for item in db.scalars(select(RoadmapItem).where(RoadmapItem.user_id == user.id)):
        _ensure_milestone(
            db, user, "roadmap_item", item.id, item.title, bool(item.completed),
            item.created_at if item.completed else None,
        )
        count += 1
    for prio in db.scalars(select(WeeklyPriority).where(WeeklyPriority.user_id == user.id)):
        _ensure_milestone(
            db, user, "priority", prio.id, prio.title, bool(prio.completed),
            prio.created_at if prio.completed else None,
        )
        count += 1
    for task in db.scalars(select(Task).where(Task.user_id == user.id)):
        done = task.status == TaskStatus.DONE
        _ensure_milestone(
            db, user, "task", task.id, task.title, done, task.created_at if done else None
        )
        count += 1
    db.commit()
    return count


def milestone_completion(db: Session, user: User) -> dict:
    milestones = list(db.scalars(select(GrowthMilestone).where(GrowthMilestone.user_id == user.id)))
    done = sum(1 for m in milestones if m.status == "done")
    total = len(milestones)
    rated = [m for m in milestones if m.self_rated_helpful is not None]
    helpful = sum(1 for m in rated if m.self_rated_helpful)
    ratio = (done / total) if total else 0.0
    return {
        "completion": round(ratio * 100, 1),
        "ratio": round(ratio, 3),
        "done": done,
        "total": total,
        "skipped": sum(1 for m in milestones if m.status == "skipped"),
        "helpful_rating": (round(helpful / len(rated) * 100, 1) if rated else None),
        "rated": len(rated),
    }


# --------------------------------------------------------------------------- snapshots & diff

def snapshot(db: Session, user: User, day: date | None = None, force: bool = False) -> GraphSnapshot:
    """Capture (or refresh) today's whole-graph JSON blob."""
    day = day or date.today()
    existing = db.scalar(
        select(GraphSnapshot).where(
            GraphSnapshot.user_id == user.id, GraphSnapshot.snapshot_date == day
        )
    )
    if existing is not None and not force:
        return existing

    scores = current_scores(db, user)
    event_count = db.scalar(
        select(func.count()).select_from(AppEvent).where(AppEvent.user_id == user.id)
    )
    snap = existing or GraphSnapshot(user_id=user.id, snapshot_date=day)
    snap.payload = scores
    snap.event_count = int(event_count or 0)
    if existing is None:
        db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def latest_pair(db: Session, user: User) -> list[GraphSnapshot]:
    """Newest two snapshots, newest first (for diffing)."""
    return list(
        db.scalars(
            select(GraphSnapshot)
            .where(GraphSnapshot.user_id == user.id)
            .order_by(GraphSnapshot.snapshot_date.desc())
            .limit(2)
        )
    )


def diff_snapshots(prev: dict | None, curr: dict | None, threshold: float = 10.0) -> dict:
    """Nodes added/removed and dimensions that moved more than ``threshold``."""
    prev = prev or {}
    curr = curr or {}
    added: list[dict] = []
    removed: list[dict] = []
    changed: list[dict] = []

    for dimension in sorted(set(prev) | set(curr)):
        prev_labels = prev.get(dimension) or {}
        curr_labels = curr.get(dimension) or {}
        for label in sorted(set(prev_labels) | set(curr_labels)):
            before = prev_labels.get(label)
            after = curr_labels.get(label)
            if before is None and after is not None:
                added.append({"dimension": dimension, "label": label, "to": after})
            elif before is not None and after is None:
                removed.append({"dimension": dimension, "label": label, "from": before})
            elif before is not None and after is not None:
                delta = round(float(after) - float(before), 2)
                if abs(delta) >= threshold:
                    changed.append(
                        {"dimension": dimension, "label": label, "from": before, "to": after, "delta": delta}
                    )
    return {"added": added, "removed": removed, "changed": changed, "threshold": threshold}


# --------------------------------------------------------------------------- composite metrics

def confidence_velocity(db: Session, user: User, days: int = 90) -> dict:
    """Net confidence movement per label per week (averaged as an absolute value)."""
    since = datetime.now() - timedelta(days=days)
    rows = list(
        db.scalars(
            select(DimensionSignal)
            .where(DimensionSignal.user_id == user.id, DimensionSignal.created_at >= since)
            .order_by(DimensionSignal.id.asc())
        )
    )
    net: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        net[(row.dimension, row.label)] += float(row.delta or 0.0)

    weeks = max(days / 7.0, 1.0)
    per_label = {f"{d}:{l}": round(v / weeks, 2) for (d, l), v in net.items()}
    if not per_label:
        return {"per_week": 0.0, "per_label": {}, "samples": 0, "window_days": days}
    avg_abs = sum(abs(v) for v in per_label.values()) / len(per_label)
    return {"per_week": round(avg_abs, 2), "per_label": per_label, "samples": len(rows), "window_days": days}


def signal_stability(db: Session, user: User, days: int = 30) -> dict:
    """Variance of confidence across repeated probes — low variance = trustworthy signal."""
    since = datetime.now() - timedelta(days=days)
    rows = list(
        db.scalars(
            select(DimensionSignal)
            .where(DimensionSignal.user_id == user.id, DimensionSignal.created_at >= since)
            .order_by(DimensionSignal.id.asc())
        )
    )
    series: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        series[(row.dimension, row.label)].append(float(row.confidence_after))

    variances = [pvariance(values) for values in series.values() if len(values) >= 2]
    avg_var = (sum(variances) / len(variances)) if variances else 0.0
    score = 100.0 / (1.0 + avg_var)
    return {
        "average_variance": round(avg_var, 2),
        "stability_score": round(score, 1),
        "labels": len(series),
        "window_days": days,
    }


def engagement_recency_days(db: Session, user: User) -> int | None:
    """Days since the last signal/event. ``None`` means no activity at all yet."""
    last_event = db.scalar(select(func.max(AppEvent.created_at)).where(AppEvent.user_id == user.id))
    last_signal = db.scalar(
        select(func.max(DimensionSignal.created_at)).where(DimensionSignal.user_id == user.id)
    )
    candidates = [d for d in (last_event, last_signal) if d is not None]
    if not candidates:
        return None
    latest = max(candidates)
    return max(0, (datetime.now() - latest).days)


def growth_index(db: Session, user: User) -> dict:
    """The five internal signals + a transparent weighted composite. Not a student-facing score."""
    velocity = confidence_velocity(db, user, days=90)
    stability = signal_stability(db, user, days=30)
    alignment = say_do_alignment(db, user)
    milestones = milestone_completion(db, user)
    recency = engagement_recency_days(db, user)

    components = {
        "confidence_velocity": round(_clamp(velocity["per_week"] * 5), 1),
        "signal_stability": stability["stability_score"],
        "say_do_alignment": alignment["alignment"],
        "milestone_completion": milestones["completion"],
        "engagement_recency": (100.0 if recency is None else round(_clamp(100 - recency * 3), 1)),
    }
    weight_total = sum(COMPOSITE_WEIGHTS.values())
    composite = sum(components[k] * COMPOSITE_WEIGHTS.get(k, 0.0) for k in components) / weight_total

    return {
        "composite": round(composite, 1),
        "components": components,
        "details": {
            "confidence_velocity": velocity,
            "signal_stability": stability,
            "say_do_alignment": alignment,
            "milestone_completion": milestones,
            "engagement_recency_days": recency,
        },
    }


# --------------------------------------------------------------------------- narrative

def narrative(db: Session, user: User) -> str:
    """Turn snapshots/diffs into the "when we first met … lately …" story."""
    scores = current_scores(db, user)
    top = sorted(
        ((label, confidence) for labels in scores.values() for label, confidence in labels.items()),
        key=lambda pair: pair[1],
        reverse=True,
    )[:3]

    pair = latest_pair(db, user)
    if len(pair) >= 2:
        diff = diff_snapshots(pair[1].payload or {}, pair[0].payload or {})
        rising = sorted(diff["changed"], key=lambda c: c["delta"], reverse=True)
        up = [c["label"] for c in rising if c["delta"] > 0][:2]
        down = [c["label"] for c in rising if c["delta"] < 0][:2]
        added = [c["label"] for c in diff["added"]][:2]
        parts = []
        if top:
            parts.append(f"Your strongest signal right now is {top[0][0]}.")
        if up:
            parts.append(f"Lately you've been leaning into {', '.join(up)}.")
        if added:
            parts.append(f"You've started showing interest in {', '.join(added)}.")
        if down:
            parts.append(f"{', '.join(down)} has cooled off since we first met.")
        if len(parts) > 1:
            return " ".join(parts)
        return parts[0] if parts else "Your profile is steady — nothing has shifted sharply yet."

    if top:
        return (
            f"You're at the start of your story. So far, {top[0][0]} stands out most; "
            f"keep building evidence and Novi will track how it changes over time."
        )
    return "Novi is still getting to know you — answer a few questions to start your graph."


# --------------------------------------------------------------------------- trends

def build_trend(db: Session, user: User, days: int = 90) -> dict:
    """Per ``dimension -> label`` daily series of confidence, for charting."""
    since = datetime.now() - timedelta(days=days)
    rows = list(
        db.scalars(
            select(DimensionSignal)
            .where(DimensionSignal.user_id == user.id, DimensionSignal.created_at >= since)
            .order_by(DimensionSignal.id.asc())
        )
    )
    series: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        day = row.created_at.date().isoformat() if row.created_at else None
        bucket = series[row.dimension][row.label]
        if bucket and bucket[-1]["date"] == day:
            bucket[-1]["confidence"] = row.confidence_after
        else:
            bucket.append({"date": day, "confidence": row.confidence_after})
    return {
        "window_days": days,
        "dimensions": {dim: {label: points for label, points in labels.items()} for dim, labels in series.items()},
    }


# --------------------------------------------------------------------------- bootstrap

def _record_event_once(
    db: Session,
    user: User,
    event_type: str,
    title: str,
    tags: list | None,
    created_at: datetime | None,
) -> bool:
    """Backfill helper: only insert if an equivalent event is not already logged."""
    conditions = [
        AppEvent.user_id == user.id,
        AppEvent.event_type == (event_type or "generic")[:64],
        AppEvent.title == (title or "")[:255],
    ]
    if created_at is not None:
        conditions.append(AppEvent.created_at == created_at)
    if db.scalar(select(AppEvent.id).where(*conditions).limit(1)) is not None:
        return False
    record_event(db, user, event_type, title, tags, created_at=created_at)
    return True


def backfill(db: Session, user: User) -> dict:
    """One-shot: seed the graph + event log from data the student already has.

    Idempotent — safe to call repeatedly. Signals are only seeded when the graph is
    still empty, and events are de-duplicated, so running it twice changes nothing.
    """
    from app.models.checkin import WeeklyCheckin
    from app.models.passport import PassportItem
    from app.models.roadmap import RoadmapItem, Task, WeeklyPriority
    from app.models.enums import TaskStatus
    from app.services.career_dna import get_dna

    dna = get_dna(user, db)
    counts = {"signals": 0, "events": 0, "milestones": 0}

    if dna is not None and not current_scores(db, user):
        counts["signals"] = record_signals_from_dna(db, user, dna, source="backfill")

    def _event(event_type: str, title: str, text: str, extra: list | None, at: datetime | None) -> None:
        if _record_event_once(db, user, event_type, title, event_tags(user, db, text, extra), at):
            counts["events"] += 1

    for item in db.scalars(select(PassportItem).where(PassportItem.user_id == user.id)):
        _event(f"passport_{item.category.value}", item.title,
               f"{item.title} {item.description or ''}", item.skills, item.created_at)

    for item in db.scalars(
        select(RoadmapItem).where(RoadmapItem.user_id == user.id, RoadmapItem.completed.is_(True))
    ):
        _event("roadmap_step_done", item.title, item.title, None, item.created_at)

    for prio in db.scalars(
        select(WeeklyPriority).where(WeeklyPriority.user_id == user.id, WeeklyPriority.completed.is_(True))
    ):
        _event("priority_done", prio.title, prio.title, None, prio.created_at)

    for task in db.scalars(
        select(Task).where(Task.user_id == user.id, Task.status == TaskStatus.DONE)
    ):
        _event("task_done", task.title, task.title, None, task.created_at)

    for checkin in db.scalars(
        select(WeeklyCheckin).where(WeeklyCheckin.user_id == user.id, WeeklyCheckin.status != "draft")
    ):
        _event("checkin", f"Week of {checkin.week_start}",
               f"{checkin.accomplishments} {checkin.learnings}", None, checkin.updated_at)

    counts["milestones"] = sync_milestones_from_roadmap(db, user)
    snapshot(db, user, force=True)
    return counts
