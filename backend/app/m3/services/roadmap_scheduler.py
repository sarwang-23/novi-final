"""
RoadmapScheduler – Pure Deterministic Roadmap Scheduling Engine.

Responsibilities:
- Assign calendar dates (start_date, target_date) to an already-generated roadmap,
  its milestones, and its tasks.
- Pure, deterministic, and testable: strictly independent of SQLAlchemy, database
  sessions, API layers, and AI providers.
- Operates on explicit calendar dates (no datetime.now() or date.today() calls).
- When roadmap_start_date or roadmap_target_date is missing, returns an unchanged
  result without inventing default dates (+30, +60, +365, etc.).
- Enforces hierarchical date containment:
    Roadmap.start_date <= Milestone.start_date <= Task.start_date
    Task.start_date <= Task.target_date <= Milestone.target_date
    Milestone.target_date <= Roadmap.target_date
- Enforces strict milestone and task order preservation based on order_index.
- Priority influences scheduling order only within otherwise valid ordering constraints.
- Aligns tasks to Monday–Sunday weekly cycles where the milestone duration allows,
  capping gracefully when milestone duration is short.
- Preserves existing dates of completed tasks without mutation.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any


# ---------------------------------------------------------------------------
# Data Containers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScheduledTask:
    task_id: Any = None
    title: str = ""
    order_index: int = 0
    priority: str = "medium"
    status: str = "pending"
    start_date: date | None = None
    target_date: date | None = None
    raw: Any = None


@dataclass(frozen=True)
class ScheduledMilestone:
    milestone_id: Any = None
    title: str = ""
    order_index: int = 0
    status: str = "pending"
    start_date: date | None = None
    target_date: date | None = None
    tasks: list[ScheduledTask] = field(default_factory=list)
    raw: Any = None


@dataclass(frozen=True)
class ScheduledRoadmap:
    start_date: date | None = None
    target_date: date | None = None
    milestones: list[ScheduledMilestone] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers for Duck-Typing Input
# ---------------------------------------------------------------------------


def _extract(item: Any, attr: str, default: Any = None) -> Any:
    """Extract attribute or dict key gracefully."""
    if isinstance(item, Mapping):
        return item.get(attr, default)
    return getattr(item, attr, default)


def _set_if_mutable(item: Any, attr: str, value: Any) -> None:
    """If input item is mutable (e.g. dict or object with setters), update it."""
    if isinstance(item, dict):
        item[attr] = value
    elif hasattr(item, "__dict__") and hasattr(item, attr):
        try:
            setattr(item, attr, value)
        except (AttributeError, TypeError):
            pass


def _to_date(val: Any) -> date | None:
    """Safely convert datetime to date, or return date as-is."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


# ---------------------------------------------------------------------------
# Milestone Duration Allocation (Largest Remainder Method)
# ---------------------------------------------------------------------------


def _allocate_milestone_days(
    total_days: int,
    milestones_tasks_counts: list[int],
) -> list[int]:
    """Deterministically allocate total_days across K milestones weighted by task count.

    Uses the Largest Remainder (Hare-Niemeyer / Hamilton) integer allocation.
    Guarantees: sum(allocations) == total_days.
    When total_days >= K, each milestone receives at least 1 day.
    """
    k = len(milestones_tasks_counts)
    if k == 0:
        return []
    if total_days <= 0:
        return [0] * k

    # Edge case: fewer days than milestones
    if total_days < k:
        allocations = [0] * k
        for i in range(total_days):
            allocations[i] = 1
        return allocations

    # Base allocation: at least 1 day per milestone
    base = 1
    remaining_days = total_days - k
    total_tasks = sum(milestones_tasks_counts)

    if total_tasks == 0:
        # Distribute equally if no tasks exist
        extra_each = remaining_days // k
        extra_rem = remaining_days % k
        return [base + extra_each + (1 if i < extra_rem else 0) for i in range(k)]

    # Proportional quotas
    quotas = [(remaining_days * count) / total_tasks for count in milestones_tasks_counts]
    integer_parts = [int(q) for q in quotas]
    remainders = [q - int(q) for q in quotas]

    unallocated = remaining_days - sum(integer_parts)

    # Distribute leftover days to largest remainders (tie-breaker: milestone index)
    sorted_by_remainder = sorted(
        range(k),
        key=lambda idx: (remainders[idx], -idx),
        reverse=True,
    )
    extra_days = [0] * k
    for idx in sorted_by_remainder[:unallocated]:
        extra_days[idx] = 1

    return [base + integer_parts[i] + extra_days[i] for i in range(k)]


