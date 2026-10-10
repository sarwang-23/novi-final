import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RoadmapStatus = Literal["draft", "active", "paused", "completed", "abandoned"]


class RoadmapCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    target_date: date | None = None
    status: RoadmapStatus = "draft"


class RoadmapUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    target_date: date | None = None
    status: RoadmapStatus | None = None


class RoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goal_id: uuid.UUID
    title: str
    description: str | None
    start_date: date | None
    target_date: date | None
    status: RoadmapStatus
    created_at: datetime
    updated_at: datetime


class RoadmapProgressResponse(BaseModel):
    """Step 8B: Dynamic roadmap progress — computed from all task statuses across milestones."""

    roadmap_id: uuid.UUID
    total_tasks: int
    completed_tasks: int
    active_tasks: int
    pending_tasks: int
    skipped_tasks: int
    progress_percentage: float


class TaskInRoadmap(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    milestone_id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    priority: str
    order_index: int
    start_date: date | None = None
    target_date: date | None = None
    created_at: datetime
    updated_at: datetime


class MilestoneInRoadmap(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    roadmap_id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    order_index: int
    start_date: date | None = None
    target_date: date | None = None
    created_at: datetime
    updated_at: datetime
    total_tasks: int = 0
    completed_tasks: int = 0
    tasks: list[TaskInRoadmap] = Field(default_factory=list)


class RoadmapFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goal_id: uuid.UUID
    title: str
    description: str | None = None
    status: RoadmapStatus
    start_date: date | None = None
    target_date: date | None = None
    created_at: datetime
    updated_at: datetime
    progress_percentage: float = 0.0
    total_tasks: int = 0
    completed_tasks: int = 0
    milestones: list[MilestoneInRoadmap] = Field(default_factory=list)


class TimelineFocusMilestone(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    order_index: int


class TimelineTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    milestone_id: uuid.UUID
    milestone_title: str
    title: str
    description: str | None = None
    status: str
    priority: str
    order_index: int
    start_date: date | None = None
    target_date: date | None = None


class TimelineSummary(BaseModel):
    total: int = 0
    completed: int = 0
    active: int = 0
    pending: int = 0
    skipped: int = 0


class RoadmapTimelineResponse(BaseModel):
    roadmap_id: uuid.UUID
    view: str
    period_start: date
    period_end: date
    is_current: bool
    focus_milestones: list[TimelineFocusMilestone] = Field(default_factory=list)
    tasks: list[TimelineTask] = Field(default_factory=list)
    summary: TimelineSummary = Field(default_factory=TimelineSummary)
