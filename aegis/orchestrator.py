"""AegisPipeline -- wires the module skeletons together into the contract
data flow (PROJECT_AEGIS_OVERVIEW.txt / Aegis_Module_Contracts.md):

    Data -> Features -> Regime -> Strategies -> Scoring Hub -> Alpha Hub
          -> (Capital Allocation -> Strategy concentration cap) -> Risk Engine
          -> Execution Engine -> Broker -> Portfolio

Safe-by-default: this class only ever constructs a PaperBroker unless the
caller explicitly passes a different broker in. It never chooses a live
broker on its own (Aegis_Coding_Standards.txt: "Defaults must be safe (paper
trading, conservative risk)."). Nothing here places a trade outside of
run_cycle, and run_cycle always goes through the Risk Engine before
Execution -- there is no bypass path.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Optional

from .alpha import AlphaHub, CalibrationService, ModelRegistry, PredictionService
from .allocation import CapitalAllocationEngine
from .common.config import load_all_configs
from .common.logging import get_logger
from .data.engine import DataEngine
from .execution import ExecutionEngine, PaperBroker
from .features.engine import FeatureEngine
from .marketplace import (
    StrategyRegistry,
    StrategyRunner,
    StrategySelector,
    enforce_strategy_concentration,
)
from .portfolio import PortfolioManager
from .regime.engine import RegimeEngine
from .risk import RiskEngine
from .scoring import AdaptiveWeightingEngine, ExplainableDecisionEngine, MetaModelEngine, TradeScoringEngine
from .scoring.modules import (
    LiquidityScorer,
    MacroScorer,
    MLScorer,
    OrderFlowScorer,
    RegimeScorer,
    SentimentScorer,
    ShortSqueezeScorer,
    TechnicalScorer,
)
from .strategies import MomentumStrategy


class AegisPipeline:
    def __init__(
        self,
        config_dir: Optional[str] = None,
        broker: Optional[Any] = None,
        env_monitor: Optional[Any] = None,
    ):
        configs = load_all_configs(config_dir)
        self.configs = configs
        self.logger = get_logger("aegis.pipeline")

        # Data -> Features -> Regime
        self.data_engine = DataEngine()
        self.feature_engine = FeatureEngine()
        # No dedicated regime.yaml exists yet; RegimeEngine falls back to its
        # own documented defaults (trend_threshold/high_vol_threshold) until
        # one is added to aegis/config.
        self.regime_engine = RegimeEngine({})

        # Strategy Marketplace
        self.strategy_registry = StrategyRegistry()
        self.strategy_selector = StrategySelector()
        self.strategy_runner = StrategyRunner()

        # Scoring Hub
        scoring_cfg = configs.get("scoring", {})
        self.scoring_engine = TradeScoringEngine(
            scorers=[
                TechnicalScorer(),
                OrderFlowScorer(),
                ShortSqueezeScorer(),
                MLScorer(),
                RegimeScorer(),
                MacroScorer(),
                LiquidityScorer(),
                SentimentScorer(),
            ],
            weighting_engine=AdaptiveWeightingEngine(scoring_cfg),
            explainable_engine=ExplainableDecisionEngine(),
            meta_model=MetaModelEngine(scoring_cfg.get("meta_model", {})),
        )

        # Alpha Hub
        self.model_registry = ModelRegistry()
        self.alpha_hub = AlphaHub(PredictionService(), CalibrationService(), self.model_registry)

        # Portfolio, Risk, Allocation, Execution -- always paper by default
        broker = broker or PaperBroker()
        self.portfolio = PortfolioManager(configs.get("portfolio", {}), broker, self.logger)
        self.risk_engine = RiskEngine(configs.get("risk", {}), self.portfolio, env_monitor, self.logger)
        self.allocation_engine = CapitalAllocationEngine(configs.get("portfolio", {}))
        self.execution_engine = ExecutionEngine(broker, self.portfolio, self.logger, configs.get("execution", {}))
        # Wire the Risk Engine's flatten_positions() to the same execution engine.
        self.risk_engine.execution_engine = self.execution_engine

        self.max_strategy_allocation_pct = float(configs.get("portfolio", {}).get("max_strategy_allocation_pct", 0.0) or 0.0)

    def register_strategy(self, strategy, active: bool = True) -> None:
        self.strategy_registry.register(strategy.name, strategy.metadata(active=active), strategy.entry_point)

    def run_cycle(self, symbol: str, raw_bars: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs one full contract-chain cycle for a symbol.

        `raw_bars` should be the *new* bar(s) for this cycle (typically one,
        for a live/paper tick-by-tick run) -- DataEngine already retains
        everything ingested in prior cycles, and features are computed over
        that full accumulated history, not just what's passed here. Passing
        the same historical bars again each cycle would double-ingest them,
        since DataEngine does not dedupe.
        """
        self.data_engine.ingest_bars(symbol, raw_bars)
        bars = self.data_engine.get_history(symbol)
        feature_snapshot = self.feature_engine.compute(symbol, bars)
        regime_snapshot = self.regime_engine.classify(feature_snapshot)

        all_strategies = list(self.strategy_registry.snapshot().values())
        active = self.strategy_selector.select(strategies=all_strategies)
        candidate_lists = self.strategy_runner.run(symbol, feature_snapshot, regime_snapshot, strategies=active)
        candidates = [candidate for sub in candidate_lists for candidate in (sub or [])]

        empty_result = {
            "symbol": symbol,
            "regime": regime_snapshot,
            "candidates": candidates,
            "scored": [],
            "trade_intents": [],
            "approved": [],
            "rejected": [],
            "fills": [],
        }
        if not candidates:
            return empty_result

        scored = self.scoring_engine.score_trades(candidates, feature_snapshot, regime_snapshot)
        trade_intents = [self.alpha_hub.produce_trade_intent(trade) for trade in scored]

        portfolio_snapshot = self.portfolio.snapshot()
        sized = self.allocation_engine.allocate(portfolio_snapshot, {}, trade_intents)
        if self.max_strategy_allocation_pct:
            sized = enforce_strategy_concentration(sized, portfolio_snapshot, self.max_strategy_allocation_pct)

        approved, rejected = self.risk_engine.evaluate_trades(sized)
        fills = [self.execution_engine.execute_trade_intent(trade) for trade in approved]

        return {
            "symbol": symbol,
            "regime": regime_snapshot,
            "candidates": candidates,
            "scored": scored,
            "trade_intents": sized,
            "approved": approved,
            "rejected": rejected,
            "fills": fills,
        }


