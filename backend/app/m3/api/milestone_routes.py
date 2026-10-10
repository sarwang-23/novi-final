import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.m3.schemas.milestone import MilestoneCreate, MilestoneProgressResponse, MilestoneResponse, MilestoneUpdate
from app.m3.services.milestone_service import MilestoneService
from app.m3.api.task_routes import router as task_router


router = APIRouter()
router.include_router(task_router)


def _service_error(error: Exception) -> HTTPException:
    if isinstance(error, LookupError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, PermissionError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones",
    response_model=MilestoneResponse,
    status_code=201,
)
def create_milestone(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    data: MilestoneCreate,
    db: Session = Depends(get_db),
):
    try:
        return MilestoneService(db).create(student_id, goal_id, roadmap_id, data)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones",
    response_model=list[MilestoneResponse],
)
def list_milestones(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return MilestoneService(db).list(student_id, goal_id, roadmap_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
)
def get_milestone(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return MilestoneService(db).get(student_id, goal_id, roadmap_id, milestone_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.patch(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
)
def update_milestone(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
    db: Session = Depends(get_db),
):
    try:
        return MilestoneService(db).update(student_id, goal_id, roadmap_id, milestone_id, data)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.delete(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}",
    status_code=204,
)
def delete_milestone(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        MilestoneService(db).delete(student_id, goal_id, roadmap_id, milestone_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}/progress",
    response_model=MilestoneProgressResponse,
    summary="Get milestone progress",
    description="Returns dynamic task completion progress for a milestone. Progress = completed tasks / total tasks * 100. Skipped and active tasks do not count.",
)
def get_milestone_progress(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return MilestoneService(db).get_progress(student_id, goal_id, roadmap_id, milestone_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error