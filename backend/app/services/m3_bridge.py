"""m3_bridge — clean propagation seam between the V1 flow and the m3 roadmap engine.

The legacy product owns goals, the m3 engine owns date-scheduled roadmaps. This
module keeps the two in step without ever importing ``app.services.roadmap``
(the roadmp service imports the bridge, so the bridge must not import it back):

  legacy goal   ->  m3 Goal  (``sync_goal_to_m3``)
  m3 generation ->  m3 Roadmap + Milestones + Tasks (``generate_and_activate_roadmap``)
  m3 roadmap    ->  legacy RoadmapItems, grade 9-12 derivation (``mirror_roadmap_to_legacy``)
  m3 task state ->  legacy RoadmapItem completion (``reconcile_legacy_items`` / ``sync_item_completion``)
  m3 progress   ->  unified dashboard progress (``progress_percentage``)
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.roadmap import Goal as LegacyGoal
from app.models.roadmap import RoadmapItem as LegacyRoadmapItem
from app.models.user import User
from app.m3.db.models import (
    Goal as M3Goal,
    Milestone as M3Milestone,
    Roadmap as M3Roadmap,
    Student as M3Student,
    Task as M3Task,
)
from app.m3.repositories.roadmap_repository import RoadmapRepository
from app.m3.services.roadmap_generator import RoadmapGenerator
from app.m3.services.roadmap_orchestrator import generate_and_persist_roadmap

_LEGACY_TYPE_TO_M3 = {"career": "career", "university": "university", "personal": "personal"}
_LEGACY_STATUS_TO_M3 = {"active": "active", "completed": "completed", "paused": "paused"}
_PRIORITY_TO_CATEGORY = {"high": "build", "medium": "grow", "low": "explore"}


# --------------------------------------------------------------------------- student / goal sync
def ensure_m3_student(db: Session, user: User, *, commit: bool = False) -> M3Student:
    student = db.scalars(select(M3Student).where(M3Student.user_id == user.id)).first()
    if student is not None:
        return student
    student = M3Student(user_id=user.id, external_id=f"user-{user.id}")
    db.add(student)
    if commit:
        db.commit()
        db.refresh(student)
    else:
        db.flush()
    return student


def _enum_value(value) -> str | None:
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def _goal_type(goal: LegacyGoal) -> str:
    return _LEGACY_TYPE_TO_M3.get(str(_enum_value(getattr(goal, "category", None))), "career")


def _goal_status(goal: LegacyGoal) -> str:
    return _LEGACY_STATUS_TO_M3.get(str(_enum_value(getattr(goal, "status", None))), "active")


def _apply_goal_updates(existing: M3Goal, goal: LegacyGoal) -> None:
    title = (goal.title or "").strip()
    if title and existing.title != title[:200]:
        existing.title = title[:200]
    if goal.description is not None and existing.description != (goal.description or None):
        existing.description = goal.description or None
    if goal.target_date != existing.target_date:
        existing.target_date = goal.target_date
    mapped_status = _goal_status(goal)
    if existing.status != mapped_status:
        existing.status = mapped_status


def sync_goal_to_m3(
    db: Session,
    user: User,
    goal: LegacyGoal,
    *,
    student: M3Student | None = None,
    commit: bool = False,
) -> M3Goal:
    """Create or refresh the m3 Goal mirror of a legacy goal (idempotent)."""
    student = student or ensure_m3_student(db, user, commit=commit)
    existing = db.scalar(select(M3Goal).where(M3Goal.legacy_goal_id == goal.id))
    if existing is not None:
        _apply_goal_updates(existing, goal)
        if commit:
            db.commit()
        else:
            db.flush()
        return existing
    m3_goal = M3Goal(
        student_id=student.id,
        legacy_goal_id=goal.id,
        goal_type=_goal_type(goal),
        title=(goal.title or "")[:200],
        description=goal.description or None,
        target_date=goal.target_date,
        status=_goal_status(goal),
        priority="medium",
    )
    db.add(m3_goal)
    if commit:
        db.commit()
        db.refresh(m3_goal)
    else:
        db.flush()
    return m3_goal


def m3_goal_for(db: Session, user: User, goal: LegacyGoal) -> M3Goal | None:
    return db.scalar(select(M3Goal).where(M3Goal.legacy_goal_id == goal.id))


# --------------------------------------------------------------------------- generation context
def build_generation_context(db: Session, user: User) -> dict:
    """Ground m3 generation in the legacy product's best data (best-effort)."""
    context: dict = {
        "career": None,
        "career_match": None,
        "existing_skills": None,
        "skill_gaps": None,
        "readiness": None,
    }
    try:
        from app.services.careers import list_career_matches

        matches = list_career_matches(db, user)
        if matches:
            context["career"] = matches[0].career
            context["career_match"] = matches[0]
    except Exception as exc:
        print(f"[m3_bridge] career match lookup failed: {exc}")
    try:
        from app.services.career_dna import get_dna

        dna = get_dna(user, db)
        if dna is not None and dna.skills:
            context["existing_skills"] = [{"name": s} for s in dna.skills if isinstance(s, str)]
    except Exception as exc:
        print(f"[m3_bridge] career DNA lookup failed: {exc}")
    return context


