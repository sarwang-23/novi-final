import uuid

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.m3.db.models import Goal, Milestone, Roadmap, Student, Task


class MilestoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, roadmap_id: uuid.UUID, values: dict) -> Milestone:
        milestone = Milestone(roadmap_id=roadmap_id, **values)
        self.db.add(milestone)
        self.db.flush()
        self.db.refresh(milestone)
        return milestone

    def get_by_id(self, milestone_id: uuid.UUID) -> Milestone | None:
        return self.db.get(Milestone, milestone_id)

    def list_by_roadmap(self, roadmap_id: uuid.UUID) -> list[Milestone]:
        statement = select(Milestone).where(Milestone.roadmap_id == roadmap_id).order_by(
            Milestone.order_index.asc(), Milestone.created_at.asc(), Milestone.id.asc()
        )
        return list(self.db.scalars(statement).all())

    def update(self, milestone: Milestone, values: dict) -> Milestone:
        for field, value in values.items():
            setattr(milestone, field, value)
        self.db.flush()
        self.db.refresh(milestone)
        return milestone

    def delete(self, milestone: Milestone) -> None:
        self.db.delete(milestone)
        self.db.flush()

    def student_exists(self, student_id: uuid.UUID) -> bool:
        return self.db.get(Student, student_id) is not None

    def goal_exists(self, goal_id: uuid.UUID) -> bool:
        return self.db.get(Goal, goal_id) is not None

    def get_goal(self, goal_id: uuid.UUID) -> Goal | None:
        return self.db.get(Goal, goal_id)

    def get_roadmap(self, roadmap_id: uuid.UUID) -> Roadmap | None:
        return self.db.get(Roadmap, roadmap_id)

    def get_task_counts(self, milestone_id: uuid.UUID) -> dict:
        """Return task status counts for a milestone in a single SQL query.

        Uses conditional COUNT aggregation to avoid loading Task rows into Python.
        """
        row = self.db.execute(
            select(
                func.count().label("total"),
                func.sum(case((Task.status == "completed", 1), else_=0)).label("completed"),
                func.sum(case((Task.status == "active", 1), else_=0)).label("active"),
                func.sum(case((Task.status == "pending", 1), else_=0)).label("pending"),
                func.sum(case((Task.status == "skipped", 1), else_=0)).label("skipped"),
            ).where(Task.milestone_id == milestone_id)
        ).one()
        return {
            "total": int(row.total),
            "completed": int(row.completed),
            "active": int(row.active),
            "pending": int(row.pending),
            "skipped": int(row.skipped),
        }