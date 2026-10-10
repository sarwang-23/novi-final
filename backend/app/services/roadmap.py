from datetime import date, timedelta
import json
import re
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import GoalCategory, GoalStatus, RoadmapStage, TaskStatus
from app.models.roadmap import Goal, RoadmapItem, Task, WeeklyPriority
from app.models.user import User
from app.llm import prompts
from app.schemas.roadmap import (
    GoalCreate,
    GoalUpdate,
    PriorityGenerateRequest,
    RoadmapGenerateRequest,
    TaskCreate,
    TaskUpdate,
)
from app.services.career_dna import get_dna
from app.services import m3_bridge
from app.services.providers import dna_dict, gemini, memory
from app.services.student_context import load_student_context

GRADE_STAGE = {
    9: RoadmapStage.DISCOVER,
    10: RoadmapStage.EXPLORE,
    11: RoadmapStage.BUILD,
    12: RoadmapStage.APPLY,
}
STAGE_LABELS = {
    "discover": "Discover Yourself",
    "explore": "Explore & Experiment",
    "build": "Build Your Profile",
    "apply": "Apply With Confidence",
}


# --------------------------------------------------------------------------- goals
def create_goal(db: Session, user: User, data: GoalCreate) -> Goal:
    dup = db.scalar(
        select(Goal).where(
            Goal.user_id == user.id,
            Goal.status == GoalStatus.ACTIVE,
            func.lower(Goal.title) == data.title.strip().lower(),
            Goal.category == GoalCategory(data.category) if data.category in GoalCategory._value2member_map_ else GoalCategory.CAREER,
        )
    )
    if dup:
        return dup  # idempotent: the same active goal is never duplicated

    goal = Goal(
        user_id=user.id,
        title=data.title,
        description=data.description,
        category=GoalCategory(data.category) if data.category in GoalCategory._value2member_map_ else GoalCategory.CAREER,
        target_date=data.target_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    m3_bridge.sync_goal_to_m3(db, user, goal)
    memory.archive(
        user,
        f"User set a goal: {goal.title} ({goal.category.value}).",
        ("roadmap", "goal"),
    )
    return goal


def dedupe_goals(db: Session, user: User) -> int:
    """Merge duplicate active goals (same normalized title + category).

    Keeps the one that owns a roadmap (so progress is not lost), else the earliest;
    deletes the extras. Roadmap items under an extra goal cascade with it, so only
    childless duplicates are removed. Returns the number removed.
    """
    from collections import defaultdict

    groups: dict[str, list[Goal]] = defaultdict(list)
    for goal in list_goals(db, user):
        if goal.status != GoalStatus.ACTIVE:
            continue
        key = f"{goal.title.strip().lower()}|{goal.category.value}"
        groups[key].append(goal)

    removed = 0
    for goals in groups.values():
        if len(goals) < 2:
            continue
        child_counts = {
            g.id: len(list(db.scalars(select(RoadmapItem).where(RoadmapItem.goal_id == g.id))))
            for g in goals
        }
        goals.sort(key=lambda g: (-child_counts[g.id], g.created_at or g.id))
        for extra in goals[1:]:
            db.delete(extra)
            removed += 1
    if removed:
        db.commit()
    return removed


def list_goals(db: Session, user: User) -> list[Goal]:
    return list(db.scalars(select(Goal).where(Goal.user_id == user.id).order_by(Goal.created_at)))


def update_goal(db: Session, user: User, goal_id: int, data: GoalUpdate) -> Goal | None:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        return None
    if data.title is not None:
        goal.title = data.title
    if data.description is not None:
        goal.description = data.description

    _STATUS_ALIASES = {"done": "completed", "cancelled": "paused"}
    raw_status = data.status or goal.status.value
    mapped_status = _STATUS_ALIASES.get(raw_status, raw_status)
    if mapped_status in GoalStatus._value2member_map_:
        goal.status = GoalStatus(mapped_status)
        if goal.status == GoalStatus.COMPLETED:
            # Mark the m3 mirror + any active m3 roadmap completed too.
            m3_bridge.sync_goal_to_m3(db, user, goal)
            m3_bridge.set_goal_roadmap_status(db, user, goal, "completed")
        elif goal.status == GoalStatus.PAUSED:
            # Pausing abandons the scheduled plan and drops its legacy items.
            for old in db.scalars(select(RoadmapItem).where(RoadmapItem.goal_id == goal.id)):
                db.delete(old)
            db.flush()
            m3_bridge.set_goal_roadmap_status(db, user, goal, "abandoned")

    db.commit()
    db.refresh(goal)
    return goal


# --------------------------------------------------------------------------- roadmap
async def generate_roadmap(
    db: Session, user: User, request: RoadmapGenerateRequest
) -> RoadmapItem:
    """Generate a grade-by-grade roadmap for a goal. Returns the root item.

    When ``request.text`` is provided (the "what I want" field), a two-tier plan is
    produced: short-term do-now actions (stage=foundations) plus the long-term
    grade-by-grade journey, both grounded in chat memory + the student's own words.
    """
    goal = None
    if request.goal_id:
        goal = db.get(Goal, request.goal_id)
        if not goal or goal.user_id != user.id:
            goal = None
    if goal is None and request.title:
        goal = create_goal(db, user, GoalCreate(title=request.title))
    if goal is None and request.text:
        goal = create_goal(db, user, GoalCreate(title=request.text[:255]))
    if goal is None:
        raise ValueError("A goal is required")

    dna = get_dna(user, db)
    student = {"name": user.display_name, "grade": user.grade, "school": user.school}
    student.update(load_student_context(db, user))

    chat_context = ""
    if request.text:
        try:
            if user.letta_agent_id:
                chat_context = memory.recall_context(user.letta_agent_id, request.text)[:1200]
        except Exception as exc:
            print(f"[roadmap] chat recall failed: {exc}")

    short_items: list[dict] = []
    long_items: list[dict] = []
    if request.text and request.text.strip():
        try:
            result = await gemini.complete_json(
                prompts.roadmap_text_prompt(
                    {"title": goal.title, "description": goal.description, "category": goal.category.value},
                    student,
                    dna_dict(dna),
                    request.text,
                    chat_context,
                ),
                system=prompts.ROADMAP_TEXT_SYSTEM,
            )
            short_items = _clean_short_items((result or {}).get("short_term") or [])
            long_items = _clean_roadmap_items((result or {}).get("long_term") or [])
        except Exception as exc:
            print(f"[roadmap] text generation failed, using template: {exc}")
        if not short_items and not long_items:
            short_items = _template_short(goal.title)
            long_items = _template_roadmap(goal.title)
    else:
        items = _preset_items(goal) or []
        if not items:
            try:
                result = await gemini.complete_json(
                    prompts.roadmap_prompt(
                        {"title": goal.title, "description": goal.description, "category": goal.category.value},
                        student,
                        dna_dict(dna),
                    ),
                    system=prompts.ROADMAP_SYSTEM,
                )
                raw_items = result.get("items") or [] if isinstance(result, dict) else []
                items = _clean_roadmap_items(raw_items)
            except Exception as exc:
                print(f"[roadmap] generation failed, using template: {exc}")
        if not items:
            items = _template_roadmap(goal.title)
        long_items = items

    _purge_roadmap(db, user, goal.id)
    for idx, item in enumerate(long_items):
        db.add(
            RoadmapItem(
                user_id=user.id,
                goal_id=goal.id,
                grade=item["grade"],
                stage=GRADE_STAGE[item["grade"]],
                title=item["title"],
                description=item["description"],
                category=item.get("category", "explore"),
                order_index=idx,
            )
        )
    cur_grade = user.grade if user.grade in GRADE_STAGE else 9
    for idx, item in enumerate(short_items):
        db.add(
            RoadmapItem(
                user_id=user.id,
                goal_id=goal.id,
                grade=cur_grade,
                stage=RoadmapStage.FOUNDATIONS,
                title=item["title"],
                description=item["description"],
                category=item.get("category", "build"),
                order_index=idx,
            )
        )
    db.commit()
    memory.archive(
        user,
        f"User built a roadmap for goal '{goal.title}' with {len(long_items)} long-term steps "
        f"across grades 9-12 and {len(short_items)} short-term do-now steps.",
        ("roadmap", "plan"),
    )
    return goal.id


def get_roadmap(db: Session, user: User, goal_id: int | None = None) -> dict:
    stmt = select(RoadmapItem).where(RoadmapItem.user_id == user.id)
    if goal_id:
        stmt = stmt.where(RoadmapItem.goal_id == goal_id)
    items = list(db.scalars(stmt.order_by(RoadmapItem.order_index)))

    stages: dict[int, list[dict]] = {grade: [] for grade in (9, 10, 11, 12)}
    short_term: list[dict] = []
    for item in items:
        row = {
            "id": item.id,
            "grade": item.grade,
            "stage": item.stage.value,
            "title": item.title,
            "description": item.description,
            "category": item.category,
            "order_index": item.order_index,
            "completed": item.completed,
        }
        if item.stage == RoadmapStage.FOUNDATIONS:
            short_term.append(row)
        else:
            stages.setdefault(item.grade, []).append(row)

    goal = db.get(Goal, goal_id) if goal_id else None
    progress = progress_percent(db, user, goal_id)
    return {"goal": goal, "stages": stages, "short_term": short_term, "progress_percent": progress}


def toggle_roadmap_item(db: Session, user: User, item_id: int) -> RoadmapItem | None:
    item = db.get(RoadmapItem, item_id)
    if not item or item.user_id != user.id:
        return None
    item.completed = not item.completed
    db.commit()
    db.refresh(item)
    if item.completed:
        memory.archive(
            user,
            f"User completed a roadmap step (Grade {item.grade}): {item.title}.",
            ("roadmap", "milestone"),
        )
    return item


def progress_percent(db: Session, user: User, goal_id: int | None = None) -> int:
    stmt = select(RoadmapItem).where(RoadmapItem.user_id == user.id)
    if goal_id:
        stmt = stmt.where(RoadmapItem.goal_id == goal_id)
    items = list(db.scalars(stmt))
    if not items:
        return 0
    return round(100 * sum(1 for i in items if i.completed) / len(items))


# --------------------------------------------------------------------------- priorities
def week_start(d: date | None = None) -> date:
    today = d or date.today()
    return today - timedelta(days=today.weekday())


async def generate_priorities(db: Session, user: User, request: PriorityGenerateRequest) -> list[WeeklyPriority]:
    start = week_start()
    dna = get_dna(user, db)
    student = {"name": user.display_name, "grade": user.grade, "school": user.school}
    student.update(load_student_context(db, user))
    goals = list_goals(db, user)
    active_goals = [{"title": g.title, "category": g.category.value} for g in goals]
    incomplete = [
        {"grade": i.grade, "title": i.title, "category": i.category}
        for i in db.scalars(
            select(RoadmapItem).where(RoadmapItem.user_id == user.id, RoadmapItem.completed.is_(False))
        )
    ]

    priorities = None
    try:
        result = await gemini.complete_json(
            prompts.weekly_priorities_prompt(
                student, dna_dict(dna), active_goals, incomplete
            ),
            system=prompts.WEEKLY_PRIORITIES_SYSTEM,
        )
        raw = result.get("priorities") or [] if isinstance(result, dict) else []
        priorities = _clean_priorities(raw)
    except Exception as exc:
        print(f"[roadmap] priority generation failed, using fallback: {exc}")

    if not priorities:
        priorities = _fallback_priorities(incomplete)

    for old in db.scalars(select(WeeklyPriority).where(WeeklyPriority.user_id == user.id, WeeklyPriority.week_start == start)):
        db.delete(old)
    db.commit()

    stored = []
    for idx, p in enumerate(priorities[:3], start=1):
        wp = WeeklyPriority(
            user_id=user.id,
            week_start=start,
            ordinal=idx,
            skill_category=p["skill_category"],
            title=p["title"],
            minutes=int(p.get("minutes", 120)),
        )
        db.add(wp)
        stored.append(wp)
    db.commit()
    for wp in stored:
        db.refresh(wp)
    return stored


def get_priorities(db: Session, user: User, start: date | None = None) -> list[WeeklyPriority]:
    s = start or week_start()
    return list(
        db.scalars(
            select(WeeklyPriority)
            .where(WeeklyPriority.user_id == user.id, WeeklyPriority.week_start == s)
            .order_by(WeeklyPriority.ordinal)
        )
    )


def toggle_priority(db: Session, user: User, priority_id: int) -> WeeklyPriority | None:
    p = db.get(WeeklyPriority, priority_id)
    if not p or p.user_id != user.id:
        return None
    p.completed = not p.completed
    db.commit()
    db.refresh(p)
    return p


# --------------------------------------------------------------------------- tasks
def create_task(db: Session, user: User, data: TaskCreate) -> Task:
    task = Task(
        user_id=user.id,
        title=data.title,
        description=data.description,
        category=data.category,
        due_date=data.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, user: User, status: str | None = None) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user.id).order_by(Task.created_at)
    if status:
        stmt = stmt.where(Task.status == status)
    return list(db.scalars(stmt))


