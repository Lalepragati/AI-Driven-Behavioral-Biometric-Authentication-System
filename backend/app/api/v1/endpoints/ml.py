from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.modules.behavior.schemas import KeystrokeSample
from app.modules.behavior.service import BehaviorService
from app.modules.ml_engine.service import BehaviorMLService
from app.services.container import get_behavior_service, get_ml_service

router = APIRouter(prefix="/ml", tags=["ml"])


class TrainRequest(BaseModel):
    user_id: str
    samples: list[KeystrokeSample]


class PredictRequest(BaseModel):
    user_id: str
    sample: KeystrokeSample


@router.post("/train")
def train_model(payload: TrainRequest, behavior_service: BehaviorService = Depends(get_behavior_service), ml_service: BehaviorMLService = Depends(get_ml_service)):
    try:
        features = [behavior_service.summarize_sample(sample)["features"] for sample in payload.samples]
        return ml_service.train_user_model(payload.user_id, features)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/predict")
def predict_model(payload: PredictRequest, behavior_service: BehaviorService = Depends(get_behavior_service), ml_service: BehaviorMLService = Depends(get_ml_service)):
    try:
        features = behavior_service.summarize_sample(payload.sample)["features"]
        prediction = ml_service.predict(payload.user_id, features)
        return prediction.__dict__
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
