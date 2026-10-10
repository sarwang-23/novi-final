from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.models.user import User
from app.schemas.roadmap import (
    GoalCreate,
    GoalOut,
    GoalUpdate,
    PriorityGenerateRequest,
    PriorityOut,
    RoadmapGenerateRequest,
    RoadmapItemOut,
    RoadmapOut,
    TaskCreate,
    TaskOut,
    TaskUpdate,
)
from app.services import roadmap as roadmap_service
from app.services import state_sync

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


def _sync(user: User, db: Session) -> None:
    """Keep Letta's state memory in step with any roadmap mutation."""
    try:
        state_sync.push(user, db)
    except Exception as exc:
        print(f"[sync] roadmap state push failed: {exc}")


# ----------------------------------------------------------------- goals
@router.post("/goals", response_model=GoalOut)
async def create_goal(data: GoalCreate, user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    result = roadmap_service.create_goal(db, user, data)
    _sync(user, db)
    return result


@router.get("/goals", response_model=list[GoalOut])
async def list_goals(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return roadmap_service.list_goals(db, user)


@router.patch("/goals/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    goal = roadmap_service.update_goal(db, user, goal_id, data)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    _sync(user, db)
    return goal


# ----------------------------------------------------------------- roadmap
@router.post("/generate", response_model=RoadmapOut)
async def generate_roadmap(
    request: RoadmapGenerateRequest,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    try:
        goal_id = await roadmap_service.generate_roadmap(db, user, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    roadmap = roadmap_service.get_roadmap(db, user, goal_id)
    _sync(user, db)
    return _roadmap_payload(roadmap)


@router.get("", response_model=RoadmapOut)
async def get_roadmap(
    goal_id: int | None = None,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _roadmap_payload(roadmap_service.get_roadmap(db, user, goal_id))


@router.patch("/items/{item_id}", response_model=RoadmapItemOut)
async def toggle_item(
    item_id: int,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    item = roadmap_service.toggle_roadmap_item(db, user, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    _sync(user, db)
    return item


# ----------------------------------------------------------------- priorities
@router.get("/priorities", response_model=list[PriorityOut])
async def priorities(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return roadmap_service.get_priorities(db, user)


@router.post("/priorities/generate", response_model=list[PriorityOut])
async def generate_priorities(
    request: PriorityGenerateRequest,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    result = await roadmap_service.generate_priorities(db, user, request)
    _sync(user, db)
    return result


@router.patch("/priorities/{priority_id}", response_model=PriorityOut)
async def toggle_priority(
    priority_id: int,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    priority = roadmap_service.toggle_priority(db, user, priority_id)
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")
    _sync(user, db)
    return priority


# ----------------------------------------------------------------- tasks
@router.post("/tasks", response_model=TaskOut)
async def create_task(data: TaskCreate, user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    result = roadmap_service.create_task(db, user, data)
    _sync(user, db)
    return result


@router.get("/tasks", response_model=list[TaskOut])
async def list_tasks(
    status: str | None = None,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return roadmap_service.list_tasks(db, user, status=status)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    task = roadmap_service.update_task(db, user, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _sync(user, db)
    return task


def _roadmap_payload(roadmap: dict) -> dict:
    return {
        "goal": {"id": roadmap["goal"].id, "title": roadmap["goal"].title,
                 "description": roadmap["goal"].description, "category": roadmap["goal"].category.value,
                 "status": roadmap["goal"].status.value} if roadmap["goal"] else None,
        "stages": roadmap["stages"],
        "short_term": roadmap.get("short_term", []),
        "progress_percent": roadmap["progress_percent"],
    }