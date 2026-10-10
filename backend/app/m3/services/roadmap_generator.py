import json
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ValidationError

from app.m3.schemas.roadmap_generation import GeneratedRoadmap
from app.m3.services.ai_provider import (
    AIConfigurationError,
    AIProviderError,
    StructuredAIProvider,
    create_default_provider,
)
from app.m3.services.dataset_service import DatasetError, DatasetService, RoadmapContext, RoadmapNotFound


class RoadmapGenerationError(RuntimeError):
    """Raised when generated roadmap output cannot be validated."""


class RoadmapContextBuilder:
    def build(
        self,
        goal: Any,
        career: Any = None,
        career_match: Any = None,
        existing_skills: Sequence[Any] | None = None,
        skill_gaps: Sequence[Any] | None = None,
        readiness: Any = None,
        roadmap_context: Mapping[str, Any] | None = None,
        dataset_available: bool = False,
    ) -> dict[str, Any]:
        return {
            "goal": self._serialize(goal, ("title", "description", "target_date", "status", "priority")),
            "career": self._serialize(career, ("id", "name", "description", "category", "industry")),
            "career_match": self._serialize(
                career_match,
                ("id", "career_id", "final_score", "rank", "why_fit"),
            ),
            "existing_skills": [
                self._serialize(skill, ("id", "name", "level", "confidence", "source"))
                for skill in (existing_skills or [])
            ],
            "skill_gaps": [
                self._serialize(
                    gap,
                    ("id", "skill_id", "skill_name", "student_level", "required_level", "gap_level", "priority"),
                )
                for gap in (skill_gaps or [])
            ],
            "readiness": self._serialize(
                readiness,
                ("overall_score", "skills_score", "experience_score", "education_score", "gap_score", "readiness_level"),
            ),
            "roadmap_context": dict(roadmap_context) if roadmap_context else None,
            "dataset_available": dataset_available,
        }

    @staticmethod
    def _serialize(value: Any, fields: Sequence[str]) -> dict[str, Any] | None:
        if value is None:
            return None
        if isinstance(value, Mapping):
            return {field: value[field] for field in fields if field in value and value[field] is not None}
        return {
            field: getattr(value, field)
            for field in fields
            if hasattr(value, field) and getattr(value, field) is not None
        }


class RoadmapGenerator:
    def __init__(
        self,
        ai_provider: StructuredAIProvider | None = None,
        dataset_service: DatasetService | None = None,
        context_builder: RoadmapContextBuilder | None = None,
        max_dataset_topics: int = 20,
    ):
        self.ai_provider = ai_provider or create_default_provider()
        self.dataset_service = dataset_service or DatasetService()
        self.context_builder = context_builder or RoadmapContextBuilder()
        self.max_dataset_topics = max_dataset_topics

    def generate(
        self,
        goal: Any,
        career: Any = None,
        career_match: Any = None,
        existing_skills: Sequence[Any] | None = None,
        skill_gaps: Sequence[Any] | None = None,
        readiness: Any = None,
    ) -> GeneratedRoadmap:
        if goal is None:
            raise ValueError("A user goal is required for roadmap generation")

        career_name = self._career_name(career)
        dataset_context: dict[str, Any] | None = None
        dataset_available = False
        if career_name:
            try:
                roadmap = self.dataset_service.get_roadmap_by_career_name(career_name)
                dataset_context = self._dataset_context(roadmap, skill_gaps)
                dataset_available = True
            except DatasetError:
                dataset_context = None

        context = self.context_builder.build(
            goal=goal,
            career=career,
            career_match=career_match,
            existing_skills=existing_skills,
            skill_gaps=skill_gaps,
            readiness=readiness,
            roadmap_context=dataset_context,
            dataset_available=dataset_available,
        )
        prompt = self._build_prompt(context)
        try:
            generated = self.ai_provider.generate_structured(prompt, GeneratedRoadmap)
            return generated if isinstance(generated, GeneratedRoadmap) else GeneratedRoadmap.model_validate(generated)
        except ValidationError as error:
            raise RoadmapGenerationError(
                f"AI provider returned an invalid roadmap structure: {error}"
            ) from error
        except AIConfigurationError:
            raise
        except AIProviderError:
            raise

    def _dataset_context(
        self, roadmap: RoadmapContext, skill_gaps: Sequence[Any] | None
    ) -> dict[str, Any]:
        keywords = [self._skill_name(gap) for gap in (skill_gaps or [])]
        topics = self.dataset_service.get_relevant_topics(roadmap.career_name, keywords) if keywords else roadmap.topics
        return {
            "career_id": roadmap.career_id,
            "career_name": roadmap.career_name,
            "topics": [topic.model_dump_for_context() for topic in topics[: self.max_dataset_topics]],
        }

    @staticmethod
    def _skill_name(value: Any) -> str:
        if isinstance(value, Mapping):
            return str(value.get("skill_name") or value.get("name") or value.get("skill_id") or "")
        skill = getattr(value, "skill", None)
        return str(getattr(skill, "name", "") or getattr(value, "skill_name", "") or "")

    @staticmethod
    def _career_name(career: Any) -> str | None:
        if isinstance(career, Mapping):
            return career.get("name") or career.get("slug")
        return getattr(career, "name", None) or getattr(career, "slug", None)

    @staticmethod
    def _build_prompt(context: Mapping[str, Any]) -> str:
        grounding = (
            "A relevant roadmap dataset context is available. Use it as grounding, "
            "prefer its topics where useful, and personalize rather than copy it."
            if context["dataset_available"]
            else "No matching roadmap dataset context is available. Use your own knowledge."
        )
        instructions = (
            "Act as an expert career roadmap planner. Generate a personalized, practical learning roadmap. "
            "Prioritize skill gaps, do not invent user skills, and avoid repeating mastered skills unless reinforcement helps. "
            "Order milestones from foundational to advanced, make tasks actionable and reasonably granular, "
            "and respect the target date when provided. Keep the roadmap realistic and not excessively large. "
            "Return only the requested JSON schema. Do not return markdown, database IDs, or explanations outside the schema. "
            f"{grounding}"
        )
        return instructions + "\n\nUSER CONTEXT:\n" + json.dumps(context, default=str, ensure_ascii=True)