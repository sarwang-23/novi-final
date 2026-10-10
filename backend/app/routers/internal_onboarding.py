from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.onboarding_data import StudentProfile
from app.models.user import User

router = APIRouter(prefix="/internal/onboarding", tags=["internal"], include_in_schema=False)


async def verify_internal_secret(x_internal_secret: str = Header(..., alias="X-Internal-Secret")):
    if x_internal_secret != settings.INTERNAL_SHARED_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal secret")


class UniversityIn(BaseModel):
    university_name: str
    location: str
    confidence: str


class CareerIn(BaseModel):
    career_name: str
    interest_reason_summary: str


class GoalIn(BaseModel):
    goal_summary: str


def _get_or_create_profile(db: Session, student_id: int) -> StudentProfile:
    profile = db.get(StudentProfile, student_id)
    if profile is None:
        profile = StudentProfile(student_id=student_id)
        db.add(profile)
    return profile


@router.post("/{student_id}/university")
def upsert_university(
    student_id: int,
    data: UniversityIn,
    db: Session = Depends(get_db),
    _: None = Depends(verify_internal_secret),
):
    profile = _get_or_create_profile(db, student_id)
    profile.university_name = data.university_name
    profile.university_location = data.location
    profile.university_extraction_conf = data.confidence
    db.commit()
    return {"status": "ok"}


@router.post("/{student_id}/career")
def upsert_career(
    student_id: int,
    data: CareerIn,
    db: Session = Depends(get_db),
    _: None = Depends(verify_internal_secret),
):
    profile = _get_or_create_profile(db, student_id)
    profile.career_name = data.career_name
    profile.career_interest_reason = data.interest_reason_summary
    db.commit()
    return {"status": "ok"}


@router.post("/{student_id}/goal")
def upsert_goal(
    student_id: int,
    data: GoalIn,
    db: Session = Depends(get_db),
    _: None = Depends(verify_internal_secret),
):
    profile = _get_or_create_profile(db, student_id)
    profile.primary_goal = data.goal_summary
    db.commit()
    return {"status": "ok"}