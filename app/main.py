"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes.decide import router as decide_router
from app.routes.health import router as health_router


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Add API-Version header to all /v1/* responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/v1/"):
            response.headers["API-Version"] = "v1"
        return response


def create_app() -> FastAPI:
    app = FastAPI(title="HomeTask Decision API")
    app.add_middleware(APIVersionMiddleware)
    app.include_router(decide_router, prefix="/v1")
    app.include_router(decide_router)
    app.include_router(health_router)
    return app


app = create_app()
