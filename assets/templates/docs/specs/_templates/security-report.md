# Security report: <feature or release>

Status: Draft | Date: | Reviewed by:

## Scope
What was reviewed (feature/area, commit or PR range).

## ASVS checklist
| Category | Checked | Findings |
|---|---|---|
| AuthN/AuthZ | | |
| Input validation & injection | | |
| Secrets & dependencies / supply-chain | | |
| Infra & config | | |
| Database access control (roles, privilege matrix, no runtime DDL, TLS) | | |
| API security | | |
| Business-logic abuse | | |
| Compliance (see CLAUDE.md) | | |

## Findings
Logged in the shared `findings-ledger.md` for this feature, not duplicated here - see `docs/specs/<feature>/findings-ledger.md`.

## DB-guard integrity check
- `.claude/settings.json` deny rules unchanged: Yes/No
- `.claude/hooks/block-db-access.py` present and blocking: Yes/No

## Sign-off
No `Open` or `Confirmed` Critical/High row in `findings-ledger.md` before this is marked Approved.
