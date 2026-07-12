# Aegis Migration Map

This document is the canonical mapping for migrating legacy Quant_robot runtime
paths to Aegis-first entrypoints.

## Entrypoints (phase 1)

- `main.py` -> `aegis/orchestrator.py::run_robot`
- `scheduler.py` -> `aegis/orchestrator.py::run_scheduler`
- `run_daily_once.py` -> `aegis/orchestrator.py::run_daily_once`

## Entrypoints (planned phase 2)

- `live_loop.py` -> `aegis/execution/live_loop_adapter.py` (planned)
- `backtest.py` -> `aegis/research/backtest_entry.py` (planned)

## Legacy package migration targets

- `quant_bot/strategies/*` -> `aegis/strategies/*`
- `quant_bot/risk/*` -> `aegis/risk/*`
- `quant_bot/execution/*` -> `aegis/execution/*`
- `quant_bot/scoring/*` -> `aegis/scoring/*`
- `quant_bot/alpha/*` -> `aegis/alpha/*`

## Notes

- Aegis adapters are introduced first so existing operational scripts still run.
- Legacy modules are deprecated with warnings, then removed only after parity and
  smoke tests are confirmed.
- No risk checks or execution safeguards are bypassed during migration.