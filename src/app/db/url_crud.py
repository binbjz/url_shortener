import time
import asyncio
import pydantic_core
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.domain import URLModel
from app.models.schemas import URLInDB

COLLECTION_NAME = settings.database_collection_name


async def create_url(db: AsyncIOMotorClient, long_url: str, short_url: str) -> URLModel:
    existing_url = await db[COLLECTION_NAME].find_one({"long_url": str(long_url)})
    if existing_url:
        return URLModel(**existing_url)

    document = {
        "long_url": str(long_url),
        "short_url": short_url,
        "created_at": time.time_ns(),
    }
    await db[COLLECTION_NAME].insert_one(document)

    return URLModel(**document)


async def create_urls_concurrently(db: AsyncIOMotorClient, url_pairs: list[dict]) -> list[URLModel]:
    tasks = []
    for pair in url_pairs:
        pair["created_at"] = time.time_ns()

        if isinstance(pair["long_url"], pydantic_core._pydantic_core.Url):
            pair["long_url"] = str(pair["long_url"])
        if isinstance(pair["short_url"], pydantic_core._pydantic_core.Url):
            pair["short_url"] = str(pair["short_url"])

        task = db[COLLECTION_NAME].update_one(
            {"long_url": pair["long_url"]},
            {"$setOnInsert": pair},
            upsert=True
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    return [URLModel(**pair) for pair in url_pairs]


async def get_url_by_short(db: AsyncIOMotorClient, short_url: str) -> Optional[URLModel]:
    document = await db[COLLECTION_NAME].find_one({"short_url": short_url})

    return URLModel(**{**document, "id": str(document.pop("_id"))}) if document else None


async def update_access_count(db: AsyncIOMotorClient, short_url: str) -> Optional[URLInDB]:
    result = await db[COLLECTION_NAME].update_one({"short_url": short_url},
                                                  {"$inc": {"access_count": 1}})

    if result.modified_count > 0:
        updated_record = await db[COLLECTION_NAME].find_one({"short_url": short_url})
        if updated_record:
            updated_record["id"] = str(updated_record.pop("_id"))
            return URLInDB(**updated_record)

    return None


async def delete_url(db: AsyncIOMotorClient, short_url: str) -> bool:
    result = await db[COLLECTION_NAME].delete_one({"short_url": short_url})

    return result.deleted_count > 0
