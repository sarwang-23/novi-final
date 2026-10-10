from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.roadmap import RoadmapItem
from app.models.user import User
from app.services import passport as passport_svc
from app.services import roadmap as roadmap_svc
from app.services.career_dna import get_dna
from app.services.careers import career_detail, list_career_matches
from app.services.checkins import get_current
from app.services.providers import fallback_insight
from app.services.universities import average_readiness, recent_matches


def student_dashboard(db: Session, user: User) -> dict:
    dna = get_dna(user, db)
    career_matches = _career_matches_payload(db, user)
    goals = [
        {"id": g.id, "title": g.title, "description": g.description,
         "category": g.category.value, "status": g.status.value,
         "target_date": g.target_date.isoformat() if g.target_date else None}
        for g in roadmap_svc.list_goals(db, user)
    ]
    roadmap_items = _roadmap_payload(db, user)
    priorities = [
        {"id": p.id, "week_start": p.week_start.isoformat(), "ordinal": p.ordinal,
         "skill_category": p.skill_category.value, "title": p.title,
         "minutes": p.minutes, "completed": p.completed}
        for p in roadmap_svc.get_priorities(db, user)
    ]
    passport_items = _passport_payload(db, user)
    passport_completion = passport_svc.completion(db, user)
    current_checkin = get_current(db, user)
    next_task = _next_task(db, user)

    progress = _progress(db, user, passport_completion)
    focus = _today_focus(db, user, next_task, priorities, roadmap_items)
    top_career = career_matches[0]["career"]["title"] if career_matches and career_matches[0].get("career") else None
    insight = fallback_insight(
        user.first_name or "there", user.grade, _dna_plain(dna), top_career
    )
    action = None
    if top_career:
        action = "Explore the path behind this career and the next steps to get there."
    elif dna and (dna.interests or []):
        action = "Discover careers that match the interests you've shared."

    return {
        "greeting": _greeting(user.first_name or ""),
        "today_focus": focus,
        "progress": progress,
        "novi_says": insight.split("]", 1)[-1].strip() if "]" in insight else insight,
        "novi_says_action": action,
        "dna": _dna_payload(dna),
        "career_matches": career_matches,
        "goals": goals,
        "roadmap_items": roadmap_items,
        "priorities": priorities,
        "passport": passport_items,
        "passport_completion": passport_completion,
        "current_checkin": _checkin_payload(current_checkin),
        "next_task": _task_payload(next_task),
    }


# --------------------------------------------------------------------------- progress
def progress_indicators(db: Session, user: User) -> dict:
    passport_completion = passport_svc.completion(db, user)
    return _progress(db, user, passport_completion)


def _progress(db: Session, user: User, passport_completion: dict) -> dict:
    dna = get_dna(user, db)
    career_matches = list_career_matches(db, user)
    top_score = career_matches[0].score if career_matches else 0

    if not career_matches:
        direction = "Exploring" if (dna and dna.dna_filled) else "Needs Focus"
    elif top_score >= 60:
        direction = "On Track"
    elif top_score >= 40:
        direction = "Exploring"
    else:
        direction = "Needs Focus"

    dna_pct = 100 if (dna and dna.dna_filled) else 0
    if dna and not dna.dna_filled:
        dna_pct = min(100, sum(1 for f in (dna.traits, dna.interests, dna.strengths, dna.career_zones) if f) * 15)
    goals = list(roadmap_svc.list_goals(db, user))
    goal_momentum = min(100, sum(1 for g in goals if g.status.value == "active") * 20)

    profile_strength = round(
        0.35 * dna_pct
        + 0.25 * top_score
        + 0.20 * goal_momentum
        + 0.10 * roadmap_svc.progress_percent(db, user)
        + 0.10 * passport_completion["score"]
    )
    return {
        "career_direction": direction,
        "profile_strength": profile_strength,
        "university_readiness": average_readiness(db, user),
        "roadmap_progress": roadmap_svc.progress_percent(db, user),
    }


