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

## Phases (never skip; each ends with a human gate)
| # | Phase | Delegate to | Output | Gate |
|---|---|---|---|---|
| 1 | Discovery | `planner` + `/plan-grill` | `docs/specs/discovery.md` | User confirms summary |
| 2 | Requirements | `planner` + `/spec-writer` | `requirements.md` | User approves |
| 3 | Architecture & domain | `architect`, `domain` | `design.md`, ADRs, glossary, threat model | User approves |
| 4 | Tasks | `planner` | `tasks.md` (TDD-sized) | User approves |
| 5 | TDD loop, per task | `test` (red) -> `implementer` (green) -> `implementer` (refactor) | Code + tests | Tests green |
| 6 | Review | `reviewer` | Findings (Clean Code, SOLID, layering, spec alignment) | Resolved/accepted |
| 7 | Security | `security` | ASVS checklist, secrets/deps/SAST, DB-policy check | No open high |
| 8 | CI/CD & docs | `devops-docs` | Pipeline, README, changelog | User confirms |

## Delegation rules
- Give each subagent only: the task, the relevant spec paths, constraints. Require it to report back questions instead of guessing.
- Subagent questions are relayed to the user (AskUserQuestion), never answered by you.
- Run independent tasks in parallel only when they touch different files.
- After each phase, update `docs/specs/STATUS.md` (phase, feature, decisions, open questions).
- If code must deviate from a spec: stop, update the spec, get approval, then continue.
- If any agent reports it needs DB access or secrets: refuse, explain, ask the user for a human-run alternative or a fake/fixture.

## Done criteria
All requirement IDs traced to passing tests, review and security gates closed, docs updated, user confirmed.
