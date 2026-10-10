"""Nightly/weekly Student Graph snapshot + diff job.

Usage (from ``backend/``):

    python -m app.jobs.growth_snapshot            # snapshot every active student
    python -m app.jobs.growth_snapshot --user 12  # snapshot a single user id

Cron example (03:00 every day):

    0 3 * * * cd /path/to/novi_tech_app/backend && ../venv/bin/python -m app.jobs.growth_snapshot >> /tmp/novi_growth.log 2>&1

The job is idempotent per calendar day: re-running it refreshes today's snapshot
instead of creating duplicates. It never touches the core app tables.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User
from app.services import growth


def run(user_id: int | None = None) -> dict:
    processed = 0
    moved = 0
    with SessionLocal() as db:
        stmt = select(User).where(User.is_active.is_(True))
        if user_id is not None:
            stmt = stmt.where(User.id == user_id)
        else:
            stmt = stmt.where(User.role == UserRole.STUDENT)

        for user in db.scalars(stmt):
            processed += 1
            try:
                growth.sync_milestones_from_roadmap(db, user)
                snap = growth.snapshot(db, user, force=True)
                pair = growth.latest_pair(db, user)
                diff = growth.diff_snapshots(pair[1].payload, pair[0].payload) if len(pair) >= 2 else {}
                changes = len(diff.get("changed", [])) + len(diff.get("added", [])) + len(diff.get("removed", []))
                if changes:
                    moved += 1
                    print(f"[growth] user {user.id}: {changes} graph change(s) — {growth.narrative(db, user)}")
                else:
                    print(f"[growth] user {user.id}: snapshot {snap.snapshot_date} stable")
            except Exception as exc:  # one bad student must never stop the batch
                db.rollback()
                print(f"[growth] user {user.id} failed: {exc}")
    return {"processed": processed, "changed": moved}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snapshot Student Graphs and log diffs")
    parser.add_argument("--user", type=int, default=None, help="Only process this user id")
    args = parser.parse_args()
    summary = run(user_id=args.user)
    print(f"[growth] done — processed={summary['processed']} changed={summary['changed']}")
