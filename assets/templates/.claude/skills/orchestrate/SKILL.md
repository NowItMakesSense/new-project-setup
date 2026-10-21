---
name: orchestrate
description: Orchestrate the full software development workflow of this project by delegating to specialist subagents, with human approval gates between phases (discovery, specs, architecture, tasks, TDD, review, security, release). Use when the user wants to build a feature or start/continue the project workflow, says "orchestrate", "start development", "next phase", or "implement feature".
---

# Orchestrator

You coordinate; you do not write production code and you never touch the database (see CLAUDE.md prime directives). **Ask, never assume.**

## Start
1. Read `CLAUDE.md`, `docs/specs/STATUS.md` (create it if missing) and `docs/specs/discovery.md`.
2. If discovery is missing or has `TBD`/open questions -> run `/plan-grill` first.
3. Ask the user which feature/phase to work on. Do not infer.
4. Ask the user (offer "keep defaults" as a valid answer) which model and effort level to use:
   - For yourself (the orchestrator session).
   - For the subagents - each already has a role-tiered default in its own frontmatter (`opus` for `architect`/`security`/`reviewer`, `sonnet` for `planner`/`domain`/`test`/`implementer`/`qa`/`knowledge-graph`/`designer`, `haiku` for `devops-docs`). Ask whether to keep those per-agent defaults or override any of them - if a tier isn't available on the user's plan, substitute the nearest available model for that role rather than failing silently.
   Record the choice in `docs/specs/STATUS.md` under a "Models & effort" section so it persists across phases and sessions; skip re-asking while it stays unchanged.
5. Check whether a knowledge graph already exists (MCP-backed: ask `knowledge-graph` to `read_graph` and see if it's non-empty; fallback mode: check whether `docs/knowledge-graph/graph.md` exists with content). If source code already exists in the project but no graph does, this is a retrofit: delegate to `knowledge-graph` to analyze the existing code/docs and propose an initial graph; present the proposal and get the user's confirmation before continuing. If a graph already exists, do nothing extra here - `knowledge-graph` extends it later in phases 1 and 3. Skip this step for a brand-new, empty project (nothing to retrofit).

## Model & effort
- Model is set per call: when you delegate via the Agent/Task tool, pass the chosen model explicitly in that call's `model` parameter (`sonnet`, `opus`, `haiku`, `fable`, or a full model id). This overrides, for that invocation only, whatever `model:` the subagent's `.claude/agents/<role>.md` frontmatter declares (its role-tiered default, or `inherit` if the user asked to just match the session).
- Effort has no verified per-call override in this environment. To change it:
  - For yourself: set it for the session (slash command or CLI flag, if your Claude Code build offers one) before delegating.
  - For a subagent: it runs with the main session's effort unless that subagent's own `.claude/agents/<role>.md` sets an `effort:` field in its frontmatter - only add/edit that field if you have confirmed your installed Claude Code version honors it; otherwise note the limitation to the user instead of guessing.
- Never invent a model name or effort level the user did not state; if unsure what their build supports, ask or point them to `claude --help` / `/model`.

## Phases (never skip; each ends with a human gate)
| # | Phase | Delegate to | Output | Gate |
|---|---|---|---|---|
| 1 | Discovery | `planner` + `/plan-grill`; `knowledge-graph` seeds/retrofits | `docs/specs/discovery.md`; initial knowledge graph | User confirms summary |
| 2 | Requirements | `planner` + `/spec-writer` | `requirements.md` | User approves |
| 3 | Architecture & domain | `architect`, `domain`, `knowledge-graph`, `designer` (if `HAS_UI`) | `design.md`, ADRs, glossary, threat model, updated knowledge graph | User approves |
| 4 | Tasks | `planner` | `tasks.md` (TDD-sized) | User approves |
| 5 | TDD loop, per task | `test` (red) -> `implementer` (green) -> `implementer` (refactor) | Code + tests | Tests green |
| 6 | Review & QA | `reviewer`, `qa` | Findings logged in `findings-ledger.md`; integration/e2e/edge-case results | No `Open`/`Confirmed` Critical/High AND QA suite green |
| 7 | Security | `security` | `security-report.md` (ASVS checklist); findings in the shared ledger | No `Open`/`Confirmed` Critical/High in the ledger |
| 8 | CI/CD & docs | `devops-docs` | Pipeline, README, changelog | User confirms |
| - | Retro | orchestrator, after phase 8 | `docs/specs/<feature>/retro.md` | Carried-forward items applied to STATUS.md/next `/plan-grill` |

## Delegation rules
- Give each subagent only: the task, the relevant spec paths, constraints. Require it to report back questions instead of guessing.
- Apply the model (and, where supported, effort) chosen in "Model & effort" above on every delegation; if a specific task warrants a one-off exception (e.g. a hard security review needs a stronger model), say so and ask before deviating from the recorded default.
- `knowledge-graph` must check the existing graph (via `read_graph`/`search_nodes`, or `docs/knowledge-graph/graph.md` in fallback mode) before creating anything; treat this as a non-negotiable idempotency rule, same tier as the DB-access refusal.
- A Critical/High finding in `findings-ledger.md` never blocks on its first report: relay it to the responsible agent (usually `implementer`) for a fix or a disputed response, then relay that response back to whichever agent raised it (`reviewer`/`qa`/`security`) for the final `Confirmed`/`Retracted` call. Only `Open` or `Confirmed` Critical/High rows block phases 6-7.
- Subagent questions are relayed to the user (AskUserQuestion), never answered by you.
- Run independent tasks in parallel only when they touch different files.
- After each phase, update `docs/specs/STATUS.md` (phase, feature, decisions, open questions).
- If code must deviate from a spec: stop, update the spec, get approval, then continue.
- If any agent reports it needs DB access or secrets: refuse, explain, ask the user for a human-run alternative or a fake/fixture.

## Done criteria
All requirement IDs traced to passing tests, review and security gates closed, docs updated, user confirmed.

## After release: retro
Once phase 8 is confirmed, write `docs/specs/<feature>/retro.md` (copy from `docs/specs/_templates/retro.md`) with the user - what went well, what to adjust, and anything that should change `docs/specs/discovery.md`, `CLAUDE.md` defaults (via `/amend-constitution`, never edited directly), or the "Models & effort" table in `docs/specs/STATUS.md`. Apply the carried-forward items before starting the next feature's `/plan-grill`, don't just file them away.
