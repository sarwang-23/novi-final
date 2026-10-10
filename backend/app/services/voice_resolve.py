"""Turn a spoken onboarding answer into a valid step value.

Matches the user's transcript against a step's options locally (exact /
substring) first; if nothing confident matches, ask the shared Gemini
provider once to pick from the exact option strings. Never returns a value
that is not one of step.options (for single/multi steps).
"""

import json
from dataclasses import dataclass

from app.services.providers import gemini


@dataclass
class Step:
    """Minimal onboarding step surface voice resolution needs (engine-agnostic)."""

    id: str
    question: str
    kind: str  # single | multi | free
    options: list[str] | None = None

# Short or catch-all options that would match far too much text as substrings.
_SUBSTRING_IGNORE = {
    "other",
    "some other",
    "something else",
    "none really",
    "not yet",
    "maybe",
    "no idea",
}

MATCHER_SYSTEM = (
    "You map a spoken, freeform answer to one of the allowed onboarding "
    "options. You never invent options and never output an option the user "
    "did not say."
)


async def resolve_answer(step: Step, transcript_text: str):
    """Resolve `transcript_text` to a valid answer for `step`.

    Returns a str (single/free), a list[str] (multi), or None when nothing
    maps to a valid option.
    """
    text = (transcript_text or "").strip()
    if step.kind == "free":
        return text or None
    if not step.options:
        return text or None

    local = _match_local(step, text)
    if local is not None and local != []:
        return local

    return await _match_with_llm(step, text)


def _match_local(step: Step, text: str) -> str | list[str] | None:
    lowered = {str(o).lower(): o for o in step.options}
    hay = text.lower()

    exact: list[str] = []
    seen = set()
    for t in _tokens(text):
        canonical = lowered.get(t.strip().lower())
        if canonical is not None and canonical not in seen:
            exact.append(canonical)
            seen.add(canonical)

    extra: list[str] = []
    for option, canonical in lowered.items():
        if canonical in seen:
            continue
        if _substringable(option) and option in hay:
            extra.append(canonical)
            seen.add(canonical)

    if step.kind == "single":
        if exact:
            return exact[0]
        if len(extra) == 1:
            return extra[0]
        return None

    combined = exact + extra
    return combined or None


def _substringable(option: str) -> bool:
    return len(option) >= 4 and option not in _SUBSTRING_IGNORE


def _tokens(text: str) -> list[str]:
    out = [text]
    for sep in (",", ";", " and "):
        expanded = []
        for t in out:
            expanded.extend(part.strip() for part in t.split(sep))
        out = expanded
    return [t for t in out if t]


async def _match_with_llm(step: Step, text: str):
    options = [str(o) for o in step.options if str(o).strip()]
    prompt = (
        f"An onboarding step asked this question:\n\n{step.question}\n\n"
        f"The student answered by voice; here is the transcript:\n\n{text}\n\n"
        f"Allowed options:\n{json.dumps(options, ensure_ascii=False)}\n\n"
        'Pick the allowed option(s) that best match what the student said and '
        'return ONLY JSON of the form {"matches": ["option", ...]} where every '
        "entry is one of the allowed options, copied verbatim. "
        'If nothing matches, return {"matches": []}.'
    )
    try:
        result = await gemini.complete_json(prompt, system=MATCHER_SYSTEM)
    except Exception as exc:  # pragma: no cover - provider fallback behaviour
        print(f"[voice] resolve LLM failed: {exc}")
        return None

    matches = result.get("matches") if isinstance(result, dict) else result
    if not isinstance(matches, list):
        return None

    lowered = {str(o).lower(): o for o in step.options}
    valid = []
    for m in matches:
        canonical = lowered.get(str(m or "").strip().lower())
        if canonical is not None and canonical not in valid:
            valid.append(canonical)
    return valid[0] if step.kind == "single" and valid else (valid or None)