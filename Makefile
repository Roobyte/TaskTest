up:
	docker compose up -d --build

migrate:
	docker compose run --rm user-service alembic upgrade head

test:
	docker compose run --rm auth-service python -m pytest
	docker compose run --rm user-service python -m pytest

down:
	docker compose down -v
