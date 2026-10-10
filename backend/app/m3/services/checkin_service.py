import uuid
from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.m3.db.models import Roadmap, WeeklyCheckin
from app.m3.repositories.checkin_repository import WeeklyCheckinRepository
from app.m3.schemas.weekly_checkin import WeeklyCheckinCreate, WeeklyCheckinUpdate


class ConflictError(Exception):
    """Raised when a resource conflict occurs, e.g. duplicate check-in for a week."""
    pass


class WeeklyCheckinService:
    def __init__(self, db: Session):
        self.repository = WeeklyCheckinRepository(db)
        self.db = db

    def create(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        data: WeeklyCheckinCreate,
    ) -> WeeklyCheckin:
        self._owned_roadmap(student_id, goal_id, roadmap_id)

        week_start_date = data.week_start_date
        self._validate_week_start_date(week_start_date)

        existing = self.repository.get_by_roadmap_and_week(roadmap_id, week_start_date)
        if existing is not None:
            raise ConflictError("A check-in for this week already exists")

        values = {
            "week_start_date": week_start_date,
            "accomplished": data.accomplished,
            "learned": data.learned,
            "challenged": data.challenged,
            "proud_of": data.proud_of,
            "improve_next": data.improve_next,
        }

        try:
            checkin = self.repository.create(roadmap_id, values)
            self.db.commit()
            return checkin
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("A check-in for this week already exists") from exc
        except Exception:
            self.db.rollback()
            raise

    def list(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> list[WeeklyCheckin]:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        return self.repository.list_by_roadmap(roadmap_id)

    def get(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        checkin_id: uuid.UUID,
    ) -> WeeklyCheckin:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        return self._owned_checkin(roadmap_id, checkin_id)

    def update(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        checkin_id: uuid.UUID,
        data: WeeklyCheckinUpdate,
    ) -> WeeklyCheckin:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        checkin = self._owned_checkin(roadmap_id, checkin_id)

        values = data.model_dump(exclude_unset=True)
        # week_start_date is strictly immutable and cannot be updated
        values.pop("week_start_date", None)

        try:
            updated = self.repository.update(checkin, values)
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def _validate_week_start_date(self, week_start_date: date) -> None:
        if week_start_date.weekday() != 0:
            raise ValueError("week_start_date must be a Monday")

        today = date.today()
        current_week_monday = today - timedelta(days=today.weekday())
        if week_start_date > current_week_monday:
            raise ValueError("week_start_date cannot be in the future")

    def _owned_roadmap(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> Roadmap:
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        roadmap = self.repository.get_roadmap(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")
        return roadmap

    def _owned_checkin(self, roadmap_id: uuid.UUID, checkin_id: uuid.UUID) -> WeeklyCheckin:
        checkin = self.repository.get_by_id(checkin_id)
        if checkin is None:
            raise LookupError("Weekly check-in not found")
        if checkin.roadmap_id != roadmap_id:
            raise PermissionError("Weekly check-in does not belong to this roadmap")
        return checkin

    def _ensure_student(self, student_id: uuid.UUID) -> None:
        if not self.repository.student_exists(student_id):
            raise LookupError("Student not found")

    def _ensure_goal_owned_by_student(self, student_id: uuid.UUID, goal_id: uuid.UUID):
        if not self.repository.goal_exists(goal_id):
            raise LookupError("Goal not found")
        goal = self.repository.get_goal(goal_id)
        if goal.student_id != student_id:
            raise PermissionError("Goal does not belong to this student")
        return goal
