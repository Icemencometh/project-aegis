# Aegis AI Onboarding Guide

This guide is for Claude or any AI system contributing to Aegis.

---

## Read These Files First

1. PROJECT_AEGIS_OVERVIEW.txt
2. Aegis_Module_Contracts.md
3. Aegis_Coding_Standards.txt
4. Aegis_Development_Workflow.md

---

## What Aegis Is

Aegis is an autonomous quantitative research and execution platform designed to:

- run multiple strategies,
- score opportunities probabilistically,
- enforce strict risk,
- paper trade by default,
- support a controlled path to live.

---

## How Modules Interact

- Data -> Features -> Regime -> Strategies -> Scoring Hub -> Alpha Hub -> Risk Engine -> Portfolio -> Execution -> Broker.
- Research Engine runs in parallel for backtests and validation.

---

## Safe Coding Rules for AI

- Do not bypass risk controls.
- Do not introduce hidden global state.
- Do not change module contracts without updating Aegis_Module_Contracts.md.
- Prefer explicit, simple logic over clever optimizations.
- Keep behavior deterministic given inputs.

---

## How to Add Code

1. Identify the correct module (example: new scorer -> scoring/modules/).
2. Read its contract in Aegis_Module_Contracts.md.
3. Follow Aegis_Coding_Standards.txt.
4. Add unit tests.
5. Ensure CI passes.

---

## Common Mistakes to Avoid

- Mixing responsibilities (example: risk logic inside execution).
- Hard-coding thresholds instead of using config.
- Ignoring logging and audit requirements.
- Weakening risk limits.
- Adding indicators without out-of-sample validation.

---

## How to Work With Strategies

- Strategies emit trade candidates, not orders.
- Strategy Marketplace manages activation and capital allocation.
- Do not let a single strategy dominate the portfolio.

---

## How to Work With Scoring Hub

- Scoring Hub combines multiple scorers and weights.
- Meta-Model can override or adjust composite scores.
- Every scored trade must include rationale.

---

## How to Work With Risk Engine

- Risk Engine is the hard boundary before execution.
- No trade may pass without risk checks.
- Risk Engine can halt trading and flatten positions.

---

## How to Work With Execution Engine

- Execution Engine talks to brokers via abstraction.
- Must handle partial fills, retries, and disconnects.
- Must log execution quality metrics.

---

## Final Rule

If in doubt, reduce risk or stop trading.
Aegis is a research and execution platform, not a speculative bot.
