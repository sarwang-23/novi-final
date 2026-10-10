import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.models.user import User
from app.m3.db.models import Student as M3Student


def ensure_m3_student(db: Session, user: User) -> M3Student:
    """Return the module-3 Student row for the authenticated user, creating it on first use."""
    student = db.scalars(select(M3Student).where(M3Student.user_id == user.id)).first()
    if student is not None:
        return student
    student = M3Student(user_id=user.id, external_id=f"user-{user.id}")
    db.add(student)
    try:
        db.commit()
    except Exception:
        db.rollback()
        db.add(student)
        db.commit()
    db.refresh(student)
    return student


def get_m3_student_id(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_student),
) -> uuid.UUID:
    """Resolve the current student's module-3 UUID (used by the /students/me helper)."""
    return ensure_m3_student(db, user).id


def student_matches_authenticated_user(
    student_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_student),
) -> uuid.UUID | None:
    """Guard: the path student_id must belong to the authenticated student.

    Registering this dependency on a router forces every nested route to operate
    only on the authenticated student's module-3 records.
    """
    if student_id is not None:
        if student_id != ensure_m3_student(db, user).id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="student_id does not match the authenticated student",
            )
    return student_id