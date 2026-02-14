from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.shorten import ShortenRequest, ShortenResponse
from app.services.url_service import UrlService

router = APIRouter()


@router.post("", response_model=ShortenResponse)
async def shorten(
    body: ShortenRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ShortenResponse:
    """Create a short URL for the given long URL, or return existing if already shortened."""
    long_url = str(body.url)
    service = UrlService(db, redis)
    short_url, already_exists = await service.shorten_url(long_url)
    message = "URL already exists." if already_exists else None
    return ShortenResponse(short_url=short_url, message=message)
