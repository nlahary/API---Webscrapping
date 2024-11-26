"""API Router for Fast API."""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.api.routes import hello

router = APIRouter()

router.include_router(hello.router, tags=["Hello"])


@router.get("/")
async def root():
    return RedirectResponse(url="/docs")
