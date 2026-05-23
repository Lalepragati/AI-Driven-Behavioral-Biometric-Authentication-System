from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class SheetSchema:
    name: str
    columns: List[str]


SHEETS: Dict[str, SheetSchema] = {
    "Users": SheetSchema("Users", ["user_id", "name", "email", "role", "created_at", "status"]),
    "AI Agent Actions": SheetSchema(
        "AI Agent Actions",
        ["agent_name", "timestamp", "action", "target_user", "result"],
    ),
    "Security Alerts": SheetSchema(
        "Security Alerts",
        ["alert_id", "timestamp", "severity", "message", "status"],
    ),
    "Authentication Logs": SheetSchema(
        "Authentication Logs",
        ["timestamp", "user_id", "login_status", "ip_address", "device", "session_id"],
    ),
    "Session Analytics": SheetSchema(
        "Session Analytics",
        ["session_id", "user_id", "avg_dwell_time", "typing_speed", "consistency_score"],
    ),
    "Risk Events": SheetSchema(
        "Risk Events",
        ["timestamp", "user_id", "risk_score", "anomaly_score", "decision", "reason"],
    ),
}


def sheet_headers(sheet_name: str) -> List[str]:
    return list(SHEETS[sheet_name].columns)


def sheet_row(sheet_name: str, record: Dict[str, Any]) -> List[Any]:
    return [record.get(column, "") for column in sheet_headers(sheet_name)]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
