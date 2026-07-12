# CLAUDE.md — Instructions for Claude acting on this repo (PR/issue automation)

This file is read automatically by the `anthropics/claude-code-action` workflow
(`.github/workflows/claude.yml`) whenever `@claude` is mentioned in an issue
or PR. It applies to Claude running unattended in CI — be more conservative
here than in an interactive session, since there is no human watching in
real time before a PR is opened.

## This repo contains three separate systems — know which one you're in

- `aegis/` — the current, contract-driven architecture. Canonical docs:
  `PROJECT_AEGIS_OVERVIEW.txt`, `Aegis_Module_Contracts.md`,
  `Aegis_Coding_Standards.txt`, `Aegis_Development_Workflow.md`,
  `Aegis_AI_Onboarding_Guide.md`. **Read these before touching anything under
  `aegis/`.** The full contract chain is wired together in
  `aegis/orchestrator.py` (`AegisPipeline`).
- `quant_bot/` — a separate, more mature pipeline (features, regime, alpha
  models, scoring, audit logging), exercised by `examples/run_sprint6.py` /
  `run_sprint7.py`. Does not import from `aegis/`.
- Repo root (`modules/`, `main.py`, `orchestrator.py`, `live_loop.py`,
  `approval_queue.py`, etc.) — the original prototype, including the live
  Robinhood integration and the SMS trade-approval flow described in
  `docs/*_blueprint.md`.

Don't casually merge or blur these three. If a task says "the orchestrator"
or "the scoring engine," check which system it actually means before editing.

## Hard safety rules (never violate these, even if asked)

- Never place, modify, or cancel a real order against a live broker. This
  repo's default and only sanctioned execution path is `PaperBroker`
  (`aegis/execution/paper_broker.py`) or `quant_bot`'s mock/replay feed.
  `aegis/execution/live_broker.py` is an intentional placeholder — do not
  make it functional as a side effect of an unrelated task.
- Never read, print, log, or move `robinhood_credentials.json`, or any
  `.env`/API-key/token file. Don't paste secrets into PR descriptions, commit
  messages, or code comments, even to "explain" a bug.
- Never weaken a Risk Engine check, remove a `max_*` config limit, or bypass
  `RiskEngine.evaluate_trades` / `assess_trade`. If a change would do this
  even indirectly, stop and flag it in the PR description instead of making
  the change.
- When unsure, default to the safer option: reduce risk, simplify logic, or
  leave trading halted rather than enabling it.

## Coding standards (from Aegis_Coding_Standards.txt — applies repo-wide)

- Python 3.10+, type hints (PEP 484), PEP 8 style.
- One responsibility per module; don't mix data/scoring/risk/execution in a
  single file. Cross-module calls go through the defined interfaces, not
  ad-hoc imports.
- Core logic (scoring, risk, allocation) must be deterministic given its
  inputs — no hidden global state, no unseeded randomness in anything that
  feeds a trading decision.
- Thresholds and limits belong in config (`aegis/config/*.yaml`,
  `config/*.yaml`), never hardcoded in code.
- No `print()` in production code paths; use the existing logger
  (`aegis/common/logging.get_logger`, `quant_bot/utils/logging.py`).

## Before opening a PR

1. Add or update unit tests for anything you change (see `tests/`, run with
   `python -m pytest tests/ -q` or `python -m unittest discover -s tests`).
2. Keep commits small and focused; commit message format `module: short
   description`.
3. PR description must state what changed, why, what tests were run, and any
   risk (per `Aegis_Development_Workflow.md`).
4. If a change touches `Aegis_Module_Contracts.md`-defined interfaces, update
   that doc in the same PR.
5. Don't add new third-party dependencies without calling it out explicitly
   in the PR description.

## What you're allowed to do here

- Create branches and open PRs (never push directly to `main`).
- Edit and add files following the module boundaries above.
- Run the test suite.
- Ask a clarifying question in the issue/PR thread instead of guessing when
  the request is ambiguous about which system (`aegis/` vs `quant_bot/` vs
  root) it targets.
