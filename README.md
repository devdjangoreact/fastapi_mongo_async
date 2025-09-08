# Hotline Parser API

Async service for parsing products from Hotline.ua and news from various sources.

### Features

- Async FastAPI application
- MongoDB with Motor driver
- Playwright for browser automation
- API key authentication
- Product parsing from Hotline.ua
- News parsing from multiple sources
- Docker support


### Quick Start with Docker

Clone the repository:

```bash
git clone <repository-url>
```

Create environment file:

bash
```
cp .env.example .env
```
### Edit .env if needed

Start services:
```
bash
make docker-up
```
API will be available at: http://localhost:8000
testing bettar with http://127.0.0.1:8000/docs#

## Local Development

### Install Poetry:
```
bash
pip install poetry
```
### Install dependencies 
```
bash
make install
```

### Install Playwright browsers:
```
bash
make install-playwright
```

### Run the application:
```
bash
make run
```

### Available Make Commands
```
bash
make install # Install dependencies 
make run # Run locally
make test # Run tests
make lint # Run linters
make format # Format code
make clean # Clean up
make docker-up # Start Docker containers
make docker-down # Stop Docker containers
```

### API Endpoints

Products
GET /products?url={url}&timeout_limit=5&count_limit=5&price_sort=desc

News
GET /news?url={url}&until_date={date}&client=http|browser

Authentication
Include API key in headers:

text
X-API-Key: your-api-key
Default API keys (from .env): test-key-1, test-key-2