# --------------------------------------------------------------------------- generation + mirror
def generate_and_activate_roadmap(
    db: Session,
    user: User,
    goal: LegacyGoal,
    *,
    generator: RoadmapGenerator | None = None,
    start_date: date | None = None,
) -> M3Roadmap | None:
    """m3-first generation: persist an active scheduled roadmap, or None on engine failure.

    Any previously active roadmap for this goal is moved to ``abandoned`` first so
    the one-active-roadmap rule is honoured across regenerations.
    """
    m3_goal = sync_goal_to_m3(db, user, goal)
    repo = RoadmapRepository(db)
    existing_active = repo.get_active_by_goal(m3_goal.id)
    if existing_active is not None:
        existing_active.status = "abandoned"
        db.commit()

    ctx = build_generation_context(db, user)
    try:
        gen = generator or RoadmapGenerator()
    except Exception as exc:
        print(f"[m3_bridge] generator unavailable: {exc}")
        db.rollback()
        return None

    try:
        result = generate_and_persist_roadmap(
            student_id=m3_goal.student_id,
            goal_id=m3_goal.id,
            db=db,
            generator=gen,
            goal=m3_goal,
            career=ctx["career"],
            career_match=ctx["career_match"],
            existing_skills=ctx["existing_skills"],
            skill_gaps=ctx["skill_gaps"],
            readiness=ctx["readiness"],
            roadmap_status="active",
            roadmap_start_date=start_date,
        )
        return result.roadmap
    except Exception as exc:
        print(f"[m3_bridge] roadmap generation failed: {exc}")
        db.rollback()
        return None


def mirror_roadmap_to_legacy(db: Session, user: User, goal: LegacyGoal, roadmap: M3Roadmap) -> int:
    """Derive grade 9-12 RoadmapItems from the scheduled m3 roadmap. Returns # items created."""
    from app.models.enums import RoadmapStage
    from app.models.roadmap import RoadmapItem

    for old in db.scalars(select(RoadmapItem).where(RoadmapItem.goal_id == goal.id)):
        db.delete(old)
    db.flush()

    full = RoadmapRepository(db).get_full_hierarchy(roadmap.id)
    if full is None:
        return 0
    milestones = sorted(full.milestones, key=lambda m: (m.order_index, m.created_at, str(m.id)))
    total_ms = len(milestones) or 1
    stage_map = {
        9: RoadmapStage.DISCOVER,
        10: RoadmapStage.EXPLORE,
        11: RoadmapStage.BUILD,
        12: RoadmapStage.APPLY,
    }

    created = 0
    order = 0
    for i, milestone in enumerate(milestones):
        fraction = (i + 0.5) / total_ms
        grade = 12 if fraction >= 0.80 else 11 if fraction >= 0.55 else 10 if fraction >= 0.30 else 9
        tasks = sorted(milestone.tasks, key=lambda t: (t.order_index, t.created_at, str(t.id)))
        for task in tasks:
            desc = f"{milestone.title}: {task.description}" if task.description else milestone.title
            db.add(
                RoadmapItem(
                    user_id=user.id,
                    goal_id=goal.id,
                    grade=grade,
                    stage=stage_map[grade],
                    category=_PRIORITY_TO_CATEGORY.get(task.priority or "medium", "grow"),
                    title=task.title[:255],
                    description=desc,
                    order_index=order,
                    completed=task.status == "completed",
                )
            )
            order += 1
            created += 1
    db.commit()
    return created


