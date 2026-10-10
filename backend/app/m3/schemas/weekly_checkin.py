import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WeeklyCheckinCreate(BaseModel):
    week_start_date: date
    accomplished: str | None = None
    learned: str | None = None
    challenged: str | None = None
    proud_of: str | None = None
    improve_next: str | None = None


class WeeklyCheckinUpdate(BaseModel):
    accomplished: str | None = None
    learned: str | None = None
    challenged: str | None = None
    proud_of: str | None = None
    improve_next: str | None = None


class WeeklyCheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    roadmap_id: uuid.UUID
    week_start_date: date
    accomplished: str | None
    learned: str | None
    challenged: str | None
    proud_of: str | None
    improve_next: str | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Step 10: Weekly Summary schemas
# ---------------------------------------------------------------------------


class GeneratedWeeklySummary(BaseModel):
    """Pydantic schema for parsing Gemini's structured JSON output."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=50, max_length=3000)
    highlights: list[str] = Field(min_length=1, max_length=5)
    encouragement: str = Field(min_length=10, max_length=500)
    focus_for_next_week: str = Field(min_length=10, max_length=500)


class WeeklySummaryResponse(BaseModel):
    """API response for the weekly summary endpoint."""

    checkin_id: uuid.UUID
    roadmap_id: uuid.UUID
    week_start_date: date
    roadmap_title: str
    progress_percentage: float
    summary: str
    highlights: list[str]
    encouragement: str
    focus_for_next_week: str
