"""Summarize the data differences between two versions of arabterm.db.

Run by the `notify-wikitermbase` GitHub workflow, which compares the database
before and after a push to `main` and sends the result to wikitermbase, where it
becomes the description of the auto-generated "refresh DB dump" pull request.

The summary is Markdown, written to stdout. Rows are matched on their primary
key; `created_at` and `updated_at` are ignored, and so is
`dictionary.nbr_entries`, which is reported as a number of terms instead.

Like validate_db.py, it uses only the standard library, so CI can run it with
plain `python3`.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

IGNORED = {
    "dictionary": {"id", "nbr_entries", "created_at", "updated_at"},
    "term": {"id", "created_at", "updated_at"},
}

# A repository_dispatch payload is limited to 64 KB: when the summary is larger
# than this, it is rendered again without the per-term details, then cut.
MAX_BYTES = 24_000
MAX_VALUE_CHARS = 200


def code(value: object) -> str:
    """Render a value as an inline code span: no autolinks, no mentions."""
    if value is None or str(value).strip() == "":
        return "_empty_"
    text = " ".join(str(value).split())
    if len(text) > MAX_VALUE_CHARS:
        text = text[:MAX_VALUE_CHARS] + "…"
    fence = "`"
    while fence in text:
        fence += "`"
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def escape(value: object) -> str:
    text = " ".join(str(value or "").split())
    for char in "\\`*_[]<>|":
        text = text.replace(char, "\\" + char)
    return text


def delta(before: int, after: int) -> str:
    if before == after:
        return f"{after} (unchanged)"
    return f"{before} → {after} ({after - before:+d})"


def columns(con: sqlite3.Connection, schema: str, table: str) -> list[str]:
    return [row[1] for row in con.execute(f"PRAGMA {schema}.table_info({table})")]


def describe_dictionary(row: sqlite3.Row, nbr_terms: int) -> str:
    keys = row.keys()
    names = [
        escape(row[c]) for c in ("name_english", "name_arabic") if c in keys and row[c]
    ]
    parts = [f"`{row['name_tech']}`", *names]
    qid = row["wikidata_id"] if "wikidata_id" in keys else None
    if qid:
        parts.append(f"[{escape(qid)}](https://www.wikidata.org/wiki/{qid})")
    parts.append(f"{nbr_terms} terms")
    return "- " + " · ".join(parts)


def summarize(con: sqlite3.Connection, max_terms: int) -> str:
    out: list[str] = ["### Data changes", ""]

    # Schema ---------------------------------------------------------------
    shared: dict[str, list[str]] = {}
    schema_changes: list[str] = []
    for table in ("dictionary", "term"):
        old_cols, new_cols = columns(con, "old", table), columns(con, "main", table)
        shared[table] = [
            c for c in new_cols if c in old_cols and c not in IGNORED[table]
        ]
        schema_changes += [
            f"- column `{table}.{c}` added" for c in new_cols if c not in old_cols
        ]
        schema_changes += [
            f"- column `{table}.{c}` removed" for c in old_cols if c not in new_cols
        ]

    # Dictionaries ---------------------------------------------------------
    old_dicts = {r["id"]: r for r in con.execute("SELECT * FROM old.dictionary")}
    new_dicts = {r["id"]: r for r in con.execute("SELECT * FROM main.dictionary")}
    old_count = dict(
        con.execute("SELECT dictionary_id, count(*) FROM old.term GROUP BY 1")
    )
    new_count = dict(
        con.execute("SELECT dictionary_id, count(*) FROM main.term GROUP BY 1")
    )
    kept = [i for i in new_dicts if i in old_dicts]

    out += [
        f"- Dictionaries: {delta(len(old_dicts), len(new_dicts))}",
        f"- Terms: {delta(sum(old_count.values()), sum(new_count.values()))}",
    ]

    added_dicts = [i for i in new_dicts if i not in old_dicts]
    if added_dicts:
        out += ["", f"#### Dictionaries added ({len(added_dicts)})", ""]
        out += [
            describe_dictionary(new_dicts[i], new_count.get(i, 0)) for i in added_dicts
        ]

    removed_dicts = [i for i in old_dicts if i not in new_dicts]
    if removed_dicts:
        out += ["", f"#### Dictionaries removed ({len(removed_dicts)})", ""]
        out += [
            describe_dictionary(old_dicts[i], old_count.get(i, 0))
            for i in removed_dicts
        ]

    changed_dicts: list[str] = []
    for i in kept:
        old, new = old_dicts[i], new_dicts[i]
        fields = [c for c in shared["dictionary"] if old[c] != new[c]]
        if fields:
            changed_dicts.append(f"- `{new['name_tech']}`")
            changed_dicts += [
                f"  - {c}: {code(old[c])} → {code(new[c])}" for c in fields
            ]
    if changed_dicts:
        out += ["", "#### Dictionaries changed", "", *changed_dicts]

    # Terms of the dictionaries present on both sides ----------------------
    # A term that moved to another dictionary counts as removed from the first
    # and added to the second, so that each dictionary's numbers add up.
    same_term = "o.id = n.id AND o.dictionary_id = n.dictionary_id"
    compared = [c for c in shared["term"] if c != "dictionary_id"]
    differs = " OR ".join(f"n.{c} IS NOT o.{c}" for c in compared) or "0"
    queries = {
        "added": f"""
            FROM main.term n LEFT JOIN old.term o ON {same_term}
            WHERE o.id IS NULL AND n.dictionary_id IN (SELECT id FROM old.dictionary)
            """,
        "removed": f"""
            FROM old.term n LEFT JOIN main.term o ON {same_term}
            WHERE o.id IS NULL AND n.dictionary_id IN (SELECT id FROM main.dictionary)
            """,
        "modified": f"""
            FROM main.term n JOIN old.term o ON {same_term}
            WHERE {differs}
            """,
    }
    counts: dict[str, dict[int, int]] = {
        kind: dict(con.execute(f"SELECT n.dictionary_id, count(*) {query} GROUP BY 1"))
        for kind, query in queries.items()
    }
    touched = [i for i in kept if any(i in counts[kind] for kind in counts)]
    if touched:
        out += [
            "",
            "#### Terms changed in existing dictionaries",
            "",
            "| Dictionary | Added | Removed | Modified |",
            "|---|---:|---:|---:|",
        ]
        out += [
            f"| `{new_dicts[i]['name_tech']}` | {counts['added'].get(i, 0)} "
            f"| {counts['removed'].get(i, 0)} | {counts['modified'].get(i, 0)} |"
            for i in touched
        ]
    if counts["modified"]:
        per_column = con.execute(
            "SELECT "
            + ", ".join(f"sum(n.{c} IS NOT o.{c})" for c in compared)
            + queries["modified"]
        ).fetchone()
        out += [
            "",
            "Modified columns: "
            + ", ".join(f"`{c}` ({n})" for c, n in zip(compared, per_column) if n),
        ]

    slug = {i: d["name_tech"] for i, d in {**old_dicts, **new_dicts}.items()}
    before_after = ", ".join(f"o.{c} AS old_{c}, n.{c} AS new_{c}" for c in compared)
    for kind, query in queries.items():
        total = sum(counts[kind].values())
        if not total or not max_terms:
            continue
        shown = before_after if kind == "modified" else "n.arabic, n.english, n.french"
        rows = con.execute(
            f"SELECT n.id, n.dictionary_id, {shown} {query} ORDER BY n.id LIMIT ?",
            (max_terms,),
        ).fetchall()
        out += ["", f"<details><summary>Terms {kind} ({total})</summary>", ""]
        for row in rows:
            head = f"- term {row['id']} (`{slug.get(row['dictionary_id'], '?')}`)"
            if kind == "modified":
                out.append(head)
                out += [
                    f"  - {c}: {code(row['old_' + c])} → {code(row['new_' + c])}"
                    for c in compared
                    if row["old_" + c] != row["new_" + c]
                ]
            else:
                out.append(f"{head}: " + " · ".join(code(v) for v in row[2:]))
        if total > len(rows):
            out.append(f"- … and {total - len(rows)} more")
        out += ["", "</details>"]

    if schema_changes:
        out += ["", "#### Schema", "", *schema_changes]

    if not (added_dicts or removed_dicts or changed_dicts or touched or schema_changes):
        out += [
            "",
            "No difference in the `dictionary` and `term` tables (timestamps aside).",
        ]

    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("old", type=Path, help="the database before the change")
    parser.add_argument("new", type=Path, help="the database after the change")
    parser.add_argument(
        "--max-terms",
        type=int,
        default=20,
        help="how many added / removed / modified terms to list (default: 20)",
    )
    args = parser.parse_args()

    for path in (args.old, args.new):
        if not path.is_file():
            print(f"ERROR: {path} is missing", file=sys.stderr)
            return 1

    con = sqlite3.connect(f"file:{args.new}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        con.execute("ATTACH DATABASE ? AS old", (f"file:{args.old}?mode=ro",))
        summary = summarize(con, args.max_terms)
        if len(summary.encode("utf-8")) > MAX_BYTES:
            summary = summarize(con, 0)
        if len(summary.encode("utf-8")) > MAX_BYTES:
            cut = summary.encode("utf-8")[:MAX_BYTES].decode("utf-8", "ignore")
            summary = cut[: cut.rindex("\n") + 1] + "\n… (truncated)\n"
    finally:
        con.close()

    sys.stdout.write(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
