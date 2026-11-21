"""Align the domains of the dictionaries with Wikidata.

    python3 arabterm/scripts/sync_domains.py            # report, change nothing
    python3 arabterm/scripts/sync_domains.py --apply    # write to arabterm.db

A dictionary's domains are the values of "main subject" (P921) on its Wikidata
item. Each distinct value is one row of the `domain` table, which gives it a
slug and short names fit for a tag («رياضيات» for the item «مصطلحات الرياضيات»);
`dictionary_domain` links the dictionaries to them. This script reads P921 for
every dictionary and reports where `dictionary_domain` differs; with `--apply`
it makes the table match, and drops the domains no dictionary uses any more.

A P921 value that has no row in `domain` yet needs names that only a person
can choose, so it is never added silently: the script lists it with its
Wikidata labels and stops. Run it again with the names:

    python3 arabterm/scripts/sync_domains.py --apply \\
        --domain Q25261 meteorology "أرصاد جوية" "Meteorology" "Météorologie"

Unlike validate_db.py this script needs the network, so it is run by hand
(after adding a dictionary, or after editing P921 on Wikidata) and never in CI.
It uses only the standard library.
"""

from __future__ import annotations

import argparse
import json
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

API = "https://www.wikidata.org/w/api.php"
# Wikimedia asks every client to say what it is and where it comes from.
USER_AGENT = "arabterm-sync-domains/1.0 (https://github.com/forzagreen/arabterm)"
MAIN_SUBJECT = "P921"
BATCH = 50  # wbgetentities takes at most 50 ids per request
QID_RE = re.compile(r"Q[1-9]\d*")
SLUG_RE = re.compile(r"[a-z][a-z0-9_]*")


def api(params: dict[str, str]) -> dict:
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError(f"Wikidata API: {data['error'].get('info', data['error'])}")
    return data


def entities(qids: list[str], props: str, **extra: str) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for start in range(0, len(qids), BATCH):
        chunk = qids[start : start + BATCH]
        if start:
            time.sleep(0.5)
        data = api(
            {"action": "wbgetentities", "ids": "|".join(chunk), "props": props, **extra}
        )
        found.update(data.get("entities", {}))
    return found


def main_subjects(entity: dict) -> list[str]:
    """The item's P921 values in statement order: the preferred ones when it
    has any, else the normal ones (what `wdt:P921` returns in SPARQL)."""
    by_rank: dict[str, list[str]] = {"preferred": [], "normal": []}
    for statement in entity.get("claims", {}).get(MAIN_SUBJECT, []):
        value = statement.get("mainsnak", {}).get("datavalue", {}).get("value", {})
        rank = statement.get("rank")
        if rank in by_rank and isinstance(value, dict) and value.get("id"):
            by_rank[rank].append(value["id"])
    values = by_rank["preferred"] or by_rank["normal"]
    return list(dict.fromkeys(values))


def label(entity: dict, lang: str) -> str:
    return entity.get("labels", {}).get(lang, {}).get("value", "")


def parse_new_domains(specs: list[list[str]]) -> dict[str, dict[str, str]]:
    new: dict[str, dict[str, str]] = {}
    for qid, name_tech, name_arabic, name_english, name_french in specs:
        if not QID_RE.fullmatch(qid):
            sys.exit(f"--domain: {qid!r} is not a QID")
        if not SLUG_RE.fullmatch(name_tech):
            sys.exit(f"--domain: {name_tech!r} is not a slug (a-z, 0-9, _)")
        if not name_arabic.strip():
            sys.exit(f"--domain {qid}: the Arabic name is empty")
        new[qid] = {
            "name_tech": name_tech,
            "name_arabic": name_arabic.strip(),
            "name_english": name_english.strip() or None,
            "name_french": name_french.strip() or None,
        }
    return new


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument(
        "--apply", action="store_true", help="write the changes to the database"
    )
    parser.add_argument(
        "--domain",
        nargs=5,
        action="append",
        default=[],
        metavar=("QID", "NAME_TECH", "ARABIC", "ENGLISH", "FRENCH"),
        help="names of a P921 value that is not in the `domain` table yet",
    )
    args = parser.parse_args()
    new_domains = parse_new_domains(args.domain)

    if not args.db.is_file():
        print(f"{args.db} is missing — run 'make db' to unpack it from arabterm.db.gz")
        return 1

    con = sqlite3.connect(args.db)
    try:
        return sync(con, new_domains, args.apply)
    finally:
        con.close()