def update_task(db: Session, user: User, task_id: int, data: TaskUpdate) -> Task | None:
    task = db.get(Task, task_id)
    if not task or task.user_id != user.id:
        return None
    if data.status is not None and data.status in TaskStatus._value2member_map_:
        task.status = TaskStatus(data.status)
        if task.status == TaskStatus.DONE:
            memory.archive(
                user, f"User completed a task: {data.title or task.title}.", ("roadmap", "task")
            )
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    db.commit()
    db.refresh(task)
    return task


# --------------------------------------------------------------------------- curated catalog
_CATALOG_CACHE: list[dict] | None = None
_STOPWORDS = {
    "become", "be", "a", "an", "how", "to", "the", "of", "in", "on", "at", "and",
    "for", "with", "your", "i", "you", "from", "as", "is", "are", "do", "my", "want", "learn",
}
_ROADMAP_ALIASES: list[tuple[str, str]] = [
    ("software engineer", "software-architect"),
    ("software developer", "software-architect"),
    ("software development", "software-architect"),
    ("full stack", "full-stack"),
    ("frontend developer", "frontend"),
    ("front end developer", "frontend"),
    ("front end", "frontend"),
    ("backend developer", "backend"),
    ("back end developer", "backend"),
    ("web developer", "frontend"),
    ("web development", "frontend"),
    ("data science", "ai-data-scientist"),
    ("data scientist", "ai-data-scientist"),
    ("ai engineer", "ai-engineer"),
    ("artificial intelligence", "ai-engineer"),
    ("machine learning", "machine-learning"),
    ("ml engineer", "machine-learning"),
    ("android developer", "android"),
    ("ios developer", "ios"),
    ("game developer", "game-developer"),
    ("product manager", "product-manager"),
    ("ux designer", "ux-design"),
    ("ui designer", "ux-design"),
    ("cloud engineer", "aws"),
    ("cyber security", "cyber-security"),
    ("devops engineer", "devops"),
    ("python developer", "python"),
    ("java developer", "java"),
    ("react developer", "react"),
    ("sql", "sql"),
]


