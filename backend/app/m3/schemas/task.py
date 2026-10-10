import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TaskStatus = Literal["pending", "active", "completed", "skipped"]
TaskPriority = Literal["low", "medium", "high"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    target_date: date | None = None
    status: TaskStatus = "pending"
    priority: TaskPriority = "medium"
    order_index: int = Field(ge=0)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    target_date: date | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    order_index: int | None = Field(default=None, ge=0)


class TaskRescheduleRequest(BaseModel):
    """Request body for POST .../tasks/{task_id}/reschedule (Step 15)."""

    new_target_date: date = Field(description="New target date for the task.")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    milestone_id: uuid.UUID
    title: str
    description: str | None
    start_date: date | None
    target_date: date | None
    status: TaskStatus
    priority: TaskPriority
    order_index: int
    created_at: datetime
    updated_at: datetime