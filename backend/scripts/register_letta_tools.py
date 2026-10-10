"""Register the onboarding tools on the self-hosted LettA server.

Each tool POSTs the extracted fact back into the backend's internal
``/internal/onboarding/...`` routes using the agent's secrets
(INTERNAL_CALLBACK_BASE_URL / INTERNAL_SHARED_SECRET / STUDENT_ID) that were
bound to the student agent at creation time.

Idempotent: a tool already present on the server is left untouched, so re-running
this script (e.g. inside `docker compose exec`) is safe.

Usage:
    python scripts/register_letta_tools.py
"""

import json
import os
import sys
import urllib.request

from letta_client import Letta

LETTA_BASE_URL = os.environ.get("LETTA_BASE_URL", "http://localhost:8283")
letta = Letta(base_url=LETTA_BASE_URL)


def _post(route: str, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    url = f"{os.environ['INTERNAL_CALLBACK_BASE_URL']}/internal/onboarding/{os.environ['STUDENT_ID']}/{route}"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Internal-Secret": os.environ["INTERNAL_SHARED_SECRET"],
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"HTTP {resp.status}: {resp.read()[:300]}")


def save_university_interest(university_name: str, location: str, confidence: str) -> str:
    """
    Record a student's dream university.
    Args:
        university_name: The university's name as best determined from the student's text.
        location: City/country if mentioned, else "".
        confidence: "high" if unambiguous, "low" if uncertain. Defaults to "low".
    Returns:
        Confirmation string.
    """
    _post(
        "university",
        {
            "university_name": university_name,
            "location": location or "",
            "confidence": confidence or "low",
        },
    )
    return "Saved."


def save_career_interest(career_name: str, interest_reason_summary: str) -> str:
    """
    Record a student's career interest and why.
    Args:
        career_name: The career they're interested in.
        interest_reason_summary: Short (<200 char) summary of their stated reason. May be empty.
    Returns:
        Confirmation string.
    """
    _post("career", {"career_name": career_name, "interest_reason_summary": interest_reason_summary or ""})
    return "Saved."


def save_primary_goal(goal_summary: str) -> str:
    """
    Record what the student wants Novi's help with.
    Args:
        goal_summary: Short summary in the student's own words.
    Returns:
        Confirmation string.
    """
    _post("goal", {"goal_summary": goal_summary})
    return "Saved."


TOOL_FUNCTIONS = (save_university_interest, save_career_interest, save_primary_goal)


def register_tools() -> None:
    existing = {tool.name for tool in letta.tools.list()}
    for fn in TOOL_FUNCTIONS:
        if fn.__name__ in existing:
            print(f"Tool already registered, skipping: {fn.__name__}")
            continue
        tool = letta.tools.create_from_function(func=fn)
        print(f"Registered tool: {tool.name} (id={tool.id})")


if __name__ == "__main__":
    if not all(k in os.environ for k in ("INTERNAL_CALLBACK_BASE_URL", "INTERNAL_SHARED_SECRET")):
        print(
            "Missing required env vars: INTERNAL_CALLBACK_BASE_URL, INTERNAL_SHARED_SECRET "
            "(STUDENT_ID is only needed at agent runtime, not at registration)."
        )
        sys.exit(1)
    register_tools()