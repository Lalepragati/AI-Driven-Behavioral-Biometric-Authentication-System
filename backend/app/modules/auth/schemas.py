from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.modules.behavior.schemas import KeystrokeSample


class RegisterRequest(BaseModel):
    user_id: str
    password: str
    role: str = "doctor"
    full_name: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    user_id: str
    password: str
    sample: KeystrokeSample
    failed_attempts: int = 0
    ip_address: str | None = None
    device: str | None = None


class LoginResponse(BaseModel):
    user_id: str
    session_id: str
    risk_score: float
    decision: str
    anomaly_confidence: float
    token: Optional[str] = None
    explanation: str
    model_kind: str
    signals: Dict[str, float] = Field(default_factory=dict)


class ProfileResponse(BaseModel):
    user: Dict[str, Any]
    profile: Dict[str, Any]
