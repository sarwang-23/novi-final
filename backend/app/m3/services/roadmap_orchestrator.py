"""
RoadmapOrchestrator – Step 7 & Step 14B: AI Roadmap Persistence / Orchestration.

Responsibilities
----------------
- Accept a validated GeneratedRoadmap (or a raw dict validated before touching the DB).
- Verify goal ownership (student_id == goal.student_id).
- Enforce the one-active-roadmap-per-goal business rule.
- Determine roadmap date boundaries (Goal.target_date as target, date.today() as default start).
- Invoke pure RoadmapScheduler when both start and target dates are available.
- Create Roadmap → Milestones → Tasks with scheduled dates inside ONE SQLAlchemy transaction.
- Commit only when every record has been staged successfully; roll back on any failure.
- Return a RoadmapOrchestrationResult containing the persisted objects + generated UUIDs.

The module-level generate_and_persist_roadmap function wires the Step 6
RoadmapGenerator to this orchestrator so that:
  - AI generation happens OUTSIDE the DB transaction.
  - If generation fails → no DB records are created.
  - If persistence fails → rollback is complete.
"""

from datetime import date
from typing import Any
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.m3.db.models import Goal, Milestone, Roadmap, Task
from app.m3.repositories.milestone_repository import MilestoneRepository
from app.m3.repositories.roadmap_repository import RoadmapRepository
from app.m3.repositories.task_repository import TaskRepository
from app.m3.schemas.roadmap_generation import GeneratedMilestone, GeneratedRoadmap, GeneratedTask
from app.m3.services.roadmap_scheduler import ScheduledRoadmap, schedule_roadmap


# ---------------------------------------------------------------------------
# Date helper at orchestration boundary
# ---------------------------------------------------------------------------


def _today() -> date:
    """Return date.today() at the orchestration boundary (can be patched in tests)."""
    return date.today()


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class OrchestrationError(RuntimeError):
    """Raised when roadmap orchestration/persistence fails."""


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


