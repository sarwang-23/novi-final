import uuid
from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, selectinload

from app.m3.db.models import Goal, Milestone, Roadmap, Student, Task


class RoadmapRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, goal_id: uuid.UUID, values: dict) -> Roadmap:
        roadmap = Roadmap(goal_id=goal_id, **values)
        self.db.add(roadmap)
        self.db.flush()
        self.db.refresh(roadmap)
        return roadmap

    def get_by_id(self, roadmap_id: uuid.UUID) -> Roadmap | None:
        return self.db.get(Roadmap, roadmap_id)

    def list_by_goal(self, goal_id: uuid.UUID) -> list[Roadmap]:
        statement = select(Roadmap).where(Roadmap.goal_id == goal_id).order_by(Roadmap.created_at.desc())
        return list(self.db.scalars(statement).all())

    def get_active_by_goal(self, goal_id: uuid.UUID) -> Roadmap | None:
        statement = select(Roadmap).where(
            (Roadmap.goal_id == goal_id) & (Roadmap.status == "active")
        )
        return self.db.scalars(statement).first()

    def update(self, roadmap: Roadmap, values: dict) -> Roadmap:
        for field, value in values.items():
            setattr(roadmap, field, value)
        self.db.flush()
        self.db.refresh(roadmap)
        return roadmap

    def delete(self, roadmap: Roadmap) -> None:
        self.db.delete(roadmap)
        self.db.flush()

    def student_exists(self, student_id: uuid.UUID) -> bool:
        return self.db.get(Student, student_id) is not None

    def goal_exists(self, goal_id: uuid.UUID) -> bool:
        return self.db.get(Goal, goal_id) is not None

    def get_goal(self, goal_id: uuid.UUID) -> Goal | None:
        return self.db.get(Goal, goal_id)

    def get_task_counts_for_roadmap(self, roadmap_id: uuid.UUID) -> dict:
        """Return task status counts for all tasks belonging to a roadmap.

        Joins Task → Milestone in a single SQL aggregation query.
        No Task rows are loaded into Python memory.
        """
        row = self.db.execute(
            select(
                func.count().label("total"),
                func.sum(case((Task.status == "completed", 1), else_=0)).label("completed"),
                func.sum(case((Task.status == "active", 1), else_=0)).label("active"),
                func.sum(case((Task.status == "pending", 1), else_=0)).label("pending"),
                func.sum(case((Task.status == "skipped", 1), else_=0)).label("skipped"),
            )
            .join(Milestone, Task.milestone_id == Milestone.id)
            .where(Milestone.roadmap_id == roadmap_id)
        ).one()
        return {
            "total": int(row.total),
            "completed": int(row.completed),
            "active": int(row.active),
            "pending": int(row.pending),
            "skipped": int(row.skipped),
        }

    def get_full_hierarchy(self, roadmap_id: uuid.UUID) -> Roadmap | None:
        """Eagerly load Roadmap → Milestones → Tasks in bounded queries without N+1."""
        statement = (
            select(Roadmap)
            .where(Roadmap.id == roadmap_id)
            .options(
                selectinload(Roadmap.milestones).selectinload(Milestone.tasks)
            )
        )
        return self.db.scalars(statement).first()

    def get_timeline_tasks(
        self, roadmap_id: uuid.UUID, period_start: date, period_end: date
    ) -> list[tuple[Task, str, int]]:
        """Query tasks belonging to a roadmap whose target_date falls within [period_start, period_end].

        Joins Task → Milestone → Roadmap in a single SQL query, ordered by milestone.order_index, task.order_index.
        Tasks with NULL target_date are excluded.
        """
        statement = (
            select(
                Task,
                Milestone.title.label("milestone_title"),
                Milestone.order_index.label("milestone_order_index"),
            )
            .join(Milestone, Task.milestone_id == Milestone.id)
            .where(
                Milestone.roadmap_id == roadmap_id,
                Task.target_date >= period_start,
                Task.target_date <= period_end,
            )
            .order_by(Milestone.order_index.asc(), Task.order_index.asc())
        )
        return list(self.db.execute(statement).all())

