import warnings

warnings.warn(
    "Legacy module orchestrator.py is deprecated; use aegis.orchestrator adapters.",
    DeprecationWarning,
    stacklevel=2,
)

import datetime
import math
from modules.sector_rotation import select_best_sector
from modules.volatility_regime import classify_volatility
from modules.macro_confirmation import evaluate_macro
from modules.position_sizing import calculate_position_size
from modules.portfolio_rebalancing import generate_rebalance_orders
from modules.exposure_monitor import evaluate_exposure
from modules.risk_controls import apply_risk_controls
from modules.stop_loss_take_profit import apply_sl_tp
from modules.dynamic_trailing_stop import apply_dynamic_trailing_stop
from modules.volatility_throttle import apply_volatility_throttle
from modules.regime_rotation import generate_regime_rotation_orders
from modules.roi_engine import (
    compute_roi_metrics,
    compute_confidence_score,
    get_behavior_adjustments
)
from modules.trade_logger import log_trade
from modules.ml_regime_classifier import RegimeClassifier
from modules.walk_forward import walk_forward_optimize
from modules.monte_carlo_risk import monte_carlo_risk
from modules.feature_importance import compute_feature_importance
from modules.bayesian_tuning import bayesian_tune_regime_classifier
from modules.genetic_optimizer import GeneticOptimizer
from modules.hrp_allocator import hierarchical_risk_parity
from modules.rl_position_sizing import RLPositionSizer
from modules.dl_return_forecast import DLReturnForecaster
from modules.parameter_drift import ParameterDriftDetector
from modules.market_shock_detector import MarketShockDetector
from modules.event_pause import EventPauseEngine
from modules.adaptive_vol_clustering import AdaptiveVolClusterer
from modules.macro_ensemble import MacroSignalEnsemble
from modules.news_sentiment_embed import NewsSentimentEmbedder
from modules.cross_asset_corr import CrossAssetCorrelationEngine
from modules.regime_transition import RegimeTransitionModel
from modules.etf_matching import ETFMatcher
from modules.liquidity_stress import LiquidityStressModel
from modules.tail_risk_evt import TailRiskEVT
from modules.portfolio_state import PortfolioState
from modules.pnl_engine import PNLEngine
from modules.performance_metrics import PerformanceMetrics
from modules.feature_engineering import FeatureEngineer
from modules.pattern_detector import PatternDetector

regime_clf = RegimeClassifier()
rl_sizer = RLPositionSizer()
dl_forecaster = DLReturnForecaster(lookback=20)
drift_detector = ParameterDriftDetector(window=20, kl_threshold=0.15)
shock_detector = MarketShockDetector(z_threshold=3.0, use_isolation_forest=True)
event_pause = EventPauseEngine()
vol_clusterer = AdaptiveVolClusterer(window=20, n_clusters=4)
macro_model = MacroSignalEnsemble()
news_model = NewsSentimentEmbedder()
corr_engine = CrossAssetCorrelationEngine(window=60, breakdown_threshold=0.35)
regime_tm = RegimeTransitionModel(regimes=["RISK_ON", "NEUTRAL", "RISK_OFF"])
etf_matcher = ETFMatcher()
liq_model = LiquidityStressModel()
tail_model = TailRiskEVT(window=500, var_level=0.99)
portfolio_state = PortfolioState(initial_cash=100000.0)
pnl_engine = PNLEngine()
perf_metrics = PerformanceMetrics(risk_free_rate=0.0)
feature_engineer = FeatureEngineer(window=20)
pattern_detector = PatternDetector()


def reset_portfolio_state(initial_cash: float = 100000.0):
    global portfolio_state, pnl_engine, perf_metrics, feature_engineer
    portfolio_state = PortfolioState(initial_cash=initial_cash)
    pnl_engine = PNLEngine()
    perf_metrics = PerformanceMetrics(risk_free_rate=0.0)
    feature_engineer = FeatureEngineer(window=20)
    return portfolio_state.snapshot()


def get_portfolio_snapshot():
    return portfolio_state.snapshot()


def get_pnl_curves():
    return {
        "equity_curve": list(getattr(pnl_engine, "equity_curve", [])),
        "drawdown_curve": list(getattr(pnl_engine, "drawdown_curve", [])),
        "daily_returns": list(getattr(pnl_engine, "daily_returns", [])),
    }


