import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GoalType = Literal["career", "university", "personal"]
GoalStatus = Literal["active", "completed", "paused", "abandoned"]
GoalPriority = Literal["low", "medium", "high"]


class GoalCreate(BaseModel):
    goal_type: GoalType
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    target_date: date | None = None
    status: GoalStatus = "active"
    priority: GoalPriority = "medium"
    career_id: uuid.UUID | None = None
    career_match_id: uuid.UUID | None = None


class GoalUpdate(BaseModel):
    goal_type: GoalType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    target_date: date | None = None
    status: GoalStatus | None = None
    priority: GoalPriority | None = None
    career_id: uuid.UUID | None = None
    career_match_id: uuid.UUID | None = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    goal_type: GoalType
    title: str
    description: str | None
    target_date: date | None
    status: GoalStatus
    priority: GoalPriority
    career_id: uuid.UUID | None
    career_match_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime