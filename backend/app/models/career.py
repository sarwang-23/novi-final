from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), default="", index=True)
    emoji: Mapped[str] = mapped_column(String(10), default="💼")
    summary: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    what_they_do: Mapped[str] = mapped_column(Text, default="")
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    subjects: Mapped[list | None] = mapped_column(JSON, nullable=True)
    degrees: Mapped[list | None] = mapped_column(JSON, nullable=True)
    industries: Mapped[list | None] = mapped_column(JSON, nullable=True)
    future_paths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    salary_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outlook: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ranking_profile: Mapped[str] = mapped_column(String(50), default="DEFAULT", index=True)
    country_rankings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matches = relationship("CareerMatch", back_populates="career", cascade="all, delete-orphan")

    @property
    def keywords(self) -> str:
        parts = [self.title, self.category, self.summary]
        parts += self.skills or []
        parts += self.subjects or []
        parts += self.industries or []
        return " ".join(str(p).lower() for p in parts)


class CareerMatch(Base):
    __tablename__ = "career_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    career_id: Mapped[int] = mapped_column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, default=1)
    reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)
    matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="career_matches")
    career = relationship("Career", back_populates="matches")