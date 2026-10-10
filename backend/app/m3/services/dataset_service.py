import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetError(Exception):
    """Base exception for local roadmap dataset failures."""


class DatasetDirectoryNotFound(DatasetError):
    """Raised when the configured roadmap directory does not exist."""


class DatasetFileNotFound(DatasetError):
    """Raised when a requested roadmap JSON file does not exist."""


class InvalidDatasetError(DatasetError):
    """Raised when a roadmap JSON file is unreadable or malformed."""


class RoadmapNotFound(DatasetError):
    """Raised when no roadmap matches the requested career identifier."""


class RoadmapResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    title: str
    url: str


class RoadmapTopic(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str
    node_id: str = Field(alias="nodeId")
    title: str
    description: str | None = None
    resources: list[RoadmapResource] = Field(default_factory=list)

    def model_dump_for_context(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)


class RoadmapContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str
    topic_count: int = Field(alias="topicCount")
    topics: list[RoadmapTopic]

    @property
    def career_id(self) -> str:
        return self.slug

    @property
    def career_name(self) -> str:
        return self.slug.replace("-", " ")

    def model_dump_for_context(self) -> dict[str, Any]:
        value = self.model_dump(by_alias=True)
        value["career_id"] = self.career_id
        value["career_name"] = self.career_name
        return value


class AvailableRoadmap(BaseModel):
    career_id: str
    career_name: str
    topic_count: int


class DatasetService:
    """Loads normalized local roadmap JSON for downstream roadmap generation."""

    _cache: dict[Path, tuple[int, list[RoadmapContext]]] = {}

    def __init__(self, data_directory: str | Path | None = None):
        if data_directory is not None:
            self.data_directory = Path(data_directory)
        else:
            from app.core.config import PROJECT_ROOT

            self.data_directory = PROJECT_ROOT / "frontend"

    def list_available_roadmaps(self) -> list[AvailableRoadmap]:
        roadmaps: list[AvailableRoadmap] = []
        for roadmap in self._all_roadmaps():
            roadmaps.append(
                AvailableRoadmap(
                    career_id=roadmap.career_id,
                    career_name=roadmap.career_name,
                    topic_count=roadmap.topic_count,
                )
            )
        return sorted(roadmaps, key=lambda roadmap: self._normalize(roadmap.career_id))

    def get_roadmap_by_career_name(self, career_name: str) -> RoadmapContext:
        normalized_name = self._required_identifier(career_name)
        for roadmap in self._all_roadmaps():
            if self._normalize(roadmap.slug) == normalized_name:
                return roadmap
        raise RoadmapNotFound(f"Roadmap not found for career name: {career_name!r}")

    def get_roadmap_by_career_id(self, career_id: str) -> RoadmapContext:
        normalized_id = self._required_identifier(career_id)
        for roadmap in self._all_roadmaps():
            if self._normalize(roadmap.career_id) == normalized_id:
                return roadmap
        raise RoadmapNotFound(f"Roadmap not found for career id: {career_id!r}")

    def get_relevant_topics(
        self, career_name: str, keywords: list[str] | tuple[str, ...] | None = None
    ) -> list[RoadmapTopic]:
        roadmap = self.get_roadmap_by_career_name(career_name)
        if keywords is None:
            return roadmap.topics
        normalized_keywords = {
            self._required_identifier(keyword) for keyword in keywords
        }
        if not normalized_keywords:
            return []
        return [
            topic
            for topic in roadmap.topics
            if self._normalize(topic.slug) in normalized_keywords
            or self._normalize(topic.title) in normalized_keywords
        ]

    def clear_cache(self) -> None:
        self._cache.clear()

    def reload(self) -> None:
        self.clear_cache()

    def _roadmap_files(self) -> list[Path]:
        if not self.data_directory.exists():
            raise DatasetDirectoryNotFound(
                f"Roadmap dataset directory does not exist: {self.data_directory}"
            )
        if not self.data_directory.is_dir():
            raise DatasetDirectoryNotFound(
                f"Roadmap dataset path is not a directory: {self.data_directory}"
            )
        files = sorted(self.data_directory.glob("*.json"))
        if not files:
            raise DatasetFileNotFound(
                f"No roadmap JSON files found in: {self.data_directory}"
            )
        return files

    def _all_roadmaps(self) -> list[RoadmapContext]:
        roadmaps: list[RoadmapContext] = []
        seen: set[str] = set()
        for path in self._roadmap_files():
            for roadmap in self._load_file(path):
                normalized_slug = self._normalize(roadmap.slug)
                if normalized_slug in seen:
                    raise InvalidDatasetError(
                        f"Duplicate roadmap slug {roadmap.slug!r} found in {path}"
                    )
                seen.add(normalized_slug)
                roadmaps.append(roadmap)
        return roadmaps

    def _load_file(self, path: Path) -> list[RoadmapContext]:
        cache_entry = self._cache.get(path)
        modified_at = path.stat().st_mtime_ns
        if cache_entry is not None and cache_entry[0] == modified_at:
            return cache_entry[1]

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise DatasetFileNotFound(f"Roadmap dataset file does not exist: {path}") from error
        except json.JSONDecodeError as error:
            raise InvalidDatasetError(f"Invalid JSON in roadmap dataset file: {path}") from error
        except OSError as error:
            raise InvalidDatasetError(f"Could not read roadmap dataset file: {path}") from error

        try:
            roadmaps = self._parse_payload(payload, path)
        except InvalidDatasetError:
            raise
        except Exception as error:
            raise InvalidDatasetError(f"Invalid roadmap dataset structure in {path}: {error}") from error

        self._cache[path] = (modified_at, roadmaps)
        return roadmaps

    def _parse_payload(self, payload: Any, path: Path) -> list[RoadmapContext]:
        if not isinstance(payload, dict) or not isinstance(payload.get("roadmaps"), list):
            raise InvalidDatasetError(
                f"Invalid roadmap dataset structure in {path}: expected a 'roadmaps' list"
            )
        try:
            return [RoadmapContext.model_validate(item) for item in payload["roadmaps"]]
        except Exception as error:
            raise InvalidDatasetError(
                f"Invalid roadmap record in {path}: {error}"
            ) from error

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().replace("-", " ").replace("_", " ")).casefold()

    def _required_identifier(self, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Career name or id must be a non-empty string")
        return self._normalize(value)
