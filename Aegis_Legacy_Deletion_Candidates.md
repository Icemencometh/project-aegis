# Aegis Legacy Deletion Candidates (Post-Parity)

This is a planning list only. Do not delete any item until parity tests pass and runtime cutover is confirmed.

## Safe to Remove Last (After Full Cutover)

- [orchestrator.py](orchestrator.py)
- [execution_engine.py](execution_engine.py)
- [trade_risk_scoring.py](trade_risk_scoring.py)
- [strategy_layer.py](strategy_layer.py)

## Directory-Level Candidates (Phase 2+)

- [modules](modules)
- [strategies](strategies)
- [execution](execution)
- [portfolio](portfolio)
- [strategy_marketplace](strategy_marketplace)
- [quant_bot](quant_bot)

## Deletion Preconditions

1. Equivalent behavior exists in Aegis modules.
2. All production entrypoints call Aegis only.
3. Test suite includes migration parity tests.
4. CI passes without imports from target legacy path.
5. Docs and maps updated.

## Verification Checklist Before Deletion

- No imports remain from legacy path.
- Runtime smoke tests pass.
- Backtest and live-safe dry-run paths pass.
- Migration notes committed.
