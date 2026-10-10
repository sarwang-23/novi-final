"""Structured student context distilled from onboarding.

The 15-step conversational engine (``app/routers/onboarding.py``, backed by
``app/onboarding/steps.py``) distills answers into a ``StudentProfile`` row.
``load_student_context`` reads that profile and normalizes it into explicit,
deterministic fields (grade level, curriculum, enjoyed/difficult subjects,
career-in-mind, study destination, dream universities, strengths, motivators,
goals...).

For backward compatibility it also still reads a prior ``OnboardingSession``
row (data captured before the legacy flow engine was removed) so students who
onboarded under the old 34-step flow keep their captured answers; the profile
wins on overlap and session answers only fill gaps.

Only semantic helpers live here — no LLM, no writes. Used by
``career_dna``, ``careers``, ``roadmap``, ``passport`` and ``universities``.
"""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.onboarding_data import StudentProfile
from app.models.onboarding_session import OnboardingSession
from app.models.user import User
from app.models.catalog import Subject

# Prior-session step id -> (context key, kind). None step = raw value passthrough.
_SESSION_MAP: dict[str, str] = {
    "grade": "grade_level_raw",
    "curriculum": "curriculum",
    "intent": "intent",
    "parent_influence": "parents",
    "worried": "worried",
    "future_30": "goal_vision",
    "money_no_bars": "ideal_work",
    "subject_marks_irrelevant": "subject_marks_irrelevant",
    "career_awareness": "career_awareness",
    "career_detail": "career_name",
    "career_reason": "career_reason",
    "study_destination": "study_destination",
    "dream_universities": "dream_universities",
    "learning_style": "learning_preference",
    "confidence": "confidence",
    "novi_helper": "help_wish",
    "project_detail": "projects",
    "lose_track": "lose_track",
}

_SESSION_LIST_MAP: dict[str, str] = {
    "saturday": "interests",
    "videos": "interests",
    "activities": "interests",
    "friend_describe": "strengths",
    "motivators": "motivators",
    "subjects_enjoy": "subjects_enjoyed",
    "subjects_hard": "subjects_difficult",
}

_GRADE_RE = re.compile(r"\b(\d{1,2})\b")

# Normalize study-destination / university country names to a common key so a
# student's "US" matches seed country "USA", "UK" matches "United Kingdom", etc.
_COUNTRY_GROUPS: dict[str, str] = {
    "us": "usa", "usa": "usa", "united states": "usa", "america": "usa",
    "uk": "uk", "united kingdom": "uk", "britain": "uk", "england": "uk",
    "india": "india", "canada": "canada", "australia": "australia",
    "singapore": "singapore", "switzerland": "switzerland", "europe": "europe",
    "asia": "asia",
}


def _uniq(items: list) -> list:
    seen: set[str] = set()
    out: list = []
    for it in items or []:
        key = str(it).strip()
        if not key or key.lower() in seen:
            continue
        seen.add(key.lower())
        out.append(it)
    return out


def norm_country(name: str | None) -> str:
    key = str(name or "").strip().lower()
    return _COUNTRY_GROUPS.get(key, key)


def _profile_context(db: Session, profile: StudentProfile | None, ctx: dict) -> None:
    """Overlay a distilled ``StudentProfile`` (new-engine onboarding) onto the context."""
    if profile is None:
        return
    if profile.preferred_name:
        ctx["name"] = profile.preferred_name
    if profile.country_code:
        ctx["country_code"] = profile.country_code
    if profile.curriculum_id:
        ctx["curriculum"] = profile.curriculum_id
    if profile.grade_id:
        ctx["grade_id"] = profile.grade_id
    if profile.saturday_activities:
        ctx["interests"] = _uniq(list(ctx["interests"]) + list(profile.saturday_activities))
    if profile.strengths:
        ctx["strengths"] = _uniq(list(ctx["strengths"]) + list(profile.strengths))
    if profile.enjoyed_subjects:
        ctx["subjects_enjoyed"] = _uniq(list(ctx["subjects_enjoyed"]) + _subject_names(db, profile.enjoyed_subjects))
    if profile.difficult_subjects:
        ctx["subjects_difficult"] = _uniq(list(ctx["subjects_difficult"]) + _subject_names(db, profile.difficult_subjects))
    if profile.learning_preference:
        ctx["learning_preference"] = profile.learning_preference
    if profile.confidence_choice:
        ctx["confidence"] = profile.confidence_choice
    if profile.university_raw_text:
        ctx["dream_universities"] = _join_text(ctx["dream_universities"], profile.university_raw_text)
    elif profile.university_name:
        ctx["dream_universities"] = _join_text(ctx["dream_universities"], profile.university_name)
    if profile.university_location:
        ctx["study_destination"] = ctx["study_destination"] or profile.university_location
    if profile.has_career_in_mind is not None:
        ctx["career_in_mind"] = profile.has_career_in_mind
    if profile.career_name:
        ctx["career_name"] = _join_text(ctx["career_name"], profile.career_name)
    if profile.career_interest_reason:
        ctx["career_reason"] = _join_text(ctx["career_reason"], profile.career_interest_reason)
    if profile.primary_goal:
        ctx["goals"] = _uniq(list(ctx["goals"]) + [profile.primary_goal])


