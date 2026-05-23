from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.modules.auth.service import AuthService
from app.modules.behavior.service import BehaviorService
from app.modules.ml_engine.service import BehaviorMLService
from app.modules.risk_engine.scoring import RiskEngine
from app.modules.sheets_integration.client import SheetsWriter
from app.services.ollama_explainer import OllamaExplainer
from app.services.state_repository import StateRepository


@lru_cache(maxsize=1)
def get_state_repository() -> StateRepository:
    settings = get_settings()
    return StateRepository(settings.local_data_path)


@lru_cache(maxsize=1)
def get_sheets_writer() -> SheetsWriter:
    return SheetsWriter(get_settings())


@lru_cache(maxsize=1)
def get_behavior_service() -> BehaviorService:
    return BehaviorService()


@lru_cache(maxsize=1)
def get_ml_service() -> BehaviorMLService:
    settings = get_settings()
    return BehaviorMLService(settings.model_storage_path, get_state_repository())


@lru_cache(maxsize=1)
def get_risk_engine() -> RiskEngine:
    return RiskEngine()


@lru_cache(maxsize=1)
def get_ollama_explainer() -> OllamaExplainer:
    return OllamaExplainer(get_settings())


@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    return AuthService(
        state_repository=get_state_repository(),
        sheets_writer=get_sheets_writer(),
        behavior_service=get_behavior_service(),
        ml_service=get_ml_service(),
        risk_engine=get_risk_engine(),
        ollama_explainer=get_ollama_explainer(),
    )
