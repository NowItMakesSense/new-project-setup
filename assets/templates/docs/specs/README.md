# Specs

Spec-driven development: every feature lives in `docs/specs/<feature-slug>/` with `requirements.md`, `design.md`, `tasks.md`, and `security-report.md` once `security` reviews it (templates in `_templates/`).

- `discovery.md` - result of `/plan-grill` (decisions, out-of-scope, open questions)
- `STATUS.md` - current phase, feature, decisions, open questions (kept by the orchestrator)
- Status per file: `Draft | Approved | Implemented`
- Code must not contradict an approved spec; change the spec first, with approval.
