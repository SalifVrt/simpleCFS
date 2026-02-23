PYTHON = uv run

.PHONY: test run clean sync

install:
	@echo "Starting project install..."
	uv pip install -e .

test:
	@echo "🧪 Starting tests..."
	$(PYTHON) pytest

run:
	@echo "🚀 Starting CFS..."
	$(PYTHON) scfs $(FILE)

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

sync:
	uv sync