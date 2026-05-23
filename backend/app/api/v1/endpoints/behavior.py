from __future__ import annotations

from fastapi import APIRouter, Depends

from app.modules.behavior.schemas import BehaviorFeatureVector, KeystrokeSample
from app.modules.behavior.service import BehaviorService
from app.services.container import get_behavior_service

router = APIRouter(prefix="/behavior", tags=["behavior"])


@router.post("/analyze", response_model=BehaviorFeatureVector)
def analyze_behavior(sample: KeystrokeSample, behavior_service: BehaviorService = Depends(get_behavior_service)):
    return behavior_service.analyze_sample(sample)


@router.post("/profile")
def build_profile(samples: list[KeystrokeSample], behavior_service: BehaviorService = Depends(get_behavior_service)):
    return behavior_service.build_profile(samples)
