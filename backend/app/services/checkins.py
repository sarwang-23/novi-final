from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.checkin import WeeklyCheckin
from app.models.enums import CheckinStatus
from app.models.user import User
from app.llm import prompts
from app.schemas.checkin import CheckinCreate
from app.services.career_dna import get_dna
from app.services.providers import dna_dict, gemini, memory


def get_current(db: Session, user: User, start: date | None = None) -> WeeklyCheckin | None:
    s = start or _week_start()
    return db.scalar(
        select(WeeklyCheckin).where(WeeklyCheckin.user_id == user.id, WeeklyCheckin.week_start == s)
    )


def get_or_create_current(db: Session, user: User, start: date | None = None) -> WeeklyCheckin:
    checkin = get_current(db, user, start)
    if checkin:
        return checkin
    s = start or _week_start()
    checkin = WeeklyCheckin(user_id=user.id, week_start=s)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def save_answers(db: Session, user: User, data: CheckinCreate) -> WeeklyCheckin:
    checkin = get_or_create_current(db, user, data.week_start)
    checkin.accomplishments = data.accomplishments
    checkin.learnings = data.learnings
    checkin.challenges = data.challenges
    checkin.pride = data.pride
    checkin.next_week = data.next_week
    if checkin.status == CheckinStatus.DRAFT:
        checkin.status = CheckinStatus.SUBMITTED
    db.commit()
    db.refresh(checkin)
    for line in _checkin_lines(checkin):
        memory.archive(user, line, ("checkin",))
    return checkin


async def summarize(db: Session, user: User, checkin_id: int | None = None) -> WeeklyCheckin:
    checkin = checkin_id and db.get(WeeklyCheckin, checkin_id)
    if not checkin or checkin.user_id != user.id:
        checkin = get_or_create_current(db, user)

    answers = {
        "accomplishments": checkin.accomplishments,
        "learnings": checkin.learnings,
        "challenges": checkin.challenges,
        "pride": checkin.pride,
        "next_week": checkin.next_week,
    }
    summary = None
    dna = get_dna(user, db)
    dna_ctx = dna_dict(dna) if dna else {}
    try:
        result = await gemini.complete_json(
            prompts.checkin_summary_prompt(answers, dna_ctx),
            system=prompts.CHECKIN_SUMMARY_SYSTEM,
        )
        if isinstance(result, dict):
            summary = result
    except Exception as exc:
        print(f"[checkins] summary failed: {exc}")

    if summary is None:
        summary = _fallback_summary(answers)

    dna_alignment = str(summary.get("dna_alignment") or "").strip()
    if not dna_alignment and dna:
        goal = (dna.goals or [None])[0]
        zone = (dna.career_zones or [None])[0]
        target = goal or zone
        dna_alignment = (
            f"The work you logged this week moves you toward {target}."
            if target else "This week added evidence for the direction you described."
        )

    checkin.ai_summary = {
        "wins": _int(summary.get("wins"), len(checkin.accomplishments.split(",")) if checkin.accomplishments else 1),
        "new_skills": _list(summary.get("new_skills")),
        "milestones": _list(summary.get("milestones")),
        "priorities_next_week": _list(summary.get("priorities_next_week")),
        "dna_alignment": dna_alignment,
    }
    checkin.status = CheckinStatus.SUMMARIZED
    db.commit()
    db.refresh(checkin)
    for milestone in _list(summary.get("milestones"))[:3]:
        if milestone:
            memory.archive(user, f"User's weekly milestone: {milestone}.", ("checkin", "milestone"))
    return checkin


def list_checkins(db: Session, user: User, limit: int = 12) -> list[WeeklyCheckin]:
    stmt = (
        select(WeeklyCheckin)
        .where(WeeklyCheckin.user_id == user.id)
        .order_by(WeeklyCheckin.week_start.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def _week_start() -> date:
    from app.services.roadmap import week_start as ws

    return ws()


def _checkin_lines(checkin: WeeklyCheckin) -> list[str]:
    lines = []
    if checkin.accomplishments:
        for item in checkin.accomplishments.split(","):
            item = item.strip()
            if item:
                lines.append(f"User's weekly win: {item}.")
    if checkin.learnings:
        for item in checkin.learnings.split(","):
            item = item.strip()
            if item:
                lines.append(f"User learned: {item}.")
    return lines


def _int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _list(value) -> list[str]:
    return [str(v) for v in (value or []) if str(v)]


def _fallback_summary(answers: dict) -> dict:
    accomplishments = answers.get("accomplishments", "")
    learnings = answers.get("learnings", "")
    next_week = answers.get("next_week", "")
    return {
        "wins": max(1, len([x for x in accomplishments.split(",") if x.strip()])),
        "new_skills": [x.strip() for x in learnings.split(",") if x.strip()][:3],
        "milestones": [x.strip() for x in accomplishments.split(",") if x.strip()][:3],
        "priorities_next_week": [x.strip() for x in next_week.split(",") if x.strip()][:3],
    }