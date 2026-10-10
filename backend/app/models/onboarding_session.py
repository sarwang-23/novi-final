from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OnboardingSession(Base):
    """The live state of a student's conversational onboarding.

    The Q&A itself lives as real chat Messages in `conversation_id`, so the
    whole onboarding double as a chat the student can come back to — and the
    Career DNA finalize step reads that same transcript. `answers` keeps a
    structured copy per step for deterministic progress + resume; `summary`
    is the completed reveal (archetype, traits, recommendations, 30-day plan).
    """

    __tablename__ = "onboarding_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    step_index: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[list | None] = mapped_column(JSON, nullable=True)  # step ids the student chose to skip
    answers: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {step_id: value}
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # reveal payload when done

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="onboarding")