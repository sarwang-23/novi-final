from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    category: str = "career"
    target_date: date | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    description: str | None = None


class GoalOut(ORMModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    target_date: date | None = None
    created_at: datetime | None = None


class RoadmapGenerateRequest(BaseModel):
    goal_id: int | None = None
    title: str | None = None        # used when goal_id is None
    text: str | None = None         # free-form "what I want" from the roadmap input


class RoadmapItemOut(ORMModel):
    id: int
    grade: int
    stage: str
    title: str
    description: str
    category: str
    order_index: int
    completed: bool


class RoadmapOut(BaseModel):
    goal: GoalOut | None = None
    stages: dict[int, list[RoadmapItemOut]] = {}  # grade -> items
    short_term: list[RoadmapItemOut] = []         # do-now items (this week/next few weeks)
    progress_percent: int = 0


class PriorityGenerateRequest(BaseModel):
    pass


class PriorityOut(ORMModel):
    id: int
    week_start: date
    ordinal: int
    skill_category: str
    title: str
    minutes: int
    completed: bool


class PriorityCompleteRequest(BaseModel):
    completed: bool


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    category: str = "build"
    due_date: date | None = None


class TaskUpdate(BaseModel):
    status: str | None = None
    title: str | None = None
    description: str | None = None


class TaskOut(ORMModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    due_date: date | None = None
    created_at: datetime | None = None