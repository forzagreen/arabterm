
init:
	pip install -e ".[dev]"

build:
	python -m build

format:
	ruff check --select I --fix arabterm
	ruff format arabterm

init_mariadb:
	docker run -d --name mariadb \
		-e MARIADB_DATABASE=arabterm \
		-e MARIADB_ROOT_PASSWORD=${MARIADB_PASSWORD} \
		-e MARIADB_USER=arabterm \
		-p 3306:3306 mariadb:latest

delete_mariadb:
	python arabterm/scripts/delete_mariadb.py

migrate_to_mariadb:
	python arabterm/scripts/migrate_to_mariadb.py

# Usage: make search term="telescope"
search:
	python arabterm/scripts/search_mariadb.py $(term)

dump_sqlite:
	sqlite3 arabterm.db ".output arabterm/db/sqlite/arabterm.sql" .dump

dump_mariadb:
	docker exec mariadb sh -c "mariadb-dump --password=${MARIADB_PASSWORD} arabterm > /mnt/arabterm.sql"
	docker cp mariadb:/mnt/arabterm.sql arabterm/db/mariadb/arabterm.sql

dump: dump_sqlite dump_mariadb

