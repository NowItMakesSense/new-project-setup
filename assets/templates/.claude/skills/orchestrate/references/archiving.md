# Archiving

`docs/specs/STATUS.md` only holds features still in flight - once a row's phase reaches a terminal state, move it immediately rather than letting the live index grow forever:

1. The moment a feature's row becomes `Released` (after phase 8 is confirmed) or `Reverted` (per `references/revert-checklist.md`), cut that row from `docs/specs/STATUS.md` and paste it as a new entry at the top of `docs/specs/STATUS-archive.md` (create it from the template if missing) in the same write - never leave a feature duplicated in both, and never leave it in neither.
2. This only moves the index row. That feature's own `docs/specs/<feature>/STATUS.md`, `retro.md`, specs and ADRs stay exactly where they are - the archive is a pointer list, not the record itself.
3. If Start step 1's read of `docs/specs/STATUS.md` turns up a feature whose own `docs/specs/<feature>/STATUS.md` already says `Released`/`Reverted` but the index row is still live (an archival step that got missed), archive it now before moving on, and mention it to the user.
