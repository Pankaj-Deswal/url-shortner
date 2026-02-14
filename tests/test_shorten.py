import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_shorten_returns_short_url(client: AsyncClient) -> None:
    response = await client.post(
        "/shorten",
        json={"url": "https://example.com/very/long/path"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["short_url"].endswith("/1")  # Base62(1) = "1"


@pytest.mark.asyncio
async def test_shorten_invalid_url(client: AsyncClient) -> None:
    response = await client.post(
        "/shorten",
        json={"url": "not-a-valid-url"},
    )
    assert response.status_code == 422
