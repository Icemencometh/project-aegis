# Aegis GitHub + Claude Integration Checklist

This checklist prepares Claude/Copilot to safely create branches, push commits, open PRs, and participate in review.

## Repository Settings

- [ ] Default branch is `main`.
- [ ] Branch protection enabled on `main`.
- [ ] Require PR for merge to `main`.
- [ ] Require status checks before merge.
- [ ] Disallow force push to `main`.
- [ ] Disallow branch deletion of `main`.

## Required CI Checks

- [ ] `CI / lint`
- [ ] `CI / syntax`
- [ ] `CI / tests`
- [ ] `CI / aegis-blueprints`

If check names differ, update branch protection to exact workflow/check names.

## Authentication Model

- [ ] Use GitHub App or PAT with least privilege.
- [ ] If PAT used, scope minimally (`repo`, optional `workflow`).
- [ ] Never paste credentials in code, docs, issues, or PR comments.
- [ ] Rotate/revoke tokens on suspected exposure.

## Claude/Copilot Operational Rules

- [ ] Create feature branches for every change.
- [ ] Keep commits small and scoped.
- [ ] Include tests with every behavioral change.
- [ ] Open PRs against `main` unless migration policy states otherwise.
- [ ] Use PR template with Summary, Risks, Tests, Rollback.

## PR Workflow

1. Create branch: `feature/<topic>` or `migration/<topic>`.
2. Commit changes with clear module-scoped message.
3. Push branch and open PR.
4. Wait for required checks.
5. Address review comments.
6. Merge only after approvals and green checks.

## Automation Files to Keep Updated

- [CLAUDE.md](CLAUDE.md)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [Aegis_Development_Workflow.md](Aegis_Development_Workflow.md)
- [Claude_Project_Index.md](Claude_Project_Index.md)

## Mode C (Hybrid) Guardrails

- [ ] Production runtime changes must land in `aegis/` first.
- [ ] `quant_bot/` changes must be research-scoped and labeled in PR.
- [ ] Legacy/module cleanup changes must include parity evidence.

## Minimal Command Reference

```bash
git checkout -b feature/my-change
git add -A
git commit -m "module: concise change summary"
git push -u origin feature/my-change
```

Open PR:

```bash
gh pr create --base main --head feature/my-change
```