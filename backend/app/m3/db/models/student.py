import uuid

from sqlalchemy import DateTime, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Student(Base):
    __tablename__ = "m3_students"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False
    )

    external_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

#      career_dna = relationship(
#         "CareerDNA",
#         back_populates="student",
#         cascade="all, delete-orphan"
#     )

    student_skills = relationship(
        "StudentSkill",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    discovery_runs = relationship(
        "DiscoveryRun",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    goals = relationship(
        "Goal",
        back_populates="student",
        cascade="all, delete-orphan"
    )