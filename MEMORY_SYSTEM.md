# NOVI Memory & Recall System

This document explains how NOVI stores and recalls information about a student
across its 4-year high school journey (Grades 9–12), how the pieces fit
together, where the data lives, and how to operate/maintain it.

---

## 1. High-level architecture

```
 Student message
      │
      ▼
 Backend (FastAPI, backend/app/main.py) ──▶ Letta agent (Postgres + archival/vector store)
      │                                        │ (LLM: Gemini)
      │                                        ▼
      │                              Letta agent tries to respond.
      │                              (Gemini 3.x can't run Letta's tool loop,
      │                               so this step falls back — see below)
      │
      ├──▶ Recall: search Letta archival memory (semantic search)
      │         and inject relevant facts into the prompt
      │
      ├──▶ Generate reply (Gemini) using recalled facts
      │
      ├──▶ Store: extract new durable facts → insert into archival memory (deduped)
      │         update core memory "human" block with latest profile
      │
      └──▶ Every 3 messages: extract Career DNA → MySQL
```

**Key design decision (2026-08):** The Letta agent is configured with Gemini
3.x as its LLM. Google has deprecated the legacy `function` message role that
Letta's tool-calling loop uses, and older Gemini models that supported it
(e.g. `gemini-2.5-flash`) are no longer available to new keys. As a result,
**the Letta agent cannot execute its own memory tools**. Instead, the
**backend performs recall + storage directly** (searching/inserting archival
memory and updating core memory), and uses Gemini for the actual reply. This
delivers the full recall goal reliably without depending on Letta's agent loop.

---

## 2. Where information is stored

| Data | Location | How to see it |
|---|---|---|
| **Archival memory** (long-term durable facts, vector-embedded for semantic search) | Letta Postgres: `novi_letta_db` → table `archival_passages` | `GET http://localhost:8283/v1/agents/{agent_id}/archival-memory` |
| **Core memory** (always-on "human" profile block) | Letta Postgres: table `block` | `GET http://localhost:8283/v1/agents/{agent_id}/core-memory` |
| **Chat transcripts** | Letta Postgres: table `messages` | `GET http://localhost:8283/v1/agents/{agent_id}/messages` |
| **Agent → tools mapping** | Letta Postgres: table `tools_agents` | `GET .../v1/agents/{agent_id}/tools` |
| **Career DNA / goals / passport** | MySQL `novi_db` (tables `career_dna`, `goals`, ...) | see `backend/app/api/career_dna.py` |
| **App users + `letta_agent_id` link** | MySQL `novi_db` table `users` | |

### Docker volumes (physical persistence)
- `<project>_letta_pg_data` → Postgres data (all memory)
- `<project>_letta_data` → Letta app config/logs (`/root/.letta`)
- These live inside the Docker Desktop VM at
  `/var/lib/docker/volumes/<name>/_data` (not directly browsable in Finder
  on macOS — use the psql/docker commands below).

---

## 3. How recall works

When a student sends a message, `LettaService.send_message`:

1. Runs a **semantic search** over the student's archival memory using the
   message as the query (`search_archival_memory`).
2. Injects the top results into the prompt as an **`=== ARCHIVAL MEMORY ===`**
   block so the reply is personalized with facts from any earlier grade/session.
3. Sends the message through Letta; if Letta's agent errors (which it does with
   Gemini 3.x), the backend **falls back to Gemini direct** with the recalled
   facts already in context.

This is how NOVI "remembers" a student across conversations and across grades
without the student having to repeat themselves.

---

## 4. How storage works

After each message, the backend (`backend/app/main.py`) performs two writes:

### 4a. Core memory (always-on profile)
`auto_update_memory` → `GeminiService.extract_student_profile` produces the
current one-line profile (`Name / Grade / School / Career Goal / Interests /
Skills / Motivations / Preferred Roles / Learning Style`) and writes it to the
agent's `human` memory block via `update_memory_block`.

### 4b. Archival memory (durable facts) — with dedup
`GeminiService.extract_archival_facts` extracts up to 5 new durable facts from
the recent conversation, keeping phrasing that can be semantically searched.
Each fact is inserted via `insert_archival_memory`, which:

