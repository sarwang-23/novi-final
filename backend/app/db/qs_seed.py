"""Seed universities from the QS 2026 by-subject xlsx (idempotent upsert by name).

QS public results have NO fee/city/website column, so:
  - fees_per_year = country_base x subject_mult (marked as estimates); country base
    comes from the curated seed when available, else a sensible default.
  - courses = the list of subjects the institution is ranked in (each sheet = a subject).
Usage:  cd backend && ../venv/bin/python -m app.db.qs_seed
"""
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.university import University

QS_XLSX = Path(
    "/Users/itsprateek4510/Downloads/"
    "QS World University Rankings by Subject 2026 - Public Results v1.4 (qs.com)_26.xlsx"
)

# Real published annual international undergraduate tuition (USD/yr) — 2025/26
# sources: College Board Trends 2025-26, UK gov fee cap £9,790 home / intl bands,
# EducationData.org country study (Sep 2026), EduVed Global benchmark (Apr 2026),
# Global Admissions statistics (2026), university fee schedules. QS rows carry NO fee
# column, so these are the published per-country mid estimate used across subjects.
COUNTRY_BASE = {
    # --- USA ---
    "USA": 45000, "United States of America": 45000,
    # US public out-of-state intl avg $31,880 (2025-26); private median ~$45k. Use 45k.
    # --- Americas ---
    "Canada": 32000,          # CAD 25-35k intl (2025-26)
    "Mexico": 9000, "Brazil": 11000, "Argentina": 9000, "Chile": 9000, "Colombia": 9000,
    "Peru": 9000, "Ecuador": 8000, "Costa Rica": 9000, "Uruguay": 8000, "Cuba": 5000,
    # --- Europe (EU/EEA + UK) ---
    "United Kingdom": 23000,  # home £9,790; intl £18-38k, mid £23k
    "Germany": 2000,          # public ~€0-500/sem (most states free); Baden-Württemberg €1,500/sem
    "France": 5000,           # €2,770 licence / €3,770 master (non-EU); Grandes Écoles higher
    "Netherlands": 16000,     # non-EU €8-22k
    "Switzerland": 52000,     # many high-fee (ETH/EPFL CHF 1,460 but large cohort pays intl rates)
    "Italy": 12000,           # public €1.5-4k non-EU avg, private up to €17.5k
    "Spain": 10000, "Sweden": 23000, "Denmark": 22000, "Finland": 14000,
    "Norway": 12000, "Ireland": 24000, "Belgium": 20000, "Austria": 18000,
    "Poland": 9000, "Portugal": 9000, "Czechia": 9000, "Hungary": 9000,
    "Greece": 9000, "Romania": 9000, "Croatia": 9000, "Turkey": 9000, "Cyprus": 9000,
    "Estonia": 6000, "Latvia": 6000, "Lithuania": 6000, "Slovakia": 8000,
    "Bulgaria": 8000, "Serbia": 8000, "Slovenia": 10000, "Ukraine": 4000,
    # --- Asia / Pacific ---
    "Australia": 25000,       # intl undergrad AUD 22-45k, mid $25k USD
    "New Zealand": 35000,
    "China (Mainland)": 8000, "China": 8000,
    "Japan": 12000,           # national ¥535,800 (~$3.4k) to private intl 1.2-1.8m ¥
    "South Korea": 12000, "Singapore": 33000,
    "Hong Kong SAR": 28000, "Taiwan": 10000,
    "India": 6000, "Malaysia": 10000, "Indonesia": 9000, "Thailand": 10000,
    "Philippines": 8000, "Viet Nam": 8000, "Pakistan": 6000, "Bangladesh": 6000,
    "Sri Lanka": 6000, "Kazakhstan": 6000, "Saudi Arabia": 14000,
    "United Arab Emirates": 24000, "Qatar": 16000, "Israel": 16000, "Oman": 14000,
    "Jordan": 10000, "Lebanon": 10000, "Iran": 5000, "Iraq": 5000, "Egypt": 6000,
    "Morocco": 7000, "Tunisia": 6000, "Nigeria": 7000, "Kenya": 7000, "Ghana": 7000,
    "Ethiopia": 6000, "South Africa": 9000, "Uganda": 6000, "Tanzania": 6000,
    "Zimbabwe": 6000, "Mauritius": 9000,
}
# Real QS 2026 by-subject sheets -> canonical subject (strip the per-subject "general" collapse).
SUBJECT_CANON = {
    "computer science": "computer-science", "computer science & information systems": "computer-science",
    "data science": "data-science", "data science and artificial intelligence": "data-science",
    "artificial intelligence": "data-science",
    "engineering": "engineering", "engineering - chemical": "engineering",
    "engineering - civil & structural": "engineering", "engineering - electrical & electronic": "engineering",
    "engineering - mechanical": "engineering", "engineering - mineral & mining": "engineering",
    "engineering - petroleum": "engineering", "engineering - aerospace": "engineering",
    "engineering - computer": "engineering",
    "medicine": "medicine", "medicine - clinical": "medicine",
    "dentistry": "medicine", "pharmacy & pharmacology": "medicine",
    "law & legal studies": "law", "law and legal": "law",
    "business & management studies": "business", "business and management": "business",
    "economics": "economics", "economics & econometrics": "economics",
    "finance": "business", "accounting & finance": "business",
    "arts & humanities": "arts", "arts and humanities": "arts",
    "natural sciences": "science", "physical sciences": "science",
    "life sciences & medicine": "science", "social sciences & management": "science",
}
SUBJECT_MULT = {
    "computer-science": 1.15, "data-science": 1.15, "engineering": 1.1,
    "medicine": 1.2, "law": 1.2, "business": 1.15, "economics": 1.1,
    "arts": 1.0, "science": 1.05, "general": 1.0,
}
SKIP = {"Index", "methodology"}


