from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ModelArtifacts:
    user_id: str
    model_kind: str
    feature_names: List[str]
    model_path: Path
    created_at: str
    threshold: float = 0.5
