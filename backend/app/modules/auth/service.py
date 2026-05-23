from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schemas import LoginRequest, LoginResponse, RegisterRequest
from app.modules.behavior.service import BehaviorService
from app.modules.ml_engine.service import BehaviorMLService
from app.modules.risk_engine.scoring import RiskAssessment, RiskEngine
from app.modules.sheets_integration.client import SheetsWriter
from app.services.ollama_explainer import OllamaExplainer
from app.services.state_repository import StateRepository


@dataclass
class AuthService:
    state_repository: StateRepository
    sheets_writer: SheetsWriter
    behavior_service: BehaviorService
    ml_service: BehaviorMLService
    risk_engine: RiskEngine
    ollama_explainer: OllamaExplainer

    def register_user(self, request: RegisterRequest) -> Dict[str, Any]:
        if self.state_repository.get_user(request.user_id):
            raise ValueError(f"User '{request.user_id}' already exists")

        user_record = {
            "user_id": request.user_id,
            "password_hash": hash_password(request.password),
            "role": request.role,
            "full_name": request.full_name,
            "email": request.email,
            "created_at": self.state_repository.now(),
            "active": True,
        }
        self.state_repository.upsert_user(user_record)
        self.sheets_writer.append_schema_record(
            "Users",
            {
                "user_id": request.user_id,
                "name": request.full_name or request.user_id,
                "email": request.email or "",
                "role": request.role,
                "created_at": user_record["created_at"],
                "status": "active",
            },
        )
        return {"user_id": request.user_id, "role": request.role, "created_at": user_record["created_at"]}

    async def evaluate_login(self, request: LoginRequest) -> LoginResponse:
        user = self.state_repository.get_user(request.user_id)
        if not user:
            raise ValueError("Unknown user")
        if not verify_password(request.password, user["password_hash"]):
            risk = self.risk_engine.score(typing_deviation=100.0, anomaly_confidence=100.0, failed_attempts=request.failed_attempts + 1)
            explanation = await self.ollama_explainer.explain(
                {
                    "risk_score": risk.score,
                    "decision": risk.decision,
                    "anomaly_confidence": 100.0,
                    "signals": risk.signals,
                }
            )
            self._log_session(
                request,
                risk,
                explanation,
                model_kind="password_mismatch",
                token=None,
                anomaly_confidence=100.0,
                login_status="failed",
            )
            raise ValueError("Invalid credentials")

        feature_summary = self.behavior_service.summarize_sample(request.sample)
        features = feature_summary["features"]
        profile = self.state_repository.get_profile(request.user_id) or {}

        if self.ml_service.has_model(request.user_id):
            prediction = self.ml_service.predict(request.user_id, features)
            anomaly_confidence = prediction.anomaly_confidence
            model_kind = prediction.model_kind
        else:
            training_result = self.ml_service.train_user_model(request.user_id, [features])
            anomaly_confidence = 0.0
            model_kind = training_result["model_kind"]

        typing_deviation = self._compute_typing_deviation(features, profile.get("feature_means", {}))
        historical_inconsistency = float(profile.get("historical_inconsistency", 0.0))
        risk = self.risk_engine.score(
            typing_deviation=typing_deviation,
            anomaly_confidence=anomaly_confidence,
            failed_attempts=request.failed_attempts,
            historical_inconsistency=historical_inconsistency,
        )
        explanation = await self.ollama_explainer.explain(
            {
                "risk_score": risk.score,
                "decision": risk.decision,
                "anomaly_confidence": anomaly_confidence,
                "signals": risk.signals,
            }
        )
        token = create_access_token(
            request.user_id,
            additional_claims={
                "role": user.get("role"),
                "session_id": request.sample.session_id,
            },
        ) if risk.decision != "block" else None

        self._log_session(
            request,
            risk,
            explanation,
            model_kind=model_kind,
            token=token,
            anomaly_confidence=anomaly_confidence,
            login_status="success" if risk.decision == "allow" else "step_up_required" if risk.decision == "step_up" else "blocked",
        )

        if risk.decision == "allow" and not self.ml_service.has_model(request.user_id):
            self.ml_service.train_user_model(request.user_id, [features])

        return LoginResponse(
            user_id=request.user_id,
            session_id=request.sample.session_id,
            risk_score=risk.score,
            decision=risk.decision,
            anomaly_confidence=anomaly_confidence,
            token=token,
            explanation=explanation,
            model_kind=model_kind,
            signals=risk.signals,
        )

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        user = self.state_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        profile = self.state_repository.get_profile(user_id) or {}
        return {"user": {k: v for k, v in user.items() if k != "password_hash"}, "profile": profile}

    def _compute_typing_deviation(self, features: Dict[str, float], baseline: Dict[str, float]) -> float:
        if not baseline:
            return 0.0
        differences = []
        for key, baseline_value in baseline.items():
            current = float(features.get(key, 0.0))
            scale = abs(float(baseline_value)) + 1e-6
            differences.append(abs(current - float(baseline_value)) / scale)
        if not differences:
            return 0.0
        return max(0.0, min(100.0, float(sum(differences) / len(differences) * 100.0)))

    def _log_session(
        self,
        request: LoginRequest,
        risk: RiskAssessment,
        explanation: str,
        model_kind: str,
        token: str | None,
        anomaly_confidence: float,
        login_status: str,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        feature_summary = self.behavior_service.summarize_sample(request.sample)
        features = feature_summary["features"]
        session_duration_seconds = max(request.sample.events[-1].timestamp - request.sample.events[0].timestamp, 0.001) if request.sample.events else 0.001
        keydown_count = sum(1 for event in request.sample.events if event.event_type == "keydown")
        avg_dwell_time = float(features.get("dwell_mean", 0.0))
        typing_speed = float(keydown_count / session_duration_seconds)
        consistency_score = float(max(0.0, min(100.0, 100.0 - (features.get("typing_rhythm_cv", 0.0) * 100.0))))
        reason = explanation if explanation else f"Risk score {risk.score:.1f} generated decision {risk.decision}."

        session_record = {
            "user_id": request.user_id,
            "session_id": request.sample.session_id,
            "decision": risk.decision,
            "risk_score": risk.score,
            "anomaly_confidence": anomaly_confidence,
            "model_kind": model_kind,
            "token_issued": bool(token),
            "captured_at": timestamp,
            "explanation": explanation,
            "signals": risk.signals,
        }
        self.state_repository.append_session(session_record)
        self.sheets_writer.append_schema_record(
            "Authentication Logs",
            {
                "timestamp": timestamp,
                "user_id": request.user_id,
                "login_status": login_status,
                "ip_address": request.ip_address or request.sample.context.get("ip_address", "") or "",
                "device": request.device or request.sample.context.get("device", "") or "",
                "session_id": request.sample.session_id,
            },
        )
        self.sheets_writer.append_schema_record(
            "Session Analytics",
            {
                "session_id": request.sample.session_id,
                "user_id": request.user_id,
                "avg_dwell_time": round(avg_dwell_time, 6),
                "typing_speed": round(typing_speed, 6),
                "consistency_score": round(consistency_score, 6),
            },
        )
        self.sheets_writer.append_schema_record(
            "Risk Events",
            {
                "timestamp": timestamp,
                "user_id": request.user_id,
                "risk_score": round(risk.score, 6),
                "anomaly_score": round(anomaly_confidence, 6),
                "decision": risk.decision,
                "reason": reason,
            },
        )
        if risk.decision in {"step_up", "block"}:
            severity = "high" if risk.decision == "block" else "medium"
            self.sheets_writer.append_schema_record(
                "Security Alerts",
                {
                    "alert_id": f"{request.sample.session_id}-{risk.decision}",
                    "timestamp": timestamp,
                    "severity": severity,
                    "message": reason,
                    "status": "open" if risk.decision == "block" else "review",
                },
            )