def _load_catalog() -> list[dict]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        path = Path(__file__).resolve().parents[3] / "frontend" / "all-roadmaps.json"
        try:
            with open(path, encoding="utf-8") as fh:
                _CATALOG_CACHE = json.load(fh).get("roadmaps") or []
        except Exception as exc:
            print(f"[roadmap] could not load curated catalog: {exc}")
            _CATALOG_CACHE = []
    return _CATALOG_CACHE


def _tokens(text: str) -> set[str]:
    return {
        w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in _STOPWORDS and len(w) > 1
    }


def _pick_resource(topics: dict) -> tuple[str, str] | None:
    for res in topics.get("resources") or []:
        if res.get("type") == "article" and res.get("title") and res.get("url"):
            return res["title"], res["url"]
    for res in topics.get("resources") or []:
        if res.get("title") and res.get("url"):
            return res["title"], res["url"]
    return None


_FOUNDATION = {
    "introduction", "intro", "basics", "foundational", "foundations", "fundamentals", "core",
    "overview", "principles", "concepts", "what is", "what are", "how it works", "getting started",
    "understand", "types of", "models", "architecture", "design", "patterns", "techniques",
    "learn", "101", "essential", "key", "role", "responsibilities", "vs",
}
_VENDOR = {
    "atlan", "qdrant", "pinecone", "weaviate", "chroma", "ollama", "langsmith", "langfuse",
    "helicone", "haystack", "supabase", "replit", "windsurf", "cursor", "codex", "vertex", "jina",
    "arize", "posthog", "deep", "datahub", "nano", "openrouter", "lm studio", "mongo", "faiss",
    "lance", "transformers", "whisper", "dall", "atlassian", "trello", "slack", "salesforce", "sap",
}


