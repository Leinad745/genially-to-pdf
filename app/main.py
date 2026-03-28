from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.db import close_db, init_db
from app.limiter import init_limiter
from app.routes import index as index_router
from app.routes import tasks as tasks_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    init_db()
    yield
    close_db()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=app_lifespan)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # rate limiter
    init_limiter(app)

    # routers
    app.include_router(tasks_router.tasks_router)
    app.include_router(index_router.index_router)

    return app


app = create_app()
