import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.m3.db.models import Milestone
from app.m3.repositories.milestone_repository import MilestoneRepository
from app.m3.schemas.milestone import MilestoneCreate, MilestoneProgressResponse, MilestoneUpdate


class MilestoneService:
    def __init__(self, db: Session):
        self.repository = MilestoneRepository(db)
        self.db = db

    def create(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        data: MilestoneCreate,
    ) -> Milestone:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        values = data.model_dump()
        self._validate_values(values)
        try:
            milestone = self.repository.create(roadmap_id, values)
            self.db.commit()
            return milestone
        except Exception:
            self.db.rollback()
            raise

    def list(
        self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID
    ) -> list[Milestone]:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        return self.repository.list_by_roadmap(roadmap_id)

    def get(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
    ) -> Milestone:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        return self._owned_milestone(roadmap_id, milestone_id)

    def update(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        data: MilestoneUpdate,
    ) -> Milestone:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        milestone = self._owned_milestone(roadmap_id, milestone_id)
        values = data.model_dump(exclude_unset=True)
        effective_values = {
            "title": values.get("title", milestone.title),
            "start_date": values.get("start_date", milestone.start_date),
            "target_date": values.get("target_date", milestone.target_date),
            "status": values.get("status", milestone.status),
            "order_index": values.get("order_index", milestone.order_index),
        }
        self._validate_values(effective_values)
        try:
            updated = self.repository.update(milestone, values)
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def delete(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
    ) -> None:
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        milestone = self._owned_milestone(roadmap_id, milestone_id)
        try:
            self.repository.delete(milestone)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _owned_roadmap(
        self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID
    ):
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        roadmap = self.repository.get_roadmap(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")
        return roadmap

    def _owned_milestone(self, roadmap_id: uuid.UUID, milestone_id: uuid.UUID) -> Milestone:
        milestone = self.repository.get_by_id(milestone_id)
        if milestone is None:
            raise LookupError("Milestone not found")
        if milestone.roadmap_id != roadmap_id:
            raise PermissionError("Milestone does not belong to this roadmap")
        return milestone

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

    def _validate_values(self, values: dict) -> None:
        title = values.get("title")
        if not title or len(title) > 200:
            raise ValueError("title must be between 1 and 200 characters")
        if values.get("order_index") is None or values["order_index"] < 0:
            raise ValueError("order_index must be non-negative")
        if values.get("status") not in {"pending", "active", "completed", "skipped"}:
            raise ValueError("Invalid milestone status")
        start_date = values.get("start_date")
        target_date = values.get("target_date")
        if start_date and target_date and start_date > target_date:
            raise ValueError("start_date must not be after target_date")

    def get_progress(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
    ) -> MilestoneProgressResponse:
        """Step 8B: Return dynamic progress for a milestone.

        Progress = completed_tasks / total_tasks * 100, rounded to 2dp.
        skipped and active tasks do NOT count as completed.
        Returns 0.0 when the milestone has no tasks.
        Ownership is fully validated before any aggregation query.
        """
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        self._owned_milestone(roadmap_id, milestone_id)
        counts = self.repository.get_task_counts(milestone_id)
        total = counts["total"]
        completed = counts["completed"]
        percentage = round(completed / total * 100, 2) if total > 0 else 0.0
        return MilestoneProgressResponse(
            milestone_id=milestone_id,
            total_tasks=total,
            completed_tasks=completed,
            active_tasks=counts["active"],
            pending_tasks=counts["pending"],
            skipped_tasks=counts["skipped"],
            progress_percentage=percentage,
        )