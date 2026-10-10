"""Accumulated university-readiness score.

Readiness is not a single snapshot (e.g. running one readiness check produces a
number). Instead it is a *gradual, behaviour-driven* score: every signal the
student produces across the app contributes a small, capped amount, so the score
grows slowly with real, sustained effort and never jumps because of one event.

Signals used here (all deterministic, no LLM at request time):

  foundation  - year of school (always non-null for an enrolled student)
  clarity     - how much of the Career DNA is actually filled in
  evidence    - passport completion (real achievements on record)
  action      - fraction of the learning roadmap completed
  reflection  - how many weekly check-ins the student has submitted
  exploration - chat behaviour: conversations started, how many messages touch
                college/career topics, and whether they engaged recently
  direction   - career matches explored and the strength of the top fit

Because chat messages are stored locally (Conversation/Message), exploration is
assessed from what the student actually does in chat, not guessed.
"""

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import func as sqlfunc, select
from sqlalchemy.orm import Session

from app.models.chat import Conversation, Message
from app.models.checkin import WeeklyCheckin
from app.models.career import CareerMatch
from app.models.enums import CheckinStatus, MessageRole
from app.models.user import User
from app.services.career_dna import get_dna
from app.services.passport import completion as passport_completion
from app.services import roadmap as roadmap_svc

_TOPIC_RE = re.compile(
    r"\b(college|university|admission|application|sat|act|toefl|ielts|scholarship|"
    r"major|career|internship|study abroad|exam|college prep)[\w-]*",
    re.I,
)

_SCORE_TO_LABEL = (
    (75, "Application ready"),
    (60, "Strong profile"),
    (40, "Taking shape"),
    (20, "Building a base"),
    (0, "Just starting"),
)


def activity_ratio(db: Session, user: User) -> float:
    """How much the student has actually DONE (0..1) — evidence, not words.
    Used to dampen raw AI/heuristic fit scores down to a believable number."""
    comp = passport_completion(db, user)
    rp = roadmap_svc.progress_percent(db, user)
    weeks = (
        db.scalar(
            select(sqlfunc.count())
            .select_from(WeeklyCheckin)
            .where(
                WeeklyCheckin.user_id == user.id,
                WeeklyCheckin.status.in_([CheckinStatus.SUBMITTED, CheckinStatus.SUMMARIZED]),
            )
        )
        or 0
    )
    evidence = comp["score"] / 100.0
    action = rp / 100.0
    reflection = min(1.0, weeks / 8.0)
    return round(min(1.0, 0.65 * evidence + 0.25 * action + 0.15 * reflection), 3)


def credible_fit(raw_score: int | float, activity: float) -> int:
    """Dampen a raw AI/heuristic career-fit to a believable number.

    Raw match scores come purely from DNA overlap and routinely land at 92-95%
    for students who have done almost nothing yet. Blend the raw score with the
    student's actual activity so 'fit' reflects evidence too — and cap at 88,
    because nobody is an 89%+ fit."""
    if not raw_score:
        return 0
    credible = raw_score * (0.65 + 0.35 * activity)
    return int(min(88, round(credible)))