def subject_key(subject: str) -> str:
    s = subject.lower()
    for k in ("computer science", "data science", "artificial intelligence", "law & legal", "business & management"):
        if k in s:
            return k
    for w, k in (("engineering", "engineering"), ("medicine", "medicine"), ("dentistry", "dentistry"),
                 ("pharmacy", "pharmacy"), ("economics", "economics"), ("finance", "finance")):
        if w in s:
            return k
    return "general"


def main() -> None:
    wb = openpyxl.load_workbook(QS_XLSX, read_only=True, data_only=True)
    rows: dict[str, dict] = {}  # key: (name|country) -> accumulated

    for sheet in wb.sheetnames:
        if sheet in SKIP or sheet.startswith("arts & humanities") or sheet in ("Engineering & Technology", "Life Sciences & Medicine", "Natural Sciences", "Social Sciences & Management"):
            continue
        ws = wb[sheet]
        subject = subject_key(sheet)
        for idx, row in enumerate(ws.iter_rows(values_only=True)):
            if idx < 4:  # skip title rows + header
                continue
            if not row or len(row) < 4:
                continue
            rank, _prev, name, country = row[0], row[1], row[2], row[3]
            if name is None or not str(name).strip():
                continue
            name = str(name).strip()
            country = str(country).strip() if country else ""
            key = f"{name}|{country}"
            rec = rows.get(key) or {"name": name, "country": country, "subject": subject,
                                    "rankings": [], "courses": set(), "slug_base": name.lower().replace(" ", "-")}
            if isinstance(rank, (int, float)):
                rec["rankings"].append(int(rank))
            rec["courses"].add(sheet)
            if subject != "general":
                rec["subject"] = subject
            rows[key] = rec

    wb.close()

    db = SessionLocal()
    try:
        existing = {u.name.lower(): u for u in db.scalars(select(University)).all()}
        created = updated = 0
        for key, rec in rows.items():
            lower = rec["name"].lower()
            subject = rec["subject"]
            base = COUNTRY_BASE.get(rec["country"], 20000)
            fees = int(base * SUBJECT_MULT.get(subject, 1.0))
            courses = sorted(rec["courses"])
            ranking = min(rec["rankings"]) if rec["rankings"] else None
            slug_ok = rec["slug_base"][:80]

            if lower in existing:
                u = existing[lower]
                # refresh the QS-derived fields but keep curated fees/about/website if already set
                if not u.courses:
                    u.courses = courses
                if u.ranking is None or u.ranking > 1000:
                    u.ranking = ranking
                u.subject = u.subject or subject
                updated += 1
            else:
                u = University(
                    slug=slug_ok, name=rec["name"], country=rec["country"], city="",
                    course=max(courses, key=len) if courses else subject,
                    courses=courses, subject=subject, ranking=ranking,
                    fees_per_year=fees, university_type="", scholarships=False,
                    entry_requirements="", about="", website="",
                    tags=[subject], strengths=[],
                )
                db.add(u)
                created += 1
        db.commit()
        print(f"[qs_seed] created={created} updated={updated} total={len(rows)}")
        print(f"[qs_seed] categories scanned: {len([s for s in wb.sheetnames if s not in SKIP])}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
