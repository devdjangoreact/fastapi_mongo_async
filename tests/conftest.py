import asyncio

import pytest
from fastapi.testclient import TestClient

from src.hotline_parser.core.database import close_db, init_db
from src.hotline_parser.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_client():
    await init_db()
    with TestClient(app) as client:
        yield client
    await close_db()


@pytest.fixture
def api_key():
    return "test-key-1"
