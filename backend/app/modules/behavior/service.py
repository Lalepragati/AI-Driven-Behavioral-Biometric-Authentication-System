from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.modules.behavior.features import extract_keystroke_features, feature_vector, session_signature
from app.modules.behavior.schemas import BehaviorFeatureVector, KeystrokeSample


@dataclass
class BehaviorService:
    def analyze_sample(self, sample: KeystrokeSample) -> BehaviorFeatureVector:
        features = extract_keystroke_features(sample.events)
        feature_names, values = feature_vector(features)
        return BehaviorFeatureVector(
            feature_names=feature_names,
            values=values,
            sample_size=len(sample.events),
            extracted_at=datetime.now(timezone.utc),
        )

    def summarize_sample(self, sample: KeystrokeSample) -> Dict[str, Any]:
        features = extract_keystroke_features(sample.events)
        return {
            "user_id": sample.user_id,
            "session_id": sample.session_id,
            "feature_signature": session_signature(features),
            "features": features,
            "sample_size": len(sample.events),
        }

    def build_profile(self, samples: List[KeystrokeSample]) -> Dict[str, Any]:
        if not samples:
            return {"sample_count": 0, "feature_means": {}, "feature_order": []}

        extracted = [extract_keystroke_features(sample.events) for sample in samples]
        feature_order = list(extracted[0].keys())
        feature_means = {name: float(sum(record[name] for record in extracted) / len(extracted)) for name in feature_order}
        return {
            "sample_count": len(samples),
            "feature_means": feature_means,
            "feature_order": feature_order,
            "baseline_signature": session_signature(feature_means),
        }
