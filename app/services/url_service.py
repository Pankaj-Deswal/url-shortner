from redis.asyncio import Redis

from app.core.config import settings
from app.repositories.url_repository import UrlRepository
from app.utils.base62 import encode
from sqlalchemy.ext.asyncio import AsyncSession

REDIS_COUNTER_KEY = "url:id_counter"
REDIS_CACHE_PREFIX = "url:"


class UrlService:
    """Orchestrates shorten and resolve flows (Redis + repository)."""

    def __init__(self, db: AsyncSession, redis: Redis) -> None:
        self._db = db
        self._redis = redis
        self._repo = UrlRepository(db)

    async def shorten_url(self, long_url: str) -> str:
        """
        Generate a short code for long_url: Redis INCR -> Base62 -> persist -> cache.
        Returns the full short URL (base_url + short_code).
        """
        next_id = await self._redis.incr(REDIS_COUNTER_KEY)
        short_code = encode(next_id)
        await self._repo.create(short_code=short_code, long_url=long_url)
        cache_key = f"{REDIS_CACHE_PREFIX}{short_code}"
        if settings.redis_cache_ttl_seconds is not None:
            await self._redis.setex(cache_key, settings.redis_cache_ttl_seconds, long_url)
        else:
            await self._redis.set(cache_key, long_url)
        base = settings.base_url.rstrip("/")
        return f"{base}/{short_code}"

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
