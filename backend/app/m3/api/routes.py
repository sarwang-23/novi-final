import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student, get_current_user
from app.models.user import User
from app.m3.api.deps import student_matches_authenticated_user
from app.m3.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.m3.services.goal_service import GoalService
from app.m3.api.roadmap_routes import router as roadmap_router


router = APIRouter(
    dependencies=[
        Depends(get_current_student),
        Depends(student_matches_authenticated_user),
    ]
)
router.include_router(roadmap_router)

from fastapi.responses import JSONResponse


@router.get("/students/me")
def get_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return the authenticated student's module-3 identity (for use in nested paths)."""
    from app.m3.api.deps import ensure_m3_student

    student = ensure_m3_student(db, user)
    return {"id": student.id, "external_id": student.external_id}


def _service_error(error: Exception) -> HTTPException:
	if isinstance(error, LookupError):
		return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
	if isinstance(error, PermissionError):
		return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
	return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/students/{student_id}/goals", response_model=GoalResponse, status_code=201)
def create_goal(student_id: uuid.UUID, data: GoalCreate, db: Session = Depends(get_db)):
	try:
		return GoalService(db).create(student_id, data)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.get("/students/{student_id}/goals", response_model=list[GoalResponse])
def list_goals(student_id: uuid.UUID, db: Session = Depends(get_db)):
	try:
		return GoalService(db).list(student_id)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.get("/students/{student_id}/goals/{goal_id}", response_model=GoalResponse)
def get_goal(student_id: uuid.UUID, goal_id: uuid.UUID, db: Session = Depends(get_db)):
	try:
		return GoalService(db).get(student_id, goal_id)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.patch("/students/{student_id}/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
	student_id: uuid.UUID,
	goal_id: uuid.UUID,
	data: GoalUpdate,
	db: Session = Depends(get_db),
):
	try:
		return GoalService(db).update(student_id, goal_id, data)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.delete("/students/{student_id}/goals/{goal_id}", status_code=204)
def delete_goal(student_id: uuid.UUID, goal_id: uuid.UUID, db: Session = Depends(get_db)):
	try:
		GoalService(db).delete(student_id, goal_id)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error
