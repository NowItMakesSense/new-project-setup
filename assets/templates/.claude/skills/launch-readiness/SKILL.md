---
name: launch-readiness
description: Pre-release checklist for phase 8 - performance budget, observability, rollout and rollback, migration safety, documentation and ADRs - scaled to the project's real scenario. Use before releasing a feature, when the user says "release", "ship", "go live", "launch", "deploy plan", or when devops-docs prepares phase 8.
---

# launch-readiness

Run it per feature in phase 8 and record the result in the feature's `docs/specs/<feature>/STATUS.md`. Scale it to the project (`PROJECT_TYPE`, `COMPLIANCE`, `TEAM` in CLAUDE.md): a solo CLI needs three lines per section, a regulated API needs all of it. Mark a section `N/A` with a reason instead of skipping it silently. Never deploy, push or publish from here - this skill produces the checklist and the evidence; a human performs the release.

## 1. Evidence the gates passed
Read, don't assume: `check-traceability.py --feature <f>` clean; `findings-ledger.md` has no `Open`/`Confirmed` Critical/High; `security-report.md` approved; coverage vs `COVERAGE_THRESHOLD` is a number from real output.

## 2. Performance
Compare the feature against the NFR targets in `requirements.md` (latency p50/p95/p99, throughput). Measure before optimizing: name the measurement (benchmark, load test against a fake/disposable environment, profiler output) or record "no target defined" as an open item for the user. Look for N+1 access, unbounded queries/lists, missing pagination, work on the hot path, and (UI) bundle weight and Core Web Vitals. Never load-test against the system database.

## 3. Observability
For each failure mode in `design.md`: is it logged (structured, no secrets or personal data), counted (request rate, errors, duration), and traceable (correlation id)? Is there at least one alert on a user-visible symptom rather than an internal cause? Can on-call tell "it is broken" from "it is slow" from the dashboards that exist?

## 4. Rollout and rollback
- How does it reach users: all at once, staged, behind a flag? Which is safest for this change?
- How is it undone: revert commit, flag off, redeploy previous artifact? State the exact steps and who confirms them (see `orchestrate/references/revert-checklist.md`).
- Migrations: generated as files only; backward-compatible with the previous app version (expand -> migrate -> contract); applied by a human with the migrator role, never by the application at startup and never by an agent.
- Config and secrets the release needs are named, with where they come from - values are never read or written by agents.

## 5. Documentation and decisions
README/setup/runbook updated to match the release; changelog entry written; every architectural decision made while building has an ADR in `docs/adr/`; `docs/glossary.md` matches the code's names; the docs index and graph are refreshed (`index-docs.py`, `render-graph.py`).

## 6. Output
A short checklist with each item `done` / `N/A (reason)` / `open (owner)`. Any `open` item is reported to the orchestrator before the phase 8 gate; the user decides whether it blocks.

## Rationalizations (rejected)
| Excuse | Reality |
|---|---|
| "We can add monitoring after launch" | You are blind exactly when it matters; at minimum log and count failures now. |
| "Rollback is just git revert" | Not once a migration or external side effect has run; say what happens to the data. |
| "Performance was fine on my machine" | Without a named measurement against the NFR target it is an opinion. |
