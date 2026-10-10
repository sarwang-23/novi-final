from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.models.growth import AppEvent, DimensionSignal, GraphSnapshot, GrowthMilestone
from app.models.user import User
from app.schemas.growth import (
    EventCreate,
    EventOut,
    MilestoneOut,
    MilestoneUpdate,
    SignalOut,
    SnapshotOut,
)
from app.services import growth as growth_service

router = APIRouter(prefix="/growth", tags=["growth"])


# --------------------------------------------------------------------------- graph & index

@router.get("/graph")
async def graph(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    """The current Student Graph: latest confidence per dimension and label."""
    scores = growth_service.current_scores(db, user)
    return {
        "dimensions": {
            dim: sorted(
                ({"label": label, "confidence": conf} for label, conf in labels.items()),
                key=lambda row: row["confidence"],
                reverse=True,
            )
            for dim, labels in scores.items()
        },
        "label_count": sum(len(labels) for labels in scores.values()),
    }


@router.get("/index")
async def index(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    """Internal composite Growth Index — components plus a transparent weighted score."""
    payload = growth_service.growth_index(db, user)
    payload["narrative"] = growth_service.narrative(db, user)
    return payload


@router.get("/narrative")
async def narrative(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return {"narrative": growth_service.narrative(db, user)}


@router.get("/trends")
async def trends(
    days: int = Query(default=90, ge=1, le=730),
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return growth_service.build_trend(db, user, days=days)


# --------------------------------------------------------------------------- signals

@router.get("/signals", response_model=list[SignalOut])
async def signals(
    dimension: str | None = None,
    label: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    stmt = select(DimensionSignal).where(DimensionSignal.user_id == user.id)
    if dimension:
        stmt = stmt.where(DimensionSignal.dimension == dimension.strip().lower())
    if label:
        stmt = stmt.where(DimensionSignal.label == label.strip().lower())
    stmt = stmt.order_by(DimensionSignal.id.desc()).limit(limit)
    return list(db.scalars(stmt))


# --------------------------------------------------------------------------- behaviour & alignment

@router.get("/alignment")
async def alignment(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return growth_service.say_do_alignment(db, user)


@router.get("/events", response_model=list[EventOut])
async def events(
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    stmt = (
        select(AppEvent)
        .where(AppEvent.user_id == user.id)
        .order_by(AppEvent.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


@router.post("/events", response_model=EventOut)
async def create_event(
    data: EventCreate,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return growth_service.record_event(db, user, data.event_type, data.title, data.tags)


# --------------------------------------------------------------------------- milestones

@router.get("/milestones", response_model=list[MilestoneOut])
async def milestones(
    status: str | None = None,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    stmt = select(GrowthMilestone).where(GrowthMilestone.user_id == user.id)
    if status:
        stmt = stmt.where(GrowthMilestone.status == status)
    stmt = stmt.order_by(GrowthMilestone.id.desc())
    return list(db.scalars(stmt))


@router.post("/milestones/sync")
async def sync_milestones(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    count = growth_service.sync_milestones_from_roadmap(db, user)
    return {"synced": count, "completion": growth_service.milestone_completion(db, user)}


@router.patch("/milestones/{milestone_id}", response_model=MilestoneOut)
async def update_milestone(
    milestone_id: int,
    data: MilestoneUpdate,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    milestone = db.get(GrowthMilestone, milestone_id)
    if not milestone or milestone.user_id != user.id:
        raise HTTPException(status_code=404, detail="Milestone not found")
    if data.status is not None:
        milestone.status = data.status
        milestone.completed_at = None if data.status != "done" else datetime.now()
    if data.self_rated_helpful is not None:
        milestone.self_rated_helpful = data.self_rated_helpful
    db.commit()
    db.refresh(milestone)
    return milestone


# --------------------------------------------------------------------------- snapshots & diff

@router.get("/snapshots", response_model=list[SnapshotOut])
async def snapshots(
    limit: int = Query(default=24, ge=1, le=200),
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    stmt = (
        select(GraphSnapshot)
        .where(GraphSnapshot.user_id == user.id)
        .order_by(GraphSnapshot.snapshot_date.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


@router.post("/snapshots/run")
async def run_snapshot(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    snap = growth_service.snapshot(db, user, force=True)
    pair = growth_service.latest_pair(db, user)
    diff = (
        growth_service.diff_snapshots(pair[1].payload, pair[0].payload)
        if len(pair) >= 2
        else {"added": [], "removed": [], "changed": [], "threshold": 10.0}
    )
    return {
        "snapshot_date": snap.snapshot_date,
        "label_count": sum(len(labels) for labels in (snap.payload or {}).values()),
        "diff": diff,
        "narrative": growth_service.narrative(db, user),
    }


@router.get("/snapshots/diff")
async def snapshot_diff(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    pair = growth_service.latest_pair(db, user)
    if len(pair) < 2:
        return {
            "diff": {"added": [], "removed": [], "changed": [], "threshold": 10.0},
            "snapshots": [s.snapshot_date for s in pair],
            "narrative": growth_service.narrative(db, user),
        }
    return {
        "diff": growth_service.diff_snapshots(pair[1].payload, pair[0].payload),
        "snapshots": [pair[1].snapshot_date, pair[0].snapshot_date],
        "narrative": growth_service.narrative(db, user),
    }


# --------------------------------------------------------------------------- bootstrap

@router.post("/backfill")
async def backfill(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    """Seed the graph + event log from DNA, passport, roadmap and check-ins."""
    counts = growth_service.backfill(db, user)
    return {"backfilled": counts, "index": growth_service.growth_index(db, user)}
