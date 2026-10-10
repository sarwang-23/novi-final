import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.m3.db.models import Goal, Milestone, Roadmap, Student, Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, milestone_id: uuid.UUID, values: dict) -> Task:
        task = Task(milestone_id=milestone_id, **values)
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        return self.db.get(Task, task_id)

    def list_by_milestone(self, milestone_id: uuid.UUID) -> list[Task]:
        statement = select(Task).where(Task.milestone_id == milestone_id).order_by(
            Task.order_index.asc(), Task.created_at.asc(), Task.id.asc()
        )
        return list(self.db.scalars(statement).all())

    def update(self, task: Task, values: dict) -> Task:
        for field, value in values.items():
            setattr(task, field, value)
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.flush()

    def student_exists(self, student_id: uuid.UUID) -> bool:
        return self.db.get(Student, student_id) is not None

    def goal_exists(self, goal_id: uuid.UUID) -> bool:
        return self.db.get(Goal, goal_id) is not None

    def get_goal(self, goal_id: uuid.UUID) -> Goal | None:
        return self.db.get(Goal, goal_id)

    def get_roadmap(self, roadmap_id: uuid.UUID) -> Roadmap | None:
        return self.db.get(Roadmap, roadmap_id)

    def get_milestone(self, milestone_id: uuid.UUID) -> Milestone | None:
        return self.db.get(Milestone, milestone_id)