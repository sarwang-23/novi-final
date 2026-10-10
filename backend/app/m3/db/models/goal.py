import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Goal(Base):
    __tablename__ = "m3_goals"
    __table_args__ = (
        CheckConstraint(
            "goal_type IN ('career', 'university', 'personal')",
            name="goal_type_check",
        ),
        CheckConstraint(
            "status IN ('active', 'completed', 'paused', 'abandoned')",
            name="goal_status_check",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="goal_priority_check",
        ),
        Index("idx_goals_student_id", "student_id"),
        Index("idx_goals_student_status", "student_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("m3_students.id", ondelete="CASCADE"), nullable=False
    )
    legacy_goal_id: Mapped[int | None] = mapped_column(
        Integer, index=True
    )
    goal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    target_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    career_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("m3_careers.id", ondelete="RESTRICT")
    )
    career_match_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("m3_career_matches.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    student = relationship("Student", back_populates="goals")
    career = relationship("Career", back_populates="goals")
    career_match = relationship("CareerMatch", back_populates="goals")
    roadmaps = relationship("Roadmap", back_populates="goal", cascade="all, delete-orphan")