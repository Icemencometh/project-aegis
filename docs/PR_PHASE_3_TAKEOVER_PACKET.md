# PR Packet: Phase 3 Aegis Takeover

## Suggested PR Title

`Phase 3: Full Aegis takeover + legacy system removal`

## Suggested PR Body

```md
## Summary
Finalize the migration by making Aegis the only runtime system and removing tracked legacy root modules.

## What Changed
- Removed tracked legacy modules:
  - `quant_bot/__init__.py`
  - `execution_engine.py`
  - `strategy_layer.py`
  - `trade_risk_scoring.py`
- Replaced root `orchestrator.py` with Aegis-only compatibility wrapper.
- Removed parity adapter dependencies on legacy import paths (`quant_bot.*`, `modules.*`, legacy root modules).
- Hardened CI with a legacy import guard that fails on:
  - `quant_bot.*`, `modules.*`, `execution.*`, `portfolio.*`, `strategies.*`, `strategy_marketplace.*`
- Reduced CI execution to Aegis-focused tests plus parity tests.
- Updated parity workflow branch triggers for `main` and `phase3/**`.
- Added `PHASE3_AEGIS_TAKEOVER_PLAN.md`.

## Acceptance Criteria
- No tracked legacy imports remain.
- No tracked legacy root modules remain.
- Main entrypoints run Aegis adapters only.
- CI fails on blocked legacy import paths.
- Aegis tests pass.
- Parity tests pass.

## Rollback
- Revert this PR.
- Restore removed files from git history.
- Restore prior CI workflows.
```
