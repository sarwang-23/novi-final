import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.m3.schemas.weekly_checkin import (
    WeeklyCheckinCreate,
    WeeklyCheckinResponse,
    WeeklyCheckinUpdate,
    WeeklySummaryResponse,
)
from app.m3.services.checkin_service import ConflictError, WeeklyCheckinService
from app.m3.services.summary_service import ServiceUnavailableError, WeeklySummaryService

router = APIRouter()


def _service_error(error: Exception) -> HTTPException:
    if isinstance(error, LookupError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, PermissionError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    if isinstance(error, ConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, ServiceUnavailableError):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/checkins",
    response_model=WeeklyCheckinResponse,
    status_code=201,
)
def create_weekly_checkin(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    data: WeeklyCheckinCreate,
    db: Session = Depends(get_db),
):
    try:
        return WeeklyCheckinService(db).create(student_id, goal_id, roadmap_id, data)
    except (LookupError, PermissionError, ConflictError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/checkins",
    response_model=list[WeeklyCheckinResponse],
)
def list_weekly_checkins(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return WeeklyCheckinService(db).list(student_id, goal_id, roadmap_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/checkins/{checkin_id}",
    response_model=WeeklyCheckinResponse,
)
def get_weekly_checkin(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return WeeklyCheckinService(db).get(student_id, goal_id, roadmap_id, checkin_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.patch(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/checkins/{checkin_id}",
    response_model=WeeklyCheckinResponse,
)
def update_weekly_checkin(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    checkin_id: uuid.UUID,
    data: WeeklyCheckinUpdate,
    db: Session = Depends(get_db),
):
    try:
        return WeeklyCheckinService(db).update(
            student_id, goal_id, roadmap_id, checkin_id, data
        )
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/checkins/{checkin_id}/summary",
    response_model=WeeklySummaryResponse,
)
def get_weekly_summary(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return WeeklySummaryService(db).generate(
            student_id, goal_id, roadmap_id, checkin_id
        )
    except (
        LookupError,
        PermissionError,
        ConflictError,
        ServiceUnavailableError,
        ValueError,
    ) as error:
        raise _service_error(error) from error

