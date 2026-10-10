from datetime import date
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.m3.api.deps import student_matches_authenticated_user
from app.m3.schemas.adaptation import (
    AdaptationApplyRequest,
    AdaptationApplyResponse,
    AdaptationPreviewResponse,
)
from app.m3.schemas.roadmap import (
    RoadmapCreate,
    RoadmapFullResponse,
    RoadmapProgressResponse,
    RoadmapResponse,
    RoadmapTimelineResponse,
    RoadmapUpdate,
)
from app.m3.services.adaptation_service import RoadmapAdaptationService, ServiceUnavailableError
from app.m3.services.roadmap_service import RoadmapService
from app.m3.api.milestone_routes import router as milestone_router
from app.m3.api.checkin_routes import router as checkin_router
from app.m3.repositories.roadmap_repository import RoadmapRepository
from app.m3.services.ai_provider import AIConfigurationError, AIProviderError
from app.m3.services.roadmap_generator import RoadmapGenerationError, RoadmapGenerator
from app.m3.services.roadmap_orchestrator import OrchestrationError, RoadmapOrchestrator


router = APIRouter(
    dependencies=[
        Depends(get_current_student),
        Depends(student_matches_authenticated_user),
    ]
)
router.include_router(milestone_router)
router.include_router(checkin_router)


def _service_error(error: Exception) -> HTTPException:
	if isinstance(error, LookupError):
		return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
	if isinstance(error, PermissionError):
		return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
	if isinstance(error, (ServiceUnavailableError, AIConfigurationError, AIProviderError)):
		return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
	return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/generate",
    response_model=RoadmapResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_roadmap(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        repo = RoadmapRepository(db)
        if not repo.student_exists(student_id):
            raise LookupError("Student not found")

        if not repo.goal_exists(goal_id):
            raise LookupError("Goal not found")

        goal = repo.get_goal(goal_id)
        if goal is None:
            raise LookupError("Goal not found")

        if goal.student_id != student_id:
            raise PermissionError("Goal does not belong to this student")

        if repo.get_active_by_goal(goal_id) is not None:
            raise ValueError("An active roadmap already exists for this goal")

        generator = RoadmapGenerator()
        generated = generator.generate(
            goal=goal,
            career=getattr(goal, "career", None),
            career_match=getattr(goal, "career_match", None),
        )

        orchestrator = RoadmapOrchestrator(db)
        result = orchestrator.persist_generated_roadmap(
            student_id=student_id,
            goal_id=goal_id,
            generated=generated,
            roadmap_status="draft",
        )

        return result.roadmap
    except (
        LookupError,
        PermissionError,
        ServiceUnavailableError,
        AIConfigurationError,
        AIProviderError,
        RoadmapGenerationError,
        OrchestrationError,
        ValueError,
    ) as error:
        raise _service_error(error) from error


@router.post("/students/{student_id}/goals/{goal_id}/roadmaps", response_model=RoadmapResponse, status_code=201)
def create_roadmap(
	student_id: uuid.UUID,
	goal_id: uuid.UUID,
	data: RoadmapCreate,
	db: Session = Depends(get_db),
):
	try:
		return RoadmapService(db).create(student_id, goal_id, data)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.get("/students/{student_id}/goals/{goal_id}/roadmaps", response_model=list[RoadmapResponse])
def list_roadmaps(
	student_id: uuid.UUID,
	goal_id: uuid.UUID,
	db: Session = Depends(get_db),
):
	try:
		return RoadmapService(db).list(student_id, goal_id)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.get("/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap(
	student_id: uuid.UUID,
	goal_id: uuid.UUID,
	roadmap_id: uuid.UUID,
	db: Session = Depends(get_db),
):
	try:
		return RoadmapService(db).get(student_id, goal_id, roadmap_id)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.patch("/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}", response_model=RoadmapResponse)
def update_roadmap(
	student_id: uuid.UUID,
	goal_id: uuid.UUID,
	roadmap_id: uuid.UUID,
	data: RoadmapUpdate,
	db: Session = Depends(get_db),
):
	try:
		return RoadmapService(db).update(student_id, goal_id, roadmap_id, data)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.delete("/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}", status_code=204)
def delete_roadmap(
	student_id: uuid.UUID,
	goal_id: uuid.UUID,
	roadmap_id: uuid.UUID,
	db: Session = Depends(get_db),
):
	try:
		RoadmapService(db).delete(student_id, goal_id, roadmap_id)
	except (LookupError, PermissionError, ValueError) as error:
		raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/progress",
    response_model=RoadmapProgressResponse,
    summary="Get roadmap progress",
    description="Returns dynamic task completion progress for a roadmap across ALL milestones. Progress = completed tasks / total tasks * 100. Skipped and active tasks do not count.",
)
def get_roadmap_progress(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return RoadmapService(db).get_progress(student_id, goal_id, roadmap_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/full",
    response_model=RoadmapFullResponse,
    summary="Get full roadmap hierarchy",
    description="Returns the complete roadmap hierarchy in one response (Roadmap → Milestones → Tasks) with progress and counts.",
)
def get_roadmap_full(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return RoadmapService(db).get_full(student_id, goal_id, roadmap_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


@router.get(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/timeline",
    response_model=RoadmapTimelineResponse,
    summary="Get roadmap timeline projection",
    description="Projects roadmap tasks into a Year, Month, or Week temporal window based on anchor date.",
)
def get_roadmap_timeline(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    view: str = Query(default="week"),
    date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        return RoadmapService(db).get_timeline(
            student_id=student_id,
            goal_id=goal_id,
            roadmap_id=roadmap_id,
            view=view,
            anchor_date=date,
        )
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error



@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/adaptations/preview",
    response_model=AdaptationPreviewResponse,
)
def preview_roadmap_adaptation(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return RoadmapAdaptationService(db).preview(student_id, goal_id, roadmap_id)
    except (LookupError, PermissionError, ServiceUnavailableError, ValueError) as error:
        raise _service_error(error) from error


@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/adaptations/apply",
    response_model=AdaptationApplyResponse,
)
def apply_roadmap_adaptation(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    request: AdaptationApplyRequest,
    db: Session = Depends(get_db),
):
    try:
        return RoadmapAdaptationService(db).apply(student_id, goal_id, roadmap_id, request)
    except (LookupError, PermissionError, ServiceUnavailableError, ValueError) as error:
        raise _service_error(error) from error


@router.post(
    "/students/{student_id}/goals/{goal_id}/roadmaps/{roadmap_id}/reschedule",
    response_model=RoadmapResponse,
    summary="Reschedule an existing roadmap",
    description="Deterministically recalculates milestone and task dates for an already persisted roadmap using the pure RoadmapScheduler.",
)
def reschedule_roadmap(
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return RoadmapService(db).reschedule(student_id, goal_id, roadmap_id)
    except (LookupError, PermissionError, ValueError) as error:
        raise _service_error(error) from error


