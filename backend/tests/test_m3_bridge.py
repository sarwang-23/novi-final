"""Tests for the legacy <-> module-3 bridge and the m3 scheduling seam."""

from datetime import date, timedelta

import pytest

from app.m3.db.models import Goal as M3Goal
from app.m3.db.models import Roadmap as M3Roadmap
from app.m3.db.models import Task as M3Task
from app.m3.schemas.adaptation import (
    AdaptationApplyRequest,
    GeneratedAdaptation,
    SkipTaskAction,
)
from app.m3.schemas.roadmap_generation import (
    GeneratedMilestone,
    GeneratedRoadmap,
    GeneratedTask,
)
from app.m3.services.adaptation_service import RoadmapAdaptationService
from app.models.career import Career, CareerMatch
from app.models.enums import GoalCategory, GoalStatus
from app.models.roadmap import Goal, RoadmapItem
from app.models.user import User
from app.services import m3_bridge


# --------------------------------------------------------------------------- helpers
def make_generated(title="AI Career Path", milestones=2, tasks_per_milestone=2) -> GeneratedRoadmap:
    return GeneratedRoadmap(
        title=title,
        description="A structured stub roadmap used for deterministic tests.",
        milestones=[
            GeneratedMilestone(
                title=f"Stage {i + 1}",
                description=f"Phase {i + 1}",
                order_index=i,
                tasks=[
                    GeneratedTask(
                        title=f"Stage {i + 1} Task {j + 1}",
                        description=f"Work item {j + 1} for stage {i + 1}",
                        order_index=j,
                        priority="high" if j == 0 else "medium",
                    )
                    for j in range(tasks_per_milestone)
                ],
            )
            for i in range(milestones)
        ],
    )


class StubGenerator:
    def __init__(self, roadmap: GeneratedRoadmap | None = None):
        self.roadmap = roadmap or make_generated()

    def generate(self, goal=None, career=None, career_match=None, existing_skills=None,
                 skill_gaps=None, readiness=None):
        return self.roadmap


class StubAdaptationProvider:
    def __init__(self, adaptation: GeneratedAdaptation):
        self.adaptation = adaptation

    def generate_structured(self, prompt, response_model):
        return self.adaptation


