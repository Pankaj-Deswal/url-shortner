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
    # Random Base62 code: default length 6, after last /
    short_code = data["short_url"].split("/")[-1]
    assert len(short_code) == 6
    assert short_code.isalnum()


@pytest.mark.asyncio
async def test_shorten_invalid_url(client: AsyncClient) -> None:
    response = await client.post(
        "/shorten",
        json={"url": "not-a-valid-url"},
    )
    assert response.status_code == 422
