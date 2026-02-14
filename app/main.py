from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.redis import close_redis

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup; close Redis on shutdown."""
    from app.models import Url  # noqa: F401 - register model with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_redis()


app = FastAPI(title="URL Shortener", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Render the URL shortener UI."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "base_url": settings.base_url.rstrip("/")},
    )


app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check for load balancers."""
    return {"status": "ok"}
