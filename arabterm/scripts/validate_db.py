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
not shared by two dictionaries. Likewise for the domains: every dictionary must
have one, but whether they are the ones Wikidata gives it (P921) is the job of
sync_domains.py, which does read the network and is run by hand.
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
# A domain's slug goes into URLs (`?domain=…`) and CSS classes as it is.
SLUG_RE = re.compile(r"[a-z][a-z0-9_]*")
# An archive.org item, or one file of a multi-volume item, as the page links
# need it: no /page/ or /mode/ of its own, no query, no trailing slash.
ARCHIVE_ORG_URL_RE = re.compile(
    r"https://archive\.org/details/[A-Za-z0-9][A-Za-z0-9._-]*(/[^/?#\s]+)?"
)

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


def check_archive_org_url_invalid(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        "SELECT name_tech, archive_org_url FROM dictionary"
        " WHERE archive_org_url IS NOT NULL"
    )
    return {
        slug: f"archive_org_url={url!r} is not an archive.org/details/ URL"
        for slug, url in rows
        if not ARCHIVE_ORG_URL_RE.fullmatch(url)
    }


def check_page_offset_without_url(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        "SELECT name_tech, page_offset FROM dictionary"
        " WHERE page_offset IS NOT NULL AND archive_org_url IS NULL"
    )
    return {
        slug: f"page_offset={offset} but no archive_org_url" for slug, offset in rows
    }


def check_page_offset_missing(con: sqlite3.Connection) -> Violations:
    """A scan and page numbers without the offset: no page could be linked."""
    rows = con.execute(
        """
        SELECT name_tech FROM dictionary d
        WHERE archive_org_url IS NOT NULL AND page_offset IS NULL
          AND EXISTS (
              SELECT 1 FROM term t WHERE t.dictionary_id = d.id AND t.page IS NOT NULL
          )
        """
    )
    return {
        slug: "archive_org_url and term pages are set, but not page_offset"
        for (slug,) in rows
    }


def check_dictionary_without_domain(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        """
        SELECT name_tech FROM dictionary d
        WHERE NOT EXISTS (
            SELECT 1 FROM dictionary_domain dd WHERE dd.dictionary_id = d.id
        )
        """
    )
    return {slug: "no domain — run `make sync_domains`" for (slug,) in rows}


def check_dictionary_domain_orphan(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        """
        SELECT dd.dictionary_id, dd.domain_id, d.id IS NULL, dm.id IS NULL
        FROM dictionary_domain dd
        LEFT JOIN dictionary d ON d.id = dd.dictionary_id
        LEFT JOIN domain dm ON dm.id = dd.domain_id
        WHERE d.id IS NULL OR dm.id IS NULL
        """
    )
    return {
        f"dictionary_{dict_id}_domain_{domain_id}": " and ".join(
            what
            for what, missing in (
                (f"dictionary_id={dict_id}", no_dict),
                (f"domain_id={domain_id}", no_domain),
            )
            if missing
        )
        + " does not exist"
        for dict_id, domain_id, no_dict, no_domain in rows
    }


def check_domain_invalid(con: sqlite3.Connection) -> Violations:
    """Slug, names and QID of a domain; the key is its id, the one column
    that cannot be wrong."""
    rows = con.execute(
        "SELECT id, name_tech, name_arabic, name_english, wikidata_id FROM domain"
    ).fetchall()
    qid_count: dict[str, int] = {}
    for *_, qid in rows:
        qid_count[qid] = qid_count.get(qid, 0) + 1
    violations: Violations = {}
    for domain_id, slug, arabic, english, qid in rows:
        problems = []
        if not SLUG_RE.fullmatch(slug or ""):
            problems.append(f"name_tech={slug!r} is not a slug (a-z, 0-9, _)")
        if not (arabic or "").strip():
            problems.append("name_arabic is empty")
        if not (english or "").strip():
            problems.append("name_english is empty")
        if not QID_RE.fullmatch(qid or ""):
            problems.append(f"wikidata_id={qid!r} is not a QID")
        elif qid_count[qid] > 1:
            problems.append(f"{qid} is used by more than one domain")
        if problems:
            violations[f"domain_{domain_id}"] = "; ".join(problems)
    return violations


def check_domain_unused(con: sqlite3.Connection) -> Violations:
    rows = con.execute(
        """
        SELECT name_tech FROM domain dm
        WHERE NOT EXISTS (
            SELECT 1 FROM dictionary_domain dd WHERE dd.domain_id = dm.id
        )
        """
    )
    return {slug: "no dictionary has this domain" for (slug,) in rows}


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
        "dictionary_archive_org_url_invalid": check_archive_org_url_invalid(con),
        "dictionary_page_offset_without_url": check_page_offset_without_url(con),
        "dictionary_page_offset_missing": check_page_offset_missing(con),
        "dictionary_without_domain": check_dictionary_without_domain(con),
        "dictionary_domain_orphan": check_dictionary_domain_orphan(con),
        "domain_invalid": check_domain_invalid(con),
        "domain_unused": check_domain_unused(con),
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
