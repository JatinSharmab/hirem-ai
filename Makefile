.PHONY: setup db-up db-down migrate seed api ui test lint typecheck eval
setup:
	uv sync --extra dev

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

migrate:
	uv run alembic upgrade head

seed:
	uv run python scripts/seed_demo.py

api:
	uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

ui:
	uv run streamlit run apps/ui/Home.py --server.port 8501

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy src/hireme_ai

eval:
	uv run python evaluation/run_evaluation.py
