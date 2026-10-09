.PHONY: api test migrate

api:
	python -m uvicorn app.main:app --reload --app-dir services/api

test:
	python -m pytest services/api/tests

migrate:
	python -m alembic -c services/api/alembic.ini upgrade head
