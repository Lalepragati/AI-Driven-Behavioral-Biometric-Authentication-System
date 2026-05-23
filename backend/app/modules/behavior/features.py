from __future__ import annotations

import hashlib
from statistics import mean
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import entropy, skew, kurtosis

from app.modules.behavior.collector import collect_typing_timings
from app.modules.behavior.schemas import KeystrokeEvent

FEATURE_ORDER = [
    "dwell_mean",
    "dwell_std",
    "dwell_var",
    "dwell_median",
    "dwell_min",
    "dwell_max",
    "flight_mean",
    "flight_std",
    "flight_var",
    "flight_median",
    "flight_min",
    "flight_max",
    "press_to_press_mean",
    "release_to_press_mean",
    "typing_rhythm_cv",
    "typing_entropy",
    "dwell_skew",
    "dwell_kurtosis",
    "key_repeat_ratio",
    "error_rate",
    "sample_size",
]


def _safe_stats(values: List[float]) -> Tuple[float, float, float, float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    array = np.asarray(values, dtype=float)
    return (
        float(np.mean(array)),
        float(np.std(array)),
        float(np.var(array)),
        float(np.median(array)),
        float(np.min(array)),
        float(np.max(array)),
    )


def extract_keystroke_features(events: List[KeystrokeEvent]) -> Dict[str, float]:
    timings = collect_typing_timings(events)
    dwell_times = timings["dwell_times"]
    flight_times = timings["flight_times"]
    press_to_press = timings["press_to_press"]
    release_to_press = timings["release_to_press"]
    rhythm = timings["rhythm"]
    event_count = max(int(timings["event_count"][0]), 1)
    error_events = int(timings["error_events"][0])

    dwell_mean, dwell_std, dwell_var, dwell_median, dwell_min, dwell_max = _safe_stats(dwell_times)
    flight_mean, flight_std, flight_var, flight_median, flight_min, flight_max = _safe_stats(flight_times)
    press_mean = float(np.mean(np.asarray(press_to_press, dtype=float))) if press_to_press else 0.0
    release_mean = float(np.mean(np.asarray(release_to_press, dtype=float))) if release_to_press else 0.0

    rhythm_values = np.asarray(rhythm, dtype=float)
    rhythm_cv = float(np.std(rhythm_values) / (np.mean(rhythm_values) + 1e-6)) if rhythm else 0.0
    if dwell_times:
        buckets = np.histogram(np.asarray(dwell_times, dtype=float), bins=min(10, max(2, len(dwell_times))))[0]
        typing_entropy = float(entropy(buckets + 1e-9))
    else:
        typing_entropy = 0.0

    key_sequence = [event.key for event in events if event.event_type == "keydown"]
    if len(key_sequence) > 1:
        repeats = sum(1 for left, right in zip(key_sequence, key_sequence[1:]) if left == right)
        key_repeat_ratio = repeats / (len(key_sequence) - 1)
    else:
        key_repeat_ratio = 0.0

    error_rate = error_events / event_count

    features = {
        "dwell_mean": dwell_mean,
        "dwell_std": dwell_std,
        "dwell_var": dwell_var,
        "dwell_median": dwell_median,
        "dwell_min": dwell_min,
        "dwell_max": dwell_max,
        "flight_mean": flight_mean,
        "flight_std": flight_std,
        "flight_var": flight_var,
        "flight_median": flight_median,
        "flight_min": flight_min,
        "flight_max": flight_max,
        "press_to_press_mean": press_mean,
        "release_to_press_mean": release_mean,
        "typing_rhythm_cv": rhythm_cv,
        "typing_entropy": typing_entropy,
        "dwell_skew": float(skew(np.asarray(dwell_times, dtype=float))) if len(dwell_times) > 2 else 0.0,
        "dwell_kurtosis": float(kurtosis(np.asarray(dwell_times, dtype=float))) if len(dwell_times) > 3 else 0.0,
        "key_repeat_ratio": key_repeat_ratio,
        "error_rate": error_rate,
        "sample_size": float(len(events)),
    }
    return features


def feature_vector(features: Dict[str, float]) -> Tuple[List[str], List[float]]:
    return FEATURE_ORDER, [float(features.get(name, 0.0)) for name in FEATURE_ORDER]


def session_signature(features: Dict[str, float]) -> str:
    ordered_values = "|".join(f"{name}:{features.get(name, 0.0):.6f}" for name in FEATURE_ORDER)
    return hashlib.sha256(ordered_values.encode("utf-8")).hexdigest()