def accumulated_readiness(db: Session, user: User) -> dict:
    """Compute the gradual readiness breakdown for a student (score < 100: nobody is ever 'done')."""
    components: list[dict] = []

    # 1. Foundation — year of school, a student can't game this (kept modest on purpose).
    grade = user.grade or 9
    foundation = min(2 * grade, 24)
    components.append(_comp("Foundation", foundation, f"Grade {grade}"))

    # 2. Self-knowledge — how much of the DNA is actually filled in.
    dna = get_dna(user, db)
    if dna:
        filled = sum(1 for f in (dna.interests, dna.subjects, dna.skills, dna.career_zones, dna.goals) if f)
        clarity = min(filled * 3, 15)
        detail = f"{filled}/5 DNA areas filled"
    else:
        clarity = 0
        detail = "No DNA filled yet"
    components.append(_comp("Self-knowledge", clarity, detail))

    # 3. Evidence — passport completion, capped so one entry is worth a little.
    comp = passport_completion(db, user)
    evidence = round(comp["score"] * 0.12)
    covered = len(comp["categories_covered"])
    components.append(_comp("Evidence", evidence, f"{covered}/6 passport categories started"))

    # 4. Action — what fraction of the roadmap has actually been completed.
    progress_pct = roadmap_svc.progress_percent(db, user)
    action = round(progress_pct * 0.10)
    components.append(_comp("Action", action, f"{progress_pct}% of roadmap complete"))

    # 5. Reflection — consistent weekly check-ins (one per week, capped at 4).
    weeks = (
        db.scalar(
            select(sqlfunc.count())
            .select_from(WeeklyCheckin)
            .where(
                WeeklyCheckin.user_id == user.id,
                WeeklyCheckin.status.in_([CheckinStatus.SUBMITTED, CheckinStatus.SUMMARIZED]),
            )
        )
        or 0
    )
    reflection = min(10, round(weeks * 2.5))
    components.append(_comp("Reflection", reflection, f"{weeks} weekly check-in(s)"))

    # 6. Exploration — chat behaviour: conversations, topical depth, recency.
    num_convs = (
        db.scalar(select(sqlfunc.count()).select_from(Conversation).where(Conversation.user_id == user.id))
        or 0
    )
    user_msgs = db.scalars(
        select(Message.content)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user.id, Message.role == MessageRole.USER)
        .order_by(Message.created_at.desc())
        .limit(30)
    ).all()
    top_posts = sum(1 for m in user_msgs if m and _TOPIC_RE.search(m))
    last_msg = db.scalar(
        select(Message.created_at)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user.id, Message.role == MessageRole.USER)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    fresh = 1
    if not last_msg:
        fresh = 0
    else:
        now = datetime.now(timezone.utc)
        last = last_msg.replace(tzinfo=timezone.utc) if last_msg.tzinfo is None else last_msg
        if now - last > timedelta(days=14):
            fresh = 0
    exploration = min(min(num_convs, 4) + min(top_posts, 3) + fresh, 8)
    components.append(
        _comp("Exploration", exploration, f"{num_convs} chat(s), {top_posts} college/career topics")
    )

    # 7. Direction — which careers have been explored and how strong the top fit
    #    actually is after damping it by what the student has done.
    matches = list(db.scalars(select(CareerMatch).where(CareerMatch.user_id == user.id)))
    activity = round(
        min(1.0, 0.65 * comp["score"] / 100.0 + 0.25 * progress_pct / 100.0 + 0.15 * min(1.0, weeks / 8.0)),
        3,
    )
    top_score = credible_fit(round(matches[0].score), activity) if matches else 0
    direction = min(6, len(matches) + (2 if top_score >= 75 else 0))
    detail = f"{len(matches)} career(s) explored" + (f", top fit {top_score}%" if matches else "")
    components.append(_comp("Direction", direction, detail))

    score = min(
        85,
        foundation + clarity + evidence + action + reflection + exploration + direction,
    )
    label = next(lbl for threshold, lbl in _SCORE_TO_LABEL if score >= threshold)

    return {
        "score": score,
        "label": label,
        "components": components,
        "next_move": _weakest_actionable(components),
    }


def _comp(label: str, points: int, detail: str) -> dict:
    return {"label": label, "points": points, "detail": detail}


def _weakest_actionable(components: list[dict]) -> str:
    """The single lowest-signal area is the most honest 'what to do next'."""
    weakest = min(components, key=lambda c: c["points"])
    return {
        "Foundation": "Keep your grades steady — that is the base this score rests on.",
        "Self-knowledge": "Talk to Novi about what you enjoy, what you are good at, and where you want to go.",
        "Evidence": "Add a project, competition, or leadership item to your passport — real proof earns real points.",
        "Action": "Work through your roadmap one step at a time — each step moves the needle.",
        "Reflection": "Complete a weekly check-in so Novi can help you reflect on what is working.",
        "Exploration": "Chat with Novi about colleges, careers, or anything that interests you.",
        "Direction": "Run a career match to see which paths fit your profile.",
    }.get(weakest["label"], "Keep exploring — the score moves as your effort adds up.")