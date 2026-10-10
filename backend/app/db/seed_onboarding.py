"""Seed the conversational-onboarding lookup catalog (countries/curriculums/
grades/subjects).

Idempotent: only inserts when a table is empty, so it is safe to re-run after a
fresh install (see ``app.db.init_db``, which calls ``seed_onboarding`` alongside
the existing career/university seeds).

Usage:
    python -m app.db.seed_onboarding     # standalone (tables must already exist)
"""

import re
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.database import SessionLocal  # noqa: E402  (standalone __main__ only)
from app.models.catalog import Country, Curriculum, Grade, Subject  # noqa: E402

COUNTRIES = [
    {"code": "IN", "name": "India"},
    {"code": "GB", "name": "United Kingdom"},
    {"code": "US", "name": "United States"},
]

CURRICULUMS = [
    {"id": "in-cbse", "country_code": "IN", "name": "CBSE"},
    {"id": "in-icse", "country_code": "IN", "name": "ICSE"},
    {"id": "in-state-board", "country_code": "IN", "name": "State Board"},
    {"id": "in-other", "country_code": "IN", "name": "Other"},
    {"id": "gb-gcse", "country_code": "GB", "name": "GCSE"},
    {"id": "gb-a-level", "country_code": "GB", "name": "A-Level"},
    {"id": "gb-ib", "country_code": "GB", "name": "IB"},
    {"id": "gb-other", "country_code": "GB", "name": "Other"},
    {"id": "us-public", "country_code": "US", "name": "Public"},
    {"id": "us-private", "country_code": "US", "name": "Private"},
    {"id": "us-charter", "country_code": "US", "name": "Charter"},
    {"id": "us-homeschool", "country_code": "US", "name": "Homeschool"},
]

# (country_code, curriculum_id, label word, levels)
GRADE_DEFS = [
    ("in-cbse", "IN", "Grade", ["9", "10", "11", "12"]),
    ("in-icse", "IN", "Grade", ["9", "10", "11", "12"]),
    ("in-state-board", "IN", "Grade", ["9", "10", "11", "12"]),
    ("in-other", "IN", "Grade", ["9", "10", "11", "12"]),
    ("gb-gcse", "GB", "Year", ["9", "10", "11", "12", "13"]),
    ("gb-a-level", "GB", "Year", ["9", "10", "11", "12", "13"]),
    ("gb-ib", "GB", "Year", ["9", "10", "11", "12", "13"]),
    ("gb-other", "GB", "Year", ["9", "10", "11", "12", "13"]),
    ("us-public", "US", "Grade", ["9", "10", "11", "12"]),
    ("us-private", "US", "Grade", ["9", "10", "11", "12"]),
    ("us-charter", "US", "Grade", ["9", "10", "11", "12"]),
    ("us-homeschool", "US", "Grade", ["9", "10", "11", "12"]),
]

# curriculum_id -> starter subject list (same names across all of that
# curriculum's grades + countries). Expand later.
SUBJECT_SETS = {
    "in-cbse": ["Maths", "English", "Hindi", "Science", "Social Science", "Computer Science", "Physical Education", "Art"],
    "in-icse": ["Maths", "English", "Hindi", "Science", "Social Science", "Computer Science", "Physical Education", "Art"],
    "in-state-board": ["Maths", "English", "Regional Language", "Science", "Social Science", "Computer Science", "Physical Education"],
    "in-other": ["Maths", "English", "Science", "Social Science"],
    "gb-gcse": ["Maths", "English", "Science", "History", "Geography", "French", "Computer Science", "Art & Design", "Physical Education"],
    "gb-a-level": ["Mathematics", "Further Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Psychology"],
    "gb-ib": ["Mathematics HL", "Mathematics SL", "English A", "Sciences", "History", "Computer Science", "Psychology"],
    "gb-other": ["Maths", "English", "Science", "History"],
    "us-public": ["Mathematics", "English", "Science", "History", "Geography", "Computer Science", "Spanish", "Physical Education", "Art"],
    "us-private": ["Mathematics", "English", "Science", "History", "Geography", "Computer Science", "Spanish", "Physical Education", "Art"],
    "us-charter": ["Mathematics", "English", "Science", "History", "Computer Science", "Art"],
    "us-homeschool": ["Mathematics", "English", "Science", "History"],
}

def _slugify(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", name.lower()).strip("-")


def _grade_id(curriculum_id: str, level: str) -> str:
    return f"{curriculum_id}-{level}"


def build_grades() -> list[dict]:
    grades = []
    for curriculum_id, country_code, word, levels in GRADE_DEFS:
        for level in levels:
            grades.append({
                "id": _grade_id(curriculum_id, level),
                "country_code": country_code,
                "curriculum_id": curriculum_id,
                "label": f"{word} {level}",
                "normalized_level": level,
            })
    return grades


def build_subjects() -> list[dict]:
    subjects = []
    for curriculum_id, country_code, _word, levels in GRADE_DEFS:
        for name in SUBJECT_SETS[curriculum_id]:
            for level in levels:
                grade_id = _grade_id(curriculum_id, level)
                subjects.append({
                    "id": f"{grade_id}-{_slugify(name)}",
                    "country_code": country_code,
                    "curriculum_id": curriculum_id,
                    "grade_id": grade_id,
                    "name": name,
                })
    return subjects


GRADES = build_grades()
SUBJECTS = build_subjects()


def seed_onboarding(db: Session) -> dict:
    created = {"countries": 0, "curriculums": 0, "grades": 0, "subjects": 0}

    if db.scalar(select(Country.code).limit(1)) is None:
        db.add_all([Country(**c) for c in COUNTRIES])
        created["countries"] = len(COUNTRIES)

    if db.scalar(select(Curriculum.id).limit(1)) is None:
        db.add_all([Curriculum(**c) for c in CURRICULUMS])
        created["curriculums"] = len(CURRICULUMS)

    if db.scalar(select(Grade.id).limit(1)) is None:
        db.add_all([Grade(**g) for g in GRADES])
        created["grades"] = len(GRADES)

    if db.scalar(select(Subject.id).limit(1)) is None:
        db.add_all([Subject(**s) for s in SUBJECTS])
        created["subjects"] = len(SUBJECTS)

    db.commit()
    return created


if __name__ == "__main__":
    with SessionLocal() as _db:
        counts = seed_onboarding(_db)
        print(f"[seed_onboarding] countries={counts['countries']} "
              f"curriculums={counts['curriculums']} "
              f"grades={counts['grades']} subjects={counts['subjects']}")