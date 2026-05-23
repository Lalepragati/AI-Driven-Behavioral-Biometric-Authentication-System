from __future__ import annotations

from typing import Any, Dict

import httpx

from app.core.config import Settings


class OllamaExplainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def explain(self, payload: Dict[str, Any]) -> str:
        prompt = self._build_prompt(payload)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url.rstrip('/')}/api/generate",
                    json={
                        "model": self.settings.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "") or self._fallback(payload)
        except Exception:
            return self._fallback(payload)

    def _build_prompt(self, payload: Dict[str, Any]) -> str:
        return (
            "You are a hospital security analyst. Summarize this authentication event in one concise sentence. "
            f"Risk score: {payload.get('risk_score')}. Decision: {payload.get('decision')}. "
            f"Anomaly confidence: {payload.get('anomaly_confidence')}. Signals: {payload.get('signals')}"
        )

    def _fallback(self, payload: Dict[str, Any]) -> str:
        return (
            f"Typing behavior deviates from the baseline with {payload.get('anomaly_confidence', 0):.1f}% anomaly confidence. "
            f"Risk score {payload.get('risk_score', 0):.1f} leads to a {payload.get('decision', 'step_up')} decision."
        )
