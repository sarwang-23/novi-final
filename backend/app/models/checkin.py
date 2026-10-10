from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import CheckinStatus
from app.models.user import sa_enum


class WeeklyCheckin(Base):
    __tablename__ = "weekly_checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)

    accomplishments: Mapped[str] = mapped_column(Text, default="")
    learnings: Mapped[str] = mapped_column(Text, default="")
    challenges: Mapped[str] = mapped_column(Text, default="")
    pride: Mapped[str] = mapped_column(Text, default="")
    next_week: Mapped[str] = mapped_column(Text, default="")

    ai_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)   # {"wins": n, "skills": [...], "milestones": [...], "priorities": [...]}
    status: Mapped[CheckinStatus] = mapped_column(sa_enum(CheckinStatus), default=CheckinStatus.DRAFT)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="checkins")