# Status (project index)

One row per feature in flight or done. Each feature's own phase/decisions/open-questions live in `docs/specs/<feature>/STATUS.md` (template: `_templates/feature-status.md`) - this file only indexes them, so two people working different features don't collide editing the same block of text.

| Feature | Phase | Owner | Last updated | Status |
|---|---|---|---|---|

## Concurrency
Before editing a row here, re-read the file first - if a row changed since you last looked, someone else is mid-update; reconcile with the user instead of silently overwriting it. A feature's own `docs/specs/<feature>/STATUS.md` only that feature's orchestrator session touches, so it doesn't need the same care.

## Models & effort
Set by `/orchestrate` on first run; ask the user before filling this in. Applies project-wide, not per feature.

| Role | Model | Effort |
|---|---|---|
| orchestrator | TBD | TBD |
| default (all subagents) | TBD | TBD |
| overrides | - | - |
