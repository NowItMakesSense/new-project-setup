# Findings ledger: <feature>

Shared by `reviewer`, `qa` and `security` (phases 6-7) - one running table per feature instead of three separate, disconnected reports. Append, never silently delete a row.

## Rule
A **Critical/High** finding never blocks a gate on its first report. Before it counts as blocking:
1. The agent that raised it logs it here as `Open`, with evidence (file:line, repro, or ASVS category).
2. The orchestrator asks the responsible agent (usually `implementer`, sometimes `architect`/`domain`) to respond: fix it, or dispute it with a concrete reason.
3. If disputed, the agent that raised the finding reviews the response and sets it to `Confirmed` (still blocks) or `Retracted` (false positive, logged anyway for the record - never deleted).
4. Only `Open` or `Confirmed` Critical/High rows block the phase 6/7 gate. `Fixed` and `Retracted` do not.

This exists so one wrong LLM guess doesn't stall a feature - but a real issue can't be waved away without a second, independent look either.

## Ledger
| ID | Source | Severity | Finding | Location | Status | Response / resolution |
|---|---|---|---|---|---|---|
| F-001 | reviewer / qa / security | Critical / High / Medium / Low | | file:line | Open / Fixed / Confirmed / Retracted | |

## Summary before the gate
- Open or Confirmed Critical/High: <count> (must be 0 to pass)
- Fixed: <count>
- Retracted: <count>
