# Hotline Parser API

Async service for parsing products from Hotline.ua and news from various sources.

## Features

- Async FastAPI application
- MongoDB with Motor driver
- Playwright for browser automation
- API key authentication
- Product parsing from Hotline.ua
- News parsing from multiple sources
- Docker support

## Project Structure

hotline-parser/
├── src/ # Source code
├── tests/ # Test files
├── libs/ # Virtual environment and dependencies (auto-created)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── Makefile
├── .env
└── README.md

text

## Quick Start with Docker

1. Clone the repository:

```bash
git clone <repository-url>
cd hotline-parser
```

Create environment file:

bash
cp .env.example .env

# Edit .env if needed

Start services:

bash
make docker-up
API will be available at: http://localhost:8000

Local Development
Install Poetry:

bash
pip install poetry
Install dependencies to libs folder:

bash
make install
Install Playwright browsers:

bash
make install-playwright
Start MongoDB (using Docker):

bash
docker run -d -p 27017:27017 --name mongo mongo:7.0
Run the application:

bash
make run
Available Make Commands
bash
make install # Install dependencies to libs/
make run # Run locally
make test # Run tests
make lint # Run linters
make format # Format code
make clean # Clean up
make docker-up # Start Docker containers
make docker-down # Stop Docker containers
API Endpoints
Products
GET /products/offers?url={url}&timeout_limit=5&count_limit=5&price_sort=desc

News
GET /news/source?url={url}&until_date={date}&client=http|browser

Authentication
Include API key in headers:

text
X-API-Key: your-api-key
Default API keys (from .env): test-key-1, test-key-2

Environment Variables
Create .env file:

env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hotline_parser
API_KEYS=test-key-1,test-key-2
REQUEST_TIMEOUT=30
Development Workflow
Install dependencies: make install

Start MongoDB: docker run -d -p 27017:27017 mongo:7.0

Run application: make run

Run tests: make test

Format code: make format

Docker Development
For development with Docker, the libs directory is mounted as a volume, so you can develop locally and run in Docker with the same dependencies.

License
MIT

text

### 7. .env.example

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hotline_parser
API_KEYS=test-key-1,test-key-2
REQUEST_TIMEOUT=30
Використання
Локальна розробка:
Встановлення залежностей:

bash
make install
Запуск додатка:

bash
make run
Запуск в Docker:

bash
make docker-up
Команди для роботи:
make install - встановлює залежності в папку libs/

make run - запускає додаток локально

make docker-up - запускає в Docker

make test - запускає тести

make lint - перевіряє код

make format - форматує код

Ця структура дозволяє мати всі залежності в папці libs/ у корні проекту, що спрощує розробку як локально, так і в Docker.
```
