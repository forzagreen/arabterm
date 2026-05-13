# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

`arabterm` is a curated SQLite database of Arabic/English/French multilingual dictionaries (~400k terms across ~50 dictionaries). It is the upstream data source for [Wiki Term Base](https://wikitermbase.toolforge.org/). The Python package is a thin layer over SQLAlchemy models and migration scripts — there is no application, library API, or test suite. Most "work" in this repo is producing the SQL dumps in [db/](db/) from the canonical `arabterm.db`.

A small Astro static site under [website/](website/) is also derived from `arabterm.db` at build time and deployed to GitHub Pages — see "Website" below.

## Common commands

```sh
make init                  # pip install -e ".[dev]" (ruff + pip extras)
make format                # ruff check --select I --fix + ruff format
make regenerate_dumps      # full pipeline: see "Dump regeneration" below
make dump                  # just re-dump SQLite + MariaDB without re-migrating
```

Granular Make targets (composed by `regenerate_dumps`): `init_mariadb`, `delete_mariadb`, `migrate_to_mariadb`, `search_mariadb term="..."`, `dump_sqlite`, `dump_mariadb`. No test runner — there are no tests.

Environment: copy `example.env` to `.env` and set `MARIADB_PASSWORD`. The Make targets and scripts read `SQLITE_URL`, `MARIADB_URL`, and `MARIADB_PASSWORD` from the environment.

## Architecture

### Two parallel models, one source of truth

The canonical data lives in [arabterm.db](arabterm.db) (SQLite, checked into git). MariaDB is a *derived* format, regenerated from SQLite. This is why two near-identical SQLAlchemy model files exist:

- [arabterm/sqlite_models.py](arabterm/sqlite_models.py) — typed columns without lengths; uses `onupdate=utc_now` Python-side for `updated_at`.
- [arabterm/mariadb_models.py](arabterm/mariadb_models.py) — same shape, but `String(255)`, `mysql_engine="InnoDB"`, server-side `ON UPDATE CURRENT_TIMESTAMP`, and a critical `FULLTEXT` index on `term(arabic, english, french, description)`.

The FULLTEXT index is the *reason* MariaDB exists in this project: SQLite has no equivalent for the `MATCH(...) AGAINST(... IN NATURAL LANGUAGE MODE)` search used by the consuming Toolforge app (see `search_mariadb.py`). If you change the schema, update both model files in lockstep.

### Dump regeneration pipeline

`make regenerate_dumps` chains targets via `$(MAKE)` (not as prerequisites) to enforce strict ordering:

1. `init_mariadb` — `docker start mariadb` if it exists, else `docker run` a fresh `mariadb:11.8` container with DB `arabterm` on port 3306.
2. `delete_mariadb` — runs [arabterm/scripts/delete_mariadb.py](arabterm/scripts/delete_mariadb.py). Despite the README phrasing, this drops the **tables**, not the container — it gives migration a clean slate inside the running container.
3. `migrate_to_mariadb` — [arabterm/scripts/migrate_to_mariadb.py](arabterm/scripts/migrate_to_mariadb.py). Commits dictionaries before terms to satisfy the FK; preserves SQLite PKs.
4. `search_mariadb term="telescope"` — smoke test that FULLTEXT search returns results.
5. `dump` → `dump_sqlite` + `dump_mariadb`. SQLite dumps via `sqlite3 ... .dump`; MariaDB dumps via `docker exec mariadb-dump` then `docker cp`. Both are gzipped into `db/sqlite/` and `db/mariadb/`.

### Downstream notification

[`.github/workflows/notify-wikitermbase.yml`](.github/workflows/notify-wikitermbase.yml) fires only when `db/mariadb/arabterm.sql.gz` changes on `main`. It uses the `WIKITERMBASE_DISPATCH_PAT` secret to dispatch an `arabterm-data-updated` repository_dispatch event to `forzagreen/wikitermbase`, which auto-opens a PR there. SQLite-only changes do *not* trigger the notification — if you intend to publish a data change, regenerate **both** dumps.

### Website

[website/](website/) is an [Astro](https://astro.build/) static site (deployed to <https://forzagreen.github.io/arabterm/>) that reads `arabterm.db` at build time via `better-sqlite3` and emits one HTML page per dictionary (paginated 1000 terms / page) plus a per-dict JSON download. It's a third derived view of the DB alongside the SQLite and MariaDB dumps — no JSON is committed.

Legacy unprefixed URLs from the original Angular site (e.g. `/water_engineering/`) are preserved as static HTML redirects to the canonical `name_tech` URL (`/arabterm_water_engineering/`). The legacy slug list lives in `LEGACY_SLUGS` in [website/src/lib/db.ts](website/src/lib/db.ts) — never remove a legacy slug from this list, even if its underlying dictionary changes.

[`.github/workflows/gh-pages.yml`](.github/workflows/gh-pages.yml) runs `npm run build` inside `website/` on every push to `main` and uploads `website/dist/` to GitHub Pages.

## Conventions

- Adding a new dictionary: insert into the `dictionary` table with a unique `name_tech` slug, then bulk-insert terms with the matching `dictionary_id`. Run `make regenerate_dumps` before opening a PR so the MariaDB dump is in sync. The website will pick up the new dictionary automatically on the next deploy.
- The repo contains large notebooks (`V2.ipynb`, `MigrateDB.ipynb`, etc.) and scratch directories (`playground/`, `samples/`) used for historical scraping/ingestion. They are not part of the published pipeline — don't edit them as part of routine changes.
- Python 3.10+, SQLAlchemy 2.x style (`Mapped[...]`, `mapped_column`).
