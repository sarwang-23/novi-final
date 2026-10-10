import uuid
from datetime import date
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class TaskDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    order_index: int = Field(ge=0, default=0)
    target_date: date | None = None


class AddTaskAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: Literal["add_task"] = "add_task"
    milestone_id: uuid.UUID
    task: TaskDetails
    reason: str = Field(min_length=1, max_length=1000)


class SkipTaskAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: Literal["skip_task"] = "skip_task"
    task_id: uuid.UUID
    reason: str = Field(min_length=1, max_length=1000)


class RescheduleTaskAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: Literal["reschedule_task"] = "reschedule_task"
    task_id: uuid.UUID
    new_target_date: date
    reason: str = Field(min_length=1, max_length=1000)


class AdjustPriorityAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: Literal["adjust_priority"] = "adjust_priority"
    task_id: uuid.UUID
    new_priority: Literal["low", "medium", "high"]
    reason: str = Field(min_length=1, max_length=1000)


class RescheduleRoadmapAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: Literal["reschedule_roadmap"] = "reschedule_roadmap"
    new_target_date: date
    reason: str = Field(min_length=1, max_length=1000)


AdaptationAction = Annotated[
    Union[
        AddTaskAction,
        SkipTaskAction,
        RescheduleTaskAction,
        AdjustPriorityAction,
        RescheduleRoadmapAction,
    ],
    Field(discriminator="action_type"),
]


class GeneratedAdaptation(BaseModel):
    """Pydantic schema for parsing Gemini structured AI adaptation recommendations."""

    model_config = ConfigDict(extra="forbid")

    assessment: str = Field(min_length=5, max_length=1000)
    reasoning: str = Field(min_length=10, max_length=3000)
    recommended_actions: list[AdaptationAction] = Field(default_factory=list)


class AdaptationPreviewResponse(BaseModel):
    """Response schema for the adaptation preview endpoint."""

    roadmap_id: uuid.UUID
    goal_id: uuid.UUID
    assessment: str
    reasoning: str
    progress_percentage: float
    recommended_actions: list[AdaptationAction]


class AdaptationApplyRequest(BaseModel):
    """Request schema for applying an adaptation plan."""

    model_config = ConfigDict(extra="forbid")

    actions: list[AdaptationAction] = Field(default_factory=list)


class AdaptationApplyResponse(BaseModel):
    """Response schema after applying an adaptation plan."""

    roadmap_id: uuid.UUID
    applied_actions_count: int
    message: str
    roadmap_target_date: date | None
    progress_percentage: float
