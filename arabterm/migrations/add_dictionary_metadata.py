"""Add `dict_type` and `tier` metadata columns to the dictionary table.

Adds two nullable columns to `dictionary` (if not already present) and
populates them from a curated spreadsheet (`list-dicts.xlsx`, not committed
to the repo) that maps each dictionary to:
  - a type: مصطلحات (terminology), لغوي (language), مكنز وب (thesaurus)
  - a tier: 1 (highest reliability) .. 5 (other/unranked)

Rows are matched to `dictionary` by `wikidata_id` first, falling back to an
exact `name_arabic` match for the handful of ArabTerm-website glossaries that
have no Wikidata QID. This metadata is consumed downstream by
forzagreen/wikitermbase for search ranking.

Usage:
    uv run --with openpyxl --env-file .env python -m arabterm.migrations.add_dictionary_metadata
    uv run --with openpyxl --env-file .env python -m arabterm.migrations.add_dictionary_metadata --apply
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import text

from arabterm.sqlite_models import get_sqlite_connection

XLSX_PATH = Path(__file__).resolve().parents[2] / "list-dicts.xlsx"

CATEGORY_MAP = {
    "مصطلحات": "terminology",
    "لغوي": "language",
    "مكنز وب": "thesaurus",
}


def load_spreadsheet_rows():
    import openpyxl

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        arabic, _english, _french, _entries, qid, _url, cat, tier = row[:8]
        if not arabic:
            continue
        if cat not in CATEGORY_MAP:
            raise ValueError(f"Unknown category {cat!r} for {arabic!r}")
        rows.append(
            {
                "arabic": arabic.strip(),
                "qid": (qid or "").strip(),
                "dict_type": CATEGORY_MAP[cat],
                "tier": tier,
            }
        )
    return rows


def ensure_columns(session) -> None:
    existing = {
        row[1] for row in session.execute(text("PRAGMA table_info(dictionary)")).all()
    }
    if "dict_type" not in existing:
        session.execute(text("ALTER TABLE dictionary ADD COLUMN dict_type TEXT"))
        print("Added column dictionary.dict_type")
    if "tier" not in existing:
        session.execute(text("ALTER TABLE dictionary ADD COLUMN tier INTEGER"))
        print("Added column dictionary.tier")
    session.commit()


def match_rows(session, rows):
    db_rows = session.execute(
        text("SELECT id, wikidata_id, name_arabic FROM dictionary")
    ).all()
    by_qid = {
        r.wikidata_id.strip(): r
        for r in db_rows
        if r.wikidata_id and r.wikidata_id.strip()
    }
    by_arabic = {r.name_arabic.strip(): r for r in db_rows if r.name_arabic}

    matched, unmatched = [], []
    for row in rows:
        db_row = by_qid.get(row["qid"]) if row["qid"] else None
        if db_row is None:
            db_row = by_arabic.get(row["arabic"])
        if db_row is None:
            unmatched.append(row)
        else:
            matched.append((db_row.id, row))

    matched_db_ids = {db_id for db_id, _ in matched}
    uncovered = [r for r in db_rows if r.id not in matched_db_ids]
    return matched, unmatched, uncovered


def apply_updates(session, matched) -> None:
    for db_id, row in matched:
        session.execute(
            text("UPDATE dictionary SET dict_type = :t, tier = :tier WHERE id = :id"),
            {"t": row["dict_type"], "tier": row["tier"], "id": db_id},
        )
    session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write updates to the database (default: preview only)",
    )
    args = parser.parse_args()

    rows = load_spreadsheet_rows()
    print(f"Loaded {len(rows)} rows from {XLSX_PATH.name}")

    with get_sqlite_connection() as session:
        matched, unmatched, uncovered = match_rows(session, rows)
        print(f"Matched {len(matched)} rows to existing dictionaries.")
        if unmatched:
            print("Unmatched spreadsheet rows (no dictionary in DB — skipped):")
            for row in unmatched:
                print(f"  - {row['arabic']} ({row['qid'] or 'no QID'})")
        if uncovered:
            print(
                "WARNING: dictionaries in DB with no spreadsheet row:", file=sys.stderr
            )
            for r in uncovered:
                print(f"  - id={r.id} {r.name_arabic}", file=sys.stderr)

        if not args.apply:
            print("Preview only. Re-run with --apply to update the database.")
            return

        ensure_columns(session)
        apply_updates(session, matched)
        print(f"Updated {len(matched)} rows.")


if __name__ == "__main__":
    main()
