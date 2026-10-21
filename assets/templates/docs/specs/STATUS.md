# Status (project index)

One row per feature **still in flight**. Each feature's own phase/decisions/open-questions live in `docs/specs/<feature>/STATUS.md` (template: `_templates/feature-status.md`) - this file only indexes them, so two people working different features don't collide editing the same block of text.

Once a feature's phase becomes `Released` or `Reverted`, its row moves to `docs/specs/STATUS-archive.md` instead of staying here - see `orchestrate/SKILL.md`'s "Archiving" section. This keeps the live index small on a long-running project instead of growing forever.

| Feature | Phase | Owner | Lease (who @ when) | Last updated | Status |
|---|---|---|---|---|---|

## Concurrency (lease convention, not a real lock)
This is a convention agents follow, not a filesystem lock - it narrows the two-people-same-row collision window, it doesn't eliminate it. There is still no atomic test-and-set across two sessions reading this file at nearly the same instant.

Before editing a row here:
1. Re-read the file. If the row's `Lease` is set by someone else and its timestamp is less than 15 minutes old, treat the row as mid-update - do not write; reconcile with the user instead of overwriting it.
2. If the row is free (`Lease` empty, or older than 15 minutes - stale, likely an abandoned session), set `Lease` to `<owner> @ <ISO-8601 timestamp>` before you start writing, then make your edits.
3. Clear `Lease` back to empty as the last step of your edit, in the same write that applies your change.

A feature's own `docs/specs/<feature>/STATUS.md` is only ever touched by that feature's own orchestrator session, so it doesn't need this.

## Models & effort
Set by `/orchestrate` on first run; ask the user before filling this in. Applies project-wide, not per feature.

| Role | Model | Effort |
|---|---|---|
| orchestrator | TBD | TBD |
| default (all subagents) | TBD | TBD |
| overrides | - | - |