# --------------------------------------------------------------------------- completion propagation
def active_roadmap_for(db: Session, user: User, goal: LegacyGoal) -> M3Roadmap | None:
    m3_goal = m3_goal_for(db, user, goal)
    if m3_goal is None:
        return None
    return RoadmapRepository(db).get_active_by_goal(m3_goal.id)


def sync_item_completion(db: Session, user: User, goal: LegacyGoal, legacy_item: LegacyRoadmapItem) -> bool:
    """Push a legacy RoadmapItem toggle into the matching m3 task (by title)."""
    roadmap = active_roadmap_for(db, user, goal)
    if roadmap is None:
        return False
    full = RoadmapRepository(db).get_full_hierarchy(roadmap.id)
    if full is None:
        return False
    for milestone in full.milestones:
        for task in milestone.tasks:
            if task.title and task.title == legacy_item.title:
                if legacy_item.completed and task.status != "completed":
                    task.status = "completed"
                    db.commit()
                elif not legacy_item.completed and task.status == "completed":
                    task.status = "pending"
                    db.commit()
                return True
    return False


def reconcile_legacy_items(db: Session, user: User, goal: LegacyGoal, roadmap: M3Roadmap) -> int:
    """Re-derive every legacy RoadmapItem.completed flag from the m3 roadmap state."""
    full = RoadmapRepository(db).get_full_hierarchy(roadmap.id)
    if full is None:
        return 0
    status_by_title = {
        task.title: task.status for milestone in full.milestones for task in milestone.tasks if task.title
    }
    changed = 0
    for item in db.scalars(select(LegacyRoadmapItem).where(LegacyRoadmapItem.goal_id == goal.id)):
        want = status_by_title.get(item.title)
        if want is None:
            continue
        completed = want == "completed"
        if item.completed != completed:
            item.completed = completed
            changed += 1
    if changed:
        db.commit()
    return changed


def set_goal_roadmap_status(db: Session, user: User, goal: LegacyGoal, status: str) -> int:
    """Move any active m3 roadmap for a goal to ``status`` (e.g. completed/abandoned)."""
    m3_goal = m3_goal_for(db, user, goal)
    if m3_goal is None:
        return 0
    changed = 0
    for rm in db.scalars(
        select(M3Roadmap).where(M3Roadmap.goal_id == m3_goal.id, M3Roadmap.status == "active")
    ):
        rm.status = status
        changed += 1
    if changed:
        db.commit()
    return changed


# --------------------------------------------------------------------------- progress + read views
def progress_percentage(db: Session, user: User, goal_id: int | None = None) -> int | None:
    """Aggregate completion across the user's active m3 roadmaps (optionally one goal).

    Returns None when the user has no active m3 roadmap so callers can fall back to
    the legacy items-based progress.
    """
    student = db.scalars(select(M3Student).where(M3Student.user_id == user.id)).first()
    if student is None:
        return None
    stmt = (
        select(M3Roadmap)
        .join(M3Goal, M3Goal.id == M3Roadmap.goal_id)
        .where(M3Goal.student_id == student.id, M3Roadmap.status == "active")
    )
    if goal_id is not None:
        stmt = stmt.where(M3Goal.legacy_goal_id == goal_id)
    roadmaps = list(db.scalars(stmt))
    if not roadmaps:
        return None
    repo = RoadmapRepository(db)
    total = completed = 0
    for rm in roadmaps:
        counts = repo.get_task_counts_for_roadmap(rm.id)
        total += counts["total"]
        completed += counts["completed"]
    if not total:
        return None
    return round(100 * completed / total)


