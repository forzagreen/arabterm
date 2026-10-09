.PHONY: init build format init_mariadb delete_mariadb migrate_to_mariadb search_mariadb db require_db dump_db dump_sqlite dump_mariadb dump readme validate validate_update_baseline regenerate_dumps website_init website_dev website_build website_preview


init:
	uv sync --all-extras

build:
	uv build

format:
	uv run ruff check --select I --fix arabterm
	uv run ruff format arabterm

# Caps on the MariaDB container, so that a migration cannot starve the machine
# it runs on: by default half of the CPUs and a quarter of the memory that
# Docker has (on a Mac, that of the Docker Desktop VM). Applied on every start,
# to an existing container as well; override with e.g.
# `make regenerate_dumps MARIADB_CPUS=1 MARIADB_MEMORY=2g`.
MARIADB_CPUS ?= $(shell docker info --format '{{.NCPU}}' | awk '{n = int($$1 / 2); print (n < 1 ? 1 : n)}')
MARIADB_MEMORY ?= $(shell docker info --format '{{.MemTotal}}' | awk '{m = int($$1 / 4 / 1048576); print (m < 1024 ? 1024 : m) "m"}')
MARIADB_LIMITS = --cpus $(MARIADB_CPUS) --memory $(MARIADB_MEMORY) --memory-swap $(MARIADB_MEMORY)

init_mariadb:
	@if [ $$(docker ps -a -q -f name=mariadb) ]; then \
		docker update $(MARIADB_LIMITS) mariadb && docker start mariadb; \
	else \
		. ./.env && docker run -d --name mariadb $(MARIADB_LIMITS) \
			-e MARIADB_DATABASE=arabterm \
			-e MARIADB_ROOT_PASSWORD=$$MARIADB_PASSWORD \
			-e MARIADB_USER=arabterm \
			-p 3306:3306 mariadb:11.8; \
	fi
	@# `docker start` returns before the server accepts connections
	@n=0; until docker exec mariadb healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1; do \
		n=$$((n + 1)); \
		if [ $$n -ge 120 ]; then echo "MariaDB is not ready after 120 s — see 'docker logs mariadb'"; exit 1; fi; \
		sleep 1; \
	done

delete_mariadb:
	uv run --env-file .env python arabterm/scripts/delete_mariadb.py

migrate_to_mariadb: require_db
	uv run --env-file .env python arabterm/scripts/migrate_to_mariadb.py

# Usage: make search_mariadb term="telescope"
search_mariadb:
	uv run --env-file .env python arabterm/scripts/search_mariadb.py $(term)

# arabterm.db itself is not committed: at 110 MiB it is past GitHub's 100 MiB
# per-file limit. arabterm.db.gz is, and `make db` unpacks it. Everything that
# reads the database — the website build, DBeaver, the scripts below — wants
# the unpacked file, so unpack once after cloning and work on it normally.
db:
	@test ! -f arabterm.db || { echo "arabterm.db already exists — remove it first if you really want to overwrite it from arabterm.db.gz"; exit 1; }
	gzip -dc arabterm.db.gz > arabterm.db

require_db:
	@test -f arabterm.db || { echo "arabterm.db is missing — run 'make db' to unpack it from arabterm.db.gz"; exit 1; }

# -n keeps the name and mtime out of the gzip header, so an unchanged database
# compresses to an unchanged file instead of a fresh 30 MB blob in every commit.
dump_db: require_db
	gzip -n -c arabterm.db > arabterm.db.gz

dump_sqlite: require_db
	sqlite3 arabterm.db ".output db/sqlite/arabterm.sql" .dump
	gzip --force db/sqlite/arabterm.sql

dump_mariadb:
	@. ./.env && docker exec mariadb sh -c "mariadb-dump --password=$$MARIADB_PASSWORD arabterm > /mnt/arabterm.sql"
	docker cp mariadb:/mnt/arabterm.sql db/mariadb/arabterm.sql
	gzip --force db/mariadb/arabterm.sql

dump: dump_db dump_sqlite dump_mariadb

readme: require_db
	uv run --env-file .env python arabterm/scripts/update_readme.py

# Data invariants of arabterm.db (see arabterm/scripts/validate_db.py). Plain
# python3, not `uv run`: the script is stdlib-only, so that CI can run it
# without installing anything.
validate: require_db
	python3 arabterm/scripts/validate_db.py

# Record the current violations as accepted. Review the diff before committing.
validate_update_baseline: require_db
	python3 arabterm/scripts/validate_db.py --update-baseline

regenerate_dumps:
	$(MAKE) validate
	$(MAKE) init_mariadb
	$(MAKE) delete_mariadb
	$(MAKE) migrate_to_mariadb
	$(MAKE) search_mariadb term="telescope"
	$(MAKE) dump
	$(MAKE) readme

website_init:
	cd website && npm install

website_dev: require_db
	cd website && npm run dev

website_build: require_db
	cd website && npm run build

website_preview:
	cd website && npm run preview
