from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.models.user import User
from app.schemas.dashboard import StudentDashboardOut
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=StudentDashboardOut)
async def student_dashboard(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return dashboard_service.student_dashboard(db, user)  # type: ignore[arg-type]