from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.router import router

from slowapi.middleware import SlowAPIMiddleware

from slowapi import Limiter
from slowapi.util import get_remote_address


def get_application() -> FastAPI:
    application = FastAPI(
        title="epf-flower-data-science",
        description="""Fast API""",
        version="1.0.0",
        redoc_url=None,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(SlowAPIMiddleware)
    limiter = Limiter(key_func=get_remote_address,
                      default_limits=["5 per minute"])
    application.state.limiter = limiter

    application.include_router(router)
    return application