def _today_focus(db: Session, user: User, next_task: dict | None, priorities: list[dict], roadmap_items: list[dict]) -> dict | None:
    if next_task:
        return {
            "kind": "task",
            "id": next_task["id"],
            "title": next_task["title"],
            "why": f"This strengthens your {next_task.get('category', 'current')} profile and moves you closer to your goal.",
        }
    grade_items = [r for r in roadmap_items if not r["completed"] and r["grade"] >= (user.grade or 9)]
    if grade_items:
        return {
            "kind": "roadmap",
            "id": grade_items[0]["id"],
            "title": grade_items[0]["title"],
            "why": "This is your next step on your learning roadmap.",
        }
    active = [p for p in priorities if not p["completed"]]
    if active:
        return {
            "kind": "priority",
            "id": active[0]["id"],
            "title": active[0]["title"],
            "why": f"This is your top {active[0]['skill_category']} priority for this week.",
        }
    return None


# --------------------------------------------------------------------------- payloads
def _career_matches_payload(db: Session, user: User) -> list[dict]:
    rows = []
    for m in list_career_matches(db, user):
        rows.append(
            {
                "id": m.id,
                "rank": m.rank,
                "score": round(m.score),
                "reasons": m.reasons or [],
                "career": career_detail(db, m.career),
            }
        )
    return rows


def _roadmap_payload(db: Session, user: User) -> list[dict]:
    rows = db.scalars(
        select(RoadmapItem)
        .where(RoadmapItem.user_id == user.id)
        .order_by(RoadmapItem.grade, RoadmapItem.order_index)
    )
    return [
        {"id": i.id, "grade": i.grade, "stage": i.stage.value, "title": i.title,
         "description": i.description, "category": i.category, "order_index": i.order_index,
         "completed": i.completed, "goal_id": i.goal_id}
        for i in rows
    ]


def _dna_payload(dna) -> dict | None:
    if not dna:
        return None
    return {
        "id": dna.id, "user_id": dna.user_id,
        "traits": dna.traits or [], "motivations": dna.motivations or [],
        "strengths": dna.strengths or [], "development_areas": dna.development_areas or [],
        "interests": dna.interests or [], "subjects": dna.subjects or [],
        "skills": dna.skills or [], "career_zones": dna.career_zones or [],
        "values": dna.values or [], "goals": dna.goals or [],
        "novi_reflection": dna.novi_reflection or "",
        "dna_filled": dna.dna_filled,
        "updated_at": dna.updated_at.isoformat() if dna.updated_at else None,
    }


def _dna_plain(dna) -> dict:
    if not dna:
        return {}
    return {
        "interests": dna.interests or [],
        "career_zones": dna.career_zones or [],
        "skills": dna.skills or [],
    }


def _passport_payload(db: Session, user: User) -> list[dict]:
    return [
        {"id": p.id, "category": p.category.value, "title": p.title,
         "description": p.description, "skills": p.skills or [],
         "date_achieved": p.date_achieved.isoformat() if p.date_achieved else None,
         "certificate_url": p.certificate_url, "verified": p.verified,
         "created_at": p.created_at.isoformat() if p.created_at else None}
        for p in passport_svc.list_items(db, user)
    ]


def _checkin_payload(checkin) -> dict | None:
    if not checkin:
        return None
    return {
        "id": checkin.id, "week_start": checkin.week_start.isoformat(),
        "accomplishments": checkin.accomplishments, "learnings": checkin.learnings,
        "challenges": checkin.challenges, "pride": checkin.pride,
        "next_week": checkin.next_week, "ai_summary": checkin.ai_summary,
        "status": checkin.status.value,
        "updated_at": checkin.updated_at.isoformat() if checkin.updated_at else None,
    }


def _next_task(db: Session, user: User) -> dict | None:
    from app.services.roadmap import list_tasks

    for t in list_tasks(db, user):
        if t.status.value in ("todo", "doing"):
            return {
                "id": t.id, "title": t.title, "description": t.description,
                "category": t.category, "status": t.status.value,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
    return None


def _task_payload(task: dict | None) -> dict | None:
    return task


def _greeting(first_name: str) -> str:
    hour = datetime.now().hour
    if hour < 12:
        part = "Good morning"
    elif hour < 17:
        part = "Good afternoon"
    else:
        part = "Good evening"
    return f"{part}, {first_name} 👋" if first_name else f"{part} 👋"