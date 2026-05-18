"""Fix Arabic terms stored as reversed Unicode Presentation Forms.

Some `at_*` dictionaries were ingested from PDFs in visual layout order using
Arabic Presentation Forms-B (FE70-FEFF) instead of base Arabic letters
(0600-06FF). NFKC normalisation collapses the presentation forms to base
letters; reversing then restores logical order. Example: term id=72141 has
arabic='ﺔﺼﺧر' which becomes 'رخصة'.

Detection is restricted to Presentation Forms-B because Presentation Forms-A
(FB50-FDFF) contains legitimate Persian/Urdu typography letters (e.g. ﭽ U+FBED,
ﭭ U+FBAD) used in transliteration. For mixed-script rows (Latin + Arabic), we
require a run of ≥3 consecutive PF-B chars to qualify as real corruption —
this distinguishes truly-corrupted rows like id=72222 ("EquiTool ﺆﻓﺎﻜﺘﻟا ةادأ")
from rows that just happen to have a stray PF-B char in otherwise-correct text
(e.g. id=88485). On a mixed-script row, the fix preserves Latin tokens in place
and reverses the order of script-runs so the visual layout becomes logical.

Usage:
    uv run --env-file .env python -m arabterm.migrations.fix_reversed_presentation_forms
    uv run --env-file .env python -m arabterm.migrations.fix_reversed_presentation_forms --apply
"""

import argparse
import csv
import re
import sys
import unicodedata

from sqlalchemy import text

from arabterm.sqlite_models import get_sqlite_connection

PRESENTATION_FORMS_B = re.compile(r"[ﹰ-﻿]")
PF_B_RUN = re.compile(r"[ﹰ-﻿]{3,}")
LATIN = re.compile(r"[A-Za-z]")
LATIN_RUN = re.compile(r"[A-Za-z]+")

# PDF artifact: when "ال" (definite article) or "لل" (li-l-) precedes a word
# starting with a hamza-bearing letter, the lam and the next letter get swapped.
# Applied as plain string substitutions (order matters — longer patterns first).
ARTIFACT_FIXES = [
    ("األ", "الأ"),  # ا أ ل -> ا ل أ  (e.g. األغذية -> الأغذية)
    ("اإل", "الإ"),  # ا إ ل -> ا ل إ  (e.g. اإيكولوجية -> الإيكولوجية)
    ("اال", "الا"),  # ا ا ل -> ا ل ا  (e.g. االنجراف -> الانجراف)
    ("لأل", "للأ"),  # ل أ ل -> ل ل أ  (e.g. لألسرة -> للأسرة)
    ("لإل", "للإ"),  # ل إ ل -> ل ل إ  (analogous form with hamza-below)
]

EXPECTED_COUNT = 203
COUNT_TOLERANCE = 5
PREVIEW_FILE = "fix_preview.tsv"


def is_affected(s: str | None) -> bool:
    if not s or not PRESENTATION_FORMS_B.search(s):
        return False
    # Mixed-script rows need a substantial PF-B run to count as real corruption;
    # rows with one stray PF-B char in otherwise-correct text (e.g. id=88485)
    # should not be touched.
    if LATIN.search(s):
        return bool(PF_B_RUN.search(s))
    return True


def reverse_arabic(seg: str) -> str:
    fixed = unicodedata.normalize("NFKC", seg)[::-1]
    for wrong, right in ARTIFACT_FIXES:
        fixed = fixed.replace(wrong, right)
    return fixed


def fix_segment(seg: str) -> str:
    # Split into alternating non-Latin and Latin tokens (capturing group keeps
    # the Latin runs in the result). Reverse each non-Latin token, then reverse
    # the token order so visual layout becomes logical layout. For pure-Arabic
    # input the split returns a single token and this reduces to a plain
    # NFKC + reverse.
    tokens = LATIN_RUN.split(seg)
    latins = LATIN_RUN.findall(seg)
    out = []
    for i, non_latin in enumerate(tokens):
        out.append(reverse_arabic(non_latin))
        if i < len(latins):
            out.append(latins[i])
    return "".join(reversed(out)).strip()


def fix(s: str) -> str:
    # Split on `;` so semicolon-separated synonyms keep their order
    # (reversing the whole string would flip them).
    parts = [p.strip() for p in s.split(";")]
    fixed = [fix_segment(p) for p in parts if p]
    return "; ".join(fixed)


def fetch_candidates(session):
    return session.execute(
        text(
            "SELECT t.id, t.arabic, t.english, t.french, d.name_tech "
            "FROM term t JOIN dictionary d ON d.id = t.dictionary_id "
            r"WHERE d.name_tech LIKE 'at\_%' ESCAPE '\' "
            "AND t.arabic IS NOT NULL"
        )
    ).all()


def fetch_affected(session):
    return [r for r in fetch_candidates(session) if is_affected(r.arabic)]


def write_preview(affected) -> None:
    with open(PREVIEW_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["id", "dictionary", "before", "after", "english", "french"])
        for r in affected:
            w.writerow([r.id, r.name_tech, r.arabic, fix(r.arabic), r.english or "", r.french or ""])
    print(f"Wrote preview to {PREVIEW_FILE} ({len(affected)} rows).")


def apply_fixes(session, affected) -> int:
    for r in affected:
        session.execute(
            text("UPDATE term SET arabic = :a WHERE id = :id"),
            {"a": fix(r.arabic), "id": r.id},
        )
    session.commit()
    return len(affected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Write fixes to the database (default: preview only)"
    )
    args = parser.parse_args()

    with get_sqlite_connection() as session:
        affected = fetch_affected(session)
        print(f"Found {len(affected)} affected rows in at_* dictionaries.")

        # Allow finding fewer than expected (DB may be partially fixed already),
        # but never more — that would signal scope drift.
        if len(affected) > EXPECTED_COUNT + COUNT_TOLERANCE:
            print(
                f"ERROR: expected at most {EXPECTED_COUNT + COUNT_TOLERANCE} rows, "
                f"got {len(affected)}. Investigate before applying.",
                file=sys.stderr,
            )
            sys.exit(1)

        if not args.apply:
            write_preview(affected)
            print("Re-run with --apply to update the database.")
            return

        n = apply_fixes(session, affected)
        print(f"Updated {n} rows.")


if __name__ == "__main__":
    main()
