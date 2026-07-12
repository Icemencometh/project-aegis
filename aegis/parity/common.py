from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class ParityResult:
    name: str
    ok: bool
    diff: float
    threshold: float
    details: Dict[str, Any]


def load_parity_config(config_path: str | None = None) -> Dict[str, Any]:
    path = Path(config_path or "aegis/config/parity.yaml")
    if not path.exists():
        return {
            "thresholds": {
                "scoring": 0.25,
                "risk": 0.25,
                "allocation": 0.35,
                "regime": 0.40,
                "execution": 0.10,
                "portfolio": 0.25,
            }
        }
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return dict(loaded)


def get_threshold(config: Dict[str, Any], name: str, default: float) -> float:
    return float((config.get("thresholds") or {}).get(name, default))


def bounded_ratio(a: float, b: float) -> float:
    a = float(a)
    b = float(b)
    den = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / den
