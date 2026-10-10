import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class WeeklyCheckin(Base):
    __tablename__ = "m3_weekly_checkins"
    __table_args__ = (
        UniqueConstraint("roadmap_id", "week_start_date", name="uq_weekly_checkins_roadmap_week"),
        Index("idx_weekly_checkins_roadmap_week", "roadmap_id", "week_start_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("m3_roadmaps.id", ondelete="CASCADE"), nullable=False
    )
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)

    accomplished: Mapped[str | None] = mapped_column(Text, nullable=True)
    learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    challenged: Mapped[str | None] = mapped_column(Text, nullable=True)
    proud_of: Mapped[str | None] = mapped_column(Text, nullable=True)
    improve_next: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    roadmap = relationship("Roadmap", back_populates="weekly_checkins")