def active_roadmap_full(db: Session, user: User, goal: LegacyGoal) -> dict | None:
    """Serialize the full active m3 roadmap hierarchy as a JSON-ready dict."""
    from app.m3.services.roadmap_service import RoadmapService

    m3_goal = m3_goal_for(db, user, goal)
    if m3_goal is None:
        return None
    roadmap = RoadmapRepository(db).get_active_by_goal(m3_goal.id)
    if roadmap is None:
        return None
    try:
        full = RoadmapService(db).get_full(m3_goal.student_id, m3_goal.id, roadmap.id)
    except (LookupError, PermissionError):
        return None
    return full.model_dump(mode="json")


def upcoming_tasks(db: Session, user: User, goal: LegacyGoal, limit: int = 5) -> list[dict]:
    full = active_roadmap_full(db, user, goal)
    if full is None:
        return []
    rows = []
    for milestone in full.get("milestones") or []:
        for task in milestone.get("tasks") or []:
            if task.get("status") in ("pending", "active"):
                rows.append(
                    {
                        "task_id": task["id"],
                        "title": task.get("title"),
                        "status": task.get("status"),
                        "priority": task.get("priority"),
                        "target_date": task.get("target_date"),
                        "milestone_title": milestone.get("title"),
                    }
                )
    rows.sort(
        key=lambda t: (t.get("target_date") is None, t.get("target_date") or "", t.get("task_id") or "")
    )
    return rows[:limit]


# --------------------------------------------------------------------------- ownership resolution
def resolve_task_chain(db: Session, user: User, task_id: uuid.UUID) -> dict:
    """Resolve every FK up the chain from a task and verify the user owns it."""
    task = db.get(M3Task, task_id)
    if task is None:
        raise LookupError("Task not found")
    milestone = db.get(M3Milestone, task.milestone_id)
    if milestone is None:
        raise LookupError("Milestone not found")
    roadmap = db.get(M3Roadmap, milestone.roadmap_id)
    if roadmap is None:
        raise LookupError("Roadmap not found")
    m3_goal = db.get(M3Goal, roadmap.goal_id)
    if m3_goal is None:
        raise LookupError("Goal not found")
    student = db.get(M3Student, m3_goal.student_id)
    if student is None or student.user_id != user.id:
        raise PermissionError("Task does not belong to this student")
    legacy_goal = None
    if m3_goal.legacy_goal_id is not None:
        legacy_goal = db.get(LegacyGoal, m3_goal.legacy_goal_id)
    return {
        "student_id": student.id,
        "goal_id": m3_goal.id,
        "roadmap_id": roadmap.id,
        "milestone_id": milestone.id,
        "task_id": task.id,
        "task": task,
        "milestone": milestone,
        "roadmap": roadmap,
        "m3_goal": m3_goal,
        "legacy_goal": legacy_goal,
    }


def resolve_active_roadmap(
    db: Session, user: User, goal_id: int | None
) -> tuple[M3Student, M3Goal, LegacyGoal, M3Roadmap]:
    """Resolve the legacy goal -> m3 goal -> active roadmap chain for the v2 endpoints."""
    legacy_goal = db.get(LegacyGoal, goal_id) if goal_id else None
    if legacy_goal is None or legacy_goal.user_id != user.id:
        raise LookupError("Goal not found")
    m3_goal = m3_goal_for(db, user, legacy_goal)
    if m3_goal is None:
        raise LookupError("No AI scheduled plan yet — generate your roadmap first")
    roadmap = RoadmapRepository(db).get_active_by_goal(m3_goal.id)
    if roadmap is None:
        raise LookupError("No active scheduled plan yet — generate your roadmap first")
    student = db.get(M3Student, m3_goal.student_id)
    if student is None:
        raise LookupError("Student not found")
    return student, m3_goal, legacy_goal, roadmap