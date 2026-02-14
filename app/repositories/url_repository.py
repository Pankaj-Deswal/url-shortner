from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import Url


class UrlRepository:
    """Data access for URL mappings (PostgreSQL only)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, short_code: str, long_url: str) -> Url:
        """Insert a new URL mapping and return the model."""
        url = Url(short_code=short_code, long_url=long_url)
        self._db.add(url)
        await self._db.flush()
        await self._db.refresh(url)
        return url

    async def get_long_url_by_short_code(self, short_code: str) -> str | None:
        """Return long_url for the given short_code, or None if not found."""
        result = await self._db.execute(
            select(Url.long_url).where(Url.short_code == short_code).limit(1)
        )
        row = result.scalar_one_or_none()
        return str(row) if row is not None else None
