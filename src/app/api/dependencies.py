from app.db.url_mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorClient


async def get_database_client() -> AsyncIOMotorClient:
    db = get_db()
    try:
        yield db
    finally:
        pass
