from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


class KeystrokeEvent(BaseModel):
    key: str
    event_type: Literal["keydown", "keyup"]
    timestamp: float
    code: str | None = None
    is_error: bool = False


class KeystrokeSample(BaseModel):
    user_id: str
    session_id: str
    text: str | None = None
    events: List[KeystrokeEvent]
    context: Dict[str, Any] = Field(default_factory=dict)


class BehaviorFeatureVector(BaseModel):
    feature_names: List[str]
    values: List[float]
    sample_size: int
    extracted_at: datetime


class BehaviorSummary(BaseModel):
    user_id: str
    session_id: str
    feature_vector: BehaviorFeatureVector
    anomaly_confidence: float
    typing_deviation: float
    explanation: str | None = None
