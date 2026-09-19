"""Validate the data invariants of arabterm.db.

Run by `make validate` and by the `validate-db` GitHub workflow. It uses only
the standard library, so CI needs neither `uv sync` nor a `.env` file.

Every check produces a set of violation keys: a `term.id` for term checks, a
`dictionary.name_tech` for dictionary checks. The keys are compared with the
known violations recorded in `validation_baseline.json`:

- a violation that is not in the baseline is an error: new bad data;
- a baseline entry that no longer violates is an error too: it was fixed, so it
  must be removed from the baseline, or it could silently come back later.

`--update-baseline` rewrites the baseline from the current database. The diff
of that file is then reviewed in the pull request like any other change.

The checks only read arabterm.db: nothing is fetched from the network, so the
result depends on the pull request alone. In particular, whether a QID is the
*right* Wikidata item is not checked here — only that it is well formed and
not shared by two dictionaries.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB = REPO_ROOT / "arabterm.db"
BASELINE = Path(__file__).resolve().with_name("validation_baseline.json")

QID_RE = re.compile(r"Q[1-9]\d*")

# Tab, LF, CR, space, no-break space: a value made only of these is empty.
BLANK = "char(9, 10, 13, 32, 160)"

Violations = dict[str, str]  # violation key -> human-readable detail


def _missing(column: str) -> str:
    return f"({column} IS NULL OR trim({column}, {BLANK}) = '')"


def check_term_missing(
    con: sqlite3.Connection, column: str, exempt: list[str]
) -> Violations:
    shown = [c for c in ("arabic", "english", "french") if c != column]
    placeholders = ", ".join("?" * len(exempt))
    rows = con.execute(
        f"""
        SELECT t.id, d.name_tech, t.{shown[0]}, t.{shown[1]}
        FROM term t JOIN dictionary d ON d.id = t.dictionary_id
        WHERE {_missing("t." + column)} AND d.name_tech NOT IN ({placeholders})
        """,
        exempt,
    )
    return {
        str(term_id): f"{slug}: {shown[0]}={a!r} {shown[1]}={b!r}"
        for term_id, slug, a, b in rows
    }


def check_term_orphan(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        """
        SELECT t.id, t.dictionary_id
        FROM term t LEFT JOIN dictionary d ON d.id = t.dictionary_id
        WHERE d.id IS NULL
        """
    )
    return {
        str(term_id): f"dictionary_id={dict_id} does not exist"
        for term_id, dict_id in rows
    }


def check_nbr_entries(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        """
        SELECT d.name_tech, d.nbr_entries, count(t.id)
        FROM dictionary d LEFT JOIN term t ON t.dictionary_id = d.id
        GROUP BY d.id
        HAVING d.nbr_entries IS NOT count(t.id)
        """
    )
    return {
        slug: f"nbr_entries={declared} but {actual} term rows"
        for slug, declared, actual in rows
    }


def check_wikidata_id_invalid(con: sqlite3.Connection) -> Violations:
    rows = con.execute("SELECT name_tech, wikidata_id FROM dictionary")
    return {
        slug: f"wikidata_id={qid!r} is not a QID"
        for slug, qid in rows
        if not QID_RE.fullmatch(qid or "")
    }


def check_wikidata_id_duplicate(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        """
        SELECT name_tech, wikidata_id FROM dictionary
        WHERE wikidata_id IN (
            SELECT wikidata_id FROM dictionary
            WHERE wikidata_id IS NOT NULL
            GROUP BY wikidata_id HAVING count(*) > 1
        )
        """
    )
    return {slug: f"{qid} is used by more than one dictionary" for slug, qid in rows}


def run_checks(
    con: sqlite3.Connection, exempt: dict[str, list[str]]
) -> dict[str, Violations]:
    return {
        "term_missing_english": check_term_missing(
            con, "english", exempt.get("term_missing_english", [])
        ),
        "term_missing_arabic": check_term_missing(
            con, "arabic", exempt.get("term_missing_arabic", [])
        ),
        "term_orphan": check_term_orphan(con),
        "dictionary_nbr_entries_mismatch": check_nbr_entries(con),
        "dictionary_wikidata_id_invalid": check_wikidata_id_invalid(con),
        "dictionary_wikidata_id_duplicate": check_wikidata_id_duplicate(con),
    }


def _sort_key(key: str) -> tuple[int, str]:
    return (int(key), "") if key.isdigit() else (0, key)


def _to_json(keys: list[str]) -> list[int | str]:
    return [int(k) if k.isdigit() else k for k in sorted(keys, key=_sort_key)]


def error(message: str) -> None:
    prefix = "::error::" if os.environ.get("GITHUB_ACTIONS") else "ERROR: "
    print(f"{prefix}{message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="record the current violations as the new baseline",
    )
    args = parser.parse_args()

    if not args.db.is_file():
        error(f"{args.db} is missing — run 'make db' to unpack it from arabterm.db.gz")
        return 1

    config = json.loads(args.baseline.read_text(encoding="utf-8"))
    exempt: dict[str, list[str]] = config.get("exempt", {})
    baseline: dict[str, list] = config.get("baseline", {})

    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        found = run_checks(con, exempt)
    finally:
        con.close()

    if args.update_baseline:
        for check, violations in found.items():
            baseline[check] = _to_json(list(violations))
        config["baseline"] = baseline
        args.baseline.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Baseline updated: {args.baseline}")
        return 0

    failures = 0
    for check, violations in found.items():
        known = {str(k) for k in baseline.get(check, [])}
        new = sorted(set(violations) - known, key=_sort_key)
        stale = sorted(known - set(violations), key=_sort_key)
        status = "FAIL" if new or stale else "ok"
        print(
            f"[{status:>4}] {check}: {len(violations)} found, {len(known)} in baseline"
        )
        for key in new:
            error(f"{check}: {key} — {violations[key]}")
        for key in stale:
            error(
                f"{check}: {key} is in the baseline but is no longer a violation — "
                "remove it (--update-baseline)"
            )
        failures += len(new) + len(stale)

    if failures:
        print(
            f"\n{failures} problem(s). Fix the data in arabterm.db, or, for a "
            "violation that is accepted, record it with "
            "`make validate_update_baseline` and commit the baseline."
        )
        return 1
    print("\narabterm.db is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
