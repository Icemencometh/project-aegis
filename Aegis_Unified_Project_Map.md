# Unified Aegis Project Map

This document defines the canonical structure for the merged Quant_robot and Aegis codebase.

## Canonical Runtime Surface

Use these as the primary runtime entrypoints:

- [main.py](main.py)
- [scheduler.py](scheduler.py)
- [run_daily_once.py](run_daily_once.py)

These now delegate to Aegis adapters in:

- [aegis/orchestrator.py](aegis/orchestrator.py)

## Canonical Domain Layout (Aegis)

Core package root:

- [aegis](aegis)

Domain modules:

- Data: [aegis/data](aegis/data)
- Features: [aegis/features](aegis/features)
- Regime: [aegis/regime](aegis/regime)
- Strategies: [aegis/strategies](aegis/strategies)
- Scoring: [aegis/scoring](aegis/scoring)
- Alpha: [aegis/alpha](aegis/alpha)
- Risk: [aegis/risk](aegis/risk)
- Allocation: [aegis/allocation](aegis/allocation)
- Portfolio: [aegis/portfolio](aegis/portfolio)
- Execution: [aegis/execution](aegis/execution)
- Marketplace: [aegis/marketplace](aegis/marketplace)
- Meta: [aegis/meta](aegis/meta)
- Backtest (phase 2): [aegis/backtest](aegis/backtest)
- Shared utilities: [aegis/common](aegis/common)
- Aegis configs: [aegis/config](aegis/config)

## Parallel Legacy Surfaces (Still Present)

These exist and may still be referenced; treat as migration sources:

- Legacy root scripts: many files at repo root
- Legacy module tree: [modules](modules)
- Legacy strategy tree: [strategies](strategies)
- Legacy execution package: [execution](execution)
- Legacy portfolio package: [portfolio](portfolio)
- Legacy marketplace package: [strategy_marketplace](strategy_marketplace)
- Sprint package tree: [quant_bot](quant_bot)

## Target Source-of-Truth Policy

For new work, write code in Aegis paths only.

- New strategy logic -> [aegis/strategies](aegis/strategies)
- New scoring logic -> [aegis/scoring](aegis/scoring)
- New risk logic -> [aegis/risk](aegis/risk)
- New execution logic -> [aegis/execution](aegis/execution)
- New portfolio logic -> [aegis/portfolio](aegis/portfolio)
- New integration pipeline logic -> [aegis/orchestrator.py](aegis/orchestrator.py)

## Mapping: Legacy to Aegis

High-level mappings:

- Root orchestrator flow -> [aegis/orchestrator.py](aegis/orchestrator.py)
- [strategies](strategies) and [quant_bot/alpha](quant_bot/alpha) strategy surfaces -> [aegis/strategies](aegis/strategies)
- [modules/risk_controls.py](modules/risk_controls.py) and [trade_risk_scoring.py](trade_risk_scoring.py) -> [aegis/risk](aegis/risk)
- [modules/execution_engine.py](modules/execution_engine.py) and [execution_engine.py](execution_engine.py) -> [aegis/execution](aegis/execution)
- [portfolio_manager.py](portfolio_manager.py) and [portfolio](portfolio) -> [aegis/portfolio](aegis/portfolio)
- [quant_bot/scoring](quant_bot/scoring) -> [aegis/scoring](aegis/scoring)
- [quant_bot/regime](quant_bot/regime) -> [aegis/regime](aegis/regime)
- [quant_bot/features](quant_bot/features) -> [aegis/features](aegis/features)

Detailed entrypoint migration map is maintained in:

- [Aegis_Migration_Map.md](Aegis_Migration_Map.md)

## Test Topology

Aegis-focused tests live under:

- [tests/test_aegis_blueprints.py](tests/test_aegis_blueprints.py)
- [tests/test_aegis_pipeline.py](tests/test_aegis_pipeline.py)
- [tests/test_aegis_data_engine.py](tests/test_aegis_data_engine.py)
- [tests/test_aegis_features_engine.py](tests/test_aegis_features_engine.py)
- [tests/test_aegis_regime_engine.py](tests/test_aegis_regime_engine.py)
- [tests/test_aegis_strategies.py](tests/test_aegis_strategies.py)
- [tests/test_aegis_marketplace_concentration.py](tests/test_aegis_marketplace_concentration.py)
- [tests/test_aegis_risk_extended.py](tests/test_aegis_risk_extended.py)

Legacy tests still present should be kept green until full cutover.

## Merge Readiness Status

Migration phase complete:

- Entrypoint adapters added
- High-impact root scripts migrated
- Legacy warnings added

Next phases:

1. Continue domain-by-domain parity checks.
2. Move remaining runtime calls to Aegis.
3. Decommission legacy modules only after parity verification.
