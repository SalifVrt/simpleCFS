.PHONY: test run clean sync

test:
	@echo "🧪 Lancement des tests..."
	uv run pytest

run:
	@echo "🚀 Lancement de la simulation CFS..."
	uv run src/cfs_scheduler/main.py

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

sync:
	uv sync