def sync(
    con: sqlite3.Connection, new_domains: dict[str, dict[str, str]], apply: bool
) -> int:
    dictionaries = con.execute(
        "SELECT id, name_tech, wikidata_id FROM dictionary ORDER BY id"
    ).fetchall()
    domains = con.execute(
        "SELECT id, name_tech, name_arabic, wikidata_id FROM domain ORDER BY id"
    ).fetchall()
    domain_of_qid = {qid: domain_id for domain_id, _, _, qid in domains if qid}
    if len(domain_of_qid) != len(domains):
        sys.exit(
            "Two domains share a Wikidata item, or one has none: fix the `domain`"
            " table first (`make validate` says which)."
        )
    slug_of_domain = {domain_id: slug for domain_id, slug, _, _ in domains}
    current: dict[int, set[int]] = {dict_id: set() for dict_id, _, _ in dictionaries}
    for dict_id, domain_id in con.execute(
        "SELECT dictionary_id, domain_id FROM dictionary_domain"
    ):
        current.setdefault(dict_id, set()).add(domain_id)

    for qid, names in new_domains.items():
        if qid in domain_of_qid:
            sys.exit(
                f"--domain: {qid} is already the domain "
                f"`{slug_of_domain[domain_of_qid[qid]]}`"
            )
        if names["name_tech"] in slug_of_domain.values():
            sys.exit(f"--domain: the slug `{names['name_tech']}` is already taken")

    qids = [qid for _, _, qid in dictionaries if qid and QID_RE.fullmatch(qid)]
    try:
        items = entities(qids, "claims")
    except (urllib.error.URLError, RuntimeError, TimeoutError) as error:
        print(f"Could not read Wikidata: {error}")
        return 1

    subjects: dict[int, list[str]] = {}
    no_subject: list[str] = []
    for dict_id, slug, qid in dictionaries:
        values = main_subjects(items.get(qid, {})) if qid else []
        if values:
            subjects[dict_id] = values
        else:
            # Nothing to align with: the links it has are left alone, and
            # `make validate` complains if it has none.
            no_subject.append(f"{slug} ({qid or 'no QID'})")

    used = {value for values in subjects.values() for value in values}
    unknown = sorted(
        used - set(domain_of_qid) - set(new_domains), key=lambda q: int(q[1:])
    )
    if unknown:
        try:
            labels = entities(unknown, "labels", languages="ar|en|fr")
        except (urllib.error.URLError, RuntimeError, TimeoutError):
            labels = {}
        print(f"{len(unknown)} P921 value(s) without a row in `domain`:")
        for value in unknown:
            users = [s for i, s, _ in dictionaries if value in subjects.get(i, [])]
            entity = labels.get(value, {})
            print(
                f"  {value}: ar={label(entity, 'ar')!r} en={label(entity, 'en')!r} "
                f"fr={label(entity, 'fr')!r} — used by {', '.join(users)}"
            )
        print(
            "Give each one a slug and short display names, then run again:\n"
            '  --domain QID name_tech "الاسم" "English name" "Nom français"'
        )
        return 1
    unused_specs = sorted(set(new_domains) - used)
    if unused_specs:
        sys.exit(f"--domain: no dictionary has {', '.join(unused_specs)} as P921")

    # Ids of the domains to create are only known once inserted, so the plan
    # is made of QIDs and turned into ids when it is applied.
    qid_of_domain = {domain_id: qid for qid, domain_id in domain_of_qid.items()}
    names = {qid: slug_of_domain[domain_id] for qid, domain_id in domain_of_qid.items()}
    names.update({qid: spec["name_tech"] for qid, spec in new_domains.items()})
    changes = 0
    to_add: list[tuple[int, str]] = []
    to_remove: list[tuple[int, int]] = []
    for dict_id, slug, _ in dictionaries:
        if dict_id not in subjects:
            continue
        wanted = subjects[dict_id]
        have = {qid_of_domain.get(domain_id) for domain_id in current[dict_id]}
        added = [qid for qid in wanted if qid not in have]
        removed = sorted(
            d for d in current[dict_id] if qid_of_domain.get(d) not in wanted
        )
        if added or removed:
            changes += 1
            print(
                f"  {slug}: "
                + " ".join(
                    [f"+{names[qid]}" for qid in added]
                    + [f"-{slug_of_domain[d]}" for d in removed]
                )
            )
        to_add += [(dict_id, qid) for qid in added]
        to_remove += [(dict_id, domain_id) for domain_id in removed]

    still_used = {
        domain_id
        for dict_id, linked in current.items()
        for domain_id in linked
        if (dict_id, domain_id) not in set(to_remove)
    } | {domain_of_qid[qid] for _, qid in to_add if qid in domain_of_qid}
    orphans = [domain_id for domain_id in slug_of_domain if domain_id not in still_used]

    for qid, spec in new_domains.items():
        print(f"  new domain `{spec['name_tech']}` ({qid}): {spec['name_arabic']}")
    for domain_id in orphans:
        print(
            f"  domain `{slug_of_domain[domain_id]}` is used by no dictionary: removed"
        )
    if no_subject:
        print(
            f"{len(no_subject)} dictionary(ies) without P921 on Wikidata, left as is:"
        )
        for line in no_subject:
            print(f"  {line}")

    if not (changes or new_domains or orphans):
        print(f"The domains of {len(subjects)} dictionaries match Wikidata.")
        return 0
    if not apply:
        print(
            f"\n{changes} dictionary(ies) differ from Wikidata. Nothing was written: "
            "run again with --apply."
        )
        return 0

    with con:
        for qid, spec in new_domains.items():
            cursor = con.execute(
                "INSERT INTO domain (name_tech, name_arabic, name_english, name_french,"
                " wikidata_id) VALUES (?, ?, ?, ?, ?)",
                (
                    spec["name_tech"],
                    spec["name_arabic"],
                    spec["name_english"],
                    spec["name_french"],
                    qid,
                ),
            )
            domain_of_qid[qid] = cursor.lastrowid
        con.executemany(
            "DELETE FROM dictionary_domain WHERE dictionary_id = ? AND domain_id = ?",
            to_remove,
        )
        con.executemany(
            "INSERT INTO dictionary_domain (dictionary_id, domain_id) VALUES (?, ?)",
            [(dict_id, domain_of_qid[qid]) for dict_id, qid in to_add],
        )
        con.executemany("DELETE FROM domain WHERE id = ?", [(d,) for d in orphans])
    print(
        f"\nWritten to {con.execute('PRAGMA database_list').fetchone()[2]}: "
        f"{len(to_add)} link(s) added, {len(to_remove)} removed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
