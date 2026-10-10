import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel


class AIConfigurationError(RuntimeError):
    """Raised when the configured AI provider cannot be initialized."""


class AIProviderError(RuntimeError):
    """Raised when a configured AI provider cannot generate a response."""


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


class StructuredAIProvider(Protocol):
    def generate_structured(
        self, prompt: str, response_model: type[ResponseModel]
    ) -> ResponseModel | Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class AISettings:
    provider: str = "gemini"
    api_key: str | None = None
    model: str = "gemini-2.5-flash"

    @classmethod
    def from_environment(cls) -> "AISettings":
        from app.core.config import settings

        provider = os.getenv("AI_PROVIDER", "gemini").strip().casefold()
        api_key = (
            os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or None
        ) if provider == "gemini" else None
        model = (
            os.getenv("GEMINI_MODEL") or settings.GEMINI_MODEL or "gemini-2.5-flash"
        ).strip()
        return cls(provider=provider, api_key=api_key, model=model)


class GeminiProvider:
    """Gemini adapter behind the provider-neutral structured generation contract."""

    def __init__(self, settings: AISettings | None = None, client: Any = None):
        self.settings = settings or AISettings.from_environment()
        if self.settings.provider != "gemini":
            raise AIConfigurationError(
                f"Unsupported AI provider for this adapter: {self.settings.provider!r}"
            )
        if not self.settings.api_key and client is None:
            raise AIConfigurationError("GEMINI_API_KEY is not configured")
        self._client = client

    def generate_structured(
        self, prompt: str, response_model: type[ResponseModel]
    ) -> ResponseModel | Mapping[str, Any]:
        generate_text = None
        try:
            client = self._client or self._create_client()

            is_roadmap = response_model.__name__ == "GeneratedRoadmap"
            is_adaptation = response_model.__name__ == "GeneratedAdaptation"
            full_prompt = prompt
            if is_roadmap:
                # Build an ultra-explicit prompt with a concrete example so Gemini
                # knows *exactly* what field names and value types are expected.
                example = (
                    '{\n'
                    '  "title": "Roadmap title here",\n'
                    '  "description": "Overall description of the roadmap",\n'
                    '  "milestones": [\n'
                    '    {\n'
                    '      "title": "Milestone 1 title",\n'
                    '      "description": "What this milestone covers",\n'
                    '      "order_index": 0,\n'
                    '      "tasks": [\n'
                    '        {\n'
                    '          "title": "Task title",\n'
                    '          "description": "Detailed task description",\n'
                    '          "order_index": 0,\n'
                    '          "priority": "high"\n'
                    '        }\n'
                    '      ]\n'
                    '    }\n'
                    '  ]\n'
                    '}'
                )
                full_prompt = (
                    f"{prompt}\n\n"
                    "CRITICAL OUTPUT RULES:\n"
                    "1. Return ONLY raw JSON — no markdown, no ```json fences, no extra text.\n"
                    "2. Every task MUST be an object with keys: title, description, order_index (integer), priority (\"low\"|\"medium\"|\"high\").\n"
                    "3. Do NOT add any extra keys (e.g. target_date, status, id) to milestones or tasks.\n"
                    "4. Every milestone MUST include order_index (0-based integer).\n"
                    "5. Match this exact JSON structure:\n"
                    f"{example}"
                )
            elif is_adaptation:
                # Adaptation actions have strict field names; give Gemini an
                # exact example so it does not invent top-level keys.
                adaptation_example = (
                    '{\n'
                    '  "assessment": "The student is progressing steadily through the foundations.",\n'
                    '  "reasoning": "They completed the core math tasks and reported strong focus, so the next step is to deepen practice.",\n'
                    '  "recommended_actions": [\n'
                    '    {\n'
                    '      "action_type": "adjust_priority",\n'
                    '      "task_id": "00000000-0000-0000-0000-000000000001",\n'
                    '      "new_priority": "high",\n'
                    '      "reason": "This task builds on the concepts already learned."\n'
                    '    },\n'
                    '    {\n'
                    '      "action_type": "add_task",\n'
                    '      "milestone_id": "00000000-0000-0000-0000-000000000002",\n'
                    '      "task": {\n'
                    '        "title": "Review gradient descent notes",\n'
                    '        "description": "Consolidate the intuition and derivation",\n'
                    '        "priority": "medium",\n'
                    '        "order_index": 3,\n'
                    '        "target_date": "2026-10-15"\n'
                    '      },\n'
                    '      "reason": "A short review consolidates the recent milestone."\n'
                    '    }\n'
                    '  ]\n'
                    '}'
                )
                full_prompt = (
                    f"{prompt}\n\n"
                    "CRITICAL OUTPUT RULES:\n"
                    "1. Return ONLY raw JSON — no markdown, no ```json fences, no extra text.\n"
                    "2. Use EXACTLY these top-level keys: assessment (string), reasoning (string), recommended_actions (array). Do NOT add other top-level keys (e.g. summary, highlighted_actions).\n"
                    "3. recommended_actions MUST be an array; if empty, return an empty array.\n"
                    "4. Each action MUST include action_type plus reason (non-empty), plus the specific fields shown in the example.\n"
                    "5. Use ONLY milestone_id/task_id values from the CURRENT CONTEXT above — never invent ids.\n"
                    "6. Match this exact JSON structure:\n"
                    f"{adaptation_example}"
                )

            response = client.models.generate_content(
                model=self.settings.model,
                contents=full_prompt,
                config={"response_mime_type": "application/json"},
            )

            generate_text = getattr(response, "text", None)
            if not generate_text:
                raise AIProviderError("Gemini returned an empty response")

            # Strip markdown code fences if Gemini wraps in ```json … ```
            text = generate_text.strip()
            if text.startswith("```"):
                lines = text.splitlines()
                text = "\n".join(
                    line for line in lines if not line.startswith("```")
                ).strip()

            data = json.loads(text)
            # Normalize: coerce string tasks → task objects, strip unknown fields.
            if is_roadmap:
                data = self._normalize_roadmap_data(data)
            return response_model.model_validate(data)

        except AIProviderError:
            raise
        except Exception as error:
            snippet = ""
            if generate_text:
                snippet = f" Response: {generate_text[:300]}"
            raise AIProviderError(
                f"Gemini structured generation failed: {type(error).__name__}{snippet}"
            ) from error

    @staticmethod
    def _clean_schema(schema: dict[str, Any]) -> dict[str, Any]:
        """Recursively remove keys that Gemini's API does not accept."""
        REMOVE_KEYS = {"additionalProperties", "additional_properties", "$defs", "title"}
        if not isinstance(schema, dict):
            return schema
        cleaned = {}
        for k, v in schema.items():
            if k in REMOVE_KEYS:
                continue
            if isinstance(v, dict):
                cleaned[k] = GeminiProvider._clean_schema(v)
            elif isinstance(v, list):
                cleaned[k] = [
                    GeminiProvider._clean_schema(item) if isinstance(item, dict) else item
                    for item in v
                ]
            else:
                cleaned[k] = v
        return cleaned

    @staticmethod
    def _normalize_roadmap_data(data: Any) -> Any:
        """Coerce Gemini's response into the exact shape our Pydantic schema expects.

        Handles two common deviations:
        - Tasks returned as plain strings instead of {title, description, order_index, priority}
        - Extra fields on milestones/tasks (e.g. target_date, status) that extra="forbid" rejects.
        """
        if not isinstance(data, dict):
            return data

        MILESTONE_KEYS = {"title", "description", "order_index", "tasks"}
        TASK_KEYS = {"title", "description", "order_index", "priority"}
        VALID_PRIORITIES = {"low", "medium", "high"}

        normalized_milestones = []
        for m_idx, milestone in enumerate(data.get("milestones", [])):
            if not isinstance(milestone, dict):
                continue

            # Strip any extra keys Gemini added that our schema forbids.
            clean_milestone = {k: v for k, v in milestone.items() if k in MILESTONE_KEYS}

            # Ensure order_index exists.
            if "order_index" not in clean_milestone:
                clean_milestone["order_index"] = m_idx

            # Normalize tasks list.
            normalized_tasks = []
            for t_idx, task in enumerate(milestone.get("tasks", [])):
                if isinstance(task, str):
                    # Gemini returned tasks as plain strings – convert to full objects.
                    normalized_tasks.append({
                        "title": task[:200],
                        "description": task,
                        "order_index": t_idx,
                        "priority": "medium",
                    })
                elif isinstance(task, dict):
                    clean_task = {k: v for k, v in task.items() if k in TASK_KEYS}
                    if "order_index" not in clean_task:
                        clean_task["order_index"] = t_idx
                    if "priority" not in clean_task or clean_task["priority"] not in VALID_PRIORITIES:
                        clean_task["priority"] = "medium"
                    if "description" not in clean_task:
                        clean_task["description"] = clean_task.get("title", "")
                    normalized_tasks.append(clean_task)

            clean_milestone["tasks"] = normalized_tasks
            normalized_milestones.append(clean_milestone)

        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "milestones": normalized_milestones,
        }

    def _create_client(self) -> Any:
        try:
            from google import genai

            self._client = genai.Client(api_key=self.settings.api_key)
            return self._client
        except Exception as error:
            raise AIProviderError(
                f"Gemini client initialization failed: {type(error).__name__}"
            ) from error


def create_default_provider(settings: AISettings | None = None) -> StructuredAIProvider:
    resolved = settings or AISettings.from_environment()
    if resolved.provider == "gemini":
        return GeminiProvider(resolved)
    raise AIConfigurationError(f"Unsupported AI provider: {resolved.provider!r}")