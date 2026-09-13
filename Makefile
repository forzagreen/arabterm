.PHONY: init build format init_mariadb delete_mariadb migrate_to_mariadb search_mariadb db require_db dump_db dump_sqlite dump_mariadb dump readme regenerate_dumps website_init website_dev website_build website_preview


init:
	uv sync --all-extras

build:
	uv build

format:
	uv run ruff check --select I --fix arabterm
	uv run ruff format arabterm

init_mariadb:
	@if [ $$(docker ps -a -q -f name=mariadb) ]; then \
		docker start mariadb; \
	else \
		. ./.env && docker run -d --name mariadb \
			-e MARIADB_DATABASE=arabterm \
			-e MARIADB_ROOT_PASSWORD=$$MARIADB_PASSWORD \
			-e MARIADB_USER=arabterm \
			-p 3306:3306 mariadb:11.8; \
	fi

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

regenerate_dumps:
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
