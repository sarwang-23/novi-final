from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SnapshotCreate(BaseModel):
    label: str = Field(default="", max_length=160)
    note: str = Field(default="", max_length=2000)


class SnapshotUpdate(BaseModel):
    label: Optional[str] = Field(default=None, max_length=160)
    note: Optional[str] = Field(default=None, max_length=2000)


class SnapshotDelta(BaseModel):
    """What changed vs the previous chronological snapshot (gradual progress view)."""
    traits_added: list[str] = Field(default_factory=list)
    traits_removed: list[str] = Field(default_factory=list)
    motivations_added: list[str] = Field(default_factory=list)
    motivations_removed: list[str] = Field(default_factory=list)
    strengths_added: list[str] = Field(default_factory=list)
    strengths_removed: list[str] = Field(default_factory=list)
    development_areas_added: list[str] = Field(default_factory=list)
    development_areas_removed: list[str] = Field(default_factory=list)
    interests_added: list[str] = Field(default_factory=list)
    interests_removed: list[str] = Field(default_factory=list)
    subjects_added: list[str] = Field(default_factory=list)
    subjects_removed: list[str] = Field(default_factory=list)
    skills_added: list[str] = Field(default_factory=list)
    skills_removed: list[str] = Field(default_factory=list)
    career_zones_added: list[str] = Field(default_factory=list)
    career_zones_removed: list[str] = Field(default_factory=list)
    values_added: list[str] = Field(default_factory=list)
    values_removed: list[str] = Field(default_factory=list)
    goals_added: list[str] = Field(default_factory=list)
    goals_removed: list[str] = Field(default_factory=list)


class SnapshotOut(BaseModel):
    id: int
    user_id: int
    label: str
    note: str
    traits: list[str] = Field(default_factory=list)
    motivations: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    development_areas: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    subjects: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    career_zones: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    delta: Optional[SnapshotDelta] = None