- **Deduplicates** — both exact and *near-duplicate* facts are skipped
  (rephrased versions like "User loves to eat bread" vs "User loves eating
  bread" are caught via light stemming + normalized word-overlap).
- **Tags by grade** — facts are tagged `["student", f"grade{grade}"]` so
  multi-year facts remain attributable to the grade in which they were learned.

---

## 5. Caching (added to reduce per-message overhead)

`LettaService` uses two in-process caches so we don't hit Letta's API
unnecessarily on every message:

| Cache | What it skips | TTL |
|---|---|---|
| `_archival_cache` | Re-fetching all archival passages (used by dedup + existing-text check) | 30 s, invalidated on insert |
| `_upgrade_ok` | Re-fetching agent tools + catalog (tool upgrade only needs to happen once) | 30 min |

The **recall search** itself is *not* cached — it must run fresh each message.

There is **no persistence** of these caches; restarting the backend clears them
and they repopulate lazily.

---

## 6. Operational commands

### Start / restart the backend
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app    # uvicorn on port 8000
```
Kill an existing backend first: `lsof -t -iTCP:8000 -sTCP:LISTEN | xargs kill`

### View a student's memory (archival + core)
```bash
AID=<agent_id>          # e.g. agent-4ecca7c9-b120-478c-9a74-e84d3cb2a240
TOKEN="$(grep LETTA_API_KEY backend/.env | cut -d= -f2)"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8283/v1/agents/$AID/archival-memory"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8283/v1/agents/$AID/core-memory"
```

### Raw DB (Postgres / Letta memory)
```bash
docker exec -it novi_letta_db psql -U novi_user -d letta
```
```sql
\dt
SELECT left(text,80), tags FROM archival_passages;
SELECT label, left(value,150) FROM block;
SELECT id, name FROM agents;
```

### Raw DB (Career DNA / MySQL)
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p novi_db
SELECT user_id, interests, career_zones FROM career_dna;
```

### Clean up duplicates + backfill grade tags
```bash
cd backend
source ../venv/bin/activate
python scripts/memory_cleanup.py --dry-run   # preview what would be removed
python scripts/memory_cleanup.py             # actually delete duplicates
python scripts/memory_cleanup.py --retag     # also backfill gradeN tags
```
Run it after introducing new students or if you ever notice duplicate facts.

---

## 7. Updating the Gemini API key

The key is read at process start from two places — **keep both in sync**:

1. `backend/.env` → `GEMINI_API_KEY` (used by the backend's Gemini calls)
2. Root `.env` → `GEMINI_API_KEY` (injected into the `novi_letta` container via
   `docker-compose.yml`; the `${GEMINI_API_KEY}` substitution reads this file)

After changing the key, restart both:
```bash
# 1. Restart the letta container with the new key (DB/data is preserved)
docker compose up -d letta

# 2. Restart the backend
lsof -t -iTCP:8000 -sTCP:LISTEN | xargs kill; cd backend && source ../venv/bin/activate && python main.py &
```

Note: the Letta agent's own agent-loop tool calls will still fail against
Gemini 3.x (see §1). The backend reliably handles recall/storage instead.

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `402 Payment Required` / `429 RESOURCE_EXHAUSTED` from Letta | Stale/expired Gemini key in the container | Update **both** `.env` files, `docker compose up -d letta`, restart backend |
| `400 INVALID_ARGUMENT ... Role 'function' is not supported` | Gemini 3.x doesn't support Letta's tool-call role (expected) | Not an error to fix — backend falls back to Gemini direct; see §1 |
| Duplicate facts appearing | Facts added before dedup was deployed | Run `python scripts/memory_cleanup.py --retag` |
| Missing grade tags | Facts stored before grade-tagging existed | Run `python scripts/memory_cleanup.py --retag` |
| Backend won't start | Port 8000 in use | `lsof -t -iTCP:8000 -sTCP:LISTEN \| xargs kill` then start again |

---

## 9. Current student agents (reference)

| Student | Letta agent_id | Grade |
|---|---|---|
| Prateek Kushwaha | `agent-4ecca7c9-b120-478c-9a74-e84d3cb2a240` | 10 |
| Final Test | `agent-ca45c295-786e-48c9-b8d4-1e8fe603445d` | 10 |
| arnab goswami | `agent-fde044ea-b928-4bd9-a426-5c7bc74154f8` | 9 |
| Test Archival | `agent-08117a94-20ba-49ea-b1c3-43a4c662a65e` | 10 |

You can also look up any user's agent via MySQL: `SELECT id, letta_agent_id FROM users;`