def _topic_score(title: str, slug_tokens: set[str]) -> int:
    low = title.lower()
    toks = set(re.findall(r"[a-z0-9]+", low))
    score = sum(5 if t != "ai" else 2 for t in (toks & slug_tokens))
    for keyword in _FOUNDATION:
        if keyword in low:
            score += 2
    if re.search(r"^(what are|what is|how|introduction|understanding|understand|overview|guide|basics)", low):
        score += 3
    if any(v in low for v in _VENDOR):
        score -= 3
    if re.search(r"\b(vs|versus|compar|difference)\b", low):
        score -= 1
    if not any(k in low for k in _FOUNDATION) and not (toks & slug_tokens - {"ai"}):
        score -= 3
    return score


def _topics_to_items(rm: dict) -> list[dict]:
    """Curate a pedagogical grade-9-to-12 plan from a curated roadmap's topics."""
    slug_tokens = set(re.findall(r"[a-z0-9]+", rm.get("slug", "")))
    seen: set[str] = set()
    ranked = []
    for topic in rm.get("topics") or []:
        title = str(topic.get("title") or "").strip()
        if not title:
            continue
        key = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        ranked.append(topic)
    ranked.sort(key=lambda t: (-_topic_score(t["title"], slug_tokens), t["title"].lower()))
    chosen = ranked[:10]

    items = []
    for i, topic in enumerate(chosen):
        f = (i + 0.5) / len(chosen)
        if f < 0.30:
            grade, category = 9, "explore"
        elif f < 0.55:
            grade, category = 10, "grow"
        elif f < 0.80:
            grade, category = 11, "build"
        else:
            grade, category = 12, "build"
        desc = (topic.get("description") or "").strip()
        res = _pick_resource(topic)
        if res:
            desc = f"{desc}\n\nDive deeper: {res[0]} — {res[1]}"
        items.append(
            {
                "grade": grade,
                "stage": GRADE_STAGE[grade].value,
                "category": category,
                "title": str(topic.get("title") or "")[:255],
                "description": desc,
            }
        )
    return items


