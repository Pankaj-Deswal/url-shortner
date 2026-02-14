from fastapi import APIRouter

from app.api.routes import redirect, shorten

api_router = APIRouter()
api_router.include_router(shorten.router, prefix="/shorten", tags=["shorten"])
api_router.include_router(redirect.router, tags=["redirect"])
