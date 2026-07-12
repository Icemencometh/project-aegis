"""Data Engine (Aegis_Module_Contracts.md: "Ingest, validate, normalize, and
store market and event data.").

Contract:
- Must not depend on strategy or scoring logic.
- Must expose a read-only interface for downstream modules.
- Must tag data with timestamps, symbols, and versions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

REQUIRED_BAR_FIELDS = ("timestamp", "open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class Bar:
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    version: str = "v1"


class DataEngine:
    """Ingests, validates, normalizes, and stores OHLCV bars in memory.

    Downstream modules only ever get copies (lists of Bar / dict snapshots),
    never a reference into internal storage, satisfying the "read-only
    interface for downstream modules" contract requirement.
    """

    def __init__(self, version: str = "v1"):
        self.version = str(version)
        self._series: Dict[str, List[Bar]] = {}

    def ingest_bar(self, symbol: str, raw_bar: Dict[str, Any]) -> Bar:
        bar = self._normalize(symbol, raw_bar)
        self._series.setdefault(bar.symbol, []).append(bar)
        return bar

    def ingest_bars(self, symbol: str, raw_bars: List[Dict[str, Any]]) -> List[Bar]:
        return [self.ingest_bar(symbol, raw_bar) for raw_bar in raw_bars]

    def get_history(self, symbol: str, lookback: Optional[int] = None) -> List[Bar]:
        series = list(self._series.get(str(symbol), []))
        if lookback is not None:
            series = series[-int(lookback):]
        return series

    def get_latest(self, symbol: str) -> Optional[Bar]:
        series = self._series.get(str(symbol))
        return series[-1] if series else None

    def symbols(self) -> List[str]:
        return sorted(self._series)

    def _normalize(self, symbol: str, raw_bar: Dict[str, Any]) -> Bar:
        missing = [key for key in REQUIRED_BAR_FIELDS if key not in raw_bar]
        if missing:
            raise ValueError(f"DataEngine: bar for {symbol!r} missing fields {missing}")
        return Bar(
            symbol=str(symbol),
            timestamp=str(raw_bar["timestamp"]),
            open=float(raw_bar["open"]),
            high=float(raw_bar["high"]),
            low=float(raw_bar["low"]),
            close=float(raw_bar["close"]),
            volume=float(raw_bar["volume"]),
            version=self.version,
        )
