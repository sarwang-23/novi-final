"""One source of truth stitched to the chat mentor.

Every page (roadmap, passport, tasks, check-ins, DNA) writes its changes into
Letta's archival memory as a single replaceable "novistate" passage, so the chat
agent always knows the student's CURRENT app state. Because recall_context loads
that passage deterministically on every message, chat and pages stay in sync
both ways:

  pages -> chat : a mutation on any page refreshes Letta's state memory
  chat  -> pages: after a chat turn Letta's memory is re-synced with the DB, and
                  the DNA auto-refresh already lands on the page the next render
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.career_dna import CareerDNA
from app.models.checkin import WeeklyCheckin
from app.models.passport import PassportItem
from app.models.roadmap import Goal, RoadmapItem, Task, WeeklyPriority
from app.services.providers import memory


def build_snapshot(user, db: Session) -> str:
    """A compact, current cross-page snapshot used to seed Letta's state memory."""
    parts: list[str] = []

    dna = db.scalar(select(CareerDNA).where(CareerDNA.user_id == user.id))
    if dna and dna.dna_filled:
        bits = []
        if dna.career_zones:
            bits.append("focus: " + ", ".join(dna.career_zones[:3]))
        if dna.goals:
            bits.append("goals: " + "; ".join(dna.goals[:3]))
        if dna.interests:
            bits.append("interests: " + ", ".join(dna.interests[:4]))
        if bits:
            parts.append("Career DNA — " + " | ".join(bits))

    goals = list(db.scalars(select(Goal).where(Goal.user_id == user.id)))
    for goal in sorted([g for g in goals if g.status.value == "active"], key=lambda g: g.created_at):
        items = list(db.scalars(select(RoadmapItem).where(RoadmapItem.goal_id == goal.id)))
        if not items:
            parts.append(f'Active goal: "{goal.title}" ({goal.category.value}) — roadmap not generated yet')
            continue
        done = sum(1 for i in items if i.completed)
        incomplete = [i.title for i in items if not i.completed and i.grade <= (user.grade or 12)][:2]
        line = f'Active goal: "{goal.title}" ({goal.category.value}) — {done}/{len(items)} roadmap steps done'
        if incomplete:
            line += "; next: " + "; ".join(incomplete)
        parts.append(line)

    all_items = list(db.scalars(select(RoadmapItem).where(RoadmapItem.user_id == user.id)))
    if all_items:
        parts.append(f"Roadmap overall: {sum(1 for i in all_items if i.completed)}/{len(all_items)} steps done")

    priorities = list(
        db.scalars(
            select(WeeklyPriority).where(WeeklyPriority.user_id == user.id).order_by(WeeklyPriority.week_start.desc())
        )
    )
    if priorities:
        prio = [p for p in priorities if p.week_start == priorities[0].week_start]
        done = sum(1 for p in prio if p.completed)
        parts.append(
            f"This week's priorities ({done}/{len(prio)} done): "
            + "; ".join(f"{p.title}{' ✓' if p.completed else ''}" for p in prio[:3])
        )

    tasks = list(db.scalars(select(Task).where(Task.user_id == user.id)))
    open_tasks = [t for t in tasks if t.status.value != "done"]
    done_tasks = len(tasks) - len(open_tasks)
    if tasks:
        parts.append(
            f"Tasks ({len(open_tasks)} open, {done_tasks} done): "
            + "; ".join(t.title for t in open_tasks[:3])
            + (" …" if len(open_tasks) > 3 else "")
        )

    passport_items = list(
        db.scalars(select(PassportItem).where(PassportItem.user_id == user.id).order_by(PassportItem.created_at.desc()))
    )
    if passport_items:
        verified = sum(1 for p in passport_items if p.verified)
        parts.append(
            f"Passport ({len(passport_items)} entries, {verified} verified): "
            + "; ".join(p.title for p in passport_items[:3])
        )

    checkins = list(db.scalars(select(WeeklyCheckin).where(WeeklyCheckin.user_id == user.id)))
    submitted = [c for c in checkins if c.status.value in ("submitted", "summarized")]
    if submitted:
        parts.append(f"Check-ins logged: {len(submitted)} week(s)")

    if not parts:
        return ""
    return (
        "The student's current state across the app (authoritative, synced from the app database). "
        "Ground every reply in this.\n- " + "\n- ".join(parts)
    )


def push(user, db: Session) -> bool:
    """Mirror the current DB state into Letta's state memory (pages -> chat).

    Fire-and-forget friendly: silently returns False when Letta is down or the
    student has no agent yet.
    """
    agent = getattr(user, "letta_agent_id", None)
    if not agent or not memory.is_reachable():
        return False
    text = build_snapshot(user, db)
    if not text:
        return False
    try:
        return memory.set_state(agent, text, grade=getattr(user, "grade", None))
    except Exception as exc:
        print(f"[state_sync] push failed: {exc}")
        return False