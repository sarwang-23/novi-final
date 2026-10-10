import uuid

from sqlalchemy import CheckConstraint

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Career(Base):
    __tablename__ = "m3_careers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    category: Mapped[str | None] = mapped_column(
        String(100)
    )

    industry: Mapped[str | None] = mapped_column(
        String(100)
    )

    experience_level: Mapped[str | None] = mapped_column(
        String(100)
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    career_skills = relationship(
        "CareerSkill",
        back_populates="career",
        cascade="all, delete-orphan",
    )

    career_tags = relationship(
        "CareerTag",
        back_populates="career",
        cascade="all, delete-orphan",
    )

    career_matches = relationship(
        "CareerMatch",
        back_populates="career",
    )

    goals = relationship(
        "Goal",
        back_populates="career",
    )


class CareerSkill(Base):
    __tablename__ = "m3_career_skills"

    __table_args__ = (
        CheckConstraint(
            "importance BETWEEN 1 AND 5",
            name="career_skill_importance_check",
        ),
    )

    career_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_careers.id", ondelete="CASCADE"),
        primary_key=True,
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_skills.id", ondelete="CASCADE"),
        primary_key=True,
    )

    importance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    required_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_core: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    career = relationship(
        "Career",
        back_populates="career_skills",
    )

    skill = relationship(
        "Skill",
        back_populates="career_skills",
    )


class CareerTag(Base):
    __tablename__ = "m3_career_tags"

    career_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_careers.id", ondelete="CASCADE"),
        primary_key=True,
    )

    tag: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    career = relationship(
        "Career",
        back_populates="career_tags",
    )