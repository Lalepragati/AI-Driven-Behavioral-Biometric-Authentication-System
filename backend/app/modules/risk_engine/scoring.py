from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

DecisionType = Literal["allow", "step_up", "block"]


@dataclass
class RiskAssessment:
    score: float
    decision: DecisionType
    signals: Dict[str, float]


class RiskEngine:
    def score(
        self,
        typing_deviation: float,
        anomaly_confidence: float,
        failed_attempts: int = 0,
        historical_inconsistency: float = 0.0,
    ) -> RiskAssessment:
        score = (
            0.4 * float(typing_deviation)
            + 0.35 * float(anomaly_confidence)
            + 0.15 * min(float(failed_attempts) * 12.0, 30.0)
            + 0.1 * float(historical_inconsistency)
        )
        score = max(0.0, min(100.0, score))
        decision = self.decision_from_score(score)
        return RiskAssessment(
            score=score,
            decision=decision,
            signals={
                "typing_deviation": float(typing_deviation),
                "anomaly_confidence": float(anomaly_confidence),
                "failed_attempts": float(failed_attempts),
                "historical_inconsistency": float(historical_inconsistency),
            },
        )

    def decision_from_score(self, score: float) -> DecisionType:
        if score <= 30:
            return "allow"
        if score <= 70:
            return "step_up"
        return "block"
