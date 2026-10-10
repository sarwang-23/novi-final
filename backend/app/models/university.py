from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), default="", index=True)
    city: Mapped[str] = mapped_column(String(100), default="")
    course: Mapped[str] = mapped_column(String(255), default="")
    subject: Mapped[str] = mapped_column(String(100), default="", index=True)
    ranking: Mapped[int | None] = mapped_column(Integer, nullable=True)         # lower = better
    fees_per_year: Mapped[int | None] = mapped_column(Integer, nullable=True)   # in USD (approx)
    university_type: Mapped[str] = mapped_column(String(50), default="")
    scholarships: Mapped[bool] = mapped_column(default=False, server_default="0")
    entry_requirements: Mapped[str] = mapped_column(Text, default="")
    about: Mapped[str] = mapped_column(Text, default="")
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)        # e.g. ["#1 in AI research"]
    courses: Mapped[list | None] = mapped_column(JSON, nullable=True)          # clean subject labels this uni is ranked in
    rankings: Mapped[dict | None] = mapped_column(JSON, nullable=True)         # {subject_slug: best_rank}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matches = relationship("UniversityMatch", back_populates="university", cascade="all, delete-orphan")

    @property
    def keywords(self) -> str:
        parts = [self.name, self.country, self.city, self.course, self.subject, self.about]
        parts += self.tags or []
        return " ".join(str(p).lower() for p in parts)


class UniversityMatch(Base):
    __tablename__ = "university_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    university_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("universities.id", ondelete="CASCADE"), index=True
    )
    course: Mapped[str] = mapped_column(String(255), default="")
    readiness: Mapped[float] = mapped_column(Float, default=0.0)          # 0-100
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)   # ["Academic performance", ...]
    improvements: Mapped[list | None] = mapped_column(JSON, nullable=True)
    next_steps: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 3 recommendations
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="university_matches")
    university = relationship("University", back_populates="matches")