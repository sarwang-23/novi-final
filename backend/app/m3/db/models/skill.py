import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from sqlalchemy import CheckConstraint


class Skill(Base):
    __tablename__ = "m3_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100)
    )

    description: Mapped[str | None] = mapped_column(
        Text
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

    student_skills = relationship(
        "StudentSkill",
        back_populates="skill",
    )

    career_skills = relationship(
        "CareerSkill",
        back_populates="skill",
    )

    career_match_gaps = relationship(
        "CareerMatchGap",
        back_populates="skill",
    )


class StudentSkill(Base):
    __tablename__ = "m3_student_skills"

    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="student_skill_confidence_check",
        ),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_students.id", ondelete="CASCADE"),
        primary_key=True,
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("m3_skills.id", ondelete="CASCADE"),
        primary_key=True,
    )

    level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
    Float
)

    source: Mapped[str | None] = mapped_column(
        String(100)
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student = relationship(
        "Student",
        back_populates="student_skills",
    )

    skill = relationship(
        "Skill",
        back_populates="student_skills",
    )