from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


@dataclass
class RepositoryPaths:
    base_dir: Path

    @property
    def users_file(self) -> Path:
        return self.base_dir / "users.json"

    @property
    def profiles_file(self) -> Path:
        return self.base_dir / "profiles.json"

    @property
    def sessions_file(self) -> Path:
        return self.base_dir / "sessions.json"

    @property
    def events_file(self) -> Path:
        return self.base_dir / "events.json"


class StateRepository:
    def __init__(self, base_dir: Path) -> None:
        self.paths = RepositoryPaths(base_dir=base_dir)
        self.paths.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_json(self, path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, default=str)

    def upsert_user(self, user_record: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            users = self._read_json(self.paths.users_file, {})
            users[user_record["user_id"]] = user_record
            self._write_json(self.paths.users_file, users)
            return user_record

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        users = self._read_json(self.paths.users_file, {})
        return users.get(user_id)

    def list_users(self) -> List[Dict[str, Any]]:
        users = self._read_json(self.paths.users_file, {})
        return list(users.values())

    def upsert_profile(self, user_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            profiles = self._read_json(self.paths.profiles_file, {})
            profiles[user_id] = profile
            self._write_json(self.paths.profiles_file, profiles)
            return profile

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        profiles = self._read_json(self.paths.profiles_file, {})
        return profiles.get(user_id)

    def append_session(self, session_record: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            sessions = self._read_json(self.paths.sessions_file, [])
            sessions.append(session_record)
            self._write_json(self.paths.sessions_file, sessions)
            return session_record

    def append_event(self, event_record: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            events = self._read_json(self.paths.events_file, [])
            events.append(event_record)
            self._write_json(self.paths.events_file, events)
            return event_record

    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
