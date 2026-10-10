from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SignalOut(ORMModel):
    id: int
    dimension: str
    label: str
    signal_value: float
    confidence_before: float
    confidence_after: float
    delta: float
    source: str
    source_ref: str | None = None
    created_at: datetime | None = None


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=64)
    title: str = ""
    tags: list[str] = []


class EventOut(ORMModel):
    id: int
    event_type: str
    title: str
    tags: list | None = None
    created_at: datetime | None = None


class MilestoneOut(ORMModel):
    id: int
    source_type: str
    source_id: int | None = None
    title: str
    status: str
    self_rated_helpful: bool | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class MilestoneUpdate(BaseModel):
    status: str | None = Field(default=None, pattern="^(pending|done|skipped)$")
    self_rated_helpful: bool | None = None


class SnapshotOut(ORMModel):
    id: int
    snapshot_date: date
    payload: dict | None = None
    event_count: int = 0
    created_at: datetime | None = None
