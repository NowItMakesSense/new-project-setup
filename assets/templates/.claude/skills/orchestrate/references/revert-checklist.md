# If a released feature needs reverting

This is not automated - it's a checklist so nothing gets missed:

1. Revert the actual code (git revert the relevant commits/merge) - a human confirms this, same as any outward-facing action.
2. Mark that feature's `docs/specs/<feature>/STATUS.md` phase as "Reverted" with the reason, and update its row in the top-level index (or in the archive, if it had already been moved there - see `references/archiving.md`).
3. Record an ADR in `docs/adr/` explaining why it was reverted and what was learned.
4. Rebuild the project graph (`build-graph.py`) so removed files and their relationships disappear, and check `GRAPH_REPORT.md` for new broken references left behind.
5. Note it in that feature's `retro.md` (or write one now if release happened before this process existed).
