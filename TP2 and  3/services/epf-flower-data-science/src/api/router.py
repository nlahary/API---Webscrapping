"""API Router for Fast API."""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.api.routes import hello, dataset, iris

router = APIRouter()

router.include_router(hello.router, tags=["Hello"])
router.include_router(dataset.router, tags=["Dataset"])
router.include_router(iris.router, tags=["Iris"])


@router.get("/")
async def root():
    return RedirectResponse(url="/docs")
