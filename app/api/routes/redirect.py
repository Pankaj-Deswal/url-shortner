from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.services.url_service import UrlService

router = APIRouter()


@router.get("/{short_code}")
async def redirect_to_long_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> RedirectResponse:
    """Redirect the client to the original long URL. Returns 404 if not found."""
    service = UrlService(db, redis)
    long_url = await service.resolve(short_code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=long_url, status_code=302)
