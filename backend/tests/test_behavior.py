from __future__ import annotations

from app.modules.behavior.features import extract_keystroke_features
from app.modules.behavior.schemas import KeystrokeEvent
from app.modules.risk_engine.scoring import RiskEngine


def test_extract_keystroke_features_produces_expected_columns() -> None:
    events = [
        KeystrokeEvent(key="h", event_type="keydown", timestamp=0.0),
        KeystrokeEvent(key="h", event_type="keyup", timestamp=0.11),
        KeystrokeEvent(key="i", event_type="keydown", timestamp=0.18),
        KeystrokeEvent(key="i", event_type="keyup", timestamp=0.31),
    ]

    features = extract_keystroke_features(events)

    assert features["dwell_mean"] > 0
    assert features["sample_size"] == 4
    assert features["error_rate"] == 0


def test_risk_engine_thresholds() -> None:
    engine = RiskEngine()

    assert engine.score(10, 10).decision == "allow"
    assert engine.score(50, 50).decision == "step_up"
    assert engine.score(90, 95).decision == "block"
