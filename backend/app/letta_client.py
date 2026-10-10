"""Official letta-client SDK wrapper for the self-hosted LettA server.

- ``letta`` — shared client pointing at ``settings.LETTA_BASE_URL``.
- ``create_student_agent`` — one LettA agent per student, pre-wired with the
  onboarding tools + the secrets the tools need to reach the backend.
- ``send_onboarding_message`` — forwards the student's raw answer to the agent
  and returns its short reply text (or nothing if LettA is unreachable). The
  durable extraction/completion step is handled by the onboarding router
  (LettA's own agent loop can't reliably run tools against Gemini 3.x — see
  MEMORY_SYSTEM.md §1 — so the router never blocks on it).
"""

import logging
import os
from typing import Any

try:
    from letta_client import Letta, MessageCreate

    LETTA_SDK_AVAILABLE = True
except ImportError:
    # letta-client is an optional integration (the LettA server itself is
    # optional too). Keep the app importable even when the SDK isn't installed
    # — onboarding just degrades to the deterministic path, exactly as it does
    # when the LettA server is unreachable.
    LETTA_SDK_AVAILABLE = False
    Letta = None
    MessageCreate = None

from app.core.config import settings

logger = logging.getLogger("novi.letta")

letta = Letta(base_url=settings.LETTA_BASE_URL) if LETTA_SDK_AVAILABLE else None

# Model handle for the onboarding agents. Google Gemini keeps everything on the
# GEMINI_API_KEY the repo already maintains (no Anthropic key required).
# Override via LETTA_AGENT_MODEL if you need a different Google handle.
LETTA_MODEL = os.getenv("LETTA_AGENT_MODEL", "google_ai/gemini-3.6-flash")

NOVI_PERSONA = """
You are Novi, an onboarding assistant getting to know a student for the first time.

You are only ever invoked for specific, narrow extraction tasks during onboarding —
you are not running the whole conversation, and you must not ask multiple questions
at once or invent new questions.

Rules you must always follow:
- When the student describes a university and/or location, call save_university_interest.
  Extract only what is actually stated. If the country or exact location is not clear,
  leave it null and set confidence to "low" rather than guessing.
- When the student describes a career they're interested in and why, call
  save_career_interest with both the career name and a short (<200 char) summary of
  their stated reason. Do not judge, rank, or recommend the career.
- When the student describes what they'd want help with, call save_primary_goal with
  a short summary in their own words, not a rewritten generic goal.
- Never fabricate a value you were not given. Never produce a personality score or
  label. Never ask a follow-up question — a human-authored question always comes next.
- Keep any reply short (1 sentence) and warm — it will be shown as Novi's transition
  line before the next question, not as open conversation.
"""


def create_student_agent(student_id: str) -> str:
    """Create (or return) the LettA agent for a student and return its id.

    The agent is named ``novi-student-<id>``, carries the Novi persona + a
    student profile memory block, and is granted exactly the three onboarding
    tools. The tool secrets (callback URL, shared secret, student id) are stored
    as agent environment variables so the registered tools can reach the
    backend's internal endpoints.

    Raises if the letta-client SDK is missing or LettA is unreachable / rejects
    the request; callers decide how to react (onboarding degrades gracefully to
    the deterministic path).
    """
    if not LETTA_SDK_AVAILABLE or letta is None:
        raise RuntimeError(
            "letta-client SDK is not installed — run `pip install -r backend/requirements.txt` "
            "in the project venv to enable LettA onboarding agents"
        )
    agent = letta.agents.create(
        name=f"novi-student-{student_id}",
        model=LETTA_MODEL,
        embedding="letta/letta-free",
        memory_blocks=[
            {"label": "persona", "value": NOVI_PERSONA},
            {"label": "student_profile", "value": "No facts recorded yet."},
        ],
        tools=["save_university_interest", "save_career_interest", "save_primary_goal"],
        secrets={
            "INTERNAL_CALLBACK_BASE_URL": settings.INTERNAL_CALLBACK_BASE_URL,
            "INTERNAL_SHARED_SECRET": settings.INTERNAL_SHARED_SECRET,
            "STUDENT_ID": student_id,
        },
    )
    logger.info("created LettA agent %s for student %s", agent.id, student_id)
    return agent.id


def send_onboarding_message(agent_id: str, step_id: str, value: Any) -> str | None:
    """Forward one raw onboarding answer to the student's agent.

    Returns the agent's text reply (the transition line) or ``None`` when the
    letta-client SDK is missing, LettA is unreachable or produced no plain-text
    reply. Never raises — onboarding must not hard-depend on a healthy LettA
    server.
    """
    if not LETTA_SDK_AVAILABLE or letta is None:
        return None
    try:
        logger.info("sending step '%s' to LettA agent %s", step_id, agent_id)
        response = letta.agents.messages.create(
            agent_id=agent_id,
            messages=[MessageCreate(role="user", content=str(value))],
        )
        return _assistant_text(getattr(response, "data", response))
    except Exception as exc:  # LettA down, 4xx/5xx, model rejected, ... — fall back
        logger.warning("LettA agent message failed (agent=%s, step=%s): %s", agent_id, step_id, exc)
        return None


def _assistant_text(messages: Any) -> str | None:
    """Pull the first plain-text assistant line out of a LettA message list."""
    msg_list = messages.messages if hasattr(messages, "messages") else messages
    for msg in msg_list or []:
        if isinstance(msg, dict):
            if msg.get("message_type") != "assistant_message":
                continue
            content = msg.get("content") or []
            parts = [c.get("text") or "" for c in content if isinstance(c, dict) and c.get("type") == "text"]
        else:
            if getattr(msg, "message_type", None) != "assistant_message":
                continue
            content = getattr(msg, "content", None) or []
            parts = [
                (getattr(c, "text", None) or "")
                for c in content
                if getattr(c, "type", None) == "text"
            ]
        joined = " ".join(p.strip() for p in parts if p and p.strip()).strip()
        if joined:
            return joined
    return None