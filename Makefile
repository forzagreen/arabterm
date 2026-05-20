
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

migrate_to_mariadb:
	uv run --env-file .env python arabterm/scripts/migrate_to_mariadb.py

# Usage: make search_mariadb term="telescope"
search_mariadb:
	uv run --env-file .env python arabterm/scripts/search_mariadb.py $(term)

dump_sqlite:
	sqlite3 arabterm.db ".output db/sqlite/arabterm.sql" .dump
	gzip --force db/sqlite/arabterm.sql

dump_mariadb:
	@. ./.env && docker exec mariadb sh -c "mariadb-dump --password=$$MARIADB_PASSWORD arabterm > /mnt/arabterm.sql"
	docker cp mariadb:/mnt/arabterm.sql db/mariadb/arabterm.sql
	gzip --force db/mariadb/arabterm.sql

dump: dump_sqlite dump_mariadb

readme:
	uv run --env-file .env python arabterm/scripts/update_readme.py

regenerate_dumps:
	$(MAKE) init_mariadb
	$(MAKE) delete_mariadb
	$(MAKE) migrate_to_mariadb
	$(MAKE) search_mariadb term="telescope"
	$(MAKE) dump
	$(MAKE) readme