def _default_bar_from_payload(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    price = float(payload.get("price", 100.0) or 100.0)
    return {
        "timestamp": _dt.datetime.utcnow().isoformat(),
        "open": price,
        "high": float(payload.get("high", price * 1.01) or (price * 1.01)),
        "low": float(payload.get("low", price * 0.99) or (price * 0.99)),
        "close": float(payload.get("close", price) or price),
        "volume": float(payload.get("volume", 1000.0) or 1000.0),
    }


def run_daily_once(symbol: str = "SPY", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compatibility adapter used by legacy root entrypoints."""
    pipeline = AegisPipeline()
    pipeline.register_strategy(MomentumStrategy())
    bar = _default_bar_from_payload(payload)
    return pipeline.run_cycle(str(symbol), [bar])


def run_robot(symbol: str = "SPY", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Primary runtime adapter for root `main.py`."""
    return run_daily_once(symbol=symbol, payload=payload)


def run_scheduler(hour: int = 7, minute: int = 0, symbol: str = "SPY") -> None:
    """Scheduler adapter for root `scheduler.py`."""
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
    except Exception:
        result = run_daily_once(symbol=symbol)
        print("APScheduler is not installed; executed one Aegis cycle instead.")
        print("Approved:", len(result.get("approved", [])))
        print("Rejected:", len(result.get("rejected", [])))
        return

    def _job() -> None:
        outcome = run_daily_once(symbol=symbol)
        print("Aegis scheduled cycle complete.")
        print("Approved:", len(outcome.get("approved", [])))
        print("Rejected:", len(outcome.get("rejected", [])))

    scheduler = BlockingScheduler()
    scheduler.add_job(_job, "cron", hour=int(hour), minute=int(minute))
    print(f"Aegis scheduler started. Daily job set for {int(hour):02d}:{int(minute):02d}.")
    scheduler.start()
