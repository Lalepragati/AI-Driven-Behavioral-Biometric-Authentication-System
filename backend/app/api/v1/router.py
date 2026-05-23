from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.behavior import router as behavior_router
from app.api.v1.endpoints.ml import router as ml_router
from app.api.v1.endpoints.risk import router as risk_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(behavior_router)
api_router.include_router(ml_router)
api_router.include_router(risk_router)
