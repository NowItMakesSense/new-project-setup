# Orchestrator workflow

Phases run in order. Each ends with a **human gate**: the orchestrator summarizes outputs and asks for approval. Any ambiguity -> go back and ask. Never assume.

| # | Phase | Owner agent(s) | Output | Gate |
|---|---|---|---|---|
| 1 | Discovery | `planner` via `/plan-grill`; `knowledge-graph` rebuilds the graph | `docs/specs/discovery.md`; refreshed project graph | User confirms summary |
| 2 | Spec & requirements | `planner` + `/to-spec` + `/spec-writer` | `prd.md` (user stories, implementation/testing decisions), then `requirements.md` | User approves each |
| 3 | Architecture & Domain | `architect`, `domain`, `designer` (if `HAS_UI`) | `design.md` (incl. feature diagram), ADRs, glossary, threat model, `Database/` update + `overview.html` (if the feature touches UI/DB) | User approves design |
| 4 | Task breakdown | `planner` + `/to-tickets` | `tasks.md` (tracer-bullet slices with `Blocked by`, `Demo`, `Status`) | User approves tasks |
| 5 | TDD loop (per task) | `test` -> the task's owner (`implementer`, or `frontend` for `Owner: frontend`) -> refactor; `debug` if one pass of the protocol doesn't resolve it | Red, green, refactor commits | Tests green |
| 6 | Review & QA | `reviewer` (`/review-change`: Standards + Spec axes), `qa`, `ui-reviewer` (when a task has `Owner: frontend`) | Findings logged in `findings-ledger.md`; integration/e2e/edge-case test results; coverage % | No `Open`/`Confirmed` Critical/High AND QA suite green AND coverage meets `COVERAGE_THRESHOLD` |
| 7 | Security | `security` | `security-report.md` (ASVS checklist); findings in the shared ledger | No `Open`/`Confirmed` Critical/High in the ledger |
| 8 | CI/CD, docs, release | `devops-docs` (+ `launch-readiness`) | Pipeline, README, changelog, launch checklist | User confirms release |
| - | Retro | orchestrator, after phase 8 | `docs/specs/<feature>/retro.md` | Carried-forward items applied before the next feature |

Rules for the orchestrator:
- At start, asks the user which model/effort to use for itself and for the subagents - each subagent already has a role-tiered default set by the `MODEL_PRIORITY` interview answer that the user can keep or override; records the choice in `docs/specs/STATUS.md` (the index) and applies it on every delegation. See `.claude/skills/orchestrate/SKILL.md#model--effort`.
- `/orchestrate` accepts a spec path, feature slug or free-text request, and resumes from `.claude/scripts/spec-state.py` (what exists, task frontier, next phase) instead of restarting; approved artifacts are never regenerated and `done` tasks never redone.
- Also offers an opt-in "autonomous mode" for phases 1-4 only (skips re-confirming each gate individually) - phases 6, 7 and 8 are always human-gated, no matter what the user opts into.
- At the start of a feature `/orchestrate` rebuilds the project graph (`.claude/scripts/build-graph.py`: files as nodes, relationships as edges, generated from the files - nothing to retrofit or confirm).
- The graph is generated, never hand-edited; agents query it (`build-graph.py query|explain|path`) before grepping. `EXTRACTED` edges are written in the files; `INFERRED` edges are leads to verify.
- A Critical/High finding in `findings-ledger.md` never blocks on first report - the responsible agent gets a chance to fix or dispute it, then the agent that raised it makes the final `Confirmed`/`Retracted` call (see `docs/specs/_templates/findings-ledger.md`). If `implementer` still disagrees after that call, it escalates to the user as tie-breaker instead of looping the two agents again.
- If one pass of `docs/debugging-protocol.md` doesn't resolve a failure, delegates to `debug` instead of letting the same agent retry the same approach.
- Before a human gate, confirms the agent re-read its own output for completeness (no blank required section, no leftover open questions) rather than forwarding a draft that isn't actually ready.
- Engineering defaults/prime directives in `CLAUDE.md` are revised only via the `/amend-constitution` skill (which records an ADR), never edited silently - except the DB-access prime directive, which that skill also refuses to touch.
- Delegates; does not write production code itself.
- Passes each subagent only the spec paths and context it needs.
- Never runs DB commands, reads secrets, or calls a cloud secret-manager CLI; refuses and escalates.
- Keeps the feature's own `docs/specs/<feature>/STATUS.md` and the top-level `docs/specs/STATUS.md` index updated (phase, open questions) - re-reads the index before writing it, since other features/sessions share that one file.
- Specs and code must stay aligned: a code change that contradicts a spec requires updating the spec first (with approval).
- If a released feature must be reverted: git-revert the code (human-confirmed), mark the feature's status and index row, record an ADR, and rebuild the project graph so removed files and their relationships disappear.
