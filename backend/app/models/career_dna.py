from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CareerDNA(Base):
    __tablename__ = "career_dna"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    traits: Mapped[list | None] = mapped_column(JSON, nullable=True)          # e.g. ["curious", "analytical"]
    motivations: Mapped[list | None] = mapped_column(JSON, nullable=True)     # e.g. ["impact", "achievement"]
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    development_areas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    interests: Mapped[list | None] = mapped_column(JSON, nullable=True)
    subjects: Mapped[list | None] = mapped_column(JSON, nullable=True)
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    career_zones: Mapped[list | None] = mapped_column(JSON, nullable=True)
    values: Mapped[list | None] = mapped_column(JSON, nullable=True)
    goals: Mapped[list | None] = mapped_column(JSON, nullable=True)
    novi_reflection: Mapped[str | None] = mapped_column(Text, nullable=True)
    dna_filled: Mapped[bool] = mapped_column(default=False, server_default="0")

    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # evidence from chats: {field: [{value, quote, conversation_id}]}
    excluded: Mapped[list | None] = mapped_column(JSON, nullable=True)  # topics the student has moved away from, e.g. ["ai"]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="career_dna")