class RoadmapOrchestrationResult:
    """Holds the persisted SQLAlchemy objects after a successful commit."""

    def __init__(
        self,
        roadmap: Roadmap,
        milestones: list[Milestone],
        tasks_by_milestone: dict[uuid.UUID, list[Task]],
    ) -> None:
        self.roadmap = roadmap
        self.milestones = milestones
        self.tasks_by_milestone = tasks_by_milestone

    def to_dict(self) -> dict[str, Any]:
        """Return a serialisable hierarchical summary with all generated IDs and dates."""
        return {
            "roadmap_id": str(self.roadmap.id),
            "goal_id": str(self.roadmap.goal_id),
            "title": self.roadmap.title,
            "description": self.roadmap.description,
            "status": self.roadmap.status,
            "start_date": self.roadmap.start_date.isoformat() if self.roadmap.start_date else None,
            "target_date": self.roadmap.target_date.isoformat() if self.roadmap.target_date else None,
            "milestones": [
                {
                    "milestone_id": str(milestone.id),
                    "title": milestone.title,
                    "description": milestone.description,
                    "order_index": milestone.order_index,
                    "start_date": milestone.start_date.isoformat() if milestone.start_date else None,
                    "target_date": milestone.target_date.isoformat() if milestone.target_date else None,
                    "tasks": [
                        {
                            "task_id": str(task.id),
                            "title": task.title,
                            "description": task.description,
                            "priority": task.priority,
                            "order_index": task.order_index,
                            "start_date": task.start_date.isoformat() if task.start_date else None,
                            "target_date": task.target_date.isoformat() if task.target_date else None,
                        }
                        for task in self.tasks_by_milestone.get(milestone.id, [])
                    ],
                }
                for milestone in self.milestones
            ],
        }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class RoadmapOrchestrator:
    """Orchestrates atomic persistence of AI-generated roadmaps.

    The orchestrator owns the transaction boundary. It stages every entity
    with flush() so that foreign-key IDs are available before the next
    entity is created, then issues a single commit() only after the entire
    hierarchy (Roadmap → Milestones → Tasks) has been staged without error.
    Any exception triggers a full rollback so that no partial records remain.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.roadmap_repo = RoadmapRepository(db)
        self.milestone_repo = MilestoneRepository(db)
        self.task_repo = TaskRepository(db)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def persist_generated_roadmap(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        generated: "GeneratedRoadmap | dict[str, Any]",
        roadmap_status: str = "draft",
        roadmap_start_date: date | None = None,
    ) -> RoadmapOrchestrationResult:
        """Persist a validated AI-generated roadmap atomically.

        Parameters
        ----------
        student_id:
            UUID of the student who owns the goal.
        goal_id:
            UUID of the goal for which the roadmap is generated.
        generated:
            A validated GeneratedRoadmap instance **or** a raw dict that will
            be validated through the GeneratedRoadmap Pydantic schema before
            any DB operations begin. An invalid dict raises ValueError so
            that malformed AI output never reaches the database.
        roadmap_status:
            Initial status for the new Roadmap record. Defaults to "draft".
            Use "active" subject to the one-active-roadmap-per-goal rule.
        roadmap_start_date:
            Optional explicit roadmap start date. If None, defaults to date.today()
            when goal.target_date is present.

        Returns
        -------
        RoadmapOrchestrationResult
            Contains the committed Roadmap, Milestone list, and
            tasks-by-milestone dict – all with database-generated UUIDs and
            scheduler-assigned calendar dates if a target date was available.

        Raises
        ------
        ValueError
            If generated is an invalid dict, if start_date > target_date, or
            if an active roadmap already exists for the goal when roadmap_status is "active".
        LookupError
            If the student or goal cannot be found.
        PermissionError
            If the goal does not belong to the specified student.
        """
        # Validate raw dict input *before* any DB access.
        validated = self._validate_input(generated)

        try:
            # Pre-persistence ownership & business-rule checks.
            goal = self._validate_goal_ownership(student_id, goal_id)
            self._check_active_roadmap_conflict(goal_id, roadmap_status)

            # Determine roadmap start and target dates
            start_date, target_date = self._determine_roadmap_dates(
                goal=goal,
                explicit_start_date=roadmap_start_date or getattr(validated, "start_date", None),
            )

            # Invoke pure RoadmapScheduler when both dates are present
            scheduled_result: ScheduledRoadmap | None = None
            if start_date is not None and target_date is not None:
                if start_date > target_date:
                    raise ValueError(
                        f"Roadmap start date ({start_date}) must not be after target date ({target_date})"
                    )
                scheduled_result = schedule_roadmap(
                    roadmap_start_date=start_date,
                    roadmap_target_date=target_date,
                    milestones=validated.milestones,
                )

            # Atomic persistence: flush after each entity, single commit at end.
            roadmap = self._create_roadmap(
                goal_id=goal_id,
                generated=validated,
                status=roadmap_status,
                start_date=start_date,
                target_date=target_date,
            )
            milestones = self._create_milestones(
                roadmap_id=roadmap.id,
                generated_milestones=validated.milestones,
                scheduled_result=scheduled_result,
            )
            tasks_by_milestone = self._create_tasks(
                milestones=milestones,
                generated_milestones=validated.milestones,
                scheduled_result=scheduled_result,
            )

            # Single commit: everything succeeds or nothing persists.
            self.db.commit()
            return RoadmapOrchestrationResult(roadmap, milestones, tasks_by_milestone)

        except Exception:
            self.db.rollback()
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_roadmap_dates(
        goal: Goal,
        explicit_start_date: date | None = None,
    ) -> tuple[date | None, date | None]:
        """Establish start and target dates for the roadmap.

        Target date:
        - Primary source is Goal.target_date.
        - If Goal.target_date is None, Roadmap.target_date remains None (unscheduled).
        - Does NOT invent artificial dates (+30, +60, +90, +365).

        Start date:
        - If explicit_start_date is provided, use it.
        - Otherwise, if Goal.target_date is present, default to _today().
        - If Goal.target_date is None, default to explicit_start_date (or None).
        """
        target_date = goal.target_date
        if target_date is None:
            return explicit_start_date, None

        start_date = explicit_start_date or _today()
        return start_date, target_date

    @staticmethod
    def _validate_input(generated: "GeneratedRoadmap | dict[str, Any]") -> GeneratedRoadmap:
        """Return a validated GeneratedRoadmap; raise ValueError for invalid input."""
        if isinstance(generated, GeneratedRoadmap):
            return generated
        try:
            return GeneratedRoadmap.model_validate(generated)
        except ValidationError as exc:
            raise ValueError(
                f"Invalid GeneratedRoadmap data – AI output did not match the expected schema: {exc}"
            ) from exc

    def _validate_goal_ownership(self, student_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
        if not self.roadmap_repo.student_exists(student_id):
            raise LookupError("Student not found")
        if not self.roadmap_repo.goal_exists(goal_id):
            raise LookupError("Goal not found")
        goal = self.roadmap_repo.get_goal(goal_id)
        if goal.student_id != student_id:
            raise PermissionError("Goal does not belong to this student")
        return goal

    def _check_active_roadmap_conflict(self, goal_id: uuid.UUID, status: str) -> None:
        """Raise ValueError if an active roadmap already exists for the goal."""
        if status != "active":
            return
        existing_active = self.roadmap_repo.get_active_by_goal(goal_id)
        if existing_active is not None:
            raise ValueError("An active roadmap already exists for this goal")

    def _create_roadmap(
        self,
        goal_id: uuid.UUID,
        generated: GeneratedRoadmap,
        status: str,
        start_date: date | None = None,
        target_date: date | None = None,
    ) -> Roadmap:
        """Stage a new Roadmap record (flushed, not yet committed)."""
        return self.roadmap_repo.create(
            goal_id,
            {
                "title": generated.title,
                "description": generated.description,
                "status": status,
                "start_date": start_date,
                "target_date": target_date,
            },
        )

    def _create_milestones(
        self,
        roadmap_id: uuid.UUID,
        generated_milestones: list[GeneratedMilestone],
        scheduled_result: ScheduledRoadmap | None = None,
    ) -> list[Milestone]:
        """Stage all Milestone records in order (flushed after each, not committed)."""
        sched_by_order = {}
        if scheduled_result and scheduled_result.milestones:
            sched_by_order = {m.order_index: m for m in scheduled_result.milestones}

        milestones: list[Milestone] = []
        for gen_milestone in generated_milestones:
            sched_m = sched_by_order.get(gen_milestone.order_index)
            m_start = sched_m.start_date if sched_m else None
            m_target = sched_m.target_date if sched_m else None

            milestone = self.milestone_repo.create(
                roadmap_id,
                {
                    "title": gen_milestone.title,
                    "description": gen_milestone.description,
                    "order_index": gen_milestone.order_index,
                    "status": "pending",
                    "start_date": m_start,
                    "target_date": m_target,
                },
            )
            milestones.append(milestone)
        return milestones

    def _create_tasks(
        self,
        milestones: list[Milestone],
        generated_milestones: list[GeneratedMilestone],
        scheduled_result: ScheduledRoadmap | None = None,
    ) -> dict[uuid.UUID, list[Task]]:
        """Stage all Task records for every milestone (flushed, not committed)."""
        sched_tasks_by_order = {}
        if scheduled_result and scheduled_result.milestones:
            sched_tasks_by_order = {
                (m.order_index, t.order_index): t
                for m in scheduled_result.milestones
                for t in m.tasks
            }

        tasks_by_milestone: dict[uuid.UUID, list[Task]] = {}
        for milestone, gen_milestone in zip(milestones, generated_milestones):
            tasks: list[Task] = []
            for gen_task in gen_milestone.tasks:
                sched_t = sched_tasks_by_order.get(
                    (gen_milestone.order_index, gen_task.order_index)
                )
                t_start = sched_t.start_date if sched_t else None
                t_target = sched_t.target_date if sched_t else None

                task = self.task_repo.create(
                    milestone.id,
                    {
                        "title": gen_task.title,
                        "description": gen_task.description,
                        "priority": gen_task.priority,
                        "order_index": gen_task.order_index,
                        "status": "pending",
                        "start_date": t_start,
                        "target_date": t_target,
                    },
                )
                tasks.append(task)
            tasks_by_milestone[milestone.id] = tasks
        return tasks_by_milestone


# ---------------------------------------------------------------------------
# High-level coordinator: AI generation → validation → persistence
# ---------------------------------------------------------------------------


def generate_and_persist_roadmap(
    *,
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    db: Session,
    generator: Any,
    goal: Any,
    career: Any = None,
    career_match: Any = None,
    existing_skills: "list[Any] | None" = None,
    skill_gaps: "list[Any] | None" = None,
    readiness: Any = None,
    roadmap_status: str = "draft",
    roadmap_start_date: date | None = None,
) -> RoadmapOrchestrationResult:
    """Generate and persist an AI roadmap in two clearly separated phases.

    Phase 1 – AI Generation (outside DB transaction)
    -------------------------------------------------
    Calls ``generator.generate(...)`` with the provided context. The DB
    session is NOT involved at this point. If the generator raises any
    exception (AIProviderError, RoadmapGenerationError, etc.) the function
    re-raises immediately and **no DB records are created**.

    Phase 2 – Atomic Persistence
    -----------------------------
    Passes the validated ``GeneratedRoadmap`` to
    ``RoadmapOrchestrator.persist_generated_roadmap(...)``, which owns the
    transaction boundary, establishes date anchors via RoadmapScheduler, and
    commits or rolls back atomically.

    Parameters
    ----------
    student_id, goal_id:
        Identify the student and goal for ownership validation.
    db:
        Existing synchronous SQLAlchemy ``Session``.
    generator:
        A ``RoadmapGenerator`` instance (Step 6). Called to produce the roadmap.
    goal:
        The ``Goal`` SQLAlchemy model or compatible object passed to the generator.
    career, career_match, existing_skills, skill_gaps, readiness:
        Optional context forwarded to the generator.
    roadmap_status:
        Initial status of the persisted roadmap (``"draft"`` by default).
    roadmap_start_date:
        Optional explicit start date override.

    Returns
    -------
    RoadmapOrchestrationResult
        The committed hierarchy with all database-generated IDs and scheduled dates.
    """
    # Phase 1: AI generation – NO DB transaction open.
    generated: GeneratedRoadmap = generator.generate(
        goal=goal,
        career=career,
        career_match=career_match,
        existing_skills=existing_skills,
        skill_gaps=skill_gaps,
        readiness=readiness,
    )

    # Phase 2: Atomic persistence. The orchestrator validates the schema,
    # checks ownership and business rules, schedules dates, then commits or rolls back atomically.
    orchestrator = RoadmapOrchestrator(db)
    return orchestrator.persist_generated_roadmap(
        student_id=student_id,
        goal_id=goal_id,
        generated=generated,
        roadmap_status=roadmap_status,
        roadmap_start_date=roadmap_start_date,
    )
