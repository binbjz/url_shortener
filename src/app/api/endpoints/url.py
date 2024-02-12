from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from app.models import schemas
from app.api.dependencies import get_database_client
from app.services.url_service import URLShortener
from app.db.url_crud import (create_url,
                             get_url_by_short,
                             update_access_count,
                             delete_url,
                             create_urls_concurrently)

router = APIRouter()

url_shortener = URLShortener()


@router.post("/shorten/", response_model=schemas.URLResponse)
async def create_short_url(url_request: schemas.URLCreate, db: AsyncIOMotorClient = Depends(get_database_client)):
    short_url = url_shortener.add_url(url_request.long_url)
    url_model = await create_url(db, url_request.long_url, short_url)

    return schemas.URLResponse(long_url=url_model.long_url, short_url=url_model.short_url)


@router.post("/shorten/batch/", response_model=list[schemas.URLResponse])
async def create_short_urls(urls: list[schemas.URLCreate], db: AsyncIOMotorClient = Depends(get_database_client)):
    responses = []
    for url_request in urls:
        short_url = url_shortener.add_url(url_request.long_url)
        url_model = await create_url(db, url_request.long_url, short_url)
        responses.append(schemas.URLResponse(long_url=url_model.long_url, short_url=url_model.short_url))

    return responses


@router.post("/shorten/batch_conc/", response_model=list[schemas.URLResponse])
async def create_short_urls_concurrently(urls: list[schemas.URLCreate],
                                         db: AsyncIOMotorClient = Depends(get_database_client)):
    if not urls:
        raise HTTPException(status_code=400, detail="URL list is empty")

    url_pairs = [{"long_url": url_request.long_url, "short_url": url_shortener.add_url(url_request.long_url)}
                 for url_request in urls]

    await create_urls_concurrently(db, url_pairs)

    responses = [schemas.URLResponse(long_url=pair["long_url"], short_url=pair["short_url"]) for pair in url_pairs]

    return responses


@router.get("/{short_url:path}")
async def redirect_to_long_url(short_url: str, db: AsyncIOMotorClient = Depends(get_database_client)):
    url_model = await get_url_by_short(db, short_url)
    if url_model is None:
        raise HTTPException(status_code=404, detail="URL not found")
    await update_access_count(db, short_url)

    # return url_model.long_url
    return RedirectResponse(url=url_model.long_url)


@router.delete("/urls/delete/{short_url:path}")
async def delete_short_url(short_url: str, db: AsyncIOMotorClient = Depends(get_database_client)):
    success = await delete_url(db, short_url)
    if success:
        return {"detail": "URL deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="URL not found or already deleted.")