# ---------------------------------------------------------------------------
# Task Date Allocation
# ---------------------------------------------------------------------------

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _schedule_tasks_in_milestone(
    milestone_start: date,
    milestone_target: date,
    tasks_input: Sequence[Any],
) -> list[ScheduledTask]:
    """Assign start_date and target_date to tasks within milestone bounds.

    Tasks are ordered strictly by order_index ascending.
    Priority acts as a tie-breaker when order_index is identical, scheduling
    higher-priority tasks earlier without violating order_index authority.
    If the milestone duration spans multiple weeks (>= 14 days), aligns task target dates
    to weekly Sunday boundaries where possible.
    If milestone is short, spaces tasks evenly across daily slots.
    Preserves existing dates of completed tasks.
    """
    # Sort tasks by order_index ascending, priority ascending (high=0, med=1, low=2), and ID
    sorted_tasks = sorted(
        tasks_input,
        key=lambda t: (
            _extract(t, "order_index", 0),
            PRIORITY_RANK.get(str(_extract(t, "priority", "medium") or "medium").lower(), 1),
            str(_extract(t, "id", _extract(t, "task_id", ""))),
        ),
    )
    n_tasks = len(sorted_tasks)
    if n_tasks == 0:
        return []

    milestone_span = (milestone_target - milestone_start).days + 1

    scheduled_tasks: list[ScheduledTask] = []

    # Check if multi-week alignment is feasible
    first_mon = milestone_start - timedelta(days=milestone_start.weekday())
    last_sun = milestone_target + timedelta(days=(6 - milestone_target.weekday()))
    n_weeks = max(1, ((last_sun - first_mon).days // 7) + 1)
    use_weekly_rhythm = (milestone_span >= 14) and (n_weeks > 1)

    for j, raw_t in enumerate(sorted_tasks):
        t_id = _extract(raw_t, "id", _extract(raw_t, "task_id"))
        t_title = str(_extract(raw_t, "title", ""))
        t_order = int(_extract(raw_t, "order_index", j))
        t_priority = str(_extract(raw_t, "priority", "medium") or "medium")
        t_status = str(_extract(raw_t, "status", "pending") or "pending")
        t_orig_start = _to_date(_extract(raw_t, "start_date"))
        t_orig_target = _to_date(_extract(raw_t, "target_date"))

        # Preservation rule: if task is already completed and has dates, keep them unchanged
        if t_status == "completed" and (t_orig_start is not None or t_orig_target is not None):
            t_start = t_orig_start
            t_target = t_orig_target
        elif milestone_span <= 1:
            t_start = milestone_start
            t_target = milestone_target
        elif n_tasks == 1:
            t_start = milestone_start
            t_target = milestone_target
        elif use_weekly_rhythm:
            # Assign task to week index/range
            start_week = min(n_weeks - 1, (j * n_weeks) // n_tasks)
            end_week = min(n_weeks - 1, ((j + 1) * n_weeks) // n_tasks - 1)
            end_week = max(start_week, end_week)

            w_mon = first_mon + timedelta(weeks=start_week)
            w_sun = first_mon + timedelta(weeks=end_week, days=6)

            t_start = max(milestone_start, w_mon)
            t_target = min(milestone_target, w_sun)

            # Final task always stretches to milestone target date
            if j == n_tasks - 1:
                t_target = milestone_target

            # Safety clamp: start must not exceed target
            if t_start > t_target:
                t_start = t_target
        else:
            # Daily spacing for short/dense milestones
            start_offset = (j * milestone_span) // n_tasks
            end_offset = ((j + 1) * milestone_span) // n_tasks - 1
            end_offset = max(start_offset, end_offset)
            end_offset = min(milestone_span - 1, end_offset)
            if j == n_tasks - 1:
                end_offset = milestone_span - 1

            t_start = milestone_start + timedelta(days=start_offset)
            t_target = milestone_start + timedelta(days=end_offset)

        # For non-completed tasks (or completed tasks without dates), strictly clamp within milestone bounds
        if not (t_status == "completed" and (t_orig_start is not None or t_orig_target is not None)):
            if t_start is not None:
                t_start = max(milestone_start, min(milestone_target, t_start))
            if t_target is not None:
                min_target = t_start if t_start is not None else milestone_start
                t_target = max(min_target, min(milestone_target, t_target))

            _set_if_mutable(raw_t, "start_date", t_start)
            _set_if_mutable(raw_t, "target_date", t_target)

        scheduled_tasks.append(
            ScheduledTask(
                task_id=t_id,
                title=t_title,
                order_index=t_order,
                priority=t_priority,
                status=t_status,
                start_date=t_start,
                target_date=t_target,
                raw=raw_t,
            )
        )

    return scheduled_tasks


# ---------------------------------------------------------------------------
# Core Public API
# ---------------------------------------------------------------------------


def schedule_roadmap(
    roadmap_start_date: Any = None,
    roadmap_target_date: Any = None,
    milestones: Sequence[Any] | None = None,
    *,
    roadmap: Any = None,
) -> ScheduledRoadmap:
    """Deterministically schedule a roadmap and all its milestones and tasks.

    Parameters:
    -----------
    roadmap_start_date:
        Start date of the roadmap (date or datetime), or a roadmap object/dict if
        called with a single object.
    roadmap_target_date:
        Target completion date of the roadmap (date or datetime).
    milestones:
        Ordered list/sequence of milestones (dicts, models, or objects). Each milestone
        is expected to have `order_index` and a sequence of `tasks`.
    roadmap:
        Optional roadmap object/dict alternative syntax.

    Returns:
    --------
    ScheduledRoadmap:
        Immutable structured schedule with milestone and task date boundaries populated.

    Raises:
    -------
    ValueError:
        If roadmap_start_date > roadmap_target_date.
    """
    # Support schedule_roadmap(roadmap=obj) or schedule_roadmap(roadmap_obj)
    if roadmap is not None:
        start = _to_date(_extract(roadmap, "start_date"))
        target = _to_date(_extract(roadmap, "target_date"))
        raw_milestones = list(_extract(roadmap, "milestones", []) or [])
    elif (
        roadmap_start_date is not None
        and roadmap_target_date is None
        and milestones is None
        and not isinstance(roadmap_start_date, (date, datetime))
    ):
        start = _to_date(_extract(roadmap_start_date, "start_date"))
        target = _to_date(_extract(roadmap_start_date, "target_date"))
        raw_milestones = list(_extract(roadmap_start_date, "milestones", []) or [])
    else:
        start = _to_date(roadmap_start_date)
        target = _to_date(roadmap_target_date)
        raw_milestones = list(milestones or [])

    # Rule: Missing either date returns unscheduled result without inventing dates
    if start is None or target is None:
        unscheduled_milestones: list[ScheduledMilestone] = []
        for m in raw_milestones:
            m_tasks_raw = list(_extract(m, "tasks", []) or [])
            unscheduled_tasks = [
                ScheduledTask(
                    task_id=_extract(t, "id", _extract(t, "task_id")),
                    title=str(_extract(t, "title", "")),
                    order_index=int(_extract(t, "order_index", 0)),
                    priority=str(_extract(t, "priority", "medium") or "medium"),
                    status=str(_extract(t, "status", "pending") or "pending"),
                    start_date=_to_date(_extract(t, "start_date")),
                    target_date=_to_date(_extract(t, "target_date")),
                    raw=t,
                )
                for t in m_tasks_raw
            ]
            unscheduled_milestones.append(
                ScheduledMilestone(
                    milestone_id=_extract(m, "id", _extract(m, "milestone_id")),
                    title=str(_extract(m, "title", "")),
                    order_index=int(_extract(m, "order_index", 0)),
                    status=str(_extract(m, "status", "pending") or "pending"),
                    start_date=_to_date(_extract(m, "start_date")),
                    target_date=_to_date(_extract(m, "target_date")),
                    tasks=unscheduled_tasks,
                    raw=m,
                )
            )
        return ScheduledRoadmap(
            start_date=start,
            target_date=target,
            milestones=unscheduled_milestones,
        )

    # Rule: Start must not be after target
    if start > target:
        raise ValueError("roadmap_start_date must not be after roadmap_target_date")

    # Edge case: zero milestones
    if len(raw_milestones) == 0:
        return ScheduledRoadmap(
            start_date=start,
            target_date=target,
            milestones=[],
        )

    # Sort milestones strictly by order_index ascending (stable sort)
    sorted_milestones = sorted(
        raw_milestones,
        key=lambda m: (
            _extract(m, "order_index", 0),
            str(_extract(m, "id", _extract(m, "milestone_id", ""))),
        ),
    )

    k = len(sorted_milestones)
    total_days = (target - start).days + 1

    # Extract task counts per milestone
    milestone_task_lists = [list(_extract(m, "tasks", []) or []) for m in sorted_milestones]
    task_counts = [len(tasks) for tasks in milestone_task_lists]

    # Allocate calendar day counts per milestone
    durations = _allocate_milestone_days(total_days, task_counts)

    # Build scheduled milestones
    scheduled_milestones: list[ScheduledMilestone] = []
    current_start = start

    for i, raw_m in enumerate(sorted_milestones):
        m_id = _extract(raw_m, "id", _extract(raw_m, "milestone_id"))
        m_title = str(_extract(raw_m, "title", ""))
        m_order = int(_extract(raw_m, "order_index", i))
        m_status = str(_extract(raw_m, "status", "pending") or "pending")
        dur = durations[i]

        m_start = current_start
        if i == k - 1:
            # Final milestone always ends strictly on roadmap_target_date
            m_target = target
        elif dur <= 1:
            m_target = m_start
        else:
            m_target = m_start + timedelta(days=dur - 1)

        # Boundary check
        m_target = min(target, max(m_start, m_target))

        _set_if_mutable(raw_m, "start_date", m_start)
        _set_if_mutable(raw_m, "target_date", m_target)

        # Schedule tasks within this milestone's window
        scheduled_tasks = _schedule_tasks_in_milestone(
            milestone_start=m_start,
            milestone_target=m_target,
            tasks_input=milestone_task_lists[i],
        )

        scheduled_milestones.append(
            ScheduledMilestone(
                milestone_id=m_id,
                title=m_title,
                order_index=m_order,
                status=m_status,
                start_date=m_start,
                target_date=m_target,
                tasks=scheduled_tasks,
                raw=raw_m,
            )
        )

        # Next milestone starts contiguously on the following day (or same day if compressed)
        if m_target < target:
            current_start = m_target + timedelta(days=1)
        else:
            current_start = target

    return ScheduledRoadmap(
        start_date=start,
        target_date=target,
        milestones=scheduled_milestones,
    )
