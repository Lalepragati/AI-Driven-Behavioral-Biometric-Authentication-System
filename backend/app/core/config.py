from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Behavioral Authentication Platform"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"
    secret_key: str = Field(default="change-me")
    access_token_expire_minutes: int = 120
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    google_sheets_spreadsheet_id: str = ""
    google_sheets_spreadsheet_url: str = ""
    google_apps_script_webapp_url: str = ""
    google_apps_script_token: str = ""
    google_application_credentials: str = ""
    google_service_account_json: str = ""
    google_sheets_mode: str = "local"
    model_storage_dir: str = "backend/models"
    local_data_dir: str = "backend/data"
    max_login_latency_seconds: float = 2.0

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def model_storage_path(self) -> Path:
        path = Path(self.model_storage_dir)
        return path if path.is_absolute() else self.backend_root / path

    @property
    def local_data_path(self) -> Path:
        path = Path(self.local_data_dir)
        return path if path.is_absolute() else self.backend_root / path

    @property
    def allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def google_sheets_key(self) -> str:
        if self.google_sheets_spreadsheet_id.strip():
            return self.google_sheets_spreadsheet_id.strip()
        if self.google_sheets_spreadsheet_url.strip():
            match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", self.google_sheets_spreadsheet_url)
            if match:
                return match.group(1)
        return ""

    @property
    def has_apps_script_hook(self) -> bool:
        return bool(self.google_apps_script_webapp_url.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
