from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CareerOut(ORMModel):
    id: int
    slug: str
    title: str
    category: str
    emoji: str
    summary: str
    salary_range: str | None = None
    outlook: str | None = None
    ranking_profile: str | None = None
    country_rankings: list | None = None


class CareerDetailOut(ORMModel):
    id: int
    slug: str
    title: str
    category: str
    emoji: str
    summary: str
    description: str
    what_they_do: str
    skills: list | None = None
    subjects: list | None = None
    degrees: list | None = None
    industries: list | None = None
    future_paths: list | None = None
    salary_range: str | None = None
    outlook: str | None = None
    ranking_profile: str | None = None
    country_rankings: list | None = None
    fit_rating: float | None = None     # 0-100, present when the user has a stored match
    reasons: list | None = None


class CareerMatchRequest(BaseModel):
    limit: int = Field(default=6, ge=1, le=20)
    focus: str | None = None  # e.g. optional free-text focus


class CareerMatchOut(ORMModel):
    id: int
    rank: int
    score: float
    reasons: list | None = None
    career: CareerDetailOut | None = None


class AdviceStep(BaseModel):
    type: str  # project | skill | explore
    title: str
    why: str
    link: str  # passport | careers | universities | roadmap


class CareerAdviceOut(BaseModel):
    career_slug: str
    fit_rating: float | None = None
    reasons: list | None = None
    fit_statement: str
    next_steps: list[AdviceStep]