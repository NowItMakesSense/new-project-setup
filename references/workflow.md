# Orchestrator workflow

Phases run in order. Each ends with a **human gate**: the orchestrator summarizes outputs and asks for approval. Any ambiguity -> go back and ask. Never assume.

| # | Phase | Owner agent(s) | Output | Gate |
|---|---|---|---|---|
| 1 | Discovery | `planner` via `/plan-grill`; `knowledge-graph` seeds/retrofits | `docs/specs/discovery.md`; initial knowledge graph | User confirms summary |
| 2 | Specs | `planner` + `spec-writer` | `docs/specs/<feature>/requirements.md` | User approves requirements |
| 3 | Architecture & Domain | `architect`, `domain`, `knowledge-graph`, `designer` (if `HAS_UI`) | `design.md`, ADRs, glossary, threat model, updated knowledge graph | User approves design |
| 4 | Task breakdown | `planner` | `tasks.md` (TDD-sized tasks) | User approves tasks |
| 5 | TDD loop (per task) | `test` -> `implementer` -> refactor; `debug` if one pass of the protocol doesn't resolve it | Red, green, refactor commits | Tests green |
| 6 | Review & QA | `reviewer`, `qa` | Findings logged in `findings-ledger.md`; integration/e2e/edge-case test results; coverage % | No `Open`/`Confirmed` Critical/High AND QA suite green AND coverage meets `COVERAGE_THRESHOLD` |
| 7 | Security | `security` | `security-report.md` (ASVS checklist); findings in the shared ledger | No `Open`/`Confirmed` Critical/High in the ledger |
| 8 | CI/CD, docs, release | `devops-docs` | Pipeline, README, changelog | User confirms release |
| - | Retro | orchestrator, after phase 8 | `docs/specs/<feature>/retro.md` | Carried-forward items applied before the next feature |

Rules for the orchestrator:
- At start, asks the user which model/effort to use for itself and for the subagents - each subagent already has a role-tiered default set by the `MODEL_PRIORITY` interview answer that the user can keep or override; records the choice in `docs/specs/STATUS.md` (the index) and applies it on every delegation. See `.claude/skills/orchestrate/SKILL.md#model--effort`.
- Also offers an opt-in "autonomous mode" for phases 1-4 only (skips re-confirming each gate individually) - phases 6, 7 and 8 are always human-gated, no matter what the user opts into.
- Before phase 1 on a project's very first `/orchestrate` run, check whether source code already exists with no knowledge graph yet; if so, delegate to `knowledge-graph` for retrofit extraction before anything else, and have it present the proposed graph for confirmation.
- `knowledge-graph` always checks the existing graph before writing (idempotent); it must never silently delete nodes/relations; it also proposes (never auto-applies) consolidation of likely-duplicate entities at the start of each feature's phase 3.
- A Critical/High finding in `findings-ledger.md` never blocks on first report - the responsible agent gets a chance to fix or dispute it, then the agent that raised it makes the final `Confirmed`/`Retracted` call (see `docs/specs/_templates/findings-ledger.md`). If `implementer` still disagrees after that call, it escalates to the user as tie-breaker instead of looping the two agents again.
- If one pass of `docs/debugging-protocol.md` doesn't resolve a failure, delegates to `debug` instead of letting the same agent retry the same approach.
- Before a human gate, confirms the agent re-read its own output for completeness (no blank required section, no leftover open questions) rather than forwarding a draft that isn't actually ready.
- Engineering defaults/prime directives in `CLAUDE.md` are revised only via the `/amend-constitution` skill (which records an ADR), never edited silently - except the DB-access prime directive, which that skill also refuses to touch.
- Delegates; does not write production code itself.
- Passes each subagent only the spec paths and context it needs.
- Never runs DB commands, reads secrets, or calls a cloud secret-manager CLI; refuses and escalates.
- Keeps the feature's own `docs/specs/<feature>/STATUS.md` and the top-level `docs/specs/STATUS.md` index updated (phase, open questions) - re-reads the index before writing it, since other features/sessions share that one file.
- Specs and code must stay aligned: a code change that contradicts a spec requires updating the spec first (with approval).
- If a released feature must be reverted: git-revert the code (human-confirmed), mark the feature's status and index row, record an ADR, and ask `knowledge-graph` to review (never auto-delete) entities that came only from that feature.
