"""Shared singletons used across services."""

from app.llm.engine import NoviEngine
from app.llm.gemini import GeminiProvider
from app.llm.letta import LettaClient
from app.llm.memory import NoviMemory

gemini = NoviEngine()  # Gemini primary → Ollama fallback
letta = LettaClient()
memory = NoviMemory(letta=letta, gemini=gemini)


def user_context(user) -> dict:
    return {
        "name": user.display_name,
        "grade": user.grade,
        "school": user.school,
        "email": user.email,
    }


def dna_dict(dna) -> dict:
    if not dna:
        return {}
    return {
        "traits": dna.traits or [],
        "motivations": dna.motivations or [],
        "strengths": dna.strengths or [],
        "development_areas": dna.development_areas or [],
        "interests": dna.interests or [],
        "subjects": dna.subjects or [],
        "skills": dna.skills or [],
        "career_zones": dna.career_zones or [],
        "values": dna.values or [],
        "goals": dna.goals or [],
        "novi_reflection": dna.novi_reflection or "",
        "excluded": dna.excluded or [],
    }


def fallback_insight(name: str, grade: int | None, dna: dict, top_career_title: str | None) -> str:
    interests = (dna.get("interests") or [])[:2]
    zones = (dna.get("career_zones") or [])[:1]
    if top_career_title:
        return (
            f"Based on what I've learned, careers like {top_career_title} keep coming up "
            f"for {name}. Want to explore what that path actually looks like?"
        )
    if interests:
        return (
            f"I've noticed you keep gravitating toward {interests[0]}. "
            f"Let's find some careers where that can take you somewhere real."
        )
    if zones:
        return f"{zones[0]} keeps showing up in your profile — want to explore it together?"
    return f"Hi {name}! Tell me a little about what you enjoy, and I'll start mapping your future."