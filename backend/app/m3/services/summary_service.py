import json
import uuid
from datetime import date
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.m3.db.models import Roadmap, WeeklyCheckin
from app.m3.repositories.checkin_repository import WeeklyCheckinRepository
from app.m3.repositories.roadmap_repository import RoadmapRepository
from app.m3.schemas.weekly_checkin import GeneratedWeeklySummary, WeeklySummaryResponse
from app.m3.services.ai_provider import (
    AIConfigurationError,
    AIProviderError,
    StructuredAIProvider,
    create_default_provider,
)


class ServiceUnavailableError(RuntimeError):
    """Raised when an external service such as the AI provider is unavailable."""

    pass


class WeeklySummaryService:
    def __init__(
        self,
        db: Session,
        ai_provider: StructuredAIProvider | None = None,
    ):
        self.db = db
        self.checkin_repo = WeeklyCheckinRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.ai_provider = ai_provider

    def generate(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        checkin_id: uuid.UUID,
    ) -> WeeklySummaryResponse:
        roadmap = self._owned_roadmap(student_id, goal_id, roadmap_id)
        checkin = self._owned_checkin(roadmap_id, checkin_id)

        # Collect non-null, non-empty reflections only
        reflections = {}
        for field in ("accomplished", "learned", "challenged", "proud_of", "improve_next"):
            val = getattr(checkin, field)
            if val is not None and val.strip():
                reflections[field] = val.strip()

        # Reject if all 5 reflection fields are null or empty
        if not reflections:
            raise ValueError("Check-in has no reflection data to summarize")

        # Context details
        goal = self.checkin_repo.get_goal(goal_id)
        goal_title = goal.title if goal else ""
        goal_description = goal.description if goal and goal.description else ""
        goal_target_date = str(goal.target_date) if goal and getattr(goal, "target_date", None) else None

        # Calculate progress from all-time roadmap task counts
        counts = self.roadmap_repo.get_task_counts_for_roadmap(roadmap_id)
        total = counts["total"]
        completed = counts["completed"]
        progress_percentage = round(completed / total * 100, 2) if total > 0 else 0.0

        prompt = self._build_prompt(
            week_start_date=checkin.week_start_date,
            roadmap_title=roadmap.title,
            goal_title=goal_title,
            goal_description=goal_description,
            goal_target_date=goal_target_date,
            progress_percentage=progress_percentage,
            completed_tasks=completed,
            total_tasks=total,
            reflections=reflections,
        )

        provider = self.ai_provider
        if provider is None:
            try:
                provider = create_default_provider()
            except AIConfigurationError as exc:
                raise ServiceUnavailableError("AI provider is not configured") from exc

        try:
            generated = provider.generate_structured(prompt, GeneratedWeeklySummary)
            if not isinstance(generated, GeneratedWeeklySummary):
                generated = GeneratedWeeklySummary.model_validate(generated)
        except (AIProviderError, AIConfigurationError) as exc:
            raise ServiceUnavailableError(f"AI summary generation failed: {exc}") from exc
        except ValidationError as exc:
            raise ServiceUnavailableError(f"Invalid AI summary format: {exc}") from exc

        return WeeklySummaryResponse(
            checkin_id=checkin.id,
            roadmap_id=roadmap.id,
            week_start_date=checkin.week_start_date,
            roadmap_title=roadmap.title,
            progress_percentage=progress_percentage,
            summary=generated.summary,
            highlights=generated.highlights,
            encouragement=generated.encouragement,
            focus_for_next_week=generated.focus_for_next_week,
        )

    @staticmethod
    def _build_prompt(
        week_start_date: date,
        roadmap_title: str,
        goal_title: str,
        goal_description: str,
        goal_target_date: str | None,
        progress_percentage: float,
        completed_tasks: int,
        total_tasks: int,
        reflections: dict[str, str],
    ) -> str:
        instructions = (
            "You are Novi, a warm, supportive career coach.\n\n"
            "Produce:\n"
            "- 150–400 word personalized summary addressing the student directly using second-person 'you'\n"
            "- 2–4 meaningful highlights\n"
            "- one motivational encouragement sentence\n"
            "- one actionable focus for next week\n\n"
            "Ground every claim in the supplied data.\n"
            "Do not invent achievements, skills, tasks, or progress.\n"
            "Return structured JSON only.\n"
            "No markdown fences.\n"
            "Return ONLY the requested JSON object with keys: summary, highlights, encouragement, focus_for_next_week."
        )

        context: dict[str, Any] = {
            "goal_title": goal_title,
            "roadmap_title": roadmap_title,
            "week_start_date": str(week_start_date),
            "current_roadmap_progress_percentage": progress_percentage,
            "completed_task_count": completed_tasks,
            "total_task_count": total_tasks,
            "student_reflections": reflections,
        }
        if goal_target_date:
            context["goal_target_date"] = goal_target_date
        if goal_description:
            context["goal_description"] = goal_description

        return f"{instructions}\n\nCONTEXT:\n{json.dumps(context, indent=2)}"

    def _owned_roadmap(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> Roadmap:
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        roadmap = self.checkin_repo.get_roadmap(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")
        return roadmap

    def _owned_checkin(
        self,
        roadmap_id: uuid.UUID,
        checkin_id: uuid.UUID,
    ) -> WeeklyCheckin:
        checkin = self.checkin_repo.get_by_id(checkin_id)
        if checkin is None:
            raise LookupError("Weekly check-in not found")
        if checkin.roadmap_id != roadmap_id:
            raise PermissionError("Weekly check-in does not belong to this roadmap")
        return checkin

    def _ensure_student(self, student_id: uuid.UUID) -> None:
        if not self.checkin_repo.student_exists(student_id):
            raise LookupError("Student not found")

    def _ensure_goal_owned_by_student(self, student_id: uuid.UUID, goal_id: uuid.UUID):
        if not self.checkin_repo.goal_exists(goal_id):
            raise LookupError("Goal not found")
        goal = self.checkin_repo.get_goal(goal_id)
        if goal.student_id != student_id:
            raise PermissionError("Goal does not belong to this student")
        return goal
