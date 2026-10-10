import uuid

from sqlalchemy import CheckConstraint


from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DiscoveryRun(Base):
    __tablename__ = "m3_discovery_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_students.id", ondelete="CASCADE"),
        nullable=False,
    )

    career_dna_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    thread_id: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    trigger: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="RUNNING",
        nullable=False,
    )

    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True)
    )

    error_code: Mapped[str | None] = mapped_column(
        String(100)
    )

    error_message: Mapped[str | None] = mapped_column(
        String(255)
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student = relationship(
        "Student",
        back_populates="discovery_runs",
    )

    career_matches = relationship(
        "CareerMatch",
        back_populates="discovery_run",
        cascade="all, delete-orphan",
    )


class CareerMatch(Base):
    __tablename__ = "m3_career_matches"

    __table_args__ = (
        CheckConstraint(
            "(tag_score IS NULL OR tag_score BETWEEN 0 AND 1) "
            "AND (semantic_score IS NULL OR semantic_score BETWEEN 0 AND 1) "
            "AND (ai_score IS NULL OR ai_score BETWEEN 0 AND 1) "
            "AND (final_score IS NULL OR final_score BETWEEN 0 AND 1)",
            name="career_match_scores_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    discovery_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_discovery_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_students.id", ondelete="CASCADE"),
        nullable=False,
    )

    career_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_careers.id", ondelete="RESTRICT"),
        nullable=False,
    )

    tag_score: Mapped[float | None] = mapped_column(Float)

    semantic_score: Mapped[float | None] = mapped_column(Float)

    ai_score: Mapped[float | None] = mapped_column(Float)

    final_score: Mapped[float | None] = mapped_column(Float)

    rank: Mapped[int | None] = mapped_column(Integer)

    why_fit: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    discovery_run = relationship(
        "DiscoveryRun",
        back_populates="career_matches",
    )

    career = relationship(
        "Career",
        back_populates="career_matches",
    )

    gaps = relationship(
        "CareerMatchGap",
        back_populates="career_match",
        cascade="all, delete-orphan",
    )

    readiness = relationship(
        "Readiness",
        back_populates="career_match",
        uselist=False,
        cascade="all, delete-orphan",
    )

    goals = relationship(
        "Goal",
        back_populates="career_match",
    )


class CareerMatchGap(Base):
    __tablename__ = "m3_career_match_gaps"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    career_match_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_career_matches.id", ondelete="CASCADE"),
        nullable=False,
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_skills.id", ondelete="RESTRICT"),
        nullable=False,
    )

    student_level: Mapped[str | None] = mapped_column(
        String(50)
    )

    required_level: Mapped[str | None] = mapped_column(
        String(50)
    )

    gap_level: Mapped[str | None] = mapped_column(
        String(50)
    )

    priority: Mapped[str | None] = mapped_column(
        String(20)
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    career_match = relationship(
        "CareerMatch",
        back_populates="gaps",
    )

    skill = relationship(
        "Skill",
        back_populates="career_match_gaps",
    )


class Readiness(Base):
    __tablename__ = "m3_readiness"

    __table_args__ = (
        CheckConstraint(
            "(overall_score IS NULL OR overall_score BETWEEN 0 AND 1) "
            "AND (skills_score IS NULL OR skills_score BETWEEN 0 AND 1) "
            "AND (experience_score IS NULL OR experience_score BETWEEN 0 AND 1) "
            "AND (education_score IS NULL OR education_score BETWEEN 0 AND 1) "
            "AND (gap_score IS NULL OR gap_score BETWEEN 0 AND 1)",
            name="readiness_scores_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    career_match_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_career_matches.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    overall_score: Mapped[float | None] = mapped_column(Float)

    skills_score: Mapped[float | None] = mapped_column(Float)

    experience_score: Mapped[float | None] = mapped_column(Float)

    education_score: Mapped[float | None] = mapped_column(Float)

    gap_score: Mapped[float | None] = mapped_column(Float)

    readiness_level: Mapped[str | None] = mapped_column(
        String(50)
    )

    rules_version: Mapped[str] = mapped_column(
        String(50),
        default="v1",
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    career_match = relationship(
        "CareerMatch",
        back_populates="readiness",
    )