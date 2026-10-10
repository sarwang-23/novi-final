from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GeneratedTaskPriority = Literal["low", "medium", "high"]


class GeneratedTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    order_index: int = Field(ge=0)
    priority: GeneratedTaskPriority


class GeneratedMilestone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    order_index: int = Field(ge=0)
    tasks: list[GeneratedTask] = Field(min_length=1, max_length=20)


class GeneratedRoadmap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=4000)
    milestones: list[GeneratedMilestone] = Field(min_length=1, max_length=20)