from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def init_db():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]


async def close_db():
    if db.client:
        db.client.close()


def get_database():
    return db.database
