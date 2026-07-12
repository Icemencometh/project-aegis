# PR Packet: Phase 2 Parity

## Suggested PR Title

`Phase 2: Aegis parity tests + legacy replacement framework`

## Suggested PR Body

```md
## Summary
Builds the Phase 2 parity framework between Aegis and legacy systems for scoring, risk, allocation, regime, execution (paper mode), and portfolio behavior.

## What Changed
- Added parity adapter layer under `aegis/parity/`
- Added parity config at `aegis/config/parity.yaml`
- Added parity tests under `aegis/tests/parity/`
- Added parity report generator at `aegis/parity/report.py`
- Added parity workflow `.github/workflows/parity.yml`

## Acceptance Criteria
- parity test suite executes
- parity report is generated (json + markdown)
- parity workflow uploads artifacts
- no legacy deletion in this PR

## Rollback
If parity framework causes CI instability:
1. revert parity workflow file,
2. keep adapters/tests in branch for iteration,
3. re-enable workflow after threshold tuning.
```

## Merge Checklist

- [ ] Scoring parity adapter and test present
- [ ] Risk parity adapter and test present
- [ ] Allocation parity adapter and test present
- [ ] Regime parity adapter and test present
- [ ] Execution parity adapter and test present
- [ ] Portfolio parity adapter and test present
- [ ] Parity report generator writes artifacts
- [ ] CI parity workflow is green
- [ ] No legacy code removed
