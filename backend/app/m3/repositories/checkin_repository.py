import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.m3.db.models import Goal, Roadmap, Student, WeeklyCheckin


class WeeklyCheckinRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, roadmap_id: uuid.UUID, values: dict) -> WeeklyCheckin:
        checkin = WeeklyCheckin(roadmap_id=roadmap_id, **values)
        self.db.add(checkin)
        self.db.flush()
        self.db.refresh(checkin)
        return checkin

    def get_by_id(self, checkin_id: uuid.UUID) -> WeeklyCheckin | None:
        return self.db.get(WeeklyCheckin, checkin_id)

    def get_by_roadmap_and_week(
        self, roadmap_id: uuid.UUID, week_start_date: date
    ) -> WeeklyCheckin | None:
        statement = select(WeeklyCheckin).where(
            WeeklyCheckin.roadmap_id == roadmap_id,
            WeeklyCheckin.week_start_date == week_start_date,
        )
        return self.db.scalars(statement).first()

    def list_by_roadmap(self, roadmap_id: uuid.UUID) -> list[WeeklyCheckin]:
        statement = (
            select(WeeklyCheckin)
            .where(WeeklyCheckin.roadmap_id == roadmap_id)
            .order_by(WeeklyCheckin.week_start_date.desc(), WeeklyCheckin.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update(self, checkin: WeeklyCheckin, values: dict) -> WeeklyCheckin:
        for field, value in values.items():
            setattr(checkin, field, value)
        self.db.flush()
        self.db.refresh(checkin)
        return checkin

    def student_exists(self, student_id: uuid.UUID) -> bool:
        return self.db.get(Student, student_id) is not None

    def goal_exists(self, goal_id: uuid.UUID) -> bool:
        return self.db.get(Goal, goal_id) is not None

    def get_goal(self, goal_id: uuid.UUID) -> Goal | None:
        return self.db.get(Goal, goal_id)

    def get_roadmap(self, roadmap_id: uuid.UUID) -> Roadmap | None:
        return self.db.get(Roadmap, roadmap_id)
