from pydantic import BaseModel

from app.schemas.common import ORMModel


class CareerDNAOut(ORMModel):
    id: int
    user_id: int
    traits: list | None = None
    motivations: list | None = None
    strengths: list | None = None
    development_areas: list | None = None
    interests: list | None = None
    subjects: list | None = None
    skills: list | None = None
    career_zones: list | None = None
    values: list | None = None
    goals: list | None = None
    novi_reflection: str | None = None
    dna_filled: bool = False
    updated_at: str | None = None
    sources: dict | None = None
    excluded: list | None = None


class CareerDNAUpdate(BaseModel):
    traits: list | None = None
    motivations: list | None = None
    strengths: list | None = None
    development_areas: list | None = None
    interests: list | None = None
    subjects: list | None = None
    skills: list | None = None
    career_zones: list | None = None
    values: list | None = None
    goals: list | None = None
    novi_reflection: str | None = None
    dna_filled: bool | None = None


class ReflectionUpdate(BaseModel):
    accepted: bool
    feedback: str | None = None


class MagicDNARequest(BaseModel):
    text: str