# Aegis PR-Ready Handoff

This workspace does not currently have a configured git remote, so the PR cannot be opened automatically from here.

The code is prepared as a local branch and bundle artifact.

## What is included

- Runnable deterministic Aegis service skeletons:
  - scoring hub
  - alpha hub
  - risk engine
  - portfolio manager
  - execution engine
  - strategy marketplace
  - capital allocation engine
- Basic unit tests in `tests/test_aegis_blueprints.py`
- CI update in `.github/workflows/ci.yml` to run Aegis blueprint tests

## How to push and open a PR in your real repo

1. Copy or move this branch content into your git checkout with remote configured.
2. Add your remote if needed:

```bash
git remote add origin <your-remote-url>
```

3. Push the branch:

```bash
git push -u origin aegis/runnable-blueprints
```

4. Open PR (GitHub CLI):

```bash
gh pr create \
  --base main \
  --head aegis/runnable-blueprints \
  --title "Aegis: runnable blueprint modules + tests + CI" \
  --body "Implements deterministic runnable Aegis module skeletons, adds unit tests, and CI coverage."
```

## Applying from bundle (alternative)

If you receive `artifacts/aegis-runnable-blueprints.bundle`:

```bash
git clone <your-remote-url> repo
cd repo
git fetch /path/to/aegis-runnable-blueprints.bundle aegis/runnable-blueprints:aegis/runnable-blueprints
git checkout aegis/runnable-blueprints
git push -u origin aegis/runnable-blueprints
```

## PR checklist

- [ ] All unit tests pass locally
- [ ] CI passes on PR
- [ ] No secrets included in commits
- [ ] Documentation updated for new module surfaces
- [ ] Follow-up TODOs filed as issues

## Follow-up TODOs

1. Replace deterministic scoring stubs with production scoring/calibration pipelines.
2. Wire `ModelRegistry` to persistent model metadata storage.
3. Add historical replay validation and scenario-based risk tests.
4. Integrate portfolio persistence with durable store (SQLite/Postgres/S3).
5. Replace paper/live broker placeholders with production adapters and retries/circuit breakers.
6. Add marketplace governance (versioning, approval states, promotion policy).
7. Add integration test that runs scoring -> alpha -> risk -> allocation -> execution end-to-end.