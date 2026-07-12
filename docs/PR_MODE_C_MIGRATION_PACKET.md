# PR Packet: Mode C Migration and Governance

Use this packet as the PR title/body and merge checklist for branch `aegis/option-a-pipeline-wiring`.

## Suggested PR Title

`migration: Mode C hybrid cutover (Aegis adapters, deprecations, project map, Claude index)`

## Suggested PR Body

```md
## Summary
Implements the Mode C (Hybrid) migration foundation:

- Aegis is canonical for production runtime paths.
- quant_bot is retained for research/backtesting compatibility.
- legacy modules are kept temporarily with deprecation warnings and migration docs.

## What Changed

### Runtime migration
- Added Aegis compatibility adapters in `aegis/orchestrator.py`:
  - `run_robot()`
  - `run_scheduler()`
  - `run_daily_once()`
- Migrated high-impact root entrypoints to call Aegis adapters:
  - `main.py`
  - `scheduler.py`
  - `run_daily_once.py`

### Deprecation guardrails
- Added deprecation warnings to legacy surfaces:
  - `orchestrator.py`
  - `execution_engine.py`
  - `strategy_layer.py`
  - `trade_risk_scoring.py`
  - `quant_bot/__init__.py`

### Migration and governance docs
- Added migration map:
  - `Aegis_Migration_Map.md`
- Added unified architecture map:
  - `Aegis_Unified_Project_Map.md`
- Added Claude project index:
  - `Claude_Project_Index.md`
- Added legacy deletion planning:
  - `Aegis_Legacy_Deletion_Candidates.md`
- Added Mode C migration plan:
  - `Unified_Aegis_Migration_Plan.md`
- Added GitHub + Claude integration checklist:
  - `Aegis_GitHub_Claude_Integration_Checklist.md`

## Validation
- Smoke-tested migrated entrypoints:
  - `python run_daily_once.py`
  - `python main.py`
  - scheduler import smoke test
- No diagnostics errors in touched files.

## Mode C Decision
- Production runtime: `aegis/`
- Research compatibility: `quant_bot/`
- Deprecation surfaces: `modules/` + legacy root engines

## Risks
- Some legacy workflows may still import deprecated modules.
- Full parity validation is still required before deletion phases.

## Follow-up (next PRs)
1. Add parity tests between legacy and Aegis outputs for key flows.
2. Migrate remaining runtime scripts (`live_loop.py`, `backtest.py`) via adapters.
3. Start controlled removal of unused `modules/` components after import-graph validation.
```

## Merge Checklist (Reviewer)

- [ ] Entry-point wrappers call Aegis only (`main.py`, `scheduler.py`, `run_daily_once.py`).
- [ ] Legacy deprecation warnings are present and non-breaking.
- [ ] Migration docs are complete and internally consistent.
- [ ] CI status checks are green.
- [ ] No secrets/tokens in commit history.
- [ ] Rollback path documented (revert wrapper commits if needed).

## Rollback Plan

If runtime behavior regresses:

1. Revert migration wrapper commit(s) for root entrypoints.
2. Keep docs commits (non-runtime).
3. Re-run smoke scripts and CI.
4. Reintroduce adapters incrementally behind feature branches.
