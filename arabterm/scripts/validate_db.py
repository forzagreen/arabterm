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

The Wikidata checks need the network. If Wikidata cannot be reached they are
skipped with a warning instead of failing; `--offline` skips them on purpose.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB = REPO_ROOT / "arabterm.db"
BASELINE = Path(__file__).resolve().with_name("validation_baseline.json")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "arabterm-validate-db/1.0 (https://github.com/forzagreen/arabterm)"
WIKIDATA_BATCH = 50  # wbgetentities accepts at most 50 ids per request
WIKIDATA_CHECKS = ("wikidata_entity_missing", "wikidata_year_mismatch")

QID_RE = re.compile(r"Q[1-9]\d*")
YEAR_RE = re.compile(r"(?<!\d)(1[89]\d\d|20\d\d)(?!\d)")

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


def fetch_wikidata(qids: list[str]) -> dict[str, dict]:
    entities: dict[str, dict] = {}
    for start in range(0, len(qids), WIKIDATA_BATCH):
        query = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(qids[start : start + WIKIDATA_BATCH]),
                "props": "claims|info",
                "format": "json",
            }
        )
        request = urllib.request.Request(
            f"{WIKIDATA_API}?{query}", headers={"User-Agent": USER_AGENT}
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    entities.update(json.load(response)["entities"])
                break
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
                if attempt == 2:
                    raise
                time.sleep(2**attempt * 5)
    return entities


def _publication_years(entity: dict) -> set[int]:
    years = set()
    for claim in entity.get("claims", {}).get("P577", []):
        value = claim["mainsnak"].get("datavalue", {}).get("value", {})
        if "time" in value:  # e.g. "+2024-00-00T00:00:00Z"
            years.add(int(value["time"][1:5]))
    return years


def check_wikidata(con: sqlite3.Connection) -> dict[str, Violations]:
    """Cross-check each dictionary with its Wikidata item.

    The year check is what catches a QID pointing at another edition of the
    same work: the year in `name_arabic` must be one of the item's publication
    dates (P577). Dictionaries without a year in their name, and items without
    P577, are not checked.
    """
    rows = [
        (slug, name, qid)
        for slug, name, qid in con.execute(
            "SELECT name_tech, name_arabic, wikidata_id FROM dictionary"
        )
        if QID_RE.fullmatch(qid or "")
    ]
    entities = fetch_wikidata(sorted({qid for _, _, qid in rows}))

    missing: Violations = {}
    year_mismatch: Violations = {}
    for slug, name, qid in rows:
        entity = entities.get(qid, {"missing": ""})
        if "missing" in entity:
            missing[slug] = f"{qid} does not exist on Wikidata"
            continue
        if "redirects" in entity:
            missing[slug] = f"{qid} is a redirect to {entity['redirects']['to']}"
        name_years = {int(y) for y in YEAR_RE.findall(name or "")}
        wikidata_years = _publication_years(entity)
        if name_years and wikidata_years and not name_years & wikidata_years:
            year_mismatch[slug] = (
                f"{qid}: name_arabic says {sorted(name_years)} "
                f"but Wikidata publication date (P577) is {sorted(wikidata_years)}"
            )
    return {
        "wikidata_entity_missing": missing,
        "wikidata_year_mismatch": year_mismatch,
    }


def run_checks(
    con: sqlite3.Connection, exempt: dict[str, list[str]], offline: bool
) -> tuple[dict[str, Violations], list[str]]:
    """Return the violations per check, and the names of the skipped checks."""
    found = {
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
    if offline:
        return found, list(WIKIDATA_CHECKS)
    try:
        found.update(check_wikidata(con))
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as error:
        warn(f"Wikidata could not be reached, its checks are skipped: {error}")
        return found, list(WIKIDATA_CHECKS)
    return found, []


def _sort_key(key: str) -> tuple[int, str]:
    return (int(key), "") if key.isdigit() else (0, key)


def _to_json(keys: list[str]) -> list[int | str]:
    return [int(k) if k.isdigit() else k for k in sorted(keys, key=_sort_key)]


def warn(message: str) -> None:
    prefix = "::warning::" if os.environ.get("GITHUB_ACTIONS") else "WARNING: "
    print(f"{prefix}{message}")


def error(message: str) -> None:
    prefix = "::error::" if os.environ.get("GITHUB_ACTIONS") else "ERROR: "
    print(f"{prefix}{message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument(
        "--offline", action="store_true", help="skip the Wikidata checks"
    )
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
        found, skipped = run_checks(con, exempt, args.offline)
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
        if skipped:
            warn(f"Not updated, because skipped: {', '.join(skipped)}")
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
    for check in skipped:
        print(f"[skip] {check}")

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
