# Aegis Development Workflow

This document defines how changes are made to Aegis.

---

## Branching Model

- main: stable, production-ready.
- develop: integration branch (optional).
- Feature branches: feature/<short-name>.

---

## Commit Rules

- Small, focused commits.
- Clear messages: module: short description.
- No committing secrets or credentials.

---

## Pull Requests

- Every change goes through a PR.
- PR title must be clear and descriptive.
- PR description must include what changed, why, tests run, and risks.

---

## CI and Testing

- CI must run pytest and linting on every PR.
- All tests must pass before merge.
- New modules must include tests.

---

## Adding New Strategies

1. Implement strategy in strategies/.
2. Register in Strategy Marketplace.
3. Add tests and backtests.
4. Run paper trading.
5. Only then consider promotion.

---

## Adding New Scorers

1. Implement new scorer in scoring/modules/.
2. Update scoring config with weights and parameters.
3. Add unit tests.
4. Validate impact via backtests.

---

## Adding New Models

1. Register in Model Registry.
2. Train with walk-forward validation.
3. Add calibration and decay monitoring.
4. Only then integrate into Alpha Hub.

---

## Adding New Risk Rules

1. Modify risk config.
2. Update Risk Engine checks.
3. Add tests and simulations.
4. Confirm no weakening of protections.

---

## Release Workflow

- Tag releases with semantic versioning.
- Document changes in CHANGELOG.
- Never deploy untested changes to live.
