import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.m3.db.models import Career, CareerMatch, Goal, Student


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, student_id: uuid.UUID, values: dict) -> Goal:
        goal = Goal(student_id=student_id, **values)
        self.db.add(goal)
        self.db.flush()
        self.db.refresh(goal)
        return goal

    def get_by_id(self, goal_id: uuid.UUID) -> Goal | None:
        return self.db.get(Goal, goal_id)

    def list_by_student(self, student_id: uuid.UUID) -> list[Goal]:
        statement = select(Goal).where(Goal.student_id == student_id).order_by(Goal.created_at.desc())
        return list(self.db.scalars(statement).all())

    def update(self, goal: Goal, values: dict) -> Goal:
        for field, value in values.items():
            setattr(goal, field, value)
        self.db.flush()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: Goal) -> None:
        self.db.delete(goal)
        self.db.flush()

    def student_exists(self, student_id: uuid.UUID) -> bool:
        return self.db.get(Student, student_id) is not None

    def career_exists(self, career_id: uuid.UUID) -> bool:
        return self.db.get(Career, career_id) is not None

    def get_career_match(self, career_match_id: uuid.UUID) -> CareerMatch | None:
        return self.db.get(CareerMatch, career_match_id)