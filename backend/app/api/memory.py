from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.models.user import User
from app.schemas.memory import StudentMemoryOut
from app.services.chat import _lazy_ensure_agent
from app.services.providers import memory

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=StudentMemoryOut)
async def student_memory(user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    """Easy retrieval of a student's long-term Letta memory, grouped by school year."""
    agent_id = _lazy_ensure_agent(user, db)
    if not agent_id or not memory.is_reachable():
        return StudentMemoryOut()
    return memory.timeline(agent_id)
@router.post("/archive", response_model=dict)
async def archive_fact(
    user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
    fact: str = Body(...),
    tags: list[str] = Body(["chat"]),
):
    """Archive a fact to the student's Letta memory."""
    agent_id = _lazy_ensure_agent(user, db)
    if not agent_id:
        return {"status": "error", "message": "Could not create Letta agent"}
    result = memory.archive(user, fact, tags)
    return {"status": "success" if result else "partial", "archived": result}
