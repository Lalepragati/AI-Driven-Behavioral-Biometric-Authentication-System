from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import gspread
import httpx
from google.oauth2.service_account import Credentials

from app.core.config import Settings
from app.modules.sheets_integration.schema import sheet_headers, sheet_row, utc_now

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsWriter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.local_spool_dir = settings.local_data_path / "sheets_spool"
        self.local_spool_dir.mkdir(parents=True, exist_ok=True)
        self._client = self._build_client()

    def _build_client(self):
        spreadsheet_id = self.settings.google_sheets_key
        if not spreadsheet_id:
            return None

        if self.settings.google_service_account_json:
            raw_json = Path(self.settings.google_service_account_json)
            if raw_json.exists():
                credentials = Credentials.from_service_account_file(str(raw_json), scopes=SCOPES)
            else:
                service_account_info = json.loads(self.settings.google_service_account_json)
                credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        elif self.settings.google_application_credentials:
            credentials = Credentials.from_service_account_file(self.settings.google_application_credentials, scopes=SCOPES)
        else:
            return None

        return gspread.authorize(credentials).open_by_key(spreadsheet_id)

    @property
    def has_apps_script_hook(self) -> bool:
        return self.settings.has_apps_script_hook

    @property
    def is_enabled(self) -> bool:
        return self._client is not None

    def append_row(self, sheet_name: str, row: Iterable[Any]) -> None:
        values = list(row)
        if self.has_apps_script_hook:
            self._post_to_apps_script(sheet_name, {"values": values})
            return

        if self._client is None:
            self._write_local_spool(sheet_name, {"values": values})
            return

        worksheet = self._get_or_create_worksheet(sheet_name)
        worksheet.append_row(values, value_input_option="USER_ENTERED")

    def append_record(self, sheet_name: str, record: Dict[str, Any]) -> None:
        ordered_values = sheet_row(sheet_name, record)
        if self.has_apps_script_hook:
            self._post_to_apps_script(sheet_name, record)
            return

        if self._client is None:
            self._write_local_spool(sheet_name, record)
            return

        worksheet = self._get_or_create_worksheet(sheet_name)
        headers = sheet_headers(sheet_name)
        if worksheet.row_count == 0:
            worksheet.append_row(headers, value_input_option="USER_ENTERED")
        worksheet.append_row(ordered_values, value_input_option="USER_ENTERED")

    def append_schema_record(self, sheet_name: str, record: Dict[str, Any]) -> None:
        self.append_record(sheet_name, record)

    def _post_to_apps_script(self, sheet_name: str, record: Dict[str, Any]) -> None:
        payload = {
            "token": self.settings.google_apps_script_token,
            "sheet": sheet_name,
            "record": record,
        }
        try:
            response = httpx.post(
                self.settings.google_apps_script_webapp_url,
                json=payload,
                timeout=10.0,
                follow_redirects=True,
            )
            response.raise_for_status()
            result = response.json()
            if not result.get("ok", False):
                raise RuntimeError(f"Apps Script rejected sheet write for '{sheet_name}': {result}")
        except Exception as exc:
            self._write_local_spool(
                sheet_name,
                {
                    **record,
                    "apps_script_error": str(exc),
                    "fallback": "local_spool",
                },
            )

    def _get_or_create_worksheet(self, sheet_name: str):
        try:
            return self._client.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            return self._client.add_worksheet(title=sheet_name, rows=1000, cols=40)

    def _write_local_spool(self, sheet_name: str, payload: Dict[str, Any]) -> None:
        file_path = self.local_spool_dir / f"{sheet_name}.jsonl"
        payload = {**payload, "sheet_name": sheet_name, "captured_at": utc_now()}
        with file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str))
            handle.write("\n")
