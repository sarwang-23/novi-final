"""Career DNA snapshots — frozen copies of the student's DNA over time.

The DNA changes gradually, across many years (teen -> young adult). A snapshot
freezes the full DNA set at a point in time so you can look back, diff it against
the previous snapshot (delta view: what actually changed), and keep editing or
deleting old snapshots for years.
"""
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CareerDNASnapshot(Base):
    __tablename__ = "career_dna_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(160), default="")      # e.g. "My DNA · age 16"
    note: Mapped[str] = mapped_column(Text, default="")

    # frozen DNA fields at snapshot time (plain JSON copies)
    traits: Mapped[list | None] = mapped_column(JSON, nullable=True)
    motivations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    development_areas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    interests: Mapped[list | None] = mapped_column(JSON, nullable=True)
    subjects: Mapped[list | None] = mapped_column(JSON, nullable=True)
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    career_zones: Mapped[list | None] = mapped_column(JSON, nullable=True)
    values: Mapped[list | None] = mapped_column(JSON, nullable=True)
    goals: Mapped[list | None] = mapped_column(JSON, nullable=True)
    novi_reflection: Mapped[str | None] = mapped_column(Text, nullable=True)
    dna_filled: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- relationship back to the owning student --------------------------
    user = relationship("User", back_populates="dna_snapshots")
