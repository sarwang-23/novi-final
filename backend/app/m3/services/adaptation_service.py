import json
import uuid
from datetime import date
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.m3.db.models import Goal, Roadmap, Task
from app.m3.repositories.checkin_repository import WeeklyCheckinRepository
from app.m3.repositories.goal_repository import GoalRepository
from app.m3.repositories.milestone_repository import MilestoneRepository
from app.m3.repositories.roadmap_repository import RoadmapRepository
from app.m3.repositories.task_repository import TaskRepository
from app.m3.schemas.adaptation import (
    AdaptationAction,
    AdaptationApplyRequest,
    AdaptationApplyResponse,
    AdaptationPreviewResponse,
    AddTaskAction,
    AdjustPriorityAction,
    GeneratedAdaptation,
    RescheduleRoadmapAction,
    RescheduleTaskAction,
    SkipTaskAction,
)
from app.m3.services.ai_provider import (
    AIConfigurationError,
    AIProviderError,
    StructuredAIProvider,
    create_default_provider,
)


class ServiceUnavailableError(RuntimeError):
    """Raised when an external service such as the AI provider is unavailable."""

    pass


class RoadmapAdaptationService:
    def __init__(
        self,
        db: Session,
        ai_provider: StructuredAIProvider | None = None,
    ):
        self.db = db
        self.roadmap_repo = RoadmapRepository(db)
        self.milestone_repo = MilestoneRepository(db)
        self.task_repo = TaskRepository(db)
        self.checkin_repo = WeeklyCheckinRepository(db)
        self.goal_repo = GoalRepository(db)
        self.ai_provider = ai_provider

    def preview(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> AdaptationPreviewResponse:
        """Preview an AI adaptation plan without writing anything to the database."""
        roadmap = self._owned_roadmap(student_id, goal_id, roadmap_id)
        goal = self.roadmap_repo.get_goal(goal_id)

        # Progress calculation
        counts = self.roadmap_repo.get_task_counts_for_roadmap(roadmap_id)
        total = counts["total"]
        completed = counts["completed"]
        progress_percentage = round(completed / total * 100, 2) if total > 0 else 0.0

        # Milestones and tasks
        milestones = self.milestone_repo.list_by_roadmap(roadmap_id)
        milestones_context = []
        for m in milestones:
            m_tasks = self.task_repo.list_by_milestone(m.id)
            completed_titles = [t.title for t in m_tasks if t.status == "completed"]
            active_or_pending = [
                {
                    "task_id": str(t.id),
                    "title": t.title,
                    "description": t.description,
                    "status": t.status,
                    "priority": t.priority,
                    "order_index": t.order_index,
                    "target_date": str(t.target_date) if t.target_date else None,
                }
                for t in m_tasks
                if t.status in ("active", "pending")
            ]
            milestones_context.append({
                "milestone_id": str(m.id),
                "title": m.title,
                "order_index": m.order_index,
                "completed_tasks": completed_titles,
                "active_and_pending_tasks": active_or_pending,
            })

        # Recent weekly check-ins (non-null reflections only)
        checkins = self.checkin_repo.list_by_roadmap(roadmap_id)
        checkin_reflections = []
        for c in checkins[:3]:  # up to 3 recent check-ins
            reflections = {}
            for field in ("accomplished", "learned", "challenged", "proud_of", "improve_next"):
                val = getattr(c, field)
                if val is not None and val.strip():
                    reflections[field] = val.strip()
            if reflections:
                checkin_reflections.append({
                    "week_start_date": str(c.week_start_date),
                    "reflections": reflections,
                })

        prompt = self._build_prompt(
            goal=goal,
            roadmap=roadmap,
            counts=counts,
            progress_percentage=progress_percentage,
            milestones_context=milestones_context,
            checkin_reflections=checkin_reflections,
        )

        provider = self.ai_provider
        if provider is None:
            try:
                provider = create_default_provider()
            except AIConfigurationError as exc:
                raise ServiceUnavailableError("AI provider is not configured") from exc

        try:
            generated = provider.generate_structured(prompt, GeneratedAdaptation)
            if not isinstance(generated, GeneratedAdaptation):
                generated = GeneratedAdaptation.model_validate(generated)
        except (AIProviderError, AIConfigurationError) as exc:
            raise ServiceUnavailableError(f"AI adaptation generation failed: {exc}") from exc
        except (ValidationError, ValueError) as exc:
            raise ValueError(f"Invalid AI adaptation output: {exc}") from exc

        # Validate recommended actions against current DB state (fail-fast)
        self._validate_actions_against_db(roadmap, goal, generated.recommended_actions)

        # Zero DB writes - preview is completely read-only
        return AdaptationPreviewResponse(
            roadmap_id=roadmap.id,
            goal_id=goal.id,
            assessment=generated.assessment,
            reasoning=generated.reasoning,
            progress_percentage=progress_percentage,
            recommended_actions=generated.recommended_actions,
        )

    def apply(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        request: AdaptationApplyRequest,
    ) -> AdaptationApplyResponse:
        """Apply an approved adaptation plan atomically."""
        roadmap = self._owned_roadmap(student_id, goal_id, roadmap_id)
        goal = self.roadmap_repo.get_goal(goal_id)

        # Re-validate all actions against CURRENT database state
        self._validate_actions_against_db(roadmap, goal, request.actions)

        # Apply actions atomically
        try:
            applied_count = 0
            for action in request.actions:
                self._execute_action(roadmap, action)
                applied_count += 1
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        # Refresh progress and roadmap status
        self.db.refresh(roadmap)
        counts = self.roadmap_repo.get_task_counts_for_roadmap(roadmap_id)
        total = counts["total"]
        completed = counts["completed"]
        progress_percentage = round(completed / total * 100, 2) if total > 0 else 0.0

        return AdaptationApplyResponse(
            roadmap_id=roadmap.id,
            applied_actions_count=applied_count,
            message="Adaptation plan applied successfully",
            roadmap_target_date=roadmap.target_date,
            progress_percentage=progress_percentage,
        )

    def _validate_actions_against_db(
        self,
        roadmap: Roadmap,
        goal: Goal,
        actions: list[AdaptationAction],
    ) -> None:
        """Validate every action against the CURRENT database state."""
        milestones = self.milestone_repo.list_by_roadmap(roadmap.id)
        milestone_ids = {m.id for m in milestones}

        task_map: dict[uuid.UUID, Task] = {}
        for m in milestones:
            for t in self.task_repo.list_by_milestone(m.id):
                task_map[t.id] = t

        for action in actions:
            if isinstance(action, AddTaskAction):
                if action.milestone_id not in milestone_ids:
                    raise ValueError(
                        f"Milestone {action.milestone_id} does not belong to this roadmap or does not exist"
                    )
                if not action.task.title.strip():
                    raise ValueError("Task title cannot be empty")
                if action.task.order_index < 0:
                    raise ValueError("Task order_index must be non-negative")

            elif isinstance(action, SkipTaskAction):
                task = task_map.get(action.task_id)
                if task is None:
                    raise ValueError(
                        f"Task {action.task_id} does not belong to this roadmap or does not exist"
                    )
                if task.status == "completed":
                    raise ValueError(f"Completed task {action.task_id} cannot be modified or skipped")
                if task.status == "active":
                    raise ValueError(f"Active task {action.task_id} cannot be skipped by AI")
                if task.status != "pending":
                    raise ValueError(
                        f"Cannot skip task {action.task_id} with status '{task.status}'"
                    )

            elif isinstance(action, RescheduleTaskAction):
                task = task_map.get(action.task_id)
                if task is None:
                    raise ValueError(
                        f"Task {action.task_id} does not belong to this roadmap or does not exist"
                    )
                if task.status == "completed":
                    raise ValueError(f"Completed task {action.task_id} cannot be modified or rescheduled")
                if task.status not in ("pending", "active"):
                    raise ValueError(
                        f"Cannot reschedule task {action.task_id} with status '{task.status}'"
                    )

            elif isinstance(action, AdjustPriorityAction):
                task = task_map.get(action.task_id)
                if task is None:
                    raise ValueError(
                        f"Task {action.task_id} does not belong to this roadmap or does not exist"
                    )
                if task.status == "completed":
                    raise ValueError(f"Completed task {action.task_id} cannot have priority changed")
                if task.status not in ("pending", "active"):
                    raise ValueError(
                        f"Cannot adjust priority for task {action.task_id} with status '{task.status}'"
                    )

            elif isinstance(action, RescheduleRoadmapAction):
                if goal.target_date is not None and action.new_target_date > goal.target_date:
                    raise ValueError(
                        f"Roadmap target date {action.new_target_date} cannot exceed goal target date {goal.target_date}"
                    )
                if goal.target_date is None and roadmap.target_date is not None and action.new_target_date > roadmap.target_date:
                    raise ValueError(
                        "Cannot extend roadmap target date when goal target date is not set"
                    )

    def _execute_action(self, roadmap: Roadmap, action: AdaptationAction) -> None:
        """Execute a single validated action inside the transaction."""
        if isinstance(action, AddTaskAction):
            existing_tasks = self.task_repo.list_by_milestone(action.milestone_id)
            target_order = action.task.order_index
            # Shift existing tasks if collision
            for existing in existing_tasks:
                if existing.order_index >= target_order:
                    self.task_repo.update(existing, {"order_index": existing.order_index + 1})

            self.task_repo.create(
                action.milestone_id,
                {
                    "title": action.task.title,
                    "description": action.task.description,
                    "priority": action.task.priority,
                    "order_index": target_order,
                    "target_date": action.task.target_date,
                    "status": "pending",
                },
            )

        elif isinstance(action, SkipTaskAction):
            task = self.task_repo.get_by_id(action.task_id)
            if task:
                self.task_repo.update(task, {"status": "skipped"})

        elif isinstance(action, RescheduleTaskAction):
            task = self.task_repo.get_by_id(action.task_id)
            if task:
                self.task_repo.update(task, {"target_date": action.new_target_date})

        elif isinstance(action, AdjustPriorityAction):
            task = self.task_repo.get_by_id(action.task_id)
            if task:
                self.task_repo.update(task, {"priority": action.new_priority})

        elif isinstance(action, RescheduleRoadmapAction):
            self.roadmap_repo.update(roadmap, {"target_date": action.new_target_date})

    @staticmethod
    def _build_prompt(
        goal: Goal,
        roadmap: Roadmap,
        counts: dict[str, int],
        progress_percentage: float,
        milestones_context: list[dict[str, Any]],
        checkin_reflections: list[dict[str, Any]],
    ) -> str:
        instructions = (
            "You are Novi, an expert career and learning roadmap coach. "
            "Analyze the student's current learning progress, recent weekly check-in reflections, and "
            "roadmap status. Recommend an actionable adaptation plan to optimize their learning journey.\n\n"
            "STRICT RULES:\n"
            "1. You may ONLY recommend these 5 action types: add_task, skip_task, reschedule_task, adjust_priority, reschedule_roadmap.\n"
            "2. Completed tasks MUST NEVER be modified, skipped, deleted, or rescheduled. Do not touch completed tasks.\n"
            "3. Active tasks can have their target_date or priority adjusted, but CANNOT be skipped or marked completed.\n"
            "4. Only pending tasks can be skipped.\n"
            "5. Tasks can ONLY be added to existing milestones using valid milestone_ids from the context.\n"
            "6. If goal has a target_date, roadmap target_date MUST NOT exceed goal target_date. If goal target_date is not set, do not extend roadmap target date.\n"
            "7. Return ONLY raw JSON conforming to the requested schema. No markdown fences."
        )

        context = {
            "goal": {
                "title": goal.title,
                "description": goal.description,
                "target_date": str(goal.target_date) if goal.target_date else None,
                "goal_type": goal.goal_type,
            },
            "roadmap": {
                "title": roadmap.title,
                "description": roadmap.description,
                "target_date": str(roadmap.target_date) if roadmap.target_date else None,
                "status": roadmap.status,
            },
            "progress": {
                "total_tasks": counts["total"],
                "completed_tasks": counts["completed"],
                "active_tasks": counts["active"],
                "pending_tasks": counts["pending"],
                "skipped_tasks": counts["skipped"],
                "progress_percentage": progress_percentage,
            },
            "recent_checkin_reflections": checkin_reflections,
            "milestones_and_tasks": milestones_context,
        }

        return f"{instructions}\n\nCURRENT CONTEXT:\n{json.dumps(context, indent=2)}"

    def _owned_roadmap(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> Roadmap:
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        roadmap = self.roadmap_repo.get_by_id(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")
        return roadmap

    def _ensure_student(self, student_id: uuid.UUID) -> None:
        if not self.roadmap_repo.student_exists(student_id):
            raise LookupError("Student not found")

    def _ensure_goal_owned_by_student(self, student_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
        if not self.roadmap_repo.goal_exists(goal_id):
            raise LookupError("Goal not found")
        goal = self.roadmap_repo.get_goal(goal_id)
        if goal.student_id != student_id:
            raise PermissionError("Goal does not belong to this student")
        return goal
