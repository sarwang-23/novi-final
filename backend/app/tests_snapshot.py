"""One-shot: verify Career DNA snapshot CRUD + delta path against the live API (port 8800).

Covers the exact user need: *progress is gradual, DNA changes across many years —
save a snapshot now, come back years later to update (label/note) or delete it.*
Run: ../venv/bin/python -m app.tests_snapshot
"""
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8800"
TOKEN = None


def call(method, path, body=None, token=None, expect=200):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        resp = urllib.request.urlopen(req, data)
        raw = resp.read().decode()
        status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        status = e.code
    parsed = json.loads(raw) if raw.strip() else None
    ok = status == expect
    print(f"[{method:6}] {path:30} -> {status}" + ("" if ok else f"  EXPECTED {expect}  ERR: {parsed}"))
    if not ok:
        raise SystemExit(1)
    return parsed


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;")


def main():
    global TOKEN
    # --- register (fresh user each run so snapshots are ours alone) ---
    email = "snap_test_" + str(int.from_bytes(__import__("os").urandom(2), "big")) + "@novi.app"
    payload = {"email": email, "password": "SnapshotTest!42", "name": "DNA Snapshot QA", "role": "student"}
    r = call("POST", "/api/auth/register", payload)
    t = r.get("access_token") or r.get("token") or (r.get("data") or {}).get("access_token")
    if not t:
        # try login path via /auth/login
        r = call("POST", "/api/auth/login", {"email": payload["email"], "password": payload["password"]}, expect=200)
        t = r.get("access_token") or r.get("token") or (r.get("data") or {}).get("access_token")
    assert t, "no token"
    TOKEN = t

    # --- seed the DNA so a snapshot has real content ---
    dna_payload = {
        "traits": ["curious", "analytical", "persistent"],
        "motivations": ["impact", "achievement"],
        "strengths": ["coding", "public speaking"],
        "development_areas": ["public speaking", "consistency"],
        "interests": ["robotics", "AI"],
        "subjects": ["maths", "physics"],
        "skills": ["python", "data analysis"],
        "career_zones": ["engineering", "research"],
        "values": ["creativity", "impact"],
        "goals": ["build an AI company"],
        "dna_filled": True,
    }
    call("PATCH", "/api/dna", dna_payload)
    call("POST", "/api/dna/reflect", {"reflection": "I love building things that help people."}, expect=200)

    # --- 1. empty at start ---
    snaps0 = call("GET", "/api/dna/snapshots")
    assert snaps0 == [], "should start empty"

    # --- 2. save first snapshot (age 14) ---
    s1 = call("POST", "/api/dna/snapshots", {"label": "My DNA · age 14", "note": "Just starting out."})
    assert s1["label"] == "My DNA · age 14"
    assert set(s1["traits"]) == set(dna_payload["traits"]), "traits frozen"
    assert s1["created_at"], "timestamp present"
    s1_id = s1["id"]

    # --- 3. years pass: DNA drifts; save second snapshot (age 19) ---
    drifted = dict(dna_payload)
    drifted["interests"] = ["robotics", "AI", "startups"]       # +startups
    drifted["skills"] = ["python", "data analysis", "ML"]       # +ML
    drifted["subjects"] = ["maths", "physics", "computer science"]  # +comp sci
    drifted["goals"] = ["build an AI company", "publish research"]   # +publish
    drifted.pop("development_areas")                            # leave one list
    call("PATCH", "/api/dna", drifted)
    s2 = call("POST", "/api/dna/snapshots", {"label": "My DNA · age 19", "note": "The startup bug bit me."})
    s2_id = s2["id"]
    d = s2.get("delta") or {}
    assert "startups" in (d.get("interests_added") or []), f"delta interests_added missing: {d}"
    assert "ML" in (d.get("skills_added") or []), f"delta skills_added missing: {d}"
    assert "computer science" in (d.get("subjects_added") or []), f"delta subjects_added missing: {d}"
    assert "publish research" in (d.get("goals_added") or []), f"delta goals_added missing: {d}"
    print("[delta] age14 -> age19 progress OK (+" + ", +".join(
        sorted(set((d.get(k) or []) for k in ("interests_added", "skills_added", "subjects_added", "goals_added")) and
            [])) + ")")

    # --- 4. list repr (chronological) ---
    all_snaps = call("GET", "/api/dna/snapshots")
    assert len(all_snaps) == 2, "two snapshots"
    assert all_snaps[0]["id"] == s1_id, "oldest first"
    assert all_snaps[0]["delta"] is None, "first snapshot has no delta (nothing before it)"

    # --- 5. years pass again: label/note editing (update) ---
    up = call("PATCH", f"/api/dna/snapshots/{s1_id}", {"label": "My DNA · age 14 (retro)", "note": "Wish I'd saved more!"})
    assert up["label"] == "My DNA · age 14 (retro)", "label updated"
    assert up["note"] == "Wish I'd saved more!", "note updated"

    # --- 6. of the many years, some snapshots no longer matter: delete one ---
    call("DELETE", f"/api/dna/snapshots/{s1_id}", expect=204)
    after_del = call("GET", "/api/dna/snapshots")
    assert len(after_del) == 1 and after_del[0]["id"] == s2_id, "only the 19yo snapshot remains"

    print("\n[PASS] snapshot save / list / delta / update / delete roundtrip green")
    print("[PASS] timeline keeps the *current* snapshot; previous one is gone but its gold lives on")


if __name__ == "__main__":
    main()
