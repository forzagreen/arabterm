# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

`arabterm` is a curated SQLite database of Arabic/English/French multilingual dictionaries (~400k terms across ~50 dictionaries). It is the upstream data source for [Wiki Term Base](https://wikitermbase.toolforge.org/). The Python package is a thin layer over SQLAlchemy models and migration scripts — there is no application, library API, or test suite. Most "work" in this repo is producing the SQL dumps in [db/](db/) from the canonical `arabterm.db`.

A small Astro static site under [website/](website/) is also derived from `arabterm.db` at build time and deployed to GitHub Pages — see "Website" below.

## Common commands

```sh
make db                    # unpack arabterm.db from the committed arabterm.db.gz (do this first)
make init                  # uv sync --all-extras
make format                # ruff check --select I --fix + ruff format (via uv run)
make regenerate_dumps      # full pipeline: see "Dump regeneration" below
make dump                  # just re-dump SQLite + MariaDB without re-migrating
make readme                # regenerate the Dictionaries table in README.md from arabterm.db
make validate              # check the data invariants of arabterm.db (also run in CI)
make website_init          # npm install inside website/ (first time only)
make website_dev           # astro dev server (HMR) at http://localhost:4321/arabterm/
make website_build         # build website/dist/ for production
make website_preview       # serve the built dist/ — use this to test the prod bundle
```

Granular Make targets (composed by `regenerate_dumps`): `init_mariadb`, `delete_mariadb`, `migrate_to_mariadb`, `search_mariadb term="..."`, `validate`, `dump_sqlite`, `dump_mariadb`, `readme`. No test runner — there are no code tests; `make validate` tests the *data*.

Environment: copy `example.env` to `.env` and set `MARIADB_PASSWORD`. Python recipes invoke `uv run --env-file .env`, which loads `SQLITE_URL`, `MARIADB_URL`, and `MARIADB_PASSWORD` for the script. The two shell-only recipes that need `MARIADB_PASSWORD` (`init_mariadb`, `dump_mariadb`) source `.env` inline. No manual `source .env` is needed.

## Architecture

### Two parallel models, one source of truth

The canonical data lives in `arabterm.db` (SQLite). MariaDB is a *derived* format, regenerated from SQLite.

`arabterm.db` itself is **gitignored**: at ~110 MiB it is past GitHub's hard 100 MiB per-file limit. What is committed is [arabterm.db.gz](arabterm.db.gz) (~30 MiB), and `make db` unpacks it. `make db` refuses to overwrite an existing `arabterm.db`, so it can never clobber local edits; every target that reads the database depends on `require_db`, which fails with a pointer to `make db` rather than a confusing SQLite error. `make dump` recompresses it (`gzip -n`, so an unchanged database produces an unchanged file rather than a fresh 30 MB blob), which means the archive cannot go stale as long as changes go through `make regenerate_dumps`. Note that `db/sqlite/arabterm.sql.gz` carries the same content again in `.dump` form — the redundancy is deliberate for now, but it is the obvious thing to drop if repo size becomes pressing. This is why two near-identical SQLAlchemy model files exist:

- [arabterm/sqlite_models.py](arabterm/sqlite_models.py) — typed columns without lengths; uses `onupdate=utc_now` Python-side for `updated_at`.
- [arabterm/mariadb_models.py](arabterm/mariadb_models.py) — same shape, but `String(255)`, `mysql_engine="InnoDB"`, server-side `ON UPDATE CURRENT_TIMESTAMP`, and a critical `FULLTEXT` index on `term(arabic, english, french, description)`.

The FULLTEXT index is the *reason* MariaDB exists in this project: SQLite has no equivalent for the `MATCH(...) AGAINST(... IN NATURAL LANGUAGE MODE)` search used by the consuming Toolforge app (see `search_mariadb.py`). If you change the schema, update both model files in lockstep.

### Dump regeneration pipeline

`make regenerate_dumps` chains targets via `$(MAKE)` (not as prerequisites) to enforce strict ordering:

0. `validate` — see "Data validation" below. Runs first so that bad data fails in seconds, before any dump is produced.
1. `init_mariadb` — `docker start mariadb` if it exists, else `docker run` a fresh `mariadb:11.8` container with DB `arabterm` on port 3306.
2. `delete_mariadb` — runs [arabterm/scripts/delete_mariadb.py](arabterm/scripts/delete_mariadb.py). Despite the README phrasing, this drops the **tables**, not the container — it gives migration a clean slate inside the running container.
3. `migrate_to_mariadb` — [arabterm/scripts/migrate_to_mariadb.py](arabterm/scripts/migrate_to_mariadb.py). Commits dictionaries before terms to satisfy the FK; preserves SQLite PKs.
4. `search_mariadb term="telescope"` — smoke test that FULLTEXT search returns results.
5. `dump` → `dump_db` + `dump_sqlite` + `dump_mariadb`. `dump_db` recompresses `arabterm.db` into `arabterm.db.gz`. SQLite dumps via `sqlite3 ... .dump`; MariaDB dumps via `docker exec mariadb-dump` then `docker cp`. Both are gzipped into `db/sqlite/` and `db/mariadb/`.
6. `readme` — [arabterm/scripts/update_readme.py](arabterm/scripts/update_readme.py). Regenerates the Dictionaries table in [README.md](README.md) (between the `DICTIONARIES_TABLE_START`/`_END` HTML comment markers) from the current `dictionary` table. Sorted most-recently-added first (`created_at DESC, id DESC`). Never hand-edit that block.

### Data validation

[arabterm/scripts/validate_db.py](arabterm/scripts/validate_db.py) (`make validate`) checks the invariants of `arabterm.db`: every term has an Arabic and an English value, no orphan terms, `nbr_entries` equals the real row count, every `wikidata_id` is a well-formed and unique QID. It reads only `arabterm.db` and never the network, so that a CI result depends on the pull request alone and not on somebody editing Wikidata. The consequence: it cannot tell whether a QID is the *right* item (e.g. the item of another edition of the same work) — that stays a manual check, step 2 of the new-dictionary checklist. The script is stdlib-only on purpose, so CI runs it with plain `python3`.

Existing violations are recorded in [arabterm/scripts/validation_baseline.json](arabterm/scripts/validation_baseline.json) (term ids / `name_tech` slugs per check, plus `exempt` for whole dictionaries such as `al_mawrid_al_hadeeth`, which has no Arabic column). The baseline is a ratchet: a violation not in it fails, and so does a baseline entry that is no longer a violation — after fixing data, run `make validate_update_baseline` and commit the shrunken file. Never use `validate_update_baseline` to silence a new violation that is a real data error; fix the data instead.

[`.github/workflows/validate-db.yml`](.github/workflows/validate-db.yml) runs `make db` + `make validate` on every pull request that touches `arabterm.db.gz`, the script or the baseline.

### Downstream notification

[`.github/workflows/notify-wikitermbase.yml`](.github/workflows/notify-wikitermbase.yml) fires only when `db/mariadb/arabterm.sql.gz` changes on `main`. It uses the `WIKITERMBASE_DISPATCH_PAT` secret to dispatch an `arabterm-data-updated` repository_dispatch event to `forzagreen/wikitermbase`, which auto-opens a PR there. SQLite-only changes do *not* trigger the notification — if you intend to publish a data change, regenerate **both** dumps.

### Website

[website/](website/) is an [Astro](https://astro.build/) static site (deployed to <https://forzagreen.github.io/arabterm/>) that reads `arabterm.db` at build time (the gh-pages workflow runs `make db` first, since the unpacked file is not in the checkout) via `better-sqlite3` and emits one HTML page per dictionary (paginated 1000 terms / page) plus a per-dict JSON download. It's a third derived view of the DB alongside the SQLite and MariaDB dumps — no JSON is committed.

Legacy unprefixed URLs from the original Angular site (e.g. `/water_engineering/`) are preserved as static HTML redirects to the canonical `name_tech` URL (`/at_water_engineering/`). The legacy slug list lives in `LEGACY_SLUGS` in [website/src/lib/db.ts](website/src/lib/db.ts) — never remove a legacy slug from this list, even if its underlying dictionary changes.

[`.github/workflows/gh-pages.yml`](.github/workflows/gh-pages.yml) runs `npm run build` inside `website/` on every push to `main` and uploads `website/dist/` to GitHub Pages.

## Conventions

- Adding a new dictionary — full checklist:
  1. **Back up first**: `cp arabterm.db arabterm.db.bak` (gitignored). A botched insert into the canonical SQLite is the only real failure mode here.
  2. **Resolve the Wikidata labels** if the dictionary has a QID — fetch `https://www.wikidata.org/wiki/Special:EntityData/<QID>.json` and use the official `ar`/`en`/`fr` labels. Append the publication year in parentheses to `name_arabic` to match the existing series (e.g. `... (2020)`). Wikidata sometimes uses ALL CAPS or typos in the English/French labels — match the style of existing entries (sentence case for French, no typos).
  3. **Pick a `name_tech` slug**: follow the existing series naming. The 2020 educational series uses `topic_NN` (e.g. `educational_supervision_47`); older ArabTerm-website entries use the `at_` prefix (e.g. `at_water_engineering`). `samples/NN_topic_…/` folder names flip to `topic_NN` slugs.
  4. **Insert** the `dictionary` row (set `nbr_entries` to the actual row count) **and** the `term` rows in a single SQLite transaction. Pre-check that the slug and `wikidata_id` aren't already taken. Use the `Dictionary.id` returned by `lastrowid` as the `term.dictionary_id`.
  5. **Run `make regenerate_dumps`** — it starts with `make validate`, so a term without Arabic/English, a wrong `nbr_entries` or a duplicate QID stops it before any dump is written. That single target now also rewrites the Dictionaries table in `README.md`. Commit the resulting `arabterm.db.gz`, `db/sqlite/arabterm.sql.gz`, `db/mariadb/arabterm.sql.gz`, and `README.md` together (plus `validation_baseline.json` if it changed). `arabterm.db` is gitignored and is never committed. The website will pick up the new dictionary automatically on the next deploy.
  6. Per the user's `feedback_conventional_commits` memory: branch `feat/...`, commit `feat: ...`.
- The repo contains large notebooks (`V2.ipynb`, `MigrateDB.ipynb`, etc.) and scratch directories (`playground/`, `samples/`) used for historical scraping/ingestion. They are not part of the published pipeline — don't edit them as part of routine changes.
- Python 3.10+, SQLAlchemy 2.x style (`Mapped[...]`, `mapped_column`).
