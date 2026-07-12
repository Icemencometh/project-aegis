# Phase 3 Aegis Takeover Plan

## Goal

Make `aegis/` the only runtime system and block reintroduction of legacy imports.

## Deletion Map (Applied to Tracked Files in This Repository State)

Removed in this phase:
- `quant_bot/__init__.py`
- `execution_engine.py`
- `strategy_layer.py`
- `trade_risk_scoring.py`

Not present as tracked files on current `main` snapshot:
- `quant_bot/alpha`, `quant_bot/audit`, `quant_bot/calendar`, `quant_bot/features`, `quant_bot/feed`, `quant_bot/orchestrator`, `quant_bot/promoter`, `quant_bot/regime`, `quant_bot/risk`, `quant_bot/scoring`, `quant_bot/session`, `quant_bot/utils`
- `modules/`
- `execution/`
- `portfolio/`
- `strategies/`
- `strategy_marketplace/`
- `config/*.yaml`

## Canonical Replacements

Aegis canonical runtime modules:
- `aegis/orchestrator.py`
- `aegis/execution/*`
- `aegis/portfolio/*`
- `aegis/risk/*`
- `aegis/regime/*`
- `aegis/scoring/*`
- `aegis/strategies/*`
- `aegis/config/*.yaml`

Root entrypoints (Aegis-only):
- `main.py` -> `aegis.orchestrator.run_robot()`
- `scheduler.py` -> `aegis.orchestrator.run_scheduler()`
- `run_daily_once.py` -> `aegis.orchestrator.run_daily_once()`
- `orchestrator.py` -> compatibility wrapper delegating to Aegis

## CI Gates (Aegis-only)

`/.github/workflows/ci.yml` now:
- runs compile lint
- runs `legacy-import-guard` to fail on import of:
  - `quant_bot.*`
  - `modules.*`
  - `execution.*` (legacy)
  - `portfolio.*` (legacy)
  - `strategies.*` (legacy)
  - `strategy_marketplace.*`
- runs Aegis-focused tests
- runs parity tests
- enforces final CI gate on these jobs

`/.github/workflows/parity.yml` now includes `main`, `phase3/**`, `phase2/**`, and `parity/**` pushes.

## Rollback

- Revert the Phase 3 PR merge commit.
- Restore removed legacy files from git history.
- Restore previous CI workflow definitions.
