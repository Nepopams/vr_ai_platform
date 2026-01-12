"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.routes.decide import router as decide_router


def create_app() -> FastAPI:
    app = FastAPI(title="HomeTask Decision API")
    app.include_router(decide_router)
    return app


app = create_app()
