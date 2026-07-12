# Phase 2 Parity Plan

This plan tracks parity validation between legacy behavior and Aegis canonical runtime.

## Goal

Validate functional parity for key decision stages before any legacy removals.

## Scope

1. Scoring parity
2. Risk decision parity
3. Allocation sizing parity
4. Execution result normalization parity

## Milestones

### M1: Fixture Baseline
- Build deterministic fixture payloads for candidate trades, features, and regime snapshots.
- Capture expected outputs from current canonical Aegis path.

### M2: Parity Harness
- Add test harness that executes comparable functions across legacy/Aegis adapters.
- Compute diff metrics and fail on threshold breaches.

### M3: Runtime Confidence
- Add smoke tests across migrated entrypoints.
- Validate no risk bypass and safe defaults.

### M4: Deprecation Gate
- Mark legacy modules removable only after parity suite is green for 2 consecutive runs.

## Acceptance Criteria

- All parity tests green.
- No production entrypoint calls legacy engines directly.
- Migration map and deletion candidates updated after each parity PR.

## Execution Order

1. Scoring parity tests.
2. Risk parity tests.
3. Allocation parity tests.
4. Execution parity tests.
5. Legacy removal PRs (small, scoped).