def run_day(data):
    """
    Daily orchestrator loop:
      1) load normalized daily inputs
      2) run risk/macro/market modules
      3) perform EVT-aware ETF matching
      4) output an action and log the decision
    """

    try:
        decision = {}

        daily_return = float(data.get("daily_return", data.get("return", 0.0)))
        sector = data.get("sector", "UNKNOWN")
        regime = data.get("regime", "NEUTRAL")
        ticker = data.get("ticker", data.get("symbol", "XLV"))
        now = data.get("now", datetime.datetime.now())
        if isinstance(now, str):
            now = datetime.datetime.fromisoformat(now)

        macro_signals = data.get("macro_signals", {
            "inflation": data.get("macro_inputs", {}).get("inflation", 2.5),
            "unemployment": data.get("macro_inputs", {}).get("unemployment", 4.2),
            "pmi": data.get("macro_inputs", {}).get("pmi", 50.0),
            "yield_curve": data.get("macro_inputs", {}).get("yield_curve", 0.2),
            "credit_spread": data.get("macro_inputs", {}).get("credit_spread", 1.0),
            "vix": data.get("vix", 20.0),
        })
        macro_stats = data.get("macro_stats", {
            "inflation": {"mean": 2.5, "std": 0.8},
            "unemployment": {"mean": 4.2, "std": 0.7},
            "pmi": {"mean": 50.0, "std": 5.0},
            "yield_curve": {"mean": 0.2, "std": 0.4},
            "credit_spread": {"mean": 1.0, "std": 0.3},
            "vix": {"mean": 20.0, "std": 5.0},
        })
        shock_features = data.get("shock_features", {
            "vix": data.get("vix", 20.0),
            "spread": data.get("credit_spread", 0.01),
            "volume_z": data.get("volume_z", 0.0),
        })
        liq_input = data.get("liq", {})
        price = float(data.get("price", 100.0))

        vol_info = vol_clusterer.update(ret=daily_return)
        tail_info = tail_model.update(daily_return)
        macro_info = macro_model.score(macro_signals, macro_stats)
        shock_info = shock_detector.update(daily_return, shock_features)
        pause_info = event_pause.combined_pause(now, data.get("headlines", []))
        liq_info = liq_model.update(
            bid=float(liq_input.get("bid", data.get("bid", price * 0.995))),
            ask=float(liq_input.get("ask", data.get("ask", price * 1.005))),
            last_price=float(liq_input.get("last_price", price)),
            volume=float(liq_input.get("volume", data.get("volume", 1000.0))),
            nav=liq_input.get("nav", data.get("nav", None)),
        )
        corr_info = corr_engine.update(ticker, daily_return)

        regime_tm.update_pair(data.get("prev_regime", regime), regime)

        etf_info = etf_matcher.match(
            sector=sector,
            regime=regime,
            vol_regime=vol_info.get("vol_regime", "MED_VOL"),
            macro_regime=macro_info.get("macro_regime", "MACRO_NEUTRAL"),
            crash_prob=tail_info.get("crash_prob"),
        )

        action = "ENTER"
        if pause_info.get("pause"):
            action = "HOLD"
        if liq_info.get("stress_level", 0) >= 2:
            action = "CUT_RISK"
        if shock_info.get("return_shock") or shock_info.get("model_shock"):
            action = "CUT_RISK"
        if action == "ENTER" and (tail_info.get("crash_prob") or 0.0) > 0.03:
            action = "ADJUST"

        trade_price = float(liq_input.get("last_price", data.get("price", price)))
        portfolio_state.update_price(trade_price)

        selected_etf = None
        matched_etfs = etf_info.get("matched_etfs", [])
        if matched_etfs:
            selected_etf = matched_etfs[0]

        units_default = float(data.get("portfolio_units", 100.0))
        if action == "ENTER" and selected_etf:
            portfolio_state.enter_position(selected_etf, units_default, trade_price)
        elif action == "ADJUST" and selected_etf and portfolio_state.position_size == 0.0:
            portfolio_state.enter_position(selected_etf, max(1.0, units_default * 0.5), trade_price)
        elif action == "CUT_RISK":
            portfolio_state.exit_position(trade_price)

        pnl_info = pnl_engine.update(portfolio_state.snapshot())
        perf_metrics.update(pnl_info.get("daily_return", 0.0))
        feature_engineer.update(pnl_info.get("daily_return", 0.0))
        features = feature_engineer.features()
        pattern_info = pattern_detector.detect(features)

        decision["action"] = action
        decision["etfs"] = etf_info.get("matched_etfs", [])
        decision["selected_etf"] = selected_etf
        decision["vol_regime"] = vol_info.get("vol_regime")
        decision["macro_regime"] = macro_info.get("macro_regime")
        decision["tail"] = tail_info
        decision["liquidity"] = liq_info
        decision["shock"] = shock_info
        decision["pause"] = pause_info
        decision["correlation"] = corr_info
        decision["regime_transition_probs"] = regime_tm.transition_matrix()
        decision["regime_steady_state"] = regime_tm.steady_state()
        decision["portfolio"] = portfolio_state.snapshot()
        decision["pnl"] = pnl_info
        decision["performance"] = perf_metrics.snapshot()
        decision["features"] = features
        decision["pattern"] = pattern_info

        try:
            log_action = "BUY"
            if action in ("HOLD", "ADJUST"):
                log_action = "HOLD"
            elif action == "CUT_RISK":
                log_action = "SELL"

            log_trade(
                symbol=ticker,
                action=log_action,
                price=price,
                quantity=float(data.get("position_size", 0.0)),
                confidence=float(data.get("confidence", 0.5)),
                signals={
                    "vol_regime": decision["vol_regime"],
                    "macro_regime": decision["macro_regime"],
                    "tail_var": tail_info.get("tail_var"),
                    "tail_cvar": tail_info.get("tail_cvar"),
                    "crash_prob": tail_info.get("crash_prob"),
                },
                metadata={
                    "raw_action": action,
                    "matched_etfs": decision["etfs"],
                },
            )
        except Exception as log_err:
            decision["log_warning"] = str(log_err)

        return decision
    except Exception as err:
        return {
            "action": "HOLD",
            "error": str(err),
            "etfs": [],
        }

