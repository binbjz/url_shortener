from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


def get_db() -> AsyncIOMotorClient:
    assert MongoDB.client is not None, "MongoDB client has not been initialized."

    return MongoDB.client[settings.database_name]
