from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import GoalCategory, GoalStatus, PrioritySkill, RoadmapStage, TaskStatus
from app.models.user import sa_enum


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[GoalCategory] = mapped_column(sa_enum(GoalCategory), default=GoalCategory.CAREER)
    status: Mapped[GoalStatus] = mapped_column(sa_enum(GoalStatus), default=GoalStatus.ACTIVE)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="goals")


class RoadmapItem(Base):
    """A single step in a student's grade-by-grade roadmap."""

    __tablename__ = "roadmap_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)
    grade: Mapped[int] = mapped_column(Integer, default=9)                       # 9-12
    stage: Mapped[RoadmapStage] = mapped_column(sa_enum(RoadmapStage, 30), default=RoadmapStage.DISCOVER)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="explore")         # build|explore|grow
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="roadmap_items")
    goal = relationship("Goal")


class WeeklyPriority(Base):
    """This week's 3 priorities for a student."""

    __tablename__ = "weekly_priorities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    ordinal: Mapped[int] = mapped_column(Integer, default=1)                      # 1-3
    skill_category: Mapped[PrioritySkill] = mapped_column(sa_enum(PrioritySkill), default=PrioritySkill.BUILD)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    minutes: Mapped[int] = mapped_column(Integer, default=120)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="priorities")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="build")
    status: Mapped[TaskStatus] = mapped_column(sa_enum(TaskStatus), default=TaskStatus.TODO)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tasks")