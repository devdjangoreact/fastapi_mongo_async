.PHONY: install run test lint format clean docker-up docker-down docker-rm-api docker-rm docker-up-db

install:
	poetry config virtualenvs.in-project true
	poetry install

run:
	poetry run uvicorn src.hotline_parser.main:app --reload --host 0.0.0.0 --port 8000
	docker compose up -d mongo mongo-express
	
test:
	poetry run pytest tests/ -v

lint:
	poetry run black src tests
	poetry run isort src tests
	poetry run flake8 src tests
	poetry run mypy src

format:
	poetry run black src tests
	poetry run isort src tests

clean:
	rm -rf .venv/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

docker-up:
	docker compose up -d

docker-down:
	docker compose down


docker-up-db:
	docker compose up -d mongo mongo-express


docker-down-db:
	docker compose stop mongo mongo-express

docker-build:
	docker compose build

docker-logs:
	docker compose logs -f api



# Видалити тільки контейнер api
docker-rm-api:
	docker compose rm -f -s -v api


# Перезапустити тільки контейнер api
docker-restart-api:
	docker compose restart api


# Перебудувати і перезапустити тільки контейнер api
docker-rebuild-api:
	docker compose up -d --build --force-recreate api


venv-activate:
	@echo "Run: source .venv/bin/activate"

