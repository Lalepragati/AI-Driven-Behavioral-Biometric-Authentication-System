from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.modules.behavior.schemas import KeystrokeEvent


def collect_typing_timings(events: List[KeystrokeEvent]) -> Dict[str, List[float]]:
    ordered = sorted(events, key=lambda event: event.timestamp)
    key_downs: Dict[str, List[KeystrokeEvent]] = defaultdict(list)
    dwell_times: List[float] = []
    flight_times: List[float] = []
    release_to_press: List[float] = []
    press_to_press: List[float] = []
    rhythm: List[float] = []

    for index, event in enumerate(ordered):
        if event.event_type == "keydown":
            key_downs[event.key].append(event)
            if index > 0:
                previous = ordered[index - 1]
                press_to_press.append(max(event.timestamp - previous.timestamp, 0.0))
                if previous.event_type == "keyup":
                    release_to_press.append(max(event.timestamp - previous.timestamp, 0.0))
                if previous.event_type == "keydown":
                    flight_times.append(max(event.timestamp - previous.timestamp, 0.0))
            rhythm.append(event.timestamp)
        elif event.event_type == "keyup" and key_downs[event.key]:
            start = key_downs[event.key].pop(0)
            dwell_times.append(max(event.timestamp - start.timestamp, 0.0))

    return {
        "dwell_times": dwell_times,
        "flight_times": flight_times,
        "press_to_press": press_to_press,
        "release_to_press": release_to_press,
        "rhythm": rhythm,
        "event_count": [float(len(ordered))],
        "error_events": [float(sum(1 for event in ordered if event.is_error))],
    }
