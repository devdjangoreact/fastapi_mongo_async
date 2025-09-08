FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to NOT use virtualenvs in Docker
RUN poetry config virtualenvs.create false

# Install dependencies using poetry (globally, no virtualenv)
RUN poetry install --without dev --no-interaction --no-ansi --no-root

# Install Playwright system dependencies and browser
RUN playwright install --with-deps chromium

# Copy source code
COPY src/ ./src/

# Create non-root user first
RUN useradd -m -u 1000 user

# Now install Playwright browser for the specific user
USER user
RUN playwright install chromium

# Switch back to root to fix permissions
USER root
RUN chown -R user:user /app

# Switch to user for runtime
USER user

EXPOSE 8000

# Directly use uvicorn (installed globally)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]