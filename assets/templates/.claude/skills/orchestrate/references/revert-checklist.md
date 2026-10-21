# If a released feature needs reverting

This is not automated - it's a checklist so nothing gets missed:

1. Revert the actual code (git revert the relevant commits/merge) - a human confirms this, same as any outward-facing action.
2. Mark that feature's `docs/specs/<feature>/STATUS.md` phase as "Reverted" with the reason, and update its row in the top-level index (or in the archive, if it had already been moved there - see `references/archiving.md`).
3. Record an ADR in `docs/adr/` explaining why it was reverted and what was learned.
4. Ask `knowledge-graph` to review entities/relations that came *only* from this feature and propose removing or marking them deprecated - never auto-delete, since later features may have built on them too.
5. Note it in that feature's `retro.md` (or write one now if release happened before this process existed).
