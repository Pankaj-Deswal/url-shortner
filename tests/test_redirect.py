import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_redirect_to_long_url(client: AsyncClient) -> None:
    # Create a short URL first
    create_resp = await client.post(
        "/shorten",
        json={"url": "https://example.com/target"},
    )
    assert create_resp.status_code == 200
    short_url = create_resp.json()["short_url"]
    short_code = short_url.split("/")[-1]

    # Follow redirects=False to get 302 and Location header
    redirect_resp = await client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["location"] == "https://example.com/target"


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient) -> None:
    response = await client.get("/nonexistent123")
    assert response.status_code == 404
