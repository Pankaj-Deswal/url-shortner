from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency that yields the shared async Redis client."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    yield _redis


async def close_redis() -> None:
    """Close the global Redis connection (e.g. on app shutdown)."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
