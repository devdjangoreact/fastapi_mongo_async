from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings
from .logger import log


class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


db = Database()


async def init_db():
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        log.success("Database initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize database: {str(e)}")
        raise


async def close_db():
    from ..services.scheduler import scheduler_service

    if db.client:
        # await scheduler_service.stop_scheduler()
        db.client.close()
        log.info("Database connection closed")


def get_database() -> AsyncIOMotorDatabase:
    if db.database is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db.database


def get_collection(collection_name: str):
    """Get collection with lazy initialization"""
    database = get_database()
    return database[collection_name]
