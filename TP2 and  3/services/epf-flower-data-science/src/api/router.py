"""API Router for Fast API."""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.api.routes import hello
from src.api.routes import data

router = APIRouter()

router.include_router(hello.router, tags=["Hello"])
router.include_router(data.router, tags=["Data"])


@router.get("/")
async def root():
    return RedirectResponse(url="/docs")
