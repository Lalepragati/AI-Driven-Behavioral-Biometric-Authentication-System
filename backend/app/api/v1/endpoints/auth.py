from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.schemas import LoginRequest, LoginResponse, ProfileResponse, RegisterRequest
from app.services.container import get_auth_service
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=LoginResponse)
async def login_user(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return await auth_service.evaluate_login(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/profile/{user_id}", response_model=ProfileResponse)
def get_profile(user_id: str, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.get_profile(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
