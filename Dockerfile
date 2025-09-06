FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to install dependencies to ./libs
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry config virtualenvs.path "/app/libs/.venv"

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Install Playwright browsers
RUN poetry run playwright install chromium \
    && poetry run playwright install-deps chromium

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY .env ./

# Create non-root user
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

USER user

EXPOSE 8000

# Use Poetry's virtual environment
CMD ["poetry", "run", "uvicorn", "src.hotline_parser.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]