from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from app.api.endpoints import url as url_router
from app.core.config import settings
from app.db.url_mongodb import MongoDB
from app.utils.rate_limiter import RateLimiter


@asynccontextmanager
async def app_lifespan(app_instance: FastAPI):
    print("Application Shortener startup.")
    MongoDB.client = AsyncIOMotorClient(settings.database_url)
    print("MongoDB client has been created.")
    yield
    MongoDB.client.close()
    print("MongoDB client has been shut down.")


def create_app() -> FastAPI:
    ENABLE_DOCS = settings.ENABLE_DOCS
    _app = FastAPI(docs_url="/docs" if ENABLE_DOCS else None,
                   redoc_url="/redoc" if ENABLE_DOCS else None,
                   lifespan=app_lifespan)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.enable_rate_limit:
        _app.add_middleware(RateLimiter, max_requests=2, period=60)

    _app.include_router(url_router.router, prefix="/api/v1")

    @_app.get("/")
    async def root():
        return {"message": "Welcome to the URL Shortener API"}

    @_app.delete("/test-delete")
    async def test_delete():
        return {"message": "DELETE method is allowed"}

    return _app


app = create_app()
