.PHONY: install run test lint format clean docker-up docker-down

install:
	poetry config virtualenvs.in-project true
	poetry config virtualenvs.path "libs/.venv"
	poetry install

run:
	poetry run uvicorn src.hotline_parser.main:app --reload --host 0.0.0.0 --port 8000

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
	rm -rf libs/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f api

install-playwright:
	poetry run playwright install chromium
	poetry run playwright install-deps chromium