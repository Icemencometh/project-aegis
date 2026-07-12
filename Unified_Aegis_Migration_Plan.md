# Unified Aegis Migration Plan (Mode C: Hybrid)

Mode C decision: Aegis is canonical for live and production runtime, while `quant_bot` remains available for research/backtesting until parity and replacement are complete.

## Objectives

1. Make Aegis the only production runtime path.
2. Preserve research continuity via `quant_bot` during transition.
3. Remove legacy `modules/` era code in controlled phases.
4. Maintain deterministic behavior and risk-first safeguards.

## System-of-Record Policy

- Production runtime source of truth: `aegis/`
- Research/legacy reference surface: `quant_bot/`
- Deprecation surface (no new features): `modules/`, root legacy engines.

## Phase Plan

### Phase 1: Runtime Cutover (Done/In Progress)

- Keep root entrypoints (`main.py`, `scheduler.py`, `run_daily_once.py`) as compatibility wrappers.
- Route wrappers into `aegis.orchestrator` adapters.
- Add deprecation warnings on legacy modules.

Exit criteria:

- Root runtime entrypoints execute Aegis only.
- Smoke tests pass for wrappers.

### Phase 2: Parity Validation (Next)

- Add parity tests for key behavior groups:
  - scoring outputs
  - risk approvals/rejections
  - allocation sizing
  - execution fill handling
- Compare Aegis outputs vs quant_bot baselines on fixed fixtures/replay data.

Exit criteria:

- Parity test suite green.
- No production code path imports legacy execution or risk engines.

### Phase 3: Research Bridging

- Keep `quant_bot` for:
  - historical examples
  - model promotion experiments
  - replay-based research workflows
- Add adapters where needed so research artifacts can feed Aegis-compatible payloads.

Exit criteria:

- Research can run without touching production runtime code paths.

### Phase 4: Legacy Decommission

- Remove `modules/` era runtime dependencies first.
- Remove root legacy engines after import graph is clear.
- Keep a final archival tag before deletion PR merge.

Exit criteria:

- No imports from decommissioned paths.
- Full CI passes.

## Merge Targets (Legacy -> Aegis)

- `orchestrator.py` -> `aegis/orchestrator.py`
- `execution_engine.py` and `modules/execution_engine.py` -> `aegis/execution/*`
- `trade_risk_scoring.py` and `quant_bot/risk/*` -> `aegis/risk/*`
- `strategy_layer.py`, `strategies/*`, `quant_bot/alpha/*` -> `aegis/strategies/*` and `aegis/alpha/*`
- `portfolio_manager.py`, `portfolio/*` -> `aegis/portfolio/*`
- `quant_bot/scoring/*` -> `aegis/scoring/*`

## Safe Deletion Order

1. Unused root helper scripts with no imports.
2. `modules/` components no longer referenced by tests or runtime.
3. Root legacy engines (after parity and adapters confirmed).
4. Optional: archive `quant_bot` only after research replacement is complete.

## Risk Controls During Migration

- Never bypass `aegis.risk` checks in runtime paths.
- Keep paper-safe defaults.
- Require tests for every migration step.
- Treat any ambiguity as halt/reduce-risk condition.

## Required PR Template for Migration Steps

Each migration PR must include:

1. Files migrated and legacy paths touched.
2. Tests added/updated.
3. Runtime smoke evidence.
4. Rollback instructions.
5. Residual risk notes.