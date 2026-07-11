from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

TradeIntent = Dict[str, Any]
ScoredTrade = Dict[str, Any]


@dataclass
class RiskDecision:
    allowed: bool
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
