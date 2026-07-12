from __future__ import annotations

from typing import Any, Dict


def sample_scoring_signal() -> Dict[str, Any]:
    return {
        "symbol": "AAPL",
        "direction": "long",
        "score": 0.73,
        "alpha_id": "alpha_v1",
        "edge_pct": 0.03,
    }


def sample_feature_snapshot() -> Dict[str, Any]:
    return {
        "technical": {"trend": 0.22, "rsi": 58.0, "momentum": 0.18, "last_price": 150.0},
        "order_flow": {"AAPL": {"rel_volume": 1.5, "imbalance": 0.25, "vwap_dist": 0.1}},
        "squeeze": {"AAPL": {"short_interest": 0.12, "borrow_fee": 0.06, "days_to_cover": 4.2}},
        "ml": {"AAPL": {"prob_up": 0.66, "uncertainty": 0.21}},
        "liquidity": {"AAPL": {"adv_ratio": 0.02, "spread_bps": 18.0}},
        "macro": {"growth": 0.2, "inflation": 0.08, "rates": 0.06},
        "sentiment": {"AAPL": {"sentiment": 0.2, "news_score": 0.12, "social_score": 0.18}},
    }


def sample_trade_intent() -> Dict[str, Any]:
    return {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": 10,
        "entry": 150.0,
        "price": 150.0,
        "strategy": "momentum",
        "sector": "TECH",
    }


def sample_portfolio_snapshot() -> Dict[str, Any]:
    return {
        "cash": 100000.0,
        "equity": 100000.0,
        "drawdown": 0.0,
        "gross_exposure": 15000.0,
        "positions": {
            "AAPL": {"qty": 100, "avg_price": 148.0, "market_price": 150.0, "sector": "TECH"}
        },
    }


def sample_regime_snapshot() -> Dict[str, Any]:
    return {"name": "bull", "confidence": 0.75, "risk": 0.2}
