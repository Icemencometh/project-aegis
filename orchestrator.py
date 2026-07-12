from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from aegis.orchestrator import run_daily_once as _run_daily_once
from aegis.orchestrator import run_robot as _run_robot
from aegis.orchestrator import run_scheduler as _run_scheduler

warnings.warn(
    "Root orchestrator.py is legacy compatibility only; use aegis.orchestrator.",
    DeprecationWarning,
    stacklevel=2,
)


def run_day(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(data or {})
    symbol = str(payload.get("symbol") or payload.get("ticker") or "SPY")
    return _run_daily_once(symbol=symbol, payload=payload)


def run_daily_once(symbol: str = "SPY", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _run_daily_once(symbol=symbol, payload=payload)


def run_robot(symbol: str = "SPY", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _run_robot(symbol=symbol, payload=payload)


def run_scheduler(hour: int = 7, minute: int = 0, symbol: str = "SPY") -> None:
    _run_scheduler(hour=hour, minute=minute, symbol=symbol)
