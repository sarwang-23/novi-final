import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.m3.schemas.task import TaskCreate, TaskRescheduleRequest, TaskResponse, TaskUpdate
from app.m3.services.task_service import TaskService


router = APIRouter()


def _service_error(error: Exception) -> HTTPException:
    if isinstance(error, LookupError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, PermissionError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}/tasks",
    response_model=TaskResponse,
    status_code=201,
)
def create_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: TaskCreate,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).create(student_id, goal_id, roadmap_id, milestone_id, data)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}/tasks",
    response_model=list[TaskResponse],
)
def list_tasks(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).list(student_id, goal_id, roadmap_id, milestone_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).get(student_id, goal_id, roadmap_id, milestone_id, task_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.patch(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).update(student_id, goal_id, roadmap_id, milestone_id, task_id, data)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.delete(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/milestones/{milestone_id}/tasks/{task_id}",
    status_code=204,
)
def delete_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        TaskService(db).delete(student_id, goal_id, roadmap_id, milestone_id, task_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


# ---------------------------------------------------------------------------
# Step 15: Task Detail Actions (ROAD-05)
# ---------------------------------------------------------------------------

_TASK_ACTION_PATH = (
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}"
    "/milestones/{milestone_id}/tasks/{task_id}"
)


@router.post(
    _TASK_ACTION_PATH + "/start",
    response_model=TaskResponse,
    summary="Start a task",
    description="Transition a pending task to active. Returns 400 if the task is not pending.",
)
def start_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).start(student_id, goal_id, roadmap_id, milestone_id, task_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.post(
    _TASK_ACTION_PATH + "/complete",
    response_model=TaskResponse,
    summary="Complete a task",
    description="Transition a pending or active task to completed. Returns 400 if already completed or skipped.",
)
def complete_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).complete(student_id, goal_id, roadmap_id, milestone_id, task_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.post(
    _TASK_ACTION_PATH + "/skip",
    response_model=TaskResponse,
    summary="Skip a task",
    description="Transition a pending task to skipped. Active and completed tasks cannot be skipped.",
)
def skip_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).skip(student_id, goal_id, roadmap_id, milestone_id, task_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.post(
    _TASK_ACTION_PATH + "/reschedule",
    response_model=TaskResponse,
    summary="Reschedule a task",
    description=(
        "Move a pending or active task's target_date to a new date. "
        "Completed and skipped tasks are immutable. "
        "new_target_date must be >= task.start_date (if set) and <= milestone.target_date (if set)."
    ),
)
def reschedule_task(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    milestone_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskRescheduleRequest,
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).reschedule(
            student_id, goal_id, roadmap_id, milestone_id, task_id, data
        )
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error