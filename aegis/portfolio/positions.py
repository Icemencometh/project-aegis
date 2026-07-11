from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    symbol: str
    qty: int = 0
    avg_price: float = 0.0