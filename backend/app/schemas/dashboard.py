from pydantic import BaseModel

from app.schemas.career import CareerMatchOut
from app.schemas.career_dna import CareerDNAOut
from app.schemas.checkin import CheckinOut
from app.schemas.passport import PassportItemOut, PassportCompletionOut
from app.schemas.roadmap import GoalOut, PriorityOut, RoadmapItemOut, TaskOut


class FocusChip(BaseModel):
    kind: str = "priority"                  # "task" | "roadmap" | "priority"
    id: int | None = None
    title: str
    why: str


class ProgressIndicators(BaseModel):
    career_direction: str = "Exploring"      # "On Track" | "Exploring" | "Needs Focus"
    profile_strength: int = 0
    university_readiness: int = 0
    roadmap_progress: int = 0


class StudentDashboardOut(BaseModel):
    greeting: str
    today_focus: FocusChip | None = None
    progress: ProgressIndicators
    novi_says: str
    novi_says_action: str | None = None
    dna: CareerDNAOut | None = None
    career_matches: list[CareerMatchOut] = []
    goals: list[GoalOut] = []
    roadmap_items: list[RoadmapItemOut] = []
    priorities: list[PriorityOut] = []
    passport: list[PassportItemOut] = []
    passport_completion: PassportCompletionOut | None = None
    current_checkin: CheckinOut | None = None
    next_task: TaskOut | None = None


class ParentChildSummary(BaseModel):
    name: str
    grade: int | None = None
    career_direction: str = "Exploring"
    profile_strength: int = 0
    university_readiness: int = 0
    month_focus: list[str] = []
    insight: str


class ParentDashboardOut(BaseModel):
    children: list[ParentChildSummary]
    insight: str