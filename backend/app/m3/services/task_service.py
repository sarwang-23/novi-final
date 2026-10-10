import uuid

from sqlalchemy.orm import Session

from app.m3.db.models import Milestone, Task
from app.m3.repositories.task_repository import TaskRepository
from app.m3.schemas.task import TaskCreate, TaskRescheduleRequest, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.repository = TaskRepository(db)
        self.db = db

    def create(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        data: TaskCreate,
    ) -> Task:
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        values = data.model_dump()
        self._validate_values(values)
        try:
            task = self.repository.create(milestone_id, values)
            self.db.commit()
            return task
        except Exception:
            self.db.rollback()
            raise

    def list(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
    ) -> list[Task]:
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        return self.repository.list_by_milestone(milestone_id)

    def get(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> Task:
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        return self._owned_task(milestone_id, task_id)

    def update(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        task_id: uuid.UUID,
        data: TaskUpdate,
    ) -> Task:
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        task = self._owned_task(milestone_id, task_id)
        values = data.model_dump(exclude_unset=True)
        effective_values = {
            "title": values.get("title", task.title),
            "start_date": values.get("start_date", task.start_date),
            "target_date": values.get("target_date", task.target_date),
            "status": values.get("status", task.status),
            "priority": values.get("priority", task.priority),
            "order_index": values.get("order_index", task.order_index),
        }
        self._validate_values(effective_values)
        try:
            updated = self.repository.update(task, values)
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
        task_id: uuid.UUID,
    ) -> None:
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        task = self._owned_task(milestone_id, task_id)
        try:
            self.repository.delete(task)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # ------------------------------------------------------------------
    # Step 15: Task Detail Actions (ROAD-05)
    # ------------------------------------------------------------------

    def start(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> Task:
        """Mark a task as active (started). Only pending tasks can be started."""
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        task = self._owned_task(milestone_id, task_id)
        if task.status == "active":
            raise ValueError("Task is already active")
        if task.status == "completed":
            raise ValueError("Completed tasks cannot be started")
        if task.status == "skipped":
            raise ValueError("Skipped tasks cannot be started")
        # Only pending → active
        try:
            updated = self.repository.update(task, {"status": "active"})
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def complete(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> Task:
        """Mark a task as completed. Only pending or active tasks can be completed."""
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        task = self._owned_task(milestone_id, task_id)
        if task.status == "completed":
            raise ValueError("Task is already completed")
        if task.status == "skipped":
            raise ValueError("Skipped tasks cannot be completed")
        # pending or active → completed
        try:
            updated = self.repository.update(task, {"status": "completed"})
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def skip(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> Task:
        """Mark a task as skipped. Only pending tasks can be skipped."""
        self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        task = self._owned_task(milestone_id, task_id)
        if task.status == "completed":
            raise ValueError("Completed tasks cannot be skipped")
        if task.status == "active":
            raise ValueError("Active tasks cannot be skipped")
        if task.status == "skipped":
            raise ValueError("Task is already skipped")
        # Only pending → skipped
        try:
            updated = self.repository.update(task, {"status": "skipped"})
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def reschedule(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
        task_id: uuid.UUID,
        data: TaskRescheduleRequest,
    ) -> Task:
        """Move a task's target_date to a new date.

        Rules:
        - Only pending or active tasks may be rescheduled.
        - Completed and skipped tasks are historically immutable.
        - new_target_date must be >= task.start_date (if start_date is set).
        - new_target_date must be <= milestone.target_date (if milestone.target_date is set).
        """
        milestone = self._owned_milestone(student_id, goal_id, roadmap_id, milestone_id)
        task = self._owned_task(milestone_id, task_id)

        if task.status == "completed":
            raise ValueError("Completed tasks cannot be rescheduled")
        if task.status == "skipped":
            raise ValueError("Skipped tasks cannot be rescheduled")

        new_date = data.new_target_date

        # start_date boundary
        effective_start = task.start_date
        if effective_start is not None and new_date < effective_start:
            raise ValueError(
                f"new_target_date ({new_date}) must not be before task start_date ({effective_start})"
            )

        # milestone boundary
        if milestone.target_date is not None and new_date > milestone.target_date:
            raise ValueError(
                f"new_target_date ({new_date}) cannot exceed milestone target_date ({milestone.target_date})"
            )

        try:
            updated = self.repository.update(task, {"target_date": new_date})
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise


    def _owned_milestone(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        milestone_id: uuid.UUID,
    ) -> Milestone:
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        roadmap = self.repository.get_roadmap(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")
        milestone = self.repository.get_milestone(milestone_id)
        if milestone is None:
            raise LookupError("Milestone not found")
        if milestone.roadmap_id != roadmap_id:
            raise PermissionError("Milestone does not belong to this roadmap")
        return milestone

    def _owned_task(self, milestone_id: uuid.UUID, task_id: uuid.UUID) -> Task:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise LookupError("Task not found")
        if task.milestone_id != milestone_id:
            raise PermissionError("Task does not belong to this milestone")
        return task

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
            raise ValueError("Invalid task status")
        if values.get("priority") not in {"low", "medium", "high"}:
            raise ValueError("Invalid task priority")
        start_date = values.get("start_date")
        target_date = values.get("target_date")
        if start_date and target_date and start_date > target_date:
            raise ValueError("start_date must not be after target_date")