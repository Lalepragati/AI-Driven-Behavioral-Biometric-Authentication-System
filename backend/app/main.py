from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.container import get_state_repository

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def ensure_storage() -> None:
    get_state_repository()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": settings.app_name,
            "status": "running",
            "docs": "/docs",
            "health": "/health",
            "api_prefix": settings.api_v1_prefix,
        }
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)
