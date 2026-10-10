import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MilestoneStatus = Literal["pending", "active", "completed", "skipped"]


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    target_date: date | None = None
    status: MilestoneStatus = "pending"
    order_index: int = Field(ge=0)


class MilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    target_date: date | None = None
    status: MilestoneStatus | None = None
    order_index: int | None = Field(default=None, ge=0)


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    roadmap_id: uuid.UUID
    title: str
    description: str | None
    start_date: date | None
    target_date: date | None
    status: MilestoneStatus
    order_index: int
    created_at: datetime
    updated_at: datetime


class MilestoneProgressResponse(BaseModel):
    """Step 8B: Dynamic milestone progress — computed from task statuses, not stored."""

    milestone_id: uuid.UUID
    total_tasks: int
    completed_tasks: int
    active_tasks: int
    pending_tasks: int
    skipped_tasks: int
    progress_percentage: float