"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.routes.decide import router as decide_router
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="HomeTask Decision API")
    app.include_router(decide_router)
    app.include_router(health_router)
    return app


app = create_app()
