from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import OneClassSVM

from app.modules.behavior.features import FEATURE_ORDER
from app.services.state_repository import StateRepository


@dataclass
class PredictionResult:
    anomaly_confidence: float
    raw_score: float
    model_kind: str
    feature_names: List[str]


class BehaviorMLService:
    def __init__(self, model_dir: Path, repository: StateRepository) -> None:
        self.model_dir = model_dir
        self.repository = repository
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def model_path(self, user_id: str) -> Path:
        return self.model_dir / f"{user_id}.joblib"

    def has_model(self, user_id: str) -> bool:
        return self.model_path(user_id).exists()

    def train_user_model(self, user_id: str, feature_rows: List[Dict[str, float]], labels: Optional[List[int]] = None) -> Dict[str, Any]:
        if not feature_rows:
            raise ValueError("At least one feature row is required")

        feature_names = FEATURE_ORDER if all(name in feature_rows[0] for name in FEATURE_ORDER) else list(feature_rows[0].keys())
        matrix = np.asarray([[float(row.get(name, 0.0)) for name in feature_names] for row in feature_rows], dtype=float)

        if labels and len(set(labels)) > 1:
            pipeline = Pipeline([
                ("scaler", StandardScaler()),
                ("model", RandomForestClassifier(n_estimators=200, random_state=42)),
            ])
            pipeline.fit(matrix, labels)
            model_kind = "random_forest"
            payload = {"pipeline": pipeline, "feature_names": feature_names, "model_kind": model_kind}
        elif len(feature_rows) >= 5:
            pipeline = Pipeline([
                ("scaler", StandardScaler()),
                ("model", OneClassSVM(kernel="rbf", nu=0.1, gamma="scale")),
            ])
            pipeline.fit(matrix)
            model_kind = "one_class_svm"
            payload = {"pipeline": pipeline, "feature_names": feature_names, "model_kind": model_kind}
        else:
            pipeline = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
            pipeline.fit(matrix)
            model_kind = "isolation_forest"
            payload = {"pipeline": pipeline, "feature_names": feature_names, "model_kind": model_kind}

        model_path = self.model_path(user_id)
        joblib.dump(payload, model_path)

        self.repository.upsert_profile(
            user_id,
            {
                "user_id": user_id,
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "model_kind": model_kind,
                "feature_names": feature_names,
                "sample_count": len(feature_rows),
            },
        )

        return {"user_id": user_id, "model_kind": model_kind, "model_path": str(model_path), "sample_count": len(feature_rows)}

    def predict(self, user_id: str, feature_row: Dict[str, float]) -> PredictionResult:
        model_path = self.model_path(user_id)
        if not model_path.exists():
            raise FileNotFoundError(f"No model trained for user '{user_id}'")

        payload = joblib.load(model_path)
        pipeline = payload["pipeline"]
        feature_names = payload["feature_names"]
        model_kind = payload["model_kind"]
        matrix = np.asarray([[float(feature_row.get(name, 0.0)) for name in feature_names]], dtype=float)

        if model_kind == "random_forest":
            probabilities = pipeline.predict_proba(matrix)[0]
            raw_score = float(1.0 - max(probabilities))
        elif model_kind == "one_class_svm":
            score = float(pipeline.decision_function(matrix)[0])
            raw_score = float(1.0 / (1.0 + np.exp(score)))
        else:
            score = float(pipeline.decision_function(matrix)[0])
            raw_score = float(1.0 / (1.0 + np.exp(score)))

        anomaly_confidence = float(np.clip(raw_score * 100.0, 0.0, 100.0))
        return PredictionResult(
            anomaly_confidence=anomaly_confidence,
            raw_score=raw_score,
            model_kind=model_kind,
            feature_names=feature_names,
        )