def _preset_items(goal) -> list[dict] | None:
    """Deterministic, instantly-available preset roadmap from all-roadmaps.json."""
    catalog = _load_catalog()
    if not catalog:
        return None
    title_low = (goal.title or "").lower()
    for phrase, slug in _ROADMAP_ALIASES:
        if phrase in title_low:
            matched = next((rm for rm in catalog if rm.get("slug") == slug), None)
            if matched:
                return _topics_to_items(matched)

    needle = _tokens(f"{goal.title} {goal.description or ''}")
    if not needle:
        return None
    best, best_score = None, 0
    for rm in catalog:
        hay = set(_tokens(rm.get("slug", "").replace("-", " ")))
        for topic in (rm.get("topics") or [])[:80]:
            hay |= _tokens(topic.get("title", ""))
        overlap = len(needle & hay)
        if overlap > best_score:
            best, best_score = rm, overlap
    if best_score < 2:
        return None
    return _topics_to_items(best)


# --------------------------------------------------------------------------- helpers
def _purge_roadmap(db: Session, user: User, goal_id: int) -> None:
    for item in db.scalars(
        select(RoadmapItem).where(RoadmapItem.user_id == user.id, RoadmapItem.goal_id == goal_id)
    ):
        db.delete(item)
    db.commit()


