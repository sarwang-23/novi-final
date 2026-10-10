import calendar
import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.m3.db.models import Roadmap
from app.m3.repositories.roadmap_repository import RoadmapRepository
from app.m3.services.roadmap_scheduler import schedule_roadmap
from app.m3.schemas.roadmap import (
    MilestoneInRoadmap,
    RoadmapCreate,
    RoadmapFullResponse,
    RoadmapProgressResponse,
    RoadmapTimelineResponse,
    RoadmapUpdate,
    TaskInRoadmap,
    TimelineFocusMilestone,
    TimelineSummary,
    TimelineTask,
)


class RoadmapService:
    def __init__(self, db: Session):
        self.repository = RoadmapRepository(db)
        self.db = db

    def create(self, student_id: uuid.UUID, goal_id: uuid.UUID, data: RoadmapCreate) -> Roadmap:
        self._ensure_student(student_id)
        goal = self._ensure_goal_owned_by_student(student_id, goal_id)
        values = data.model_dump()
        self._validate_dates(values)
        self._check_active_roadmap_conflict(goal_id, values.get("status"))
        try:
            roadmap = self.repository.create(goal_id, values)
            self.db.commit()
            return roadmap
        except Exception:
            self.db.rollback()
            raise

    def list(self, student_id: uuid.UUID, goal_id: uuid.UUID) -> list[Roadmap]:
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        return self.repository.list_by_goal(goal_id)

    def get(self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID) -> Roadmap:
        roadmap = self._owned_roadmap(student_id, goal_id, roadmap_id)
        return roadmap

    def update(
        self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID, data: RoadmapUpdate
    ) -> Roadmap:
        self._ensure_student(student_id)
        goal = self._ensure_goal_owned_by_student(student_id, goal_id)

        roadmap = self.repository.get_by_id(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")

        values = data.model_dump(exclude_unset=True)
        self._validate_dates(values)

        # Check active roadmap conflict if status is being changed to 'active'
        new_status = values.get("status", roadmap.status)
        if new_status == "active" and roadmap.status != "active":
            self._check_active_roadmap_conflict(goal_id, new_status)

        # Target date update scheduling integration (Step 14D)
        target_date_in_payload = "target_date" in values
        new_target_date = values.get("target_date")
        target_date_changed = target_date_in_payload and (new_target_date != roadmap.target_date)

        # 1. Goal.target_date boundary validation
        if target_date_in_payload and new_target_date is not None:
            if goal.target_date is not None and new_target_date > goal.target_date:
                raise ValueError(
                    f"Roadmap target_date ({new_target_date}) cannot exceed goal target_date ({goal.target_date})"
                )

        # 2. Date range validation with existing start_date
        effective_start = values.get("start_date", roadmap.start_date)
        if target_date_in_payload and new_target_date is not None and effective_start is not None:
            if effective_start > new_target_date:
                raise ValueError(
                    f"start_date ({effective_start}) must not be after target_date ({new_target_date})"
                )

        try:
            # If target_date changed to a valid date and start_date exists, reschedule incomplete milestones/tasks
            if target_date_changed and new_target_date is not None and effective_start is not None:
                full_roadmap = self.repository.get_full_hierarchy(roadmap_id)
                target_rm = full_roadmap if full_roadmap is not None else roadmap
                self._apply_schedule_to_hierarchy(target_rm, effective_start, new_target_date)

            updated = self.repository.update(roadmap, values)
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def delete(self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID) -> None:
        roadmap = self._owned_roadmap(student_id, goal_id, roadmap_id)
        try:
            self.repository.delete(roadmap)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _owned_roadmap(
        self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID
    ) -> Roadmap:
        self._ensure_student(student_id)
        self._ensure_goal_owned_by_student(student_id, goal_id)
        roadmap = self.repository.get_by_id(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")
        return roadmap

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

    def _validate_dates(self, values: dict) -> None:
        """Validate date logic: start_date must not be after target_date."""
        start_date = values.get("start_date")
        target_date = values.get("target_date")
        
        if start_date and target_date and start_date > target_date:
            raise ValueError("start_date must not be after target_date")

    def _check_active_roadmap_conflict(self, goal_id: uuid.UUID, status: str | None) -> None:
        """Prevent multiple active roadmaps for the same goal."""
        if status != "active":
            return
        
        existing_active = self.repository.get_active_by_goal(goal_id)
        if existing_active is not None:
            raise ValueError("An active roadmap already exists for this goal")

    def get_progress(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> RoadmapProgressResponse:
        """Step 8B: Return dynamic progress for a roadmap.

        Progress = completed_tasks / total_tasks * 100 across ALL milestones, rounded to 2dp.
        skipped and active tasks do NOT count as completed.
        Returns 0.0 when the roadmap has no tasks.
        Ownership is fully validated before any aggregation query.
        """
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        counts = self.repository.get_task_counts_for_roadmap(roadmap_id)
        total = counts["total"]
        completed = counts["completed"]
        percentage = round(completed / total * 100, 2) if total > 0 else 0.0
        return RoadmapProgressResponse(
            roadmap_id=roadmap_id,
            total_tasks=total,
            completed_tasks=completed,
            active_tasks=counts["active"],
            pending_tasks=counts["pending"],
            skipped_tasks=counts["skipped"],
            progress_percentage=percentage,
        )

    def get_full(
        self, student_id: uuid.UUID, goal_id: uuid.UUID, roadmap_id: uuid.UUID
    ) -> RoadmapFullResponse:
        """Return the complete roadmap hierarchy in one response without N+1 queries.

        Roadmap → Milestones (ordered by order_index) → Tasks (ordered by order_index).
        Includes task counts per milestone and overall roadmap progress.
        """
        self._owned_roadmap(student_id, goal_id, roadmap_id)
        roadmap = self.repository.get_full_hierarchy(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")

        sorted_milestones = sorted(
            roadmap.milestones,
            key=lambda m: (m.order_index, m.created_at, str(m.id)),
        )

        milestones_data = []
        total_tasks = 0
        completed_tasks = 0

        for milestone in sorted_milestones:
            sorted_tasks = sorted(
                milestone.tasks,
                key=lambda t: (t.order_index, t.created_at, str(t.id)),
            )
            m_total = len(sorted_tasks)
            m_completed = sum(1 for t in sorted_tasks if t.status == "completed")
            total_tasks += m_total
            completed_tasks += m_completed

            tasks_data = [
                TaskInRoadmap.model_validate(task) for task in sorted_tasks
            ]
            milestones_data.append(
                MilestoneInRoadmap(
                    id=milestone.id,
                    roadmap_id=milestone.roadmap_id,
                    title=milestone.title,
                    description=milestone.description,
                    status=milestone.status,
                    order_index=milestone.order_index,
                    start_date=milestone.start_date,
                    target_date=milestone.target_date,
                    created_at=milestone.created_at,
                    updated_at=milestone.updated_at,
                    total_tasks=m_total,
                    completed_tasks=m_completed,
                    tasks=tasks_data,
                )
            )

        progress_percentage = (
            round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0.0
        )

        return RoadmapFullResponse(
            id=roadmap.id,
            goal_id=roadmap.goal_id,
            title=roadmap.title,
            description=roadmap.description,
            status=roadmap.status,
            start_date=roadmap.start_date,
            target_date=roadmap.target_date,
            created_at=roadmap.created_at,
            updated_at=roadmap.updated_at,
            progress_percentage=progress_percentage,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            milestones=milestones_data,
        )

    def get_timeline(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        view: str = "week",
        anchor_date: date | None = None,
    ) -> RoadmapTimelineResponse:
        """Project tasks for a roadmap into a Year, Month, or Week temporal window.

        Only tasks with target_date falling in [period_start, period_end] are included.
        Tasks with NULL target_date are excluded from calendar periods.
        """
        self._owned_roadmap(student_id, goal_id, roadmap_id)

        view_clean = (view or "week").lower().strip()
        if view_clean not in ("year", "month", "week"):
            raise ValueError(f"Invalid view: '{view}'. Must be 'year', 'month', or 'week'.")

        target = anchor_date or date.today()
        today = date.today()

        if view_clean == "week":
            period_start = target - timedelta(days=target.weekday())
            period_end = period_start + timedelta(days=6)
            current_monday = today - timedelta(days=today.weekday())
            is_current = (period_start == current_monday)
        elif view_clean == "month":
            period_start = date(target.year, target.month, 1)
            _, last_day = calendar.monthrange(target.year, target.month)
            period_end = date(target.year, target.month, last_day)
            is_current = (target.year == today.year and target.month == today.month)
        else:  # "year"
            period_start = date(target.year, 1, 1)
            period_end = date(target.year, 12, 31)
            is_current = (target.year == today.year)

        rows = self.repository.get_timeline_tasks(roadmap_id, period_start, period_end)

        timeline_tasks = []
        focus_milestones_dict = {}
        counts = {"total": 0, "completed": 0, "active": 0, "pending": 0, "skipped": 0}

        for task, milestone_title, milestone_order_index in rows:
            timeline_tasks.append(
                TimelineTask(
                    id=task.id,
                    milestone_id=task.milestone_id,
                    milestone_title=milestone_title,
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    order_index=task.order_index,
                    start_date=task.start_date,
                    target_date=task.target_date,
                )
            )
            if task.milestone_id not in focus_milestones_dict:
                focus_milestones_dict[task.milestone_id] = TimelineFocusMilestone(
                    id=task.milestone_id,
                    title=milestone_title,
                    order_index=milestone_order_index,
                )
            counts["total"] += 1
            if task.status in counts:
                counts[task.status] += 1

        sorted_focus = sorted(focus_milestones_dict.values(), key=lambda m: m.order_index)

        return RoadmapTimelineResponse(
            roadmap_id=roadmap_id,
            view=view_clean,
            period_start=period_start,
            period_end=period_end,
            is_current=is_current,
            focus_milestones=sorted_focus,
            tasks=timeline_tasks,
            summary=TimelineSummary(**counts),
        )

    def _apply_schedule_to_hierarchy(
        self,
        roadmap: Roadmap,
        start_date: date,
        target_date: date,
    ) -> None:
        """Deterministically recalculate and stage dates onto milestones and incomplete tasks."""
        milestones_input = [
            {
                "id": m.id,
                "order_index": m.order_index,
                "tasks": [
                    {
                        "id": t.id,
                        "order_index": t.order_index,
                        "priority": t.priority,
                        "status": t.status,
                        "start_date": t.start_date,
                        "target_date": t.target_date,
                    }
                    for t in m.tasks
                ],
            }
            for m in roadmap.milestones
        ]

        scheduled = schedule_roadmap(
            roadmap_start_date=start_date,
            roadmap_target_date=target_date,
            milestones=milestones_input,
        )

        sched_milestones_by_id = {m.milestone_id: m for m in scheduled.milestones}
        sched_tasks_by_id = {
            t.task_id: t
            for m in scheduled.milestones
            for t in m.tasks
        }

        for milestone in roadmap.milestones:
            sched_m = sched_milestones_by_id.get(milestone.id)
            if sched_m:
                milestone.start_date = sched_m.start_date
                milestone.target_date = sched_m.target_date

            for task in milestone.tasks:
                # Completed task immutability: do not modify historical dates of completed tasks
                if task.status == "completed" and (task.start_date is not None or task.target_date is not None):
                    continue
                sched_t = sched_tasks_by_id.get(task.id)
                if sched_t:
                    task.start_date = sched_t.start_date
                    task.target_date = sched_t.target_date

    def reschedule(
        self,
        student_id: uuid.UUID,
        goal_id: uuid.UUID,
        roadmap_id: uuid.UUID,
    ) -> Roadmap:
        """Step 14C: Deterministically recalculate milestone and task dates for an existing roadmap.

        Flow:
        1. Validate student ownership.
        2. Validate goal ownership.
        3. Validate roadmap belongs to goal.
        4. Eagerly load roadmap hierarchy (Milestones → Tasks) without N+1 queries.
        5. Validate roadmap dates: start_date and target_date must both be present.
        6. Validate roadmap date range: start_date <= target_date.
        7. Validate Goal.target_date boundary: roadmap.target_date <= goal.target_date (if goal.target_date exists).
        8. Run pure RoadmapScheduler in memory on dict representation.
        9. Stage calculated dates onto ORM Milestone and Task entities.
        10. Flush and commit atomically. Roll back on any failure.
        """
        self._ensure_student(student_id)
        goal = self._ensure_goal_owned_by_student(student_id, goal_id)

        roadmap = self.repository.get_full_hierarchy(roadmap_id)
        if roadmap is None:
            raise LookupError("Roadmap not found")
        if roadmap.goal_id != goal_id:
            raise PermissionError("Roadmap does not belong to this goal")

        # 1. Date presence validation: existing roadmap must have both dates
        if roadmap.start_date is None or roadmap.target_date is None:
            raise ValueError(
                "Cannot reschedule roadmap: start_date and target_date must both be set"
            )

        # 2. Date range validation
        if roadmap.start_date > roadmap.target_date:
            raise ValueError(
                f"Cannot reschedule roadmap: start_date ({roadmap.start_date}) must not be after target_date ({roadmap.target_date})"
            )

        # 3. Goal target date boundary validation
        if goal.target_date is not None and roadmap.target_date > goal.target_date:
            raise ValueError(
                f"Cannot reschedule roadmap: roadmap target_date ({roadmap.target_date}) cannot exceed goal target_date ({goal.target_date})"
            )

        try:
            self._apply_schedule_to_hierarchy(roadmap, roadmap.start_date, roadmap.target_date)
            self.db.flush()
            self.db.commit()
            self.db.refresh(roadmap)
            return roadmap
        except Exception:
            self.db.rollback()
            raise


