"""Onboarding lookup catalog: countries, curriculums, grades and subjects.

Seed data lives in ``app.db.seed_onboarding``. Grades/subjects are keyed to a
country+curriculum so question options can cascade via ``requires``.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Curriculum(Base):
    __tablename__ = "curriculums"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country_code: Mapped[str] = mapped_column(
        String(2), ForeignKey("countries.code", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    curriculum_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_level: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    curriculum_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    grade_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)