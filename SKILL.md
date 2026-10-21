---
name: new-project-setup
description: Bootstrap a new software project with a complete AI-agent setup - an orchestrator with a modern development workflow, specialist subagents, a grill-me style planning skill, spec-driven development (Clean Code, Clean Architecture, TDD, DDD, SOLID) and layered security that forbids agents from ever touching the system database. Use whenever the user starts a new project, says "novo projeto", "iniciar projeto", "setup do projeto", "bootstrap", "scaffold", or wants an orchestrator/agents/specs structure for a repo - even if they do not name this skill.
---

# new-project-setup

Creates, in the target project, a ready-to-use AI engineering setup for Claude Code (plus a universal `AGENTS.md`).

## Golden rules

This skill only bootstraps other projects; it has no production code, no agents and no database of its own, and it never runs its own output - it is not itself bound by the engineering/security defaults below. Rules 1, 4 and 5 govern how *this skill* behaves while scaffolding. Rules 2 and 3 describe what must be built into the *generated* project.

1. **Ask, never assume.** If any value needed is missing or ambiguous, ask the user. Use `AskUserQuestion` for choices, one topic at a time. Never invent stack, database, names, compliance needs or architecture.
2. **(In the generated project) user instructions override defaults.** Clean Code / Clean Architecture / TDD / DDD / SOLID are defaults the generated project's agents apply only when the user has not said otherwise.
3. **(In the generated project) agents never touch the system database** - no queries, no CLI, no migrations applied, no reading credentials. See `references/security-policy.md`.
4. **Never overwrite existing files silently.** Show what would change and ask.
5. **Instructions in English; project docs/specs in the user's chosen language.**

## Workflow

### Step 1 - Interview (mandatory, before writing anything)
Read `references/interview.md` and collect every required answer. Reuse what the user already said in the conversation; ask for the rest. Save answers to a JSON file (see the answers schema at the end of `interview.md`). Confirm a summary with the user before scaffolding.

### Step 2 - Scaffold
Run (from any directory):

```
python <skill-dir>/scripts/scaffold.py --target <project-dir> --answers <answers.json> [--dry-run]
```

- Always run `--dry-run` first and show the file list to the user.
- Existing files are skipped unless the user explicitly approves `--overwrite`.
- `.tmpl` files get `{{VARIABLES}}` substituted; the suffix is removed.
- Re-scaffolding an already-set-up project (new version of this skill, or retrofit): use `--merge-settings` instead of `--overwrite` to union new deny rules/hooks/`mcpServers` into the existing `.claude/settings.json` by key, without touching anything else in it or any other existing file.

### Step 3 - Verify
```
python <skill-dir>/scripts/verify_setup.py --target <project-dir> --answers <answers.json>
```
Must pass: deny rules present, DB-guard hook present and blocking, agents have valid frontmatter and none can reach the database, the knowledge-graph MCP config (if `NPX_CMD` was set) is well-formed, no unresolved `{{...}}`. Report failures honestly; do not claim success otherwise.

### Step 4 - Hand-off
Tell the user how to continue: run `/plan-grill` in the new project (planning interview), then `/orchestrate` to drive the full workflow. Explain that the DB guard is enforced by `.claude/settings.json` + hook and only works in Claude Code; `AGENTS.md` is advisory for other tools.

## What gets generated

| Path | Purpose |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | Project rules, security policy, workflow summary |
| `.claude/settings.json` | `permissions.deny` for DB/secrets + PreToolUse hook |
| `.claude/hooks/block-db-access.py` | Hard block of DB CLIs, DB URLs, secrets |
| `.claude/hooks/verify-guard.py` | CI guard-rail check: re-runs the deny-rule/hook checks on every push/PR, wired into `ci.yml` |
| `.claude/agents/*.md` | planner, architect, domain, test, qa, implementer, reviewer, security, devops-docs, knowledge-graph, and designer (only when `HAS_UI` is yes); each has a role-tiered default model (opus/sonnet/haiku), overridable per project |
| `.claude/skills/orchestrate` | The orchestrator: 8-phase workflow with human gates |
| `.claude/skills/plan-grill` | grill-me style planning interview (delegates to a real `grill-me` skill if installed) |
| `.claude/skills/spec-writer` | Writes requirements/design/tasks specs per feature |
| `.claude/skills/amend-constitution` | Revises `CLAUDE.md` engineering defaults deliberately, with an ADR - never the DB-access directive |
| `docs/specs`, `docs/adr`, `docs/glossary.md` | Spec-driven artifacts |
| `docs/test-strategy.md`, `docs/debugging-protocol.md` | Test pyramid/fixture guide; 4-phase systematic-debugging protocol |
| `docs/knowledge-graph/` | Domain model as a graph (MCP-backed when `NPX_CMD` is set; markdown fallback otherwise) |
| `docs/specs/_templates/security-report.md` | Per-feature ASVS checklist, filled by `security` |
| `docs/specs/_templates/findings-ledger.md` | Shared reviewer/QA/security findings, with a one-time dispute before a Critical/High blocks a gate |
| `docs/specs/_templates/retro.md` | Short per-feature retro after release, feeding the next `/plan-grill` |
| `.github/workflows/ci.yml` | Only when the user picked GitHub Actions |

References: `references/workflow.md`, `security-policy.md`, `engineering-principles.md`, `spec-format.md`, `test-strategy.md`, `debugging-protocol.md`.
