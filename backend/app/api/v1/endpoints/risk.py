from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.modules.risk_engine.scoring import RiskEngine
from app.services.container import get_risk_engine

router = APIRouter(prefix="/risk", tags=["risk"])


class RiskRequest(BaseModel):
    typing_deviation: float
    anomaly_confidence: float
    failed_attempts: int = 0
    historical_inconsistency: float = 0.0


@router.post("/score")
def score_risk(payload: RiskRequest, risk_engine: RiskEngine = Depends(get_risk_engine)):
    assessment = risk_engine.score(
        typing_deviation=payload.typing_deviation,
        anomaly_confidence=payload.anomaly_confidence,
        failed_attempts=payload.failed_attempts,
        historical_inconsistency=payload.historical_inconsistency,
    )
    return {
        "score": assessment.score,
        "decision": assessment.decision,
        "signals": assessment.signals,
    }
