MAIN	:= a_maze_ing.py
CONFIG	:= config.txt

install:
	uv sync

run:
	uv run $(MAIN) $(CONFIG)

debug:
	uv run python -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache

lint:
	uv run flake8 . --exclude .venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
