# Specs

Spec-driven development: every feature lives in `docs/specs/<feature-slug>/` with `requirements.md`, `design.md`, `tasks.md`, `findings-ledger.md`, `security-report.md` once `security` reviews it, and `retro.md` after release (templates in `_templates/`).

- `discovery.md` - result of `/plan-grill` (decisions, out-of-scope, open questions)
- `STATUS.md` (this directory, top-level) - an **index** of all features (phase, owner, status) and the project-wide model/effort choice; kept by whichever orchestrator session last touched a feature, re-read before each edit
- `docs/specs/<feature>/STATUS.md` - that feature's own phase/decisions/open-questions, so concurrent work on different features doesn't collide on one shared block of text
- Status per file: `Draft | Approved | Implemented`
- Code must not contradict an approved spec; change the spec first, with approval.
