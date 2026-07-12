# Claude Project Index

This index tells Claude exactly where to read and where to write.

## Read First (Required)

- [PROJECT_AEGIS_OVERVIEW.txt](PROJECT_AEGIS_OVERVIEW.txt)
- [Aegis_Module_Contracts.md](Aegis_Module_Contracts.md)
- [Aegis_Coding_Standards.txt](Aegis_Coding_Standards.txt)
- [Aegis_Development_Workflow.md](Aegis_Development_Workflow.md)
- [Aegis_AI_Onboarding_Guide.md](Aegis_AI_Onboarding_Guide.md)
- [Aegis_Claude_Usage_Note.txt](Aegis_Claude_Usage_Note.txt)
- [Aegis_Migration_Map.md](Aegis_Migration_Map.md)
- [Aegis_Unified_Project_Map.md](Aegis_Unified_Project_Map.md)
- [Unified_Aegis_Migration_Plan.md](Unified_Aegis_Migration_Plan.md)
- [Aegis_GitHub_Claude_Integration_Checklist.md](Aegis_GitHub_Claude_Integration_Checklist.md)

## Canonical Write Locations

Write new production code here:

- Pipeline orchestration: [aegis/orchestrator.py](aegis/orchestrator.py)
- Scoring: [aegis/scoring](aegis/scoring)
- Alpha: [aegis/alpha](aegis/alpha)
- Risk: [aegis/risk](aegis/risk)
- Allocation: [aegis/allocation](aegis/allocation)
- Portfolio: [aegis/portfolio](aegis/portfolio)
- Execution: [aegis/execution](aegis/execution)
- Strategy marketplace: [aegis/marketplace](aegis/marketplace)
- Strategies: [aegis/strategies](aegis/strategies)
- Data/features/regime: [aegis/data](aegis/data), [aegis/features](aegis/features), [aegis/regime](aegis/regime)
- Backtest (phase 2): [aegis/backtest](aegis/backtest)

Write new tests here:

- [tests](tests)
- Prefer Aegis-prefixed test files for Aegis features.

Write config updates here:

- [aegis/config](aegis/config)

## Legacy Paths (Read or Bridge Only)

Do not place new core logic in these unless explicitly migrating:

- Root legacy scripts and engines at repo root
- [modules](modules)
- [strategies](strategies)
- [execution](execution)
- [portfolio](portfolio)
- [strategy_marketplace](strategy_marketplace)
- [quant_bot](quant_bot)

## Contract Rules for Claude

1. Respect module boundaries.
2. Do not bypass risk or execution gates.
3. Keep logic deterministic given inputs.
4. Use config-driven thresholds.
5. Add tests for every behavior change.
6. Preserve compatibility wrappers unless explicitly removing them in a deprecation phase.

## Migration Operation Rules

When migrating legacy logic:

1. Add adapter or wrapper first.
2. Keep old path functional with deprecation warning.
3. Add tests proving parity for migrated behavior.
4. Remove legacy code only after validated cutover.

## Operating Mode

Repository currently runs in Mode C (Hybrid):

- `aegis/` is canonical for live and production runtime.
- `quant_bot/` is retained for research/backtesting compatibility.
- `modules/` and root legacy engines are deprecation surfaces only.

## Where to Put New GitHub/Claude Automation

- Workflows: [/.github/workflows](.github/workflows)
- Claude/automation conventions: [CLAUDE.md](CLAUDE.md)

## Safety Defaults

- Paper-safe behavior is default.
- If uncertain, reduce risk or halt.
- Never weaken risk constraints during refactors.