def _clean_roadmap_items(raw: list) -> list[dict]:
    cleaned = []
    for item in raw if isinstance(raw, list) else []:
        try:
            grade = int(item.get("grade", 0))
        except (TypeError, ValueError):
            continue
        if grade not in GRADE_STAGE or not item.get("title"):
            continue
        category = item.get("category", "explore")
        if category not in ("build", "explore", "grow"):
            category = "explore"
        cleaned.append(
            {
                "grade": grade,
                "stage": GRADE_STAGE[grade].value,
                "category": category,
                "title": str(item["title"])[:255],
                "description": str(item.get("description", "")),
            }
        )
    cleaned.sort(key=lambda x: (x["grade"]))
    return cleaned


def _clean_priorities(raw: list) -> list[dict]:
    cleaned = []
    for p in raw if isinstance(raw, list) else []:
        if not p.get("title"):
            continue
        category = p.get("skill_category", "build")
        if category not in ("build", "explore", "grow"):
            category = "build"
        try:
            minutes = int(p.get("minutes", 120))
        except (TypeError, ValueError):
            minutes = 120
        cleaned.append({"skill_category": category, "title": str(p["title"])[:255], "minutes": minutes})
    return cleaned[:3]


def _clean_short_items(raw: list) -> list[dict]:
    cleaned = []
    for item in raw if isinstance(raw, list) else []:
        if not item.get("title"):
            continue
        category = item.get("category", "build")
        if category not in ("build", "explore", "grow"):
            category = "build"
        cleaned.append(
            {
                "category": category,
                "title": str(item["title"])[:255],
                "description": str(item.get("description", "")),
            }
        )
    return cleaned[:8]


def _template_short(goal_title: str) -> list[dict]:
    steps = [
        ("Pin down what you want", "Write a one-paragraph description of this goal in your own words.", "explore"),
        ("List three first actions", "Identify the three smallest things you can start this week.", "build"),
        ("Set a weekly rhythm", "Block 3 focused hours each week for this goal.", "grow"),
    ]
    return [
        {"category": category, "title": title, "description": f"{desc} (toward: {goal_title})"}
        for title, desc, category in steps
    ]


def _template_roadmap(goal_title: str) -> list[dict]:
    templates = {
        9: [
            ("Explore interests tied to your goal", "Try 3 different activities to see what clicks.", "explore"),
            ("Build foundational skills", "Start learning a core skill for this field.", "grow"),
        ],
        10: [
            ("Start a beginner project", "Create something small that explores the field.", "build"),
            ("Enter your first competition", "Even participating teaches you a lot.", "build"),
        ],
        11: [
            ("Deep research project", "Go beyond a school project — real depth matters.", "build"),
            ("Take a leadership role", "Lead a team, club or community initiative.", "grow"),
        ],
        12: [
            ("Finalise university shortlist", "Build your application strategy and targets.", "explore"),
            ("Write standout essays", "Tell your story with evidence from your journey.", "build"),
            ("Manage deadlines", "Keep every application date on a single calendar.", "grow"),
        ],
    }
    return [
        {
            "grade": grade,
            "stage": GRADE_STAGE[grade].value,
            "category": category,
            "title": title,
            "description": f"{desc} (toward: {goal_title})",
        }
        for grade, rows in templates.items()
        for title, desc, category in rows
    ]


def _fallback_priorities(incomplete: list[dict]) -> list[dict]:
    builds = [i for i in incomplete if i.get("category") == "build"]
    explores = [i for i in incomplete if i.get("category") == "explore"]
    grows = [i for i in incomplete if i.get("category") == "grow"]
    picks = []
    for src, category in ((builds, "build"), (explores, "explore"), (grows, "grow")):
        if src:
            picks.append({"skill_category": category, "title": src[0]["title"], "minutes": 120})
    while len(picks) < 3:
        picks.append({"skill_category": "explore", "title": "Explore one new career or university", "minutes": 60})
    return picks[:3]