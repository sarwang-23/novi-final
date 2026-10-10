import uuid

from sqlalchemy.orm import Session

from app.m3.db.models import Goal
from app.m3.repositories.goal_repository import GoalRepository
from app.m3.schemas.goal import GoalCreate, GoalUpdate


class GoalService:
    def __init__(self, db: Session):
        self.repository = GoalRepository(db)
        self.db = db

    def create(self, student_id: uuid.UUID, data: GoalCreate) -> Goal:
        self._ensure_student(student_id)
        values = data.model_dump()
        self._validate_links(student_id, values)
        try:
            goal = self.repository.create(student_id, values)
            self.db.commit()
            return goal
        except Exception:
            self.db.rollback()
            raise

    def list(self, student_id: uuid.UUID) -> list[Goal]:
        self._ensure_student(student_id)
        return self.repository.list_by_student(student_id)

    def get(self, student_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
        goal = self._owned_goal(student_id, goal_id)
        return goal

    def update(self, student_id: uuid.UUID, goal_id: uuid.UUID, data: GoalUpdate) -> Goal:
        goal = self._owned_goal(student_id, goal_id)
        values = data.model_dump(exclude_unset=True)
        resulting_values = {
            "goal_type": values.get("goal_type", goal.goal_type),
            "career_id": values.get("career_id", goal.career_id),
            "career_match_id": values.get("career_match_id", goal.career_match_id),
        }
        if resulting_values["goal_type"] != "career":
            resulting_values["career_id"] = None
            resulting_values["career_match_id"] = None
            values["career_id"] = None
            values["career_match_id"] = None
        self._validate_links(student_id, resulting_values)
        try:
            updated = self.repository.update(goal, values)
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def delete(self, student_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        goal = self._owned_goal(student_id, goal_id)
        try:
            self.repository.delete(goal)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _owned_goal(self, student_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
        self._ensure_student(student_id)
        goal = self.repository.get_by_id(goal_id)
        if goal is None:
            raise LookupError("Goal not found")
        if goal.student_id != student_id:
            raise PermissionError("Student does not own this goal")
        return goal

    def _ensure_student(self, student_id: uuid.UUID) -> None:
        if not self.repository.student_exists(student_id):
            raise LookupError("Student not found")

    def _validate_links(self, student_id: uuid.UUID, values: dict) -> None:
        if values["goal_type"] != "career" and (
            values.get("career_id") or values.get("career_match_id")
        ):
            raise ValueError("Career links are only valid for career goals")
        if values.get("career_id") and not self.repository.career_exists(values["career_id"]):
            raise ValueError("Career not found")
        if values.get("career_match_id"):
            career_match = self.repository.get_career_match(values["career_match_id"])
            if career_match is None:
                raise ValueError("Career match not found")
            if career_match.student_id != student_id:
                raise PermissionError("Career match does not belong to this student")
            if values.get("career_id") and career_match.career_id != values["career_id"]:
                raise ValueError("Career does not match the career match provenance")