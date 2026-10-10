"""Student Graph / Growth Index storage.

Four tables implement the "knowing vs growing" split:

- ``growth_dimension_signals`` — append-only event log. Every signal that moves a
  Student-Graph dimension is written as its own row (never an overwritten score),
  so we can compute both the *current* confidence and the *trend*.
- ``growth_app_events`` — behavioural log (what the student actually did in the app),
  used to cross-check self-report against behaviour ("say-do alignment").
- ``growth_milestones`` — recommended actions (roadmap steps, weekly priorities,
  tasks) with completion + a lightweight self-rating. Ground truth for progress.
- ``growth_snapshots`` — a cheap JSON snapshot of the whole graph per day, diffed
  to produce the longitudinal "when we first met …" narrative.

All tables are ``growth_``-prefixed so they never collide with the main app tables
or the ``m3_`` module.
"""

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DimensionSignal(Base):
    """One row per signal. The current score is just the newest ``confidence_after``."""

    __tablename__ = "growth_dimension_signals"
    __table_args__ = (
        Index("ix_growth_signal_lookup", "user_id", "dimension", "created_at"),
        Index("ix_growth_signal_label", "user_id", "label"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    dimension: Mapped[str] = mapped_column(String(64), nullable=False)   # interest|strength|skill|zone|goal|motivation|value|trait
    label: Mapped[str] = mapped_column(String(191), nullable=False)      # the specific topic, e.g. "medicine"
    signal_value: Mapped[float] = mapped_column(Float, default=0.0)      # 0-100 strength of the incoming signal
    confidence_before: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_after: Mapped[float] = mapped_column(Float, default=0.0)
    delta: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(64), default="manual")    # onboarding|dna|dna_decay|backfill|manual
    source_ref: Mapped[str | None] = mapped_column(String(191), nullable=True)  # question / event name
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class AppEvent(Base):
    """Behavioural evidence: courses started, projects logged, steps completed…"""

    __tablename__ = "growth_app_events"
    __table_args__ = (Index("ix_growth_event_lookup", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    event_type: Mapped[str] = mapped_column(String(64), nullable=False)  # passport_projects|roadmap_step_done|…
    title: Mapped[str] = mapped_column(String(255), default="")
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)       # ["coding", "medicine"]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class GrowthMilestone(Base):
    """A recommended action the student can complete — the outcome ground truth."""

    __tablename__ = "growth_milestones"
    __table_args__ = (
        UniqueConstraint("user_id", "source_type", "source_id", name="uq_growth_milestone_source"),
        Index("ix_growth_milestone_lookup", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    source_type: Mapped[str] = mapped_column(String(32), default="custom")  # roadmap_item|priority|task|custom
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)  # pending|done|skipped
    self_rated_helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GraphSnapshot(Base):
    """Whole-graph JSON captured once per day; consecutive snapshots are diffed."""

    __tablename__ = "growth_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "snapshot_date", name="uq_growth_snapshot_day"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    snapshot_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)   # {"interest": {"medicine": 78.0}, …}
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
