import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from app.main import app


@pytest.fixture(scope="function", autouse=True)
def setup_mongodb():
    from app.db.url_mongodb import MongoDB
    from app.core.config import settings
    from motor.motor_asyncio import AsyncIOMotorClient

    MongoDB.client = AsyncIOMotorClient(settings.database_url)
    yield
    MongoDB.client.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/api/v1/") as async_client:
        yield async_client


async def create_short_url(client: AsyncClient, url: str = "https://example.com") -> str:
    response = await client.post("/shorten/", json={"long_url": url})
    assert response.status_code == 200, "Unexpected status code"
    assert "short_url" in response.json(), "short_url not in response"

    return response.json()["short_url"]


@pytest.mark.asyncio
async def test_create_short_url(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        await create_short_url(async_client)


@pytest.mark.asyncio
async def test_create_short_urls_batch(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        response = await async_client.post("/shorten/batch/",
                                           json=[{"long_url": "https://example.com"},
                                                 {"long_url": "https://example.org"}])
        assert response.status_code == 200, "Unexpected status code"
        assert isinstance(response.json(), list), "Response is not a list"
        assert "short_url" in response.json()[0], "short_url not in first item of response"


@pytest.mark.asyncio
async def test_create_short_urls_concurrently(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        response = await async_client.post("/shorten/batch_conc/",
                                           json=[{"long_url": "https://example.com"},
                                                 {"long_url": "https://example.org"}])
        assert response.status_code == 200, "Unexpected status code"
        assert isinstance(response.json(), list), "Response is not a list"
        assert "short_url" in response.json()[0], "short_url not in first item of response"


@pytest.mark.asyncio
async def test_redirect_to_long_url(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        short_url = await create_short_url(async_client)
        response = await async_client.get(f"/{short_url}")
        assert response.status_code == 307, "Unexpected status code"


@pytest.mark.asyncio
async def test_delete_short_url(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        short_url = await create_short_url(async_client)
        response = await async_client.delete(f"/urls/delete/{short_url}")
        assert response.status_code == 200, "Unexpected status code"
        assert response.json() == {"detail": "URL deleted successfully."}, "Unexpected response"


@pytest.mark.asyncio
async def test_redirect_to_nonexistent_short_url(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        response = await async_client.get("/nonexistent_short_url")
        assert response.status_code == 404, "Unexpected status code"


@pytest.mark.asyncio
async def test_delete_nonexistent_short_url(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        response = await async_client.delete("/urls/delete/nonexistent_short_url")
        assert response.status_code == 404, "Unexpected status code"


@pytest.mark.asyncio
async def test_create_short_urls_concurrently_with_empty_list(client: AsyncGenerator[AsyncClient, None]):
    async for async_client in client:
        response = await async_client.post("/shorten/batch_conc/", json=[])
        assert response.status_code == 400, "Unexpected status code"
