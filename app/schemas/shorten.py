from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    """Request body for POST /shorten."""

    url: HttpUrl


class ShortenResponse(BaseModel):
    """Response for POST /shorten."""

    short_url: str
