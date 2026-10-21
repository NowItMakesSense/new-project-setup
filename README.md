# new-project-setup

**A Claude Code skill that bootstraps a new software project with a real AI-engineering team already wired in — an orchestrator, specialist subagents covering planning, architecture, domain modeling, UI/UX (when there's a UI), unit testing, broader QA, implementation, code review, exhaustive security, DevOps/docs, and a domain knowledge graph — plus a relentless planning interview, spec-driven development, and a DB/secrets guard that agents cannot bypass.**

Stop hand-rolling the same `CLAUDE.md`, the same guardrails, the same "please don't run migrations against prod" reminder on every new repo. Run this skill once per project and get a setup that keeps agents honest, specs in sync with code, and your production database completely out of reach — no matter what any agent is asked to do.

## Why you'd want this

- **You stop re-writing boilerplate.** One skill call replaces an hour of copy-pasting `CLAUDE.md`/`AGENTS.md`, agent prompts and CI scaffolding between projects.
- **Agents can't touch your database — structurally, not by promise.** Four independent layers (deny rules, a PreToolUse hook, textual rules in every prompt, and no agent ever holding credentials) block `psql`, `prisma migrate`, `docker exec`, reading `.env`, and every workaround a model might try. It fails closed on malformed input.
- **No code before a spec exists.** Every feature goes through a planning interview, then EARS/Gherkin requirements, a design doc with a threat model, and TDD-sized tasks — all gated by your explicit approval, not the model's judgment call.
- **It never guesses.** Missing stack, unclear scope, an ambiguous "fast" or "secure" — the skill (and everything it generates) stops and asks instead of inventing an answer.
- **Works beyond Claude Code too.** A stack-agnostic `AGENTS.md` ships alongside the Claude-specific `.claude/` setup, so the same rules travel with you to other AI coding tools (enforcement there is advisory, not hooked).
- **Sensible cost/quality defaults out of the box, still yours to override.** Every agent ships with a role-tiered default (`opus` for architect/security/reviewer, `sonnet` for the rest of the delivery team, `haiku` for devops-docs) instead of one blanket setting - `/orchestrate` asks once whether to keep or override them.
- **A real test and QA story, not just a string.** A `references`/`docs` test-strategy guide spells out the pyramid and fixture conventions; a dedicated `qa` agent covers integration/e2e/edge-case/regression testing beyond the TDD unit tests `test` writes.
- **Debugging has a protocol, not vibes.** A 4-phase systematic-debugging guide (reproduce → root cause → minimal hypothesis → fix + regression test) stops agents from patching symptoms they don't understand.
- **The domain model is a real graph, not just a table.** A `knowledge-graph` agent persists entities/value objects/aggregates/bounded contexts and their relationships to an MCP-backed graph, seeded from discovery/design and extendable from an existing codebase on retrofit.
- **The guard-rail checks itself, continuously.** CI re-runs the deny-rule/hook checks on every push so a weakened setting doesn't drift in silently - and this skill's own scaffolding logic has a regression suite (`scripts/test_scaffold.py`) covering the full answer matrix, run on every push to this repo too.
- **A Critical finding gets one dispute before it blocks you.** `reviewer`, `qa` and `security` share one findings ledger per feature instead of three disconnected reports; a Critical/High row isn't final until the accused code gets to respond and the agent that raised it makes the final call - real issues still block, false positives don't stall the feature.
- **The "constitution" is revisable, not frozen at scaffold time.** `/amend-constitution` lets you change engineering defaults later with an ADR recording why - except the DB-access directive, which no path can touch.

## What you get, in one command

| Path | Purpose |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | Project rules, security policy, workflow summary — one Claude-specific, one universal |
| `.claude/settings.json` | `permissions.deny` blocking DB CLIs, migration runners, `docker exec`, secrets |
| `.claude/hooks/block-db-access.py` | Runtime hook: catches connection strings, wrapper calls, and workarounds the deny list misses |
| `.claude/hooks/verify-guard.py` | CI guard-rail: re-runs the deny-rule/hook checks on every push/PR so drift gets caught |
| `.claude/agents/*.md` | `planner`, `architect`, `domain`, `test`, `qa`, `implementer`, `reviewer`, `security`, `devops-docs`, `knowledge-graph`, and `designer` (only when the project has a UI) |
| `.claude/skills/orchestrate` | The orchestrator: an 8-phase workflow with a human approval gate after every phase |
| `.claude/skills/plan-grill` | A grill-me-style planning interview — one question at a time, walks every branch until nothing is ambiguous |
| `.claude/skills/spec-writer` | Writes `requirements.md` (EARS + Gherkin), `design.md`, `tasks.md` per feature |
| `.claude/skills/amend-constitution` | Revises `CLAUDE.md` engineering defaults later, with an ADR - never the DB-access directive |
| `docs/specs/`, `docs/adr/`, `docs/glossary.md` | Spec-driven artifacts, architectural decisions, ubiquitous language |
| `docs/test-strategy.md`, `docs/debugging-protocol.md` | Test pyramid/fixture guide; 4-phase systematic-debugging protocol |
| `docs/knowledge-graph/` + `.claude/agents/knowledge-graph.md` | The domain model as a real graph (entities, VOs, aggregates, bounded contexts, relationships), MCP-backed when Node/`npx` is available |
| `docs/specs/_templates/security-report.md` | Per-feature ASVS checklist, filled by `security` |
| `docs/specs/_templates/findings-ledger.md` | Shared reviewer/QA/security findings, one dispute before a Critical/High blocks a gate |
| `docs/specs/_templates/retro.md` | Short per-feature retro after release, carried into the next `/plan-grill` |
| `.github/workflows/ci.yml` | Lint/test/build/secret-scan/guard-rail pipeline (only if you picked GitHub Actions) |

Nothing here is invented per project — every value comes from an interview you confirm before anything is written, and existing files are never overwritten silently.

## The workflow it sets up

```
/plan-grill  →  requirements  →  architecture & domain  →  tasks  →  TDD loop  →  review  →  security  →  CI/CD & release
   (discovery)                                                 (red→green→refactor)
```

Each arrow is a **human gate**: the orchestrator summarizes what a subagent produced and waits for your approval before moving on. It delegates and tracks state (`docs/specs/STATUS.md`) — it never writes production code itself, and it never runs anything against a database.

| # | Phase | Delegate to | Output |
|---|---|---|---|
| 1 | Discovery | `planner` via `/plan-grill`; `knowledge-graph` seeds/retrofits | `docs/specs/discovery.md`; initial knowledge graph |
| 2 | Requirements | `planner` + `spec-writer` | `requirements.md` |
| 3 | Architecture & domain | `architect`, `domain`, `knowledge-graph`, `designer` (if the project has a UI) | `design.md`, ADRs, glossary, threat model, updated knowledge graph |
| 4 | Task breakdown | `planner` | `tasks.md` (TDD-sized) |
| 5 | TDD loop, per task | `test` → `implementer` | failing test → green → refactor |
| 6 | Review & QA | `reviewer`, `qa` | Findings in the shared `findings-ledger.md`; integration/e2e/edge-case results |
| 7 | Security | `security` | `security-report.md`: exhaustive ASVS checklist (authN/authZ, injection, secrets/supply-chain, infra, API, business-logic abuse, compliance), DB-policy check; findings in the ledger |
| 8 | CI/CD & docs | `devops-docs` | pipeline, README, changelog, tailored to the project's own scenario |
| — | Retro | orchestrator | `retro.md`, applied before the next feature's `/plan-grill` |

## The security model (defense in depth)

No agent can reach the system database — not by convention, by four independent layers:

1. **Deny rules** (`permissions.deny` in `.claude/settings.json`) block every common DB CLI, ORM/migration runner, `docker exec`/`kubectl exec`, and reads/writes of `.env*`, `secrets/`, keys and credentials.
2. **A PreToolUse hook** (`.claude/hooks/block-db-access.py`) catches what the deny list can't enumerate: raw connection strings, shell wrappers, piping through `bash -c`. It fails closed on malformed input.
3. **Textual rules** repeated in `CLAUDE.md`, `AGENTS.md`, and every single subagent prompt, so the model is told, not just blocked.
4. **Structural guarantees**: no agent ever receives credentials; tests run against fakes/in-memory doubles or disposable containers a human starts; migrations are only ever *generated as files* for a human to review and apply.
5. **Continuous verification**: `.claude/hooks/verify-guard.py` re-runs the deny-rule and hook-blocking checks in CI on every push/PR (wired into `ci.yml` when you picked GitHub Actions), so a weakened deny list or a disabled hook gets caught automatically instead of drifting silently.

If a task seems to need DB access, every agent is instructed to stop and ask — never work around the guard. Full detail: `references/security-policy.md`.

**Scope note:** this skill only bootstraps *other* projects. It has no production code, no agents and no database of its own — the engineering defaults and DB guard above describe what gets built into the *generated* project, never this skill's own behavior.

## Using it

Just tell Claude Code you're starting a project — "novo projeto", "iniciar projeto", "setup do projeto", "bootstrap", "scaffold" all trigger it, even without naming the skill. It will:

1. **Interview you** (`references/interview.md`) — project name, stack, DB engine, test strategy, compliance needs, CI provider, branching convention, engineering defaults to keep or override, whether the project has a UI (`HAS_UI`, gates the `designer` agent), and whether Node.js/`npx` is available (`NPX_CMD`, gates the MCP-backed knowledge graph). Anything you don't know is recorded as `TBD` and resolved later in `/plan-grill`, never guessed.
2. **Scaffold a dry run first**, show you the file list, then write for real:
   ```
   python scripts/scaffold.py --target <project-dir> --answers <answers.json> --dry-run
   python scripts/scaffold.py --target <project-dir> --answers <answers.json>
   ```
   Re-running this on an already-scaffolded project (new skill version, or retrofit): pass `--merge-settings` instead of `--overwrite` to union new deny rules/hooks/`mcpServers` into the existing `.claude/settings.json` by key, without touching anything else in it.
3. **Verify itself**:
   ```
   python scripts/verify_setup.py --target <project-dir> --answers <answers.json>
   ```
   Checks the deny rules, that the hook actually blocks `psql`/`docker exec`/`.env` reads and allows normal commands, that every agent carries the DB rule, that the knowledge-graph MCP config matches what the interview asked for, and that no `{{TEMPLATE_VAR}}` was left unresolved. `--answers` is optional - without it, the mcpServers check is informational only.
4. **Hand off**: run `/plan-grill` in the new project, then `/orchestrate` to drive the full workflow.

## Repository layout

```
SKILL.md                         entry point Claude Code loads
CHANGELOG.md                     this skill's own history (not shipped to generated projects)
.github/workflows/test.yml        this repo's own CI - runs scripts/test_scaffold.py on every push/PR
references/                      interview script, workflow, security policy, engineering principles,
                                  spec format, test-strategy guide, debugging protocol (this skill's own notes)
scripts/scaffold.py               renders assets/templates/ into --target (supports --merge-settings)
scripts/verify_setup.py           checks the result is actually safe and complete
scripts/test_scaffold.py          regression suite for scaffold.py/verify_setup.py (stdlib unittest)
assets/templates/                 everything scaffold.py copies into the generated project
  CLAUDE.md.tmpl, AGENTS.md.tmpl
  .claude/settings.json.tmpl, .claude/hooks/{block-db-access.py, verify-guard.py}
  .claude/agents/*.md             planner, architect, domain, test, qa, implementer, reviewer, security,
                                  devops-docs, knowledge-graph.md.tmpl, designer.md (only if HAS_UI=yes)
  .claude/skills/{orchestrate,plan-grill,spec-writer,amend-constitution}/SKILL.md
  docs/specs/, docs/specs/_templates/{security-report,findings-ledger,retro}.md, docs/adr/, docs/glossary.md,
  docs/test-strategy.md, docs/debugging-protocol.md
  docs/knowledge-graph/README.md
  .github/workflows/ci.yml.tmpl    (the generated project's own CI, distinct from this repo's test.yml above)
```

## Limits, honestly

- The deny rules and hook are enforced only by Claude Code; `AGENTS.md` is advisory for any other AI coding tool.
- Per-subagent `effort` (reasoning level) has no verified call-time override yet — only `model` does. The orchestrator will tell you if it can't honor an effort request rather than pretend it did.
- `.tmpl` files need every interview answer filled in; `scaffold.py` refuses to run with missing keys instead of defaulting them.
- The knowledge graph is MCP-backed only when Node.js/`npx` was available at setup time (`NPX_CMD` answer); without it, `mcpServers` is omitted and `knowledge-graph` falls back to a markdown-only record (`docs/knowledge-graph/graph.md`).
- The MCP memory server itself is verified, not assumed: ran `@modelcontextprotocol/server-memory` directly (`tools/list`, `create_entities`, `read_graph`) and confirmed all 9 tool names, the duplicate-name skip behavior the idempotency rule relies on, and the on-disk `.jsonl` format. What's still unverified is Claude-Code-specific: whether `mcp__knowledge-graph__<tool>` is the exact subagent `tools:` allowlist syntax, and whether `$CLAUDE_PROJECT_DIR` expands inside `mcpServers.*.env` - confirm both the first time you actually run `/orchestrate` with a real knowledge-graph delegation.
- `designer` is generated only when `HAS_UI` is yes; a pure API/CLI/library project won't get a UI/UX agent.
- `security` is one agent with an exhaustive checklist, not a split team of specialists — depth comes from its instructions, not from agent count. The findings ledger gives review/QA/security one shared, disputable record instead of three independent reports, which narrows but doesn't eliminate that limit.
- Role-tiered model defaults (`opus`/`sonnet`/`haiku`) assume all three tiers are available on your plan; if one isn't, tell the orchestrator to substitute at Start step 4 rather than letting a delegation fail silently.
- `/amend-constitution` only exists as a skill the user invokes - there's no cron-style enforcement that engineering defaults were never hand-edited; it's a convention the skill supports, not a technical guarantee like the DB guard.
- Re-running `scaffold.py` without any flag on an already-scaffolded project adds new files (e.g. a newly-added agent) correctly, since existing files are skipped by default. For `.claude/settings.json` specifically, use `--merge-settings` (not `--overwrite`) to pick up new deny rules/hooks/`mcpServers` by key - it's covered by `scripts/test_scaffold.py::test_merge_settings_unions_deny_rules_without_clobbering_custom_keys`, including a custom top-level key surviving the merge untouched.
