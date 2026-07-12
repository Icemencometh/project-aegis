# Aegis Module Contracts

This document defines the interface contracts for all core Aegis modules. Any AI or human contributor must respect these contracts.

---

## Data Engine

Purpose: Ingest, validate, normalize, and store market and event data.

Inputs:
- External data sources (broker API, feeds, files).

Outputs:
- Normalized data frames and time series.
- Versioned historical datasets.

Contract:
- Must not depend on strategy or scoring logic.
- Must expose a read-only interface for downstream modules.
- Must tag data with timestamps, symbols, and versions.

---

## Feature Engine

Purpose: Transform raw data into deterministic features.

Inputs:
- Data Engine outputs.

Outputs:
- Feature sets keyed by symbol, timeframe, and feature version.

Contract:
- Features must be deterministic and reproducible.
- Each feature family must be documented.
- No direct calls to broker or execution.

---

## Regime Engine

Purpose: Classify current market regime.

Inputs:
- Market data, volatility, breadth, macro context.

Outputs:
- Regime labels (example: trending_bullish, high_volatility).

Contract:
- Must expose a simple API: get_current_regime().
- Must not place trades or modify portfolio.

---

## Strategy Marketplace

Purpose: Run multiple independent strategies and manage their activation.

Inputs:
- Features, regime, config.

Outputs:
- Trade candidates (symbol, direction, entry context).

Contract:
- Strategies must emit trade candidates, not orders.
- Strategies must be pluggable and versioned.
- Strategy performance must be tracked per regime.

---

## Scoring Hub

Purpose: Convert trade candidates into scored, probabilistic opportunities.

Inputs:
- Trade candidates, feature snapshot, regime snapshot.

Outputs:
- Scored trades with component scores, composite probability, confidence, rationale.

Contract:
- Must call all scorers (technical, order flow, squeeze, ML, regime, macro, liquidity, sentiment).
- Must use AdaptiveWeightingEngine and ExplainableDecisionEngine.
- Must optionally use MetaModelEngine.
- Must not bypass risk or execution.

---

## Alpha Hub

Purpose: Combine scoring outputs with model predictions to produce trade intents.

Inputs:
- Scored trades, model predictions.

Outputs:
- Trade intents (symbol, side, entry, stop, target, probability, expected return, holding time).

Contract:
- Must record model version and feature version.
- Must not place orders directly.

---

## Risk Engine

Purpose: Enforce trade-level, position-level, portfolio-level, and environment risk.

Inputs:
- Trade intents, portfolio snapshot, environment snapshot, risk config.

Outputs:
- Approved trades, rejected trades with reasons, halt and flatten signals.

Contract:
- No trade may pass without risk checks.
- Must be able to halt trading and flatten positions.
- Must log all rejections and circuit breakers.

---

## Portfolio Manager

Purpose: Track positions, exposures, P&L, and portfolio heat.

Inputs:
- Broker state, executed trades.

Outputs:
- Portfolio snapshot, exposure metrics, attribution.

Contract:
- Must be the system of record for positions.
- Must reconcile with broker regularly.
- Must not place orders.

---

## Execution Engine

Purpose: Convert approved trades into broker orders.

Inputs:
- Approved trade intents, portfolio snapshot.

Outputs:
- Orders, fills, execution metrics.

Contract:
- Must use broker abstraction (PaperBroker, LiveBroker, MockBroker).
- Must handle partial fills, retries, and disconnects.
- Must not bypass risk or portfolio.

---

## Capital Allocation AI

Purpose: Allocate capital across strategies and trades under risk constraints.

Inputs:
- Strategy metrics, portfolio snapshot, trade intents.

Outputs:
- Sized trade intents (qty, notional).

Contract:
- Must respect portfolio caps and risk limits.
- Must be deterministic given inputs.

---

## Research Engine

Purpose: Backtest, simulate, and validate strategies and models.

Inputs:
- Historical data, features, strategies, models.

Outputs:
- Performance reports, validation metrics, promotion decisions.

Contract:
- Must be separate from live execution.
- Must include transaction costs, slippage, and realistic fills.