def _join_text(existing: str | None, value: str | None) -> str:
    parts = [str(p).strip() for p in (existing, value) if p and str(p).strip()]
    return " | ".join(parts) if parts else ""


def _subject_names(db: Session, subjects: list | None) -> list[str]:
    """Resolve catalog subject ids (e.g. in-cbse-10-maths) to their display names."""
    names: list[str] = []
    for subject_id in subjects or []:
        key = str(subject_id).strip()
        if not key:
            continue
        subject = db.get(Subject, key)
        names.append(subject.name if subject is not None else key)
    return names


def load_student_context(db: Session, user: User) -> dict:
    """Deterministic, structured context from everything onboarding captured."""
    ctx: dict = {
        "name": user.display_name,
        "grade": user.grade,
        "grade_level": None,
        "grade_level_raw": None,
        "school": user.school,
        "country": None,
        "curriculum": None,
        "subjects_enjoyed": [],
        "subjects_difficult": [],
        "interests": [],
        "strengths": [],
        "motivators": [],
        "goals": [],
        "career_in_mind": None,
        "career_awareness": None,
        "career_name": None,
        "career_reason": None,
        "study_destination": None,
        "dream_universities": None,
        "learning_preference": None,
        "confidence": None,
        "intent": None,
        "parents": None,
        "worried": None,
        "help_wish": None,
        "goal_vision": None,
        "ideal_work": None,
        "projects": None,
        "lose_track": None,
    }

    # Prior-session answers (pre-15-step engine) first, then the distilled
    # profile overrides on top.
    session = db.scalar(select(OnboardingSession).where(OnboardingSession.user_id == user.id))
    if session and session.answers:
        answers = session.answers
        for step_id, key in _SESSION_MAP.items():
            if step_id not in answers or key not in ctx:
                continue
            value = answers[step_id]
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            if str(value).strip() and not ctx.get(key):
                ctx[key] = str(value).strip()
        for step_id, key in _SESSION_LIST_MAP.items():
            raw = answers.get(step_id)
            if not raw:
                continue
            items = list(raw) if isinstance(raw, list) else [raw]
            existing = list(ctx[key] or [])
            merged: list = []
            for it in items:
                s = str(it).strip()
                if s:
                    merged.append(s)
            ctx[key] = _uniq(existing + merged)
        if "career_awareness" in answers:
            aware = str(answers["career_awareness"]).strip().lower()
            if ctx["career_in_mind"] is None:
                ctx["career_in_mind"] = aware not in ("no idea", "no", "maybe", "", "none")
        if ctx.get("goal_vision") and ctx["goal_vision"] not in list(ctx["goals"]):
            ctx["goals"] = _uniq(list(ctx["goals"]) + [ctx["goal_vision"]])
        if user.grade is None or not ctx["grade_level"]:
            m = _GRADE_RE.search(ctx.get("grade_level_raw") or "")
            if m:
                ctx["grade_level"] = int(m.group(1))

    _profile_context(db, db.scalar(select(StudentProfile).where(StudentProfile.student_id == user.id)), ctx)

    if user.grade is None and ctx["grade_level"] is None:
        m = _GRADE_RE.search(ctx.get("grade_level_raw") or "")
        if m:
            ctx["grade_level"] = int(m.group(1))

    # One canonical "which country" answer (student's own, else study destination).
    dest = (ctx.get("study_destination") or "").strip()
    if dest and dest.lower() not in ("not sure yet",):
        ctx["country_preference"] = norm_country(dest)

    return ctx


def career_in_mind_phrase(ctx: dict) -> str | None:
    """The student's self-declared career, when they clearly have one."""
    if not ctx or not ctx.get("career_in_mind"):
        return None
    name = (ctx.get("career_name") or "").strip()
    if not name or name.lower() in ("test answer", "none", "no", "n/a", "idk", "i don't know", "i dont know"):
        return None
    return name