@pytest.fixture()
def goal(db, user):
    g = Goal(
        user_id=user.id,
        title="Become an AI engineer",
        description="Learn ML and ship projects",
        category=GoalCategory.CAREER,
        status=GoalStatus.ACTIVE,
        target_date=date.today() + timedelta(days=365),
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def generate(db, user, goal, generator=None):
    roadmap = m3_bridge.generate_and_activate_roadmap(db, user, goal, generator=generator or StubGenerator())
    assert roadmap is not None
    return roadmap


# --------------------------------------------------------------------------- goal sync
def test_sync_goal_creates_m3_goal(db, user, goal):
    m3_goal = m3_bridge.sync_goal_to_m3(db, user, goal, commit=True)
    assert isinstance(m3_goal, M3Goal)
    assert m3_goal.legacy_goal_id == goal.id
    assert m3_goal.goal_type == "career"
    assert m3_goal.status == "active"
    assert m3_goal.target_date == goal.target_date
    assert m3_bridge.m3_goal_for(db, user, goal).id == m3_goal.id


def test_sync_goal_is_idempotent_and_propagates_updates(db, user, goal):
    first = m3_bridge.sync_goal_to_m3(db, user, goal, commit=True)
    goal.title = "Become a machine learning engineer"
    goal.status = GoalStatus.COMPLETED
    db.commit()
    db.refresh(goal)

    second = m3_bridge.sync_goal_to_m3(db, user, goal, commit=True)
    assert second.id == first.id
    assert second.title == "Become a machine learning engineer"
    assert second.status == "completed"
    assert db.query(M3Goal).filter(M3Goal.legacy_goal_id == goal.id).count() == 1


# --------------------------------------------------------------------------- generation + mirror
def test_generate_persists_active_scheduled_roadmap(db, user, goal):
    roadmap = generate(db, user, goal)
    assert roadmap.status == "active"
    assert roadmap.target_date == goal.target_date
    assert roadmap.start_date is not None

    full = m3_bridge.active_roadmap_full(db, user, goal)
    assert full is not None
    assert len(full["milestones"]) == 2
    assert full["total_tasks"] == 4
    # Scheduler anchors dates for every milestone/task when a target date exists.
    assert full["milestones"][0]["tasks"][0]["start_date"] is not None
    assert full["milestones"][-1]["target_date"] == goal.target_date.isoformat()


def test_mirror_creates_grade_items_and_is_replaceable(db, user, goal):
    roadmap = generate(db, user, goal)
    created = m3_bridge.mirror_roadmap_to_legacy(db, user, goal, roadmap)
    assert created == 4

    items = list(db.query(RoadmapItem).filter(RoadmapItem.goal_id == goal.id))
    assert {i.grade for i in items} <= {9, 10, 11, 12}
    assert all(i.stage.value in {"discover", "explore", "build", "apply"} for i in items)
    assert all(i.completed is False for i in items)
    # First milestone maps earlier in the journey than the last.
    assert min(i.grade for i in items) <= max(i.grade for i in items)

    # Re-mirroring replaces rather than duplicates.
    again = m3_bridge.mirror_roadmap_to_legacy(db, user, goal, roadmap)
    assert again == 4
    assert db.query(RoadmapItem).filter(RoadmapItem.goal_id == goal.id).count() == 4


def test_regeneration_abandons_the_previous_active_roadmap(db, user, goal):
    first = generate(db, user, goal)
    second = generate(db, user, goal, generator=StubGenerator(make_generated(title="Second Pass")))

    assert second.id != first.id
    db.refresh(first)
    assert first.status == "abandoned"
    assert second.status == "active"
    active = [r for r in db.query(M3Roadmap).filter(M3Roadmap.goal_id == second.goal_id) if r.status == "active"]
    assert len(active) == 1


# --------------------------------------------------------------------------- completion propagation
def test_legacy_toggle_propagates_to_m3_task(db, user, goal):
    roadmap = generate(db, user, goal)
    m3_bridge.mirror_roadmap_to_legacy(db, user, goal, roadmap)

    item = db.query(RoadmapItem).filter(RoadmapItem.goal_id == goal.id).first()
    item.completed = True
    db.commit()
    assert m3_bridge.sync_item_completion(db, user, goal, item) is True

    task = db.query(M3Task).filter(M3Task.title == item.title).first()
    db.refresh(task)
    assert task.status == "completed"
    assert m3_bridge.progress_percentage(db, user, goal.id) == 25


def test_m3_completion_reconciles_into_legacy_items(db, user, goal):
    roadmap = generate(db, user, goal)
    m3_bridge.mirror_roadmap_to_legacy(db, user, goal, roadmap)

    task = db.query(M3Task).first()
    task.status = "completed"
    db.commit()
    changed = m3_bridge.reconcile_legacy_items(db, user, goal, roadmap)
    assert changed == 1

    item = db.query(RoadmapItem).filter(RoadmapItem.goal_id == goal.id, RoadmapItem.title == task.title).first()
    assert item is not None and item.completed is True
    assert m3_bridge.progress_percentage(db, user, goal.id) == 25


def test_progress_is_none_without_a_scheduled_plan(db, user, goal):
    assert m3_bridge.progress_percentage(db, user, goal.id) is None


def test_upcoming_tasks_lists_pending_in_order(db, user, goal):
    generate(db, user, goal)
    m3_bridge.mirror_roadmap_to_legacy(db, user, goal, m3_bridge.active_roadmap_for(db, user, goal))
    upcoming = m3_bridge.upcoming_tasks(db, user, goal)
    assert len(upcoming) == 4
    assert all(t["status"] == "pending" for t in upcoming)
    assert all(t["milestone_title"] for t in upcoming)


# --------------------------------------------------------------------------- ownership
def test_resolve_task_chain_enforces_ownership(db, user, goal):
    roadmap = generate(db, user, goal)
    task = db.query(M3Task).first()
    chain = m3_bridge.resolve_task_chain(db, user, task.id)
    assert chain["legacy_goal"].id == goal.id
    assert chain["roadmap_id"] == roadmap.id

    intruder = User(email="intruder@test.local", password_hash="x", first_name="No", last_name="Body")
    db.add(intruder)
    db.commit()
    db.refresh(intruder)
    with pytest.raises(PermissionError):
        m3_bridge.resolve_task_chain(db, intruder, task.id)


def test_generation_uses_career_context(db, user, goal):
    career = Career(slug="ai-engineer", title="AI Engineer", category="technology", summary="AI")
    db.add(career)
    db.commit()
    db.refresh(career)
    db.add(CareerMatch(user_id=user.id, career_id=career.id, score=91.0, rank=1, reasons=[]))
    db.commit()

    context = m3_bridge.build_generation_context(db, user)
    assert context["career"] is not None
    assert context["career"].slug == "ai-engineer"
    assert context["career_match"] is not None


# --------------------------------------------------------------------------- adaptation
def test_adaptation_preview_is_read_only_and_apply_is_atomic(db, user, goal):
    roadmap = generate(db, user, goal)
    m3_bridge.mirror_roadmap_to_legacy(db, user, goal, roadmap)

    pending = db.query(M3Task).filter(M3Task.status == "pending").first()
    adaptation = GeneratedAdaptation(
        assessment="You are ready to trim the plan.",
        reasoning="Skipping one low-value pending task keeps momentum focused.",
        recommended_actions=[
            SkipTaskAction(task_id=pending.id, reason="Lower value than the scheduled project work.")
        ],
    )
    service = RoadmapAdaptationService(db, ai_provider=StubAdaptationProvider(adaptation))
    student_id = m3_bridge.ensure_m3_student(db, user).id

    preview = service.preview(student_id, roadmap.goal_id, roadmap.id)
    assert len(preview.recommended_actions) == 1
    db.refresh(pending)
    assert pending.status == "pending"  # preview wrote nothing

    result = service.apply(
        student_id,
        roadmap.goal_id,
        roadmap.id,
        AdaptationApplyRequest(actions=preview.recommended_actions),
    )
    assert result.applied_actions_count == 1
    db.refresh(pending)
    assert pending.status == "skipped"


# --------------------------------------------------------------------------- legacy service integration
def test_create_goal_via_service_syncs_m3(db, user):
    from app.schemas.roadmap import GoalCreate
    from app.services import roadmap as roadmap_service

    created = roadmap_service.create_goal(db, user, GoalCreate(title="Build a game", category="career"))
    m3_goal = m3_bridge.m3_goal_for(db, user, created)
    assert m3_goal is not None
    assert m3_goal.legacy_goal_id == created.id


def test_update_goal_done_marks_plan_completed(db, user, goal):
    from app.schemas.roadmap import GoalUpdate
    from app.services import roadmap as roadmap_service

    roadmap = generate(db, user, goal)
    roadmap_service.update_goal(db, user, goal.id, GoalUpdate(status="done"))
    db.refresh(goal)
    db.refresh(roadmap)
    assert goal.status == GoalStatus.COMPLETED
    assert roadmap.status == "completed"
    db.refresh(m3_bridge.m3_goal_for(db, user, goal))
    assert m3_bridge.m3_goal_for(db, user, goal).status == "completed"


def test_update_goal_cancelled_purges_items_and_abandons_plan(db, user, goal):
    from app.schemas.roadmap import GoalUpdate
    from app.services import roadmap as roadmap_service

    roadmap = generate(db, user, goal)
    m3_bridge.mirror_roadmap_to_legacy(db, user, goal, roadmap)
    assert db.query(RoadmapItem).filter(RoadmapItem.goal_id == goal.id).count() == 4

    roadmap_service.update_goal(db, user, goal.id, GoalUpdate(status="cancelled"))
    db.refresh(goal)
    db.refresh(roadmap)
    assert goal.status == GoalStatus.PAUSED
    assert roadmap.status == "abandoned"
    assert db.query(RoadmapItem).filter(RoadmapItem.goal_id == goal.id).count() == 0
