"""Career DNA snapshot service.

A snapshot freezes the student's DNA at one point in time. Because DNA evolves
gradually across many years (teen -> young adult), we keep a chronological
timeline: you save a snapshot ("my DNA, age 14"), then years later it drifts,
you save another, and the DELTA shows exactly what progressed between two
snapshots (which traits/subjects/skills/interests/values were added or left).
Updating a label/note and deleting stale snapshots keeps the timeline clean
for years.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.career_dna import CareerDNA
from app.models.career_dna_snapshot import CareerDNASnapshot
from app.models.user import User
from app.schemas.career_dna_snapshot import SnapshotCreate, SnapshotDelta, SnapshotUpdate

DNA_LIST_FIELDS = [
    "traits",
    "motivations",
    "strengths",
    "development_areas",
    "interests",
    "subjects",
    "skills",
    "career_zones",
    "values",
    "goals",
]


def _frozen(dna: CareerDNA | None) -> dict:
    """Copy current DNA lists so the snapshot is immutable going forward."""
    out: dict = {}
    for f in DNA_LIST_FIELDS:
        value = getattr(dna, f, None) if dna else None
        out[f] = [str(x) for x in (value or [])]
    return out


def _delta(prev: CareerDNASnapshot, cur: CareerDNASnapshot) -> SnapshotDelta:
    """Compute what progressed between two chronological snapshots."""
    delta = {}
    for f in DNA_LIST_FIELDS:
        p = set(getattr(prev, f) or [])
        c = set(getattr(cur, f) or [])
        delta[f + "_added"] = sorted(c - p)
        delta[f + "_removed"] = sorted(p - c)
    return SnapshotDelta(**delta)


def save_snapshot(user: User, data: SnapshotCreate, db: Session) -> CareerDNASnapshot:
    dna = db.execute(
        select(CareerDNA).where(CareerDNA.user_id == user.id)
    ).scalars().first()
    fields = _frozen(dna)
    snap = CareerDNASnapshot(
        user_id=user.id,
        label=data.label or f"My DNA · {datetime.now():%b %Y}",
        note=data.note,
        **fields,
        dna_filled=bool(dna and dna.dna_filled),
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def list_snapshots(user: User, db: Session) -> list[CareerDNASnapshot]:
    snaps = db.execute(
        select(CareerDNASnapshot)
        .where(CareerDNASnapshot.user_id == user.id)
        .order_by(CareerDNASnapshot.created_at.asc())
    ).scalars().all()
    # Attach the in-memory delta (vs previous chronological snapshot) for each one.
    result = []
    prev = None
    for s in snaps:
        d = _delta(prev, s) if prev else None
        setattr(s, "_snapshot_delta", d)
        result.append(s)
        prev = s
    return result


def get_snapshot(user: User, snap_id: int, db: Session) -> CareerDNASnapshot:
    snap = db.execute(
        select(CareerDNASnapshot).where(
            CareerDNASnapshot.id == snap_id, CareerDNASnapshot.user_id == user.id
        )
    ).scalars().first()
    if not snap:
        raise LookupError("snapshot not found")
    return snap


def update_snapshot(
    user: User, snap_id: int, data: SnapshotUpdate, db: Session
) -> CareerDNASnapshot:
    snap = get_snapshot(user, snap_id, db)
    if data.label is not None:
        snap.label = data.label
    if data.note is not None:
        snap.note = data.note
    db.commit()
    db.refresh(snap)
    return snap


def delete_snapshot(user: User, snap_id: int, db: Session) -> None:
    snap = get_snapshot(user, snap_id, db)
    db.delete(snap)
    db.commit()
