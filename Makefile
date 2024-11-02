
init:
	pip install -e ".[dev]"

build:
	python -m build

format:
	ruff check --select I --fix arabterm
	ruff format arabterm