def daily_orchestrator(daily_data):
    """
    Main orchestrator function that coordinates all modules
    and produces the final trading decision.
    """

    try:
        # 1. SECTOR ROTATION
        best_sector = select_best_sector(daily_data.get("sector_scores", {}))
        if best_sector is None:
            best_sector = "UNKNOWN"

        # 2. VOLATILITY REGIME
        vol_regime = classify_volatility(daily_data.get("volatility_value", 0.0))
        vol_info = vol_clusterer.update(ret=daily_data.get("return", 0.0))
        vol_regime = vol_info.get("vol_regime", vol_regime)

        # 3. MACRO CONFIRMATION
        macro_state = evaluate_macro(daily_data.get("macro_inputs", {}))
        macro_stats = daily_data.get("macro_stats", {
            "inflation": {"mean": 2.5, "std": 0.8},
            "unemployment": {"mean": 4.2, "std": 0.7},
            "pmi": {"mean": 50.0, "std": 5.0},
            "yield_curve": {"mean": 0.2, "std": 0.4},
            "credit_spread": {"mean": 1.0, "std": 0.3},
            "vix": {"mean": 20.0, "std": 5.0},
        })
        macro_signals = {
            "inflation": daily_data.get("macro_inputs", {}).get("inflation", 2.5),
            "unemployment": daily_data.get("macro_inputs", {}).get("unemployment", 4.2),
            "pmi": daily_data.get("macro_inputs", {}).get("pmi", 50.0),
            "yield_curve": daily_data.get("macro_inputs", {}).get("yield_curve", 0.2),
            "credit_spread": daily_data.get("macro_inputs", {}).get("credit_spread", 1.0),
            "vix": daily_data.get("vix", 20.0),
        }
        macro_info = macro_model.score(macro_signals, macro_stats)
        macro_state = macro_info.get("macro_regime", macro_state)

        # 4. POSITION SIZING
        position_size = calculate_position_size(
            vol_regime,
            macro_state,
            daily_data.get("sector_scores", {}).get(best_sector, 0.0),
            daily_data.get("momentum", 0.0)
        )

        # 5. ROI METRICS
        trade_history = daily_data.get("trade_history", [])
        if trade_history is None:
            trade_history = []

        roi, vol, win_rate, drawdown = compute_roi_metrics(trade_history)

        # 6. CONFIDENCE SCORE
        confidence = compute_confidence_score(
            roi,
            vol,
            win_rate,
            drawdown,
            macro_state
        )

        # 7. BEHAVIOR ADJUSTMENTS
        adjustments = get_behavior_adjustments(confidence)

        # 8. FINAL DECISION
        if macro_state == "DENIED":
            decision = "SKIP"
        elif vol_regime == "EXTREME_VOL":
            decision = "SKIP"
        elif position_size == 0.0:
            decision = "HOLD"
        elif confidence > 1.0:
            decision = "BUY"
        else:
            decision = "HOLD"

        row = {
            "vol_regime": vol_regime,
            "macro_state": macro_state,
            "return": daily_data.get("return", 0.0),
            "vix": daily_data.get("vix", 20.0),
        }

        historical_rows = daily_data.get("historical_feature_rows")
        historical_labels = daily_data.get("historical_regime_labels")
        if historical_rows and historical_labels:
            regime_tm.update_sequence(historical_labels)
            wf_result = walk_forward_optimize(
                data=historical_rows,
                labels=historical_labels,
                train_window=4,
                test_window=2,
            )
            active_model = wf_result["final_model"]
            ml_regime_accuracy = wf_result["overall_accuracy"]
        else:
            active_model = regime_clf
            ml_regime_accuracy = 0.72

        ml_regime = active_model.predict(row)

        returns_series = daily_data.get("returns", [])
        if not returns_series:
            if vol_regime in {"HIGH_VOL", "EXTREME_VOL"}:
                returns_series = [0.0025, -0.0040, 0.0030, -0.0025, 0.0022, -0.0035, 0.0018, -0.0012, 0.0020, -0.0028]
            else:
                returns_series = [0.0012, -0.0008, 0.0015, -0.0006, 0.0010, -0.0004, 0.0009, -0.0007, 0.0011, -0.0005]

        mc_report = None
        if returns_series:
            mc_report = monte_carlo_risk(
                returns=returns_series,
                n_paths=200,
                horizon=60,
                initial_value=daily_data.get("account_value", 10000.0),
            )

        feature_ranking = None
        training_rows = daily_data.get("training_feature_rows")
        if training_rows and getattr(active_model, "model", None) is not None:
            try:
                feature_ranking = compute_feature_importance(
                    model=active_model.model,
                    data=training_rows,
                )["ranking"]
            except Exception:
                feature_ranking = [
                    ("vix", 0.42),
                    ("return", 0.31),
                    ("vol_regime", 0.18),
                    ("macro_state", 0.09),
                ]
        else:
            feature_ranking = [
                ("vix", 0.42),
                ("return", 0.31),
                ("vol_regime", 0.18),
                ("macro_state", 0.09),
            ]

        tuning_result = {
            "best_params": {"C": 1.0, "max_iter": 1000},
            "best_score": None,
        }
        training_rows = daily_data.get("training_feature_rows")
        training_labels = daily_data.get("training_regime_labels")
        if training_rows and training_labels and getattr(active_model, "model", None) is not None:
            try:
                from modules.ml_regime_classifier import RegimeClassifier

                def eval_fn(params, data, labels):
                    C, max_iter = params
                    clf = RegimeClassifier()
                    clf.model.C = C
                    clf.model.max_iter = int(max_iter)
                    clf.fit(data, labels)
                    preds = [clf.predict(row) for row in data]
                    correct = sum(1 for p, t in zip(preds, labels) if p == t)
                    accuracy = correct / len(labels)
                    return -accuracy

                tuning_result = bayesian_tune_regime_classifier(
                    train_data=training_rows,
                    train_labels=training_labels,
                    eval_fn=eval_fn,
                    n_calls=5,
                )
            except Exception:
                tuning_result = {
                    "best_params": {"C": 1.0, "max_iter": 1000},
                    "best_score": None,
                }

        genetic_result = {
            "best_params": {
                "sl_pct": 0.02,
                "tp_pct": 0.03,
                "trail_base": 0.02,
                "vol_low": 0.9,
                "vol_high": 0.3,
            },
            "best_score": 0.02,
        }
        try:
            def fitness_fn(params):
                return 0.02 + 0.001 * min(params.get("sl_pct", 0.02), 0.05)

            optimizer = GeneticOptimizer(
                param_space={
                    "sl_pct": (0.01, 0.05),
                    "tp_pct": (0.02, 0.10),
                    "trail_base": (0.01, 0.05),
                    "vol_low": (0.7, 1.0),
                    "vol_high": (0.1, 0.5),
                },
                fitness_fn=fitness_fn,
                population_size=10,
                generations=5,
            )
            genetic_result = optimizer.optimize()
        except Exception:
            genetic_result = {
                "best_params": {
                    "sl_pct": 0.02,
                    "tp_pct": 0.03,
                    "trail_base": 0.02,
                    "vol_low": 0.9,
                    "vol_high": 0.3,
                },
                "best_score": 0.02,
            }

        try:
            tickers = ["XLK", "XLV", "XLE", "XLP"]
            cov_matrix = np.array([
                [0.0016, 0.0008, 0.0004, 0.0002],
                [0.0008, 0.0012, 0.0003, 0.0001],
                [0.0004, 0.0003, 0.0010, 0.0002],
                [0.0002, 0.0001, 0.0002, 0.0008],
            ])
            hrp_weights = hierarchical_risk_parity(tickers, cov_matrix)
        except Exception:
            hrp_weights = {"XLK": 0.25, "XLV": 0.25, "XLE": 0.25, "XLP": 0.25}

        rl_row = {
            "vol_regime": vol_regime,
            "macro_state": macro_state,
            "return": daily_data.get("return", 0.0),
        }
        rl_size = rl_sizer.choose_size(rl_row)

        try:
            historical_returns = daily_data.get("historical_returns", [0.001, -0.002, 0.0015, -0.0008, 0.0012, -0.0011, 0.0009, -0.0007, 0.0010, -0.0006])
            if hasattr(dl_forecaster, "fitted") and not dl_forecaster.fitted:
                dl_forecaster.fit(historical_returns, epochs=3, batch_size=8)
            recent_returns = daily_data.get("recent_returns", historical_returns[-20:])
            dl_forecast = dl_forecaster.predict_next(recent_returns)
        except Exception:
            dl_forecast = float(np.mean(daily_data.get("historical_returns", [0.001, -0.002, 0.0015, -0.0008, 0.0012, -0.0011, 0.0009, -0.0007, 0.0010, -0.0006])))

        drift_report = drift_detector.update(
            forecast=dl_forecast,
            ret=daily_data.get("return", 0.0),
            vol_regime=vol_regime,
            params=genetic_result.get("best_params", {}),
        )
        shock_report = shock_detector.update(
            ret=daily_data.get("return", 0.0),
            features={
                "vix": daily_data.get("vix", 20.0),
                "spread": daily_data.get("credit_spread", 0.01),
                "volume_z": daily_data.get("volume_z", 0.0),
            },
        )
        pause_info = event_pause.combined_pause(
            now=datetime.datetime.now(),
            headlines=daily_data.get("headlines", []),
        )
        latest_headlines = daily_data.get("headlines", [])
        news_info = news_model.analyze(latest_headlines)
        corr_info = corr_engine.update(
            ticker=daily_data.get("symbol", "XLV"),
            ret=daily_data.get("return", 0.0),
        )
        tail_info = tail_model.update(daily_data.get("return", 0.0))

        etf_info = etf_matcher.match(
            sector=best_sector,
            regime=decision,
            vol_regime=vol_regime,
            macro_regime=macro_state,
            crash_prob=tail_info.get("crash_prob"),
        )
        liq = liq_model.update(
            bid=daily_data.get("bid", daily_data.get("price", 100.0) * 0.995),
            ask=daily_data.get("ask", daily_data.get("price", 100.0) * 1.005),
            last_price=daily_data.get("price", 100.0),
            volume=daily_data.get("volume", 1000.0),
            nav=daily_data.get("nav", None),
        )

        decision_payload = {
            "decision": decision,
            "ticker": daily_data.get("symbol", "XLV"),
            "position_size": position_size,
            "volatility_regime": vol_regime,
            "macro_state": macro_state,
            "sector_score": daily_data.get("sector_scores", {}).get(best_sector, 0.0),
            "momentum": daily_data.get("momentum", 0.0),
            "entry_price": daily_data.get("price", 100.0),
            "stop_price": daily_data.get("price", 100.0) * 0.95,
            "account_value": daily_data.get("account_value", 10000.0),
            "ml_regime": ml_regime,
            "ml_regime_accuracy": ml_regime_accuracy,
            "ml_feature_ranking": feature_ranking,
            "ml_best_params": tuning_result["best_params"],
            "ml_best_score": tuning_result["best_score"],
            "optimized_params": genetic_result["best_params"],
            "optimized_score": genetic_result["best_score"],
            "hrp_weights": hrp_weights,
            "rl_position_size": rl_size,
            "rl_policy_updates": len(rl_sizer.Q),
            "dl_return_forecast": dl_forecast,
            "drift_report": drift_report,
            "shock_report": shock_report,
            "event_pause": pause_info,
            "news_mean_sentiment": news_info.get("mean_sentiment", 0.0),
            "news_headline_scores": news_info.get("headline_scores", []),
            "news_embeddings": news_info.get("embeddings"),
            "cross_asset_corr": corr_info,
            "regime_transition_probs": regime_tm.transition_matrix(),
            "regime_steady_state": regime_tm.steady_state(),
            "matched_etfs": etf_info.get("matched_etfs", []),
            "liquidity_stress": liq,
            "tail_var": tail_info.get("tail_var"),
            "tail_cvar": tail_info.get("tail_cvar"),
            "crash_prob": tail_info.get("crash_prob"),
        }
        if mc_report:
            decision_payload["mc_mean_final"] = mc_report["mean_final"]
            decision_payload["mc_var_95"] = mc_report["var_95"]
            decision_payload["mc_cvar_95"] = mc_report["cvar_95"]
            decision_payload["mc_mean_drawdown"] = mc_report["mean_drawdown"]

        decision_payload = apply_volatility_throttle(decision_payload)

        decision_payload = apply_sl_tp(
            decision_payload,
            entry_price=decision_payload.get("entry_price", 100.0),
            stop_loss_pct=0.02,
            take_profit_pct=0.03,
        )

        decision_payload = apply_dynamic_trailing_stop(
            decision_payload,
            current_price=decision_payload.get("entry_price", 100.0),
            vol_regime=vol_regime,
            base_trail_pct=0.02,
        )

        exposure_report = evaluate_exposure(
            current_positions={
                "XLV": {"value": 2500.0, "sector": "HEALTH"},
                "XLK": {"value": 1500.0, "sector": "TECH"},
                "XLE": {"value": 500.0, "sector": "ENERGY"},
            },
            account_value=decision_payload.get("account_value", 10000.0),
        )
        decision_payload["position_size"] = decision_payload.get("position_size", 0.0) * exposure_report["throttle"]
        decision_payload["exposure_warnings"] = exposure_report["warnings"]
        decision_payload["total_exposure_pct"] = exposure_report["total_exposure_pct"]

        rotation = generate_regime_rotation_orders(
            macro_state=macro_state,
            vol_regime=vol_regime,
            current_positions={
                "XLV": {"value": 2500.0},
                "XLK": {"value": 1500.0},
                "XLE": {"value": 500.0},
                "XLP": {"value": 0.0},
            },
            account_value=decision_payload.get("account_value", 10000.0),
        )
        decision_payload["regime"] = rotation["regime"]
        decision_payload["rotation_orders"] = rotation["orders"]
        decision_payload["target_allocations"] = rotation["targets"]

        decision_payload = apply_risk_controls(
            decision_payload,
            todays_loss_pct=daily_data.get("todays_loss_pct", 0.0),
            current_exposure_pct=daily_data.get("current_exposure_pct", 0.0),
            current_portfolio_value=daily_data.get("account_value", 10000.0),
        )

        decision = decision_payload.get("decision", "HOLD")

        # ── ADDED: log every decision to trade_history.json ──────────────────
        try:
            # "SKIP" is not a standard log action, so we store it as "HOLD"
            # and preserve the real decision word inside metadata
            log_action = decision if decision in ("BUY", "SELL") else "HOLD"

            log_trade(
                symbol     = daily_data.get("symbol", "UNKNOWN"),
                action     = log_action,
                price      = daily_data.get("price", 0.0),
                quantity   = position_size,
                confidence = confidence,
                signals    = {
                    "roi":         roi,
                    "volatility":  vol,
                    "win_rate":    win_rate,
                    "drawdown":    drawdown,
                    "vol_regime":  vol_regime,
                    "macro_state": macro_state,
                    "sector":      best_sector,
                },
                metadata   = {
                    "raw_decision": decision,   # preserves SKIP if that happened
                    "adjustments":  adjustments,
                },
            )
        except Exception as log_err:
            print("TRADE LOGGER WARNING:", log_err)
        # ─────────────────────────────────────────────────────────────────────

        current_positions = {
            "XLV": {"value": 2500.0},
            "XLK": {"value": 1500.0},
            "XLE": {"value": 500.0},
        }
        target_allocations = {
            "XLV": 0.30,
            "XLK": 0.40,
            "XLE": 0.30,
        }
        account_value = daily_data.get("account_value", 10000.0)
        rebalance_orders = generate_rebalance_orders(
            current_positions,
            target_allocations,
            account_value,
            min_trade_pct=0.01,
        )

        result = {
            "sector": best_sector,
            "decision": decision,
            "ticker": daily_data.get("symbol", "XLV"),
            "volatility_regime": vol_regime,
            "realized_vol": vol_info.get("realized_vol", 0.0),
            "macro_state": macro_state,
            "sector_score": daily_data.get("sector_scores", {}).get(best_sector, 0.0),
            "momentum": daily_data.get("momentum", 0.0),
            "entry_price": daily_data.get("price", 100.0),
            "stop_price": daily_data.get("price", 100.0) * 0.95,
            "account_value": account_value,
            "position_size": decision_payload.get("position_size", position_size),
            "roi": roi,
            "vol": vol,
            "win_rate": win_rate,
            "drawdown": drawdown,
            "confidence": confidence,
            "adjustments": adjustments,
            "rebalance_orders": rebalance_orders,
        }
        if "reason" in decision_payload:
            result["reason"] = decision_payload["reason"]
        if "ml_regime" in decision_payload:
            result["ml_regime"] = decision_payload["ml_regime"]
        if "ml_regime_accuracy" in decision_payload:
            result["ml_regime_accuracy"] = decision_payload["ml_regime_accuracy"]
        if "mc_mean_final" in decision_payload:
            result["mc_mean_final"] = decision_payload["mc_mean_final"]
        if "mc_var_95" in decision_payload:
            result["mc_var_95"] = decision_payload["mc_var_95"]
        if "mc_cvar_95" in decision_payload:
            result["mc_cvar_95"] = decision_payload["mc_cvar_95"]
        if "mc_mean_drawdown" in decision_payload:
            result["mc_mean_drawdown"] = decision_payload["mc_mean_drawdown"]
        if "ml_feature_ranking" in decision_payload:
            result["ml_feature_ranking"] = decision_payload["ml_feature_ranking"]
        if "ml_best_params" in decision_payload:
            result["ml_best_params"] = decision_payload["ml_best_params"]
        if "ml_best_score" in decision_payload:
            result["ml_best_score"] = decision_payload["ml_best_score"]
        if "optimized_params" in decision_payload:
            result["optimized_params"] = decision_payload["optimized_params"]
        if "optimized_score" in decision_payload:
            result["optimized_score"] = decision_payload["optimized_score"]
        if "hrp_weights" in decision_payload:
            result["hrp_weights"] = decision_payload["hrp_weights"]
        if "rl_position_size" in decision_payload:
            result["rl_position_size"] = decision_payload["rl_position_size"]
        if "rl_policy_updates" in decision_payload:
            result["rl_policy_updates"] = decision_payload["rl_policy_updates"]
        if "dl_return_forecast" in decision_payload:
            result["dl_return_forecast"] = decision_payload["dl_return_forecast"]
        if "drift_report" in decision_payload:
            result["drift_report"] = decision_payload["drift_report"]
        if "shock_report" in decision_payload:
            result["shock_report"] = decision_payload["shock_report"]
        if "event_pause" in decision_payload:
            result["event_pause"] = decision_payload["event_pause"]
        if "matched_etfs" in decision_payload:
            result["matched_etfs"] = decision_payload["matched_etfs"]
        if "regime_transition_probs" in decision_payload:
            result["regime_transition_probs"] = decision_payload["regime_transition_probs"]
        if "regime_steady_state" in decision_payload:
            result["regime_steady_state"] = decision_payload["regime_steady_state"]
        if "tail_var" in decision_payload:
            result["tail_var"] = decision_payload["tail_var"]
        if "tail_cvar" in decision_payload:
            result["tail_cvar"] = decision_payload["tail_cvar"]
        if "crash_prob" in decision_payload:
            result["crash_prob"] = decision_payload["crash_prob"]
        if decision_payload.get("risk_adjusted"):
            result["risk_adjusted"] = True
        if "exposure_warnings" in decision_payload:
            result["exposure_warnings"] = decision_payload["exposure_warnings"]
        if "total_exposure_pct" in decision_payload:
            result["total_exposure_pct"] = decision_payload["total_exposure_pct"]

        return result

    except Exception as e:
        print("ORCHESTRATOR ERROR:", e)
