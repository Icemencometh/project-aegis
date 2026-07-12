from __future__ import annotations

import warnings

warnings.warn(
    "Legacy module trade_risk_scoring.py is deprecated; use aegis.risk.",
    DeprecationWarning,
    stacklevel=2,
)


class TradeRiskScoringEngine:
    @staticmethod
    def score_trade(trade, portfolio_snapshot, regime_snapshot, vol_snapshot):
        trade = trade or {}
        portfolio_snapshot = portfolio_snapshot or {}
        regime_snapshot = regime_snapshot or {}
        vol_snapshot = vol_snapshot or {}

        qty = abs(float(trade.get("qty", 0.0)))
        price = abs(float(trade.get("price", 0.0)))
        equity = max(float(portfolio_snapshot.get("equity", 0.0)), 1e-9)
        vol = abs(float(vol_snapshot.get("vol", 0.0)))
        regime = str(regime_snapshot.get("regime", "UNKNOWN")).upper()

        notional = qty * price
        risk_perc_equity = notional / equity
        flags = []

        regime_penalty = 0.15
        if regime in {"HIGH_VOL_CRISIS", "RISK_OFF"}:
            regime_penalty = 0.45
            flags.append("HOSTILE_REGIME")
        elif regime in {"BEAR_TREND"}:
            regime_penalty = 0.3
            flags.append("BEAR_REGIME")
        elif regime in {"BULL_TREND", "RISK_ON"}:
            regime_penalty = 0.05

        vol_penalty = min(vol * 10.0, 0.35)
        if vol >= 0.03:
            flags.append("HIGH_VOL")

        correlation_penalty = 0.0
        positions = portfolio_snapshot.get("positions", {}) or {}
        if str(trade.get("symbol", "")).upper() in {str(k).upper() for k in positions}:
            correlation_penalty += 0.15
            flags.append("DUPLICATE_SYMBOL")

        metadata = trade.get("metadata", {}) or {}
        if bool(metadata.get("leveraged_etf")):
            correlation_penalty += 0.10
            flags.append("LEVERAGED_ETF")

        if str(metadata.get("strategy", "")).upper() == "VOLATILITY_SPIKE":
            vol_penalty = min(vol_penalty + 0.10, 0.45)
            flags.append("VOL_SPIKE_SETUP")

        if risk_perc_equity >= 0.1:
            flags.append("OVER_BUDGET")

        raw = risk_perc_equity * 2.5 + regime_penalty + vol_penalty + correlation_penalty
        risk_score = min(max(raw, 0.0), 1.0)

        return {
            "risk_score": risk_score,
            "risk_perc_equity": risk_perc_equity,
            "flags": flags,
        }
