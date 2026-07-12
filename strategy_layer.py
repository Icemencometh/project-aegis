from __future__ import annotations

import warnings

warnings.warn(
    "Legacy module strategy_layer.py is deprecated; use aegis.strategies and aegis.marketplace.",
    DeprecationWarning,
    stacklevel=2,
)

from copy import deepcopy
from typing import Any, Dict

from strategies import BreakoutStrategy, MeanReversionStrategy, PairsTradingStrategy, TrendFollowingStrategy
from strategies.base import MarketSnapshot, RegimeSnapshot, RiskBudgetSnapshot, VolSnapshot
from strategy_config import StrategyConfigLoader


LEVERAGED_ETF_HINTS = {"SOXL", "SOXS", "TQQQ", "SQQQ", "UPRO", "SPXU", "SPXL", "SPXS", "FAS", "FAZ"}

REGIME_ALIASES = {
    "BULL": "bull",
    "BULL_TREND": "bull",
    "RISK_ON": "bull",
    "LOW_VOL": "low_vol",
    "LOW_VOL_REGIME": "low_vol",
    "BEAR": "bear",
    "BEAR_TREND": "bear",
    "RISK_OFF": "bear",
    "HIGH_VOL": "high_vol",
    "HIGH_VOL_CRISIS": "high_vol",
    "NEUTRAL": "neutral",
    "RANGE_BOUND": "neutral",
    "UNKNOWN": "neutral",
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _normalize_regime_name(regime_name: Any) -> str:
    label = str(regime_name or "neutral").upper()
    return REGIME_ALIASES.get(label, str(regime_name or "neutral").lower())


def _extract_symbol_vols(vol_snapshot: VolSnapshot) -> Dict[str, float]:
    if not isinstance(vol_snapshot, dict):
        return {}
    if isinstance(vol_snapshot.get("symbols"), dict):
        return {str(k).upper(): _safe_float(v) for k, v in vol_snapshot.get("symbols", {}).items()}

    out: Dict[str, float] = {}
    for key, value in vol_snapshot.items():
        if isinstance(value, (int, float)):
            out[str(key).upper()] = float(value)
    return out


def _infer_vol_regime(atr_percentile: float) -> str:
    if atr_percentile >= 0.85:
        return "extreme"
    if atr_percentile >= 0.65:
        return "high"
    return "normal"


class VolatilitySpikeStrategy:
    name = "volatility_spike"

    def generate(
        self,
        market_snapshot: MarketSnapshot,
        regime_snapshot: RegimeSnapshot,
        vol_snapshot: VolSnapshot,
        risk_budget_snapshot: RiskBudgetSnapshot,
        cfg: Dict[str, Any],
        pairs_signals=None,
    ):
        _ = risk_budget_snapshot
        _ = pairs_signals
        prices = (market_snapshot or {}).get("prices", {}) or {}
        symbol_vols = _extract_symbol_vols(vol_snapshot)
        high_threshold = _safe_float(cfg.get("atr_high_threshold", 3.0), 3.0) / 100.0
        qty_multiplier = _safe_float(cfg.get("high_vol_qty_multiplier", 0.35), 0.35)

        out = []
        for symbol, vol in symbol_vols.items():
            if symbol not in prices:
                continue
            if abs(_safe_float(vol)) < high_threshold:
                continue
            out.append(
                {
                    "type": "DIRECTIONAL",
                    "symbol": symbol,
                    "side": "SELL",
                    "qty": 0,
                    "price": _safe_float(prices[symbol]),
                    "confidence": _clamp(abs(_safe_float(vol)) * 10.0),
                    "metadata": {
                        "strategy": self.name,
                        "strategy_key": self.name,
                        "signal_strength": _clamp(abs(_safe_float(vol)) * 10.0),
                        "regime": str(regime_snapshot.get("regime", "neutral")),
                        "raw_regime": str(regime_snapshot.get("raw_regime", regime_snapshot.get("regime", "neutral"))),
                        "volatility_spike": abs(_safe_float(vol)),
                        "qty_multiplier": qty_multiplier,
                        "entry_rules": ["vol_above_threshold", "defensive_rotation"],
                        "exit_rules": ["volatility_normalizes", "regime_recovers"],
                        "time_stop_bars": int(cfg.get("max_bars_in_trade", 20)),
                        "config": dict(cfg),
                    },
                }
            )
        return out


PairsStrategy = PairsTradingStrategy
VolSpikeStrategy = VolatilitySpikeStrategy


class StrategyLayer:
    def __init__(self, strategies_cfg=None, regimes_cfg=None, config_dir="config"):
        loader = StrategyConfigLoader(config_dir=config_dir)
        self.strategies_cfg = strategies_cfg or loader.load_strategy_config()
        self.regimes_cfg = regimes_cfg or loader.load_regime_map()
        self.cfg = self.strategies_cfg
        self.regime_map = self.regimes_cfg
        self.shared_cfg = {
            "position_sizing": deepcopy(self.strategies_cfg.get("position_sizing", {}) or {}),
            "exit_rules": deepcopy(self.strategies_cfg.get("exit_rules", {}) or {}),
            "volatility_sizing": deepcopy(self.strategies_cfg.get("volatility_sizing", {}) or {}),
        }
        self.strategies = self._init_strategies()
        self.strategy_registry = self.strategies

    def _init_strategies(self):
        return {
            "trend_following": TrendFollowingStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy(),
            "pairs_trading": PairsTradingStrategy(),
            "volatility_spike": VolatilitySpikeStrategy(),
        }

    def _build_strategy_cfg(self, strategy_name: str) -> Dict[str, Any]:
        cfg = deepcopy(self.strategies_cfg.get(strategy_name, {}) or {})
        cfg.setdefault("stop_atr_multiple", _safe_float(self.shared_cfg.get("exit_rules", {}).get("stop_atr_multiple", 2.0), 2.0))
        cfg.setdefault("target_atr_multiple", _safe_float(self.shared_cfg.get("exit_rules", {}).get("target_atr_multiple", 3.0), 3.0))
        cfg.setdefault("trailing_atr_multiple", _safe_float(self.shared_cfg.get("exit_rules", {}).get("trailing_atr_multiple", 2.0), 2.0))
        cfg.setdefault("max_bars_in_trade", int(self.shared_cfg.get("exit_rules", {}).get("max_bars_in_trade", 40) or 40))
        cfg["__shared__"] = deepcopy(self.shared_cfg)
        return cfg

    def _normalize_regime_snapshot(self, regime_snapshot: RegimeSnapshot, vol_snapshot: VolSnapshot | None = None) -> Dict[str, Any]:
        raw = dict(regime_snapshot or {})
        raw_regime = raw.get("regime") or raw.get("regime_label") or "neutral"
        symbol_vols = _extract_symbol_vols(vol_snapshot or {})
        avg_vol = sum(abs(v) for v in symbol_vols.values()) / len(symbol_vols) if symbol_vols else 0.0
        return {
            "regime": _normalize_regime_name(raw_regime),
            "raw_regime": str(raw_regime),
            "trend_strength": _safe_float(raw.get("trend_strength", raw.get("adx", 0.0)), 0.0),
            "volatility": _safe_float(raw.get("volatility", avg_vol), avg_vol),
            "macro": str(raw.get("macro", "neutral")),
        }

    def _normalize_vol_snapshot(self, vol_snapshot: VolSnapshot) -> Dict[str, Any]:
        symbol_vols = _extract_symbol_vols(vol_snapshot or {})
        atr = _safe_float((vol_snapshot or {}).get("atr"), 0.0) if isinstance(vol_snapshot, dict) else 0.0
        if atr <= 0 and symbol_vols:
            atr = sum(abs(v) for v in symbol_vols.values()) / len(symbol_vols)

        raw_pct = (vol_snapshot or {}).get("atr_percentile") if isinstance(vol_snapshot, dict) else None
        atr_percentile = _safe_float(raw_pct, _clamp(atr / 4.0 if atr > 0 else 0.5))
        vol_regime = str((vol_snapshot or {}).get("vol_regime", "")).strip() if isinstance(vol_snapshot, dict) else ""
        if not vol_regime:
            vol_regime = _infer_vol_regime(atr_percentile)

        return {
            "atr": atr,
            "atr_percentile": atr_percentile,
            "vol_regime": vol_regime,
            "symbols": symbol_vols,
        }

    def _normalize_risk_budget_snapshot(self, risk_budget_snapshot: RiskBudgetSnapshot) -> Dict[str, Any]:
        raw = dict(risk_budget_snapshot or {})
        size_cfg = self.shared_cfg.get("position_sizing", {})
        return {
            "equity": _safe_float(raw.get("equity", 0.0), 0.0),
            "risk_per_trade": _safe_float(raw.get("risk_per_trade", size_cfg.get("per_trade_risk_pct", 0.01)), 0.01),
            "max_symbol_exposure": _safe_float(raw.get("max_symbol_exposure", size_cfg.get("per_symbol_cap_pct", 0.10)), 0.10),
            "max_sector_exposure": _safe_float(raw.get("max_sector_exposure", size_cfg.get("sector_cap_pct", 0.25)), 0.25),
            "per_symbol": deepcopy(raw.get("per_symbol", {}) or {}),
            "portfolio": deepcopy(raw.get("portfolio", {}) or {}),
        }

    def _select_strategies_for_regime(self, regime: str):
        regime_key = _normalize_regime_name(regime)
        cfg = self.regimes_cfg.get(regime_key, {}) or self.regimes_cfg.get("neutral", {}) or {}
        return list(cfg.get("strategies", []))

    def generate_strategy_trades(
        self,
        market_snapshot: MarketSnapshot,
        regime_snapshot: RegimeSnapshot,
        vol_snapshot: VolSnapshot,
        risk_budget_snapshot: RiskBudgetSnapshot,
        pairs_signals,
    ):
        normalized_vol = self._normalize_vol_snapshot(vol_snapshot)
        normalized_regime = self._normalize_regime_snapshot(regime_snapshot, normalized_vol)
        normalized_risk = self._normalize_risk_budget_snapshot(risk_budget_snapshot)

        strategy_names = self._select_strategies_for_regime(normalized_regime.get("regime", "neutral"))
        trades = []
        for name in strategy_names:
            strategy = self.strategies.get(name)
            if strategy is None:
                continue
            cfg = self._build_strategy_cfg(name)
            trades.extend(
                strategy.generate(
                    market_snapshot=market_snapshot,
                    regime_snapshot=normalized_regime,
                    vol_snapshot=normalized_vol,
                    risk_budget_snapshot=normalized_risk,
                    cfg=cfg,
                    pairs_signals=pairs_signals,
                )
            )

        return trades
