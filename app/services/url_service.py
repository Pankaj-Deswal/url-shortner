from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.url_repository import UrlRepository
from app.utils.base62 import generate_random_base62

REDIS_CACHE_PREFIX = "url:"
MAX_SHORTEN_RETRIES = 5


class UrlService:
    """Orchestrates shorten and resolve flows (Redis + repository)."""

    def __init__(self, db: AsyncSession, redis: Redis) -> None:
        self._db = db
        self._redis = redis
        self._repo = UrlRepository(db)

    async def shorten_url(self, long_url: str) -> tuple[str, bool]:
        """
        Generate a short code for long_url, or return existing if long_url already exists.
        Returns (full_short_url, already_exists).
        """
        existing_code = await self._repo.get_short_code_by_long_url(long_url)
        if existing_code is not None:
            base = settings.base_url.rstrip("/")
            return f"{base}/{existing_code}", True
        length = settings.short_code_length
        for _ in range(MAX_SHORTEN_RETRIES):
            short_code = generate_random_base62(length)
            try:
                await self._repo.create(short_code=short_code, long_url=long_url)
                break
            except IntegrityError:
                await self._db.rollback()
                continue
        else:
            raise RuntimeError("Failed to generate unique short code after retries")
        cache_key = f"{REDIS_CACHE_PREFIX}{short_code}"
        if settings.redis_cache_ttl_seconds is not None:
            await self._redis.setex(cache_key, settings.redis_cache_ttl_seconds, long_url)
        else:
            await self._redis.set(cache_key, long_url)
        base = settings.base_url.rstrip("/")
        return f"{base}/{short_code}", False

    async def resolve(self, short_code: str) -> str | None:
        """
        Resolve short_code to long_url: Redis first, then DB on miss; cache on miss.
        Returns long_url or None if not found.
        """
        cache_key = f"{REDIS_CACHE_PREFIX}{short_code}"
        long_url = await self._redis.get(cache_key)
        if long_url is not None:
            return long_url
        long_url = await self._repo.get_long_url_by_short_code(short_code)
        if long_url is None:
            return None
        if settings.redis_cache_ttl_seconds is not None:
            await self._redis.setex(cache_key, settings.redis_cache_ttl_seconds, long_url)
        else:
            await self._redis.set(cache_key, long_url)
        return long_url
