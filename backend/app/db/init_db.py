"""Database initializer.

Usage:
    python -m app.db.init_db            # create tables (if missing) + seed catalog
    python -m app.db.init_db --reset    # DROP all app tables then recreate + seed

Run from the `backend/` directory.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import inspect, text

from app.core.database import Base, SessionLocal, engine
from app.db.run_migrations import run_migrations
from app import models  # noqa: F401  (registers all tables on Base.metadata)


def init_db(reset: bool = False) -> None:
    if reset:
        inspector = inspect(engine)
        names = inspector.get_table_names()
        with engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for name in names:
                conn.execute(text(f"DROP TABLE IF EXISTS `{name}`"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print(f"[init_db] dropped {len(names)} tables")

    Base.metadata.create_all(bind=engine)
    print("[init_db] tables ready")

    from app.m3.db.models import Base as M3Base  # noqa: F401  (module-3 models)

    M3Base.metadata.create_all(bind=engine)
    print("[init_db] module-3 tables ready")

    run_migrations()

    from app.db.seeds import seed

    with SessionLocal() as db:
        created = seed(db)
        print(f"[init_db] seeded: careers={created['careers']}, universities={created['universities']}")

    from app.db.seed_onboarding import seed_onboarding

    with SessionLocal() as db:
        onboarding = seed_onboarding(db)
        print(f"[init_db] seeded: countries={onboarding['countries']}, "
              f"curriculums={onboarding['curriculums']}, "
              f"grades={onboarding['grades']}, subjects={onboarding['subjects']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize (or reset) the NOVI database")
    parser.add_argument("--reset", action="store_true", help="Drop existing app tables first")
    args = parser.parse_args()
    init_db(reset=args.reset)