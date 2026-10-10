"""One-time maintenance script to clean up Letta archival memory:
- Deduplicate near-identical passages (keeps one per distinct fact)
- Optionally backfill grade tags on remaining passages

Usage (from backend/):
    source ../venv/bin/activate
    python scripts/memory_cleanup.py [--dry-run]
"""
import os
import re
import sys
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("LETTA_BASE_URL", "http://localhost:8283")
API_KEY = os.getenv("LETTA_API_KEY", "")

DRY_RUN = "--dry-run" in sys.argv


def headers():
    return {"Authorization": f"Bearer {API_KEY}"}


def normalize(text: str) -> str:
    t = text.lower()
    for token in ("user's name is", "user is a", "user is currently in", "user is in",
                  "user loves to", "user loves", "user lives in", "user wants to",
                  "user joined", "user aspires to", "user enjoys", "user studies"):
        t = t.replace(token, " ")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    words = []
    for w in t.split():
        if len(w) > 4 and w.endswith("ing"):
            w = w[:-3]
        elif len(w) > 3 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 3 and w.endswith("es"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        words.append(w)
    return " ".join(words)


def is_near_duplicate(a: str, b: str) -> bool:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if na in nb or nb in na:
        return True
    wa, wb = set(na.split()), set(nb.split())
    if not wa or not wb:
        return False
    return (len(wa & wb) / min(len(wa), len(wb))) >= 0.8


async def get_agents(client: httpx.AsyncClient) -> list:
    r = await client.get(f"{BASE_URL}/v1/agents/", headers=headers(), timeout=30.0)
    r.raise_for_status()
    data = r.json()
    agents = data if isinstance(data, list) else data.get("agents", [])
    return [a for a in agents if a.get("id")]


async def get_archival(client: httpx.AsyncClient, agent_id: str) -> list:
    r = await client.get(f"{BASE_URL}/v1/agents/{agent_id}/archival-memory",
                         headers=headers(), timeout=30.0)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else data.get("results", [])


async def get_grade_from_human_block(client: httpx.AsyncClient, agent_id: str) -> int | None:
    try:
        r = await client.get(f"{BASE_URL}/v1/agents/{agent_id}/core-memory",
                             headers=headers(), timeout=30.0)
        r.raise_for_status()
        blocks = r.json().get("blocks", [])
        for b in blocks:
            if b.get("label") == "human":
                m = re.search(r"Grade:\s*(\d+)", b.get("value", ""))
                if m:
                    return int(m.group(1))
    except Exception as e:
        print(f"  (could not read grade for {agent_id}: {e})")
    return None


async def delete_passage(client: httpx.AsyncClient, agent_id: str, passage_id: str) -> bool:
    r = await client.delete(f"{BASE_URL}/v1/agents/{agent_id}/archival-memory/{passage_id}",
                            headers=headers(), timeout=30.0)
    return r.status_code in (200, 204)


async def process_agent(client: httpx.AsyncClient, agent: dict) -> dict:
    agent_id = agent["id"]
    passages = await get_archival(client, agent_id)
    kept = []          # (text, passage_id, tags)
    to_delete = []
    for p in passages:
        text = (p.get("text") or p.get("content") or "").strip()
        if not text:
            continue
        if any(is_near_duplicate(text, kt) for kt, _, _ in kept):
            to_delete.append(p["id"])
        else:
            kept.append((text, p["id"], p.get("tags") or []))

    grade = await get_grade_from_human_block(client, agent_id)
    return {
        "agent_id": agent_id,
        "name": agent.get("name"),
        "grade": grade,
        "total": len(passages),
        "to_delete": to_delete,
        "kept": kept,
    }


def missing_grade_tag(passage_tags: list, grade) -> bool:
    if not grade:
        return False
    expected = f"grade{grade}"
    return not any(t.startswith("grade") for t in passage_tags) or expected not in passage_tags


async def retag_as_grade(client: httpx.AsyncClient, agent_id: str, text: str, passage_id: str, tags: list, grade) -> None:
    """Re-insert a passage with a grade tag (delete the old id, post a new one)."""
    new_tags = list(tags)
    new_tags = [t for t in new_tags if not t.startswith("grade")]
    new_tags.append(f"grade{grade}") if grade else None
    r = await client.post(
        f"{BASE_URL}/v1/agents/{agent_id}/archival-memory",
        headers=headers(), json={"text": text, "tags": new_tags}, timeout=30.0)
    if r.status_code == 200:
        await delete_passage(client, agent_id, passage_id)
        print(f"  re-tagged: '{text[:60]}' -> {new_tags}")
    else:
        print(f"  re-tag FAILED for '{text[:60]}': {r.status_code}")


async def main():
    retag = "--retag" in sys.argv
    async with httpx.AsyncClient() as client:
        agents = await get_agents(client)
        print(f"Found {len(agents)} agents\n")
        total_deleted = 0
        for agent in agents:
            result = await process_agent(client, agent)
            if result["total"] == 0:
                continue
            n = result["grade"]
            tag = f"grade{n}" if n else "grade"
            print(f"\n[{result['name']}] ({result['agent_id']}) total={result['total']} "
                  f"duplicates={len(result['to_delete'])} grade={result['grade']}")
            for pid in result["to_delete"]:
                if DRY_RUN:
                    total_deleted += 1
                    print(f"  [dry-run] would delete {pid}")
                else:
                    ok = await delete_passage(client, result["agent_id"], pid)
                    print(f"  deleted {pid}: {'OK' if ok else 'FAILED'}")
                    if ok:
                        total_deleted += 1

            if retag and result["grade"]:
                for text, pid, tags in result["kept"]:
                    if missing_grade_tag(tags, result["grade"]):
                        if DRY_RUN:
                            print(f"  [dry-run] would re-tag '{text[:50]}' -> grade{result['grade']}")
                        else:
                            await retag_as_grade(client, result["agent_id"], text, pid, tags, result["grade"])

        print(f"\nDONE. {'Would delete' if DRY_RUN else 'Deleted'} {total_deleted} duplicate passages.")


if __name__ == "__main__":
    asyncio.run(main())
