from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel

PASSPORT_CATEGORIES = (
    "projects",
    "competitions",
    "certifications",
    "leadership",
    "research",
    "activities",
    "achievements",
)


class PassportItemCreate(BaseModel):
    category: str = Field(pattern="^(projects|competitions|certifications|leadership|research|activities|achievements)$")
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    skills: list[str] = []
    date_achieved: date | None = None
    certificate_url: str | None = None


class PassportItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    skills: list[str] | None = None
    date_achieved: date | None = None
    certificate_url: str | None = None
    verified: bool | None = None


class PassportItemOut(ORMModel):
    id: int
    category: str
    title: str
    description: str
    skills: list | None = None
    date_achieved: date | None = None
    certificate_url: str | None = None
    verified: bool
    created_at: datetime | None = None


class PassportCompletionOut(BaseModel):
    score: int
    by_category: dict[str, int]  # percentage per category
    categories_covered: list[str]
    suggested_next: str
    dna_focus: str | None = None
    novi_note: str | None = None