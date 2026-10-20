# Orchestrator workflow

Phases run in order. Each ends with a **human gate**: the orchestrator summarizes outputs and asks for approval. Any ambiguity -> go back and ask. Never assume.

| # | Phase | Owner agent(s) | Output | Gate |
|---|---|---|---|---|
| 1 | Discovery | `planner` via `/plan-grill` | `docs/specs/discovery.md` | User confirms summary |
| 2 | Specs | `planner` + `spec-writer` | `docs/specs/<feature>/requirements.md` | User approves requirements |
| 3 | Architecture & Domain | `architect`, `domain` | `design.md`, ADRs, glossary, threat model | User approves design |
| 4 | Task breakdown | `planner` | `tasks.md` (TDD-sized tasks) | User approves tasks |
| 5 | TDD loop (per task) | `test` -> `implementer` -> refactor | Red, green, refactor commits | Tests green |
| 6 | Review | `reviewer` | Findings on Clean Code / SOLID / architecture | Findings resolved or accepted |
| 7 | Security | `security` | ASVS checklist, secrets/deps/SAST results | No open high findings |
| 8 | CI/CD, docs, release | `devops-docs` | Pipeline, README, changelog | User confirms release |

Rules for the orchestrator:
- Delegates; does not write production code itself.
- Passes each subagent only the spec paths and context it needs.
- Never runs DB commands or reads secrets; refuses and escalates.
- Keeps `docs/specs/STATUS.md` updated (phase, feature, open questions).
- Specs and code must stay aligned: a code change that contradicts a spec requires updating the spec first (with approval).
