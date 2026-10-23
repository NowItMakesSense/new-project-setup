# new-project-setup

**A Claude Code skill that bootstraps a new software project with a real AI-engineering team already wired in — an orchestrator, specialist subagents covering planning, architecture, domain modeling, UI/UX (when there's a UI), unit testing, broader QA, implementation, code review, exhaustive security, DevOps/docs, and a domain knowledge graph — plus a relentless planning interview, spec-driven development, and a DB/secrets guard that agents cannot bypass.**

Stop hand-rolling the same `CLAUDE.md`, the same guardrails, the same "please don't run migrations against prod" reminder on every new repo. Run this skill once per project and get a setup that keeps agents honest, specs in sync with code, and your production database completely out of reach — no matter what any agent is asked to do.

## Why you'd want this

- **You stop re-writing boilerplate.** One skill call replaces an hour of copy-pasting `CLAUDE.md`/`AGENTS.md`, agent prompts and CI scaffolding between projects.
- **Agents can't touch your database or your cloud secrets — structurally, not by promise.** Five independent layers (deny rules, a PreToolUse hook, textual rules in every prompt, no agent ever holding credentials, and continuous CI verification) block `psql`, `prisma migrate`, `docker exec`, reading `.env`, `aws secretsmanager get-secret-value`, `vault read`, `gcloud secrets versions access`, and every workaround a model might try. It fails closed on malformed input.
- **No code before a spec exists.** Every feature goes through a planning interview, then EARS/Gherkin requirements, a design doc with a threat model, and TDD-sized tasks — all gated by your explicit approval, not the model's judgment call.
- **It never guesses.** Missing stack, unclear scope, an ambiguous "fast" or "secure" — the skill (and everything it generates) stops and asks instead of inventing an answer.
- **Works beyond Claude Code too.** A stack-agnostic `AGENTS.md` ships alongside the Claude-specific `.claude/` setup, so the same rules travel with you to other AI coding tools (enforcement there is advisory, not hooked).
- **Sensible cost/quality defaults out of the box, still yours to override.** The `MODEL_PRIORITY` interview answer (`cost`/`balanced`/`quality`) sets a role-tiered default per agent at scaffold time instead of one blanket setting, and `/orchestrate` asks once whether to keep or override it per project.
- **A dedicated specialist for the bugs that resist the first fix.** When one pass of the debugging protocol by `implementer`/`qa` doesn't find the root cause, `debug` (a fresh agent, no prior guesses to anchor on) takes over instead of the same agent repeating the same approach.
- **A real coverage number, not a vibe.** `COVERAGE_THRESHOLD` is an actual interview answer wired into the generated CI pipeline and into what `qa` has to report before the review gate - not a sentence buried in prose nobody enforces.
- **Low-risk phases can move fast; the risky ones never do.** Opt into "autonomous mode" and phases 1-4 (discovery through tasks) stop asking for re-confirmation at every single gate - but review, security and release (phases 6-8) are always human-gated, no setting changes that.
- **A checklist for when a released feature turns out wrong.** Revert isn't improvised: git-revert the code, mark the feature's status, record an ADR, and have `knowledge-graph` propose (never auto-apply) removing what only that feature added.
- **A real test and QA story, not just a string.** A `references`/`docs` test-strategy guide spells out the pyramid and fixture conventions; a dedicated `qa` agent covers integration/e2e/edge-case/regression testing beyond the TDD unit tests `test` writes.
- **Debugging has a protocol, not vibes.** A 4-phase systematic-debugging guide (reproduce → root cause → minimal hypothesis → fix + regression test) stops agents from patching symptoms they don't understand.
- **The domain model is a real graph, not just a table.** A `knowledge-graph` agent persists entities/value objects/aggregates/bounded contexts and their relationships to an MCP-backed graph, seeded from discovery/design and extendable from an existing codebase on retrofit.
- **The guard-rail checks itself, continuously.** CI re-runs the deny-rule/hook checks on every push so a weakened setting doesn't drift in silently - and this skill's own scaffolding logic has a regression suite (`scripts/test_scaffold.py`) covering the full answer matrix, run on every push to this repo too.
- **A Critical finding gets one dispute before it blocks you.** `reviewer`, `qa` and `security` share one findings ledger per feature instead of three disconnected reports; a Critical/High row isn't final until the accused code gets to respond and the agent that raised it makes the final call - real issues still block, false positives don't stall the feature.
- **The "constitution" is revisable, not frozen at scaffold time.** `/amend-constitution` lets you change engineering defaults later with an ADR recording why - except the DB-access directive, which no path can touch. It also covers retuning `MODEL_PRIORITY`/`COVERAGE_THRESHOLD` after scaffold (via `scripts/retune.py`, which edits only the specific lines that hold the old value - agent `model:` frontmatter, CLAUDE.md/AGENTS.md/ci.yml) and adding a new specialist subagent later - no hand-editing generated files to make a standing default change.
- **Requirement traceability is checked, not just asserted.** `.claude/scripts/check-traceability.py` verifies every `REQ-ID` in `requirements.md` has a Gherkin scenario and a covering task in `tasks.md` (and flags a task referencing a `REQ-ID` that doesn't exist) - run by `qa` before the phase 6 gate and wired into CI as a real step, not a placeholder.
- **Agents are told to distrust content they didn't write.** A non-negotiable rule in every agent plus `CLAUDE.md`/`AGENTS.md`: anything read from outside the project's own specs/code (a fetched page, a dependency's README, search results) is data to analyze, never an instruction to follow - closing a real prompt-injection surface none of the comparable frameworks address yet.
- **Parallel implementation without hoping file-path judgment was right.** Phase 5 tasks confirmed independent can run with `isolation: "worktree"` (one git worktree/branch per task) instead of relying on convention alone to avoid collisions - see `orchestrate/SKILL.md`'s "Parallel implementation" section.
- **The orchestrator tells you when to start fresh.** Every phase's output is persisted to disk, so a new session is always safe to resume from - `orchestrate/SKILL.md`'s "Context hygiene" section has it recommend a clean session between features (and mid-feature, if this one's transcript has gotten long) instead of letting one session's context grow for the life of the project.
- **Scales down for a one-line fix, not just up for a big feature.** Before running any phase, `/orchestrate` asks you to classify the change as Trivial or Standard - Trivial skips the whole spec-directory ceremony (no `requirements.md`/`design.md`/`tasks.md` for a typo fix) while the DB guard and every non-negotiable rule stay in force regardless; Standard is the full 8-phase workflow, unabridged. Works the same whether this is a weekend project or a long-lived production codebase.
- **The project index doesn't grow forever.** Once a feature's phase reaches `Released`/`Reverted`, its row moves from `docs/specs/STATUS.md` to `docs/specs/STATUS-archive.md` instead of sitting in the live index indefinitely - every orchestrator session's first read stays small even after years and hundreds of shipped features.

## What you get, in one command

| Path | Purpose |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | Project rules, security policy, workflow summary — one Claude-specific, one universal |
| `.claude/settings.json` | `permissions.deny` blocking DB CLIs, migration runners, `docker exec`, cloud secret-manager CLIs (AWS/GCP/Azure/Vault/1Password/Doppler), secrets |
| `.claude/hooks/block-db-access.py` + `db_patterns.json` | Runtime hook: catches connection strings, wrapper calls, and workarounds the deny list misses. Rules live in the sibling JSON, reviewable on their own; the hook fails closed if that file is missing or malformed |
| `.claude/hooks/verify-guard.py` | CI guard-rail: re-runs the deny-rule/hook checks on every push/PR so drift gets caught |
| `.claude/scripts/check-traceability.py` | Verifies REQ-ID linkage between `requirements.md`/`tasks.md`, run by `qa` before phase 6 and wired into CI |
| `.claude/scripts/render-graph.py` + `graph-view.html` | Turns the knowledge graph into a full-screen 3D explorer, `docs/knowledge-graph/graph.html` (DDD kinds coloured, bounded contexts as rings, search with `/`, a detail sheet per concept), regenerated by `knowledge-graph` after every change |
| `.claude/agents/*.md` | `planner`, `architect`, `domain`, `test`, `qa`, `implementer`, `reviewer`, `security`, `devops-docs`, `knowledge-graph`, `debug`, and - only when the project has a UI - the front-end team: `designer`, `frontend`, `ui-reviewer` |
| `.claude/skills/orchestrate` + `references/` | The orchestrator: an 8-phase workflow with a human approval gate after every phase; less-frequently-needed procedures (parallel implementation, context hygiene, archiving, the revert checklist) live in its own `references/` so its `SKILL.md` body stays lean |
| `.claude/skills/plan-grill` | A grill-me-style planning interview — one question at a time, walks every branch until nothing is ambiguous |
| `.claude/skills/spec-writer` | Writes `requirements.md` (EARS + Gherkin), `design.md`, `tasks.md` per feature |
| `.claude/skills/frontend-craft` (only when the project has a UI) | The front-end team's shared house rules - art direction for pages, app-screen layout, type/colour/surfaces, motion, worst-case data and the Before/After/Why review format - distilled from Emil Kowalski's skills and taste-skill; uses their full versions (and taste-skill's real-browser `inspect.mjs`) when installed globally |
| `.claude/skills/amend-constitution` | Revises `CLAUDE.md` engineering defaults later, with an ADR - never the DB-access directive |
| `docs/specs/`, `docs/adr/`, `docs/glossary.md` | Spec-driven artifacts, architectural decisions, ubiquitous language |
| `docs/test-strategy.md`, `docs/debugging-protocol.md` | Test pyramid/fixture guide; 4-phase systematic-debugging protocol |
| `docs/security-policy.md` | The project's security baseline - DB-guard layers, the external-content rule, general practices and its compliance regime - read by `architect` and `security`, cited by every feature's `requirements.md` |
| `docs/knowledge-graph/` + `.claude/agents/knowledge-graph.md` | The domain model as a real graph (entities, VOs, aggregates, bounded contexts, relationships), MCP-backed when Node/`npx` is available |
| `Database/` (only when the project has a database) | The complete, authoritative ER diagram (`er-diagram.md`) plus one file per DB object under `tables/`, `indexes/`, `foreign-keys/`, `primary-keys/`, `packages/`, `functions/` - owned by `architect`, updated per feature |
| `docs/specs/<feature>/overview.html` (conditional, per feature) | Self-contained static HTML/SVG - no external dependency - summarizing a feature's affected screens, its scoped entity/relationship diagram, and affected `Database/` objects, for a non-technical reader. Produced only when that feature touches UI and/or the database |
| `docs/specs/_templates/security-report.md` | Per-feature ASVS checklist, filled by `security` |
| `docs/specs/_templates/findings-ledger.md` | Shared reviewer/QA/security findings, one dispute before a Critical/High blocks a gate |
| `docs/specs/_templates/retro.md` | Short per-feature retro after release, carried into the next `/plan-grill` |
| `docs/specs/_templates/feature-status.md` + `docs/specs/STATUS.md` + `docs/specs/STATUS-archive.md` | Per-feature status file + a top-level index of in-flight features + an archive for `Released`/`Reverted` ones, so the live index stays small and concurrent work on different features doesn't collide on one shared block of text |
| `.github/workflows/ci.yml` | Lint/test/build/secret-scan/guard-rail/traceability-check pipeline (only if you picked GitHub Actions) |

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
| 3 | Architecture & domain | `architect`, `domain`, `knowledge-graph`, `designer` (if the project has a UI) | `design.md` (incl. a feature-scoped entity/relationship diagram), ADRs, glossary, threat model, updated knowledge graph, `Database/` update + `overview.html` (if the feature touches UI/DB) |
| 4 | Task breakdown | `planner` | `tasks.md` (TDD-sized) |
| 5 | TDD loop, per task | `test` → `implementer`, or `frontend` for UI tasks (→ `debug` if the first fix attempt fails) | failing test → green → refactor |
| 6 | Review & QA | `reviewer`, `qa`, plus `ui-reviewer` when the feature had UI tasks | Findings in the shared `findings-ledger.md`; integration/e2e/edge-case results; coverage % vs `COVERAGE_THRESHOLD` |
| 7 | Security | `security` | `security-report.md`: exhaustive ASVS checklist (authN/authZ, injection, secrets/supply-chain, infra, API, business-logic abuse, compliance), DB-policy check; findings in the ledger |
| 8 | CI/CD & docs | `devops-docs` | pipeline, README, changelog, tailored to the project's own scenario |
| — | Retro | orchestrator | `retro.md`, applied before the next feature's `/plan-grill` |

## The security model (defense in depth)

No agent can reach the system database or your cloud secrets — not by convention, by five independent layers:

1. **Deny rules** (`permissions.deny` in `.claude/settings.json`) block every common DB CLI, ORM/migration runner, `docker exec`/`kubectl exec`/`kubectl get secret`, cloud secret-manager CLIs (`aws secretsmanager`/`ssm`, `gcloud secrets`, `az keyvault`, `vault`, `op`, `doppler`, `pass`), and reads/writes of `.env*`, `secrets/`, keys and credentials.
2. **A PreToolUse hook** (`.claude/hooks/block-db-access.py`) catches what the deny list can't enumerate: raw connection strings, shell wrappers, piping through `bash -c`, the same secret-manager calls caught again in case a deny pattern is worked around. It fails closed on malformed input.
3. **Textual rules** repeated in `CLAUDE.md`, `AGENTS.md`, and every single subagent prompt, so the model is told, not just blocked.
4. **Structural guarantees**: no agent ever receives credentials; tests run against fakes/in-memory doubles or disposable containers a human starts; migrations are only ever *generated as files* for a human to review and apply.
5. **Continuous verification**: `.claude/hooks/verify-guard.py` re-runs the deny-rule and hook-blocking checks in CI on every push/PR (wired into `ci.yml` when you picked GitHub Actions), so a weakened deny list or a disabled hook gets caught automatically instead of drifting silently.

If a task seems to need DB access, every agent is instructed to stop and ask — never work around the guard. Full detail: `references/security-policy.md` (generated into each project as `docs/security-policy.md`).

**Scope note:** this skill only bootstraps *other* projects. It has no production code, no agents and no database of its own — the engineering defaults and DB guard above describe what gets built into the *generated* project, never this skill's own behavior.

## Using it

Just tell Claude Code you're starting a project — "novo projeto", "iniciar projeto", "setup do projeto", "bootstrap", "scaffold" all trigger it, even without naming the skill. It will:

1. **Interview you** (`references/interview.md`) — project name, stack, DB engine, test strategy, compliance needs, CI provider, branching convention, engineering defaults to keep or override, whether the project has a UI (`HAS_UI`, gates the `designer` agent), whether Node.js/`npx` is available (`NPX_CMD`, gates the MCP-backed knowledge graph), whether to optimize the agent team for `cost`/`balanced`/`quality` (`MODEL_PRIORITY`), and a minimum test coverage percentage to enforce (`COVERAGE_THRESHOLD`). Anything you don't know is recorded as `TBD` and resolved later in `/plan-grill`, never guessed.
2. **Scaffold a dry run first**, show you the file list, then write for real:
   ```
   python scripts/scaffold.py --target <project-dir> --answers <answers.json> --dry-run
   python scripts/scaffold.py --target <project-dir> --answers <answers.json>
   ```
   Re-running this on an already-scaffolded project (new skill version, or retrofit): pass `--merge-settings` instead of `--overwrite` to union new deny rules/hooks into the existing `.claude/settings.json`, and new MCP servers into the existing `.mcp.json`, by key - without touching anything else in either.
3. **Verify itself**:
   ```
   python scripts/verify_setup.py --target <project-dir> --answers <answers.json>
   ```
   Checks the deny rules, that `db_patterns.json` exists and is valid, that the hook actually blocks `psql`/`docker exec`/`.env` reads and allows normal commands, that `PYTHON_CMD` actually resolves on PATH, that every agent carries the DB rule, that the knowledge-graph MCP config in `.mcp.json` matches what the interview asked for (including that `MEMORY_FILE_PATH` is a literal absolute path, since no variable form is expanded there and a relative path breaks the server), and that no `{{TEMPLATE_VAR}}` was left unresolved. It also warns if a legacy `mcpServers` block is still sitting in `.claude/settings.json`, where Claude Code ignores it. `--answers` is optional - without it, the mcpServers and `PYTHON_CMD` checks are informational only.
4. **Hand off**: run `/plan-grill` in the new project, then `/orchestrate` to drive the full workflow.

## Repository layout

```
SKILL.md                         entry point Claude Code loads
CHANGELOG.md                     this skill's own history (not shipped to generated projects)
.github/workflows/test.yml        this repo's own CI - runs scripts/test_scaffold.py on every push/PR
references/                      interview script, workflow, security policy, engineering principles,
                                  spec format, test-strategy guide, debugging protocol (this skill's own notes)
examples/answers.example.json     a fully filled-in answers.json to adapt instead of building one from scratch
scripts/scaffold.py               renders assets/templates/ into --target (supports --merge-settings)
scripts/verify_setup.py           checks the result is actually safe and complete
scripts/retune.py                 edits MODEL_PRIORITY/COVERAGE_THRESHOLD in an already-scaffolded project (used by /amend-constitution)
scripts/test_scaffold.py          regression suite for scaffold.py/verify_setup.py/retune.py (stdlib unittest)
assets/templates/                 everything scaffold.py copies into the generated project
  CLAUDE.md.tmpl, AGENTS.md.tmpl
  .claude/settings.json.tmpl, .claude/hooks/{block-db-access.py, db_patterns.json, verify-guard.py}
  .claude/scripts/check-traceability.py  REQ-ID traceability check (requirements.md vs tasks.md)
  .claude/scripts/render-graph.py        knowledge graph -> full-screen 3D docs/knowledge-graph/graph.html
  .claude/scripts/graph-view.html        the page template render-graph.py fills
  .claude/skills/frontend-craft/         front-end house rules + references/ (only if HAS_UI=yes)
  .claude/agents/*.md.tmpl         planner, architect, domain, test, qa, implementer, reviewer, security,
                                  devops-docs, knowledge-graph, debug - model: line set by MODEL_PRIORITY;
                                  designer/frontend/ui-reviewer.md.tmpl only generated if HAS_UI=yes
  .claude/skills/{orchestrate,spec-writer}/SKILL.md.tmpl (PYTHON_CMD-templated), plan-grill/amend-constitution/SKILL.md
  .claude/skills/orchestrate/references/{parallel-implementation,context-hygiene,archiving,revert-checklist}.md
                                  detail moved out of orchestrate's SKILL.md to keep its body lean (progressive disclosure)
  docs/specs/, docs/specs/_templates/{security-report,findings-ledger,retro,feature-status}.md, docs/adr/,
  docs/glossary.md, docs/test-strategy.md, docs/debugging-protocol.md, docs/security-policy.md.tmpl
  docs/knowledge-graph/README.md
  .github/workflows/ci.yml.tmpl    (the generated project's own CI, distinct from this repo's test.yml above)
```

## Limits, honestly

- The deny rules and hook are enforced only by Claude Code; `AGENTS.md` is advisory for any other AI coding tool.
- Per-subagent `effort` (reasoning level) has no verified call-time override yet — only `model` does. The orchestrator will tell you if it can't honor an effort request rather than pretend it did.
- `.tmpl` files need every interview answer filled in; `scaffold.py` refuses to run with missing keys instead of defaulting them.
- The knowledge graph is MCP-backed only when Node.js/`npx` was available at setup time (`NPX_CMD` answer); without it, `.mcp.json` is omitted and `knowledge-graph` falls back to a markdown-only record (`docs/knowledge-graph/graph.md`).
- **Even with the config correct, the MCP server needs a one-time human approval.** A project-scoped server from `.mcp.json` shows as `⏸ Pending approval` in `claude mcp list` and exposes no tools until someone approves it in an interactive `claude` run. So the first `/orchestrate` knowledge-graph delegation in a freshly scaffolded project will legitimately hit the markdown fallback unless the user approved the server first - that's the setup working as designed, not a failure.
- The MCP memory server itself is verified, not assumed: ran `@modelcontextprotocol/server-memory` directly (`tools/list`, `create_entities`, `read_graph`) and confirmed all 9 tool names, the duplicate-name skip behavior the idempotency rule relies on, and the on-disk `.jsonl` format. The Claude-Code-specific wiring was wrong until 2026-10-21 and is now verified empirically (see that date's CHANGELOG entry): servers go in `.mcp.json` at the repo root, not `.claude/settings.json`, and `MEMORY_FILE_PATH` must be a **literal absolute path** - the server resolves relative paths against its own module dir in the npx cache (writes fail with `ENOENT`), and Claude Code does not export `$CLAUDE_PROJECT_DIR` into an MCP server's environment, so no variable form works there. `mcp__knowledge-graph__<tool>` is confirmed as the subagent `tools:` allowlist syntax (the agent's `read_graph` call succeeded once the server was connected and approved).
- **The absolute `MEMORY_FILE_PATH` is not portable across machines.** A committed `.mcp.json` carries the path of whoever scaffolded the project; a teammate who clones to a different path has to edit that one line (`verify_setup.py` warns when its parent directory doesn't exist), or register the server at user scope with `claude mcp add` and remove it from `.mcp.json`. There's no portable form available - see the generated `docs/knowledge-graph/README.md` for why.
- The front-end team (`designer`, `frontend`, `ui-reviewer`) and `frontend-craft` are generated only when `HAS_UI` is yes; a pure API/CLI/library project won't get them. Their `skills:` frontmatter also names the original Emil Kowalski / taste-skill skills; Claude Code skips a preloaded skill that isn't installed (a debug-log warning, not an error), so they work without a global install - with less depth and no real-browser `inspect.mjs` check.
- `security` is one agent with an exhaustive checklist, not a split team of specialists — depth comes from its instructions, not from agent count. The findings ledger gives review/QA/security one shared, disputable record instead of three independent reports, which narrows but doesn't eliminate that limit. `/amend-constitution` documents a path to split it into narrower specialists later if one agent stops being enough, but that's a manual step the user has to decide to take, not something the skill proposes on its own.
- **The Trivial change-size lane depends on the user and orchestrator classifying honestly.** Nothing stops someone from calling a genuinely non-trivial change "trivial" to skip spec ceremony - the only backstop is the orchestrator's instruction to stop and upgrade to Standard the moment a trivial change turns out to touch more, and the DB guard/non-negotiable rules staying in force either way regardless of tier.
- **No monorepo/multi-service support.** One scaffold run produces one `CLAUDE.md`/`.claude/`/`Database/`, which assumes one deployable unit. For a monorepo with multiple independently-deployable services, the interview now flags this and asks whether to scaffold once per service (own subdirectory, own `scaffold.py` run) or once at the root if the services genuinely share one database/one set of defaults - there's no automated per-package overlay, you decide and run it that many times.
- The DB-guard hook is Python-only by construction (stdlib, no build step) and runs on every Bash/Read/Edit/Write/... call regardless of the project's own stack - so a working Python 3 interpreter at `PYTHON_CMD` must exist on every machine (and CI runner) that runs this project with Claude Code, even a pure Node/Go/Rust/.NET project that otherwise never touches Python. `verify_setup.py` now checks that `PYTHON_CMD` actually resolves on PATH (not just that it looks like a plain command name) when `--answers` is given, but it can't verify every future CI runner in advance.
- Role-tiered model defaults (`opus`/`sonnet`/`haiku`, picked by `MODEL_PRIORITY`) assume all three tiers are available on your plan; if one isn't, tell the orchestrator to substitute at Start step 5 rather than letting a delegation fail silently.
- `/amend-constitution` only exists as a skill the user invokes - there's no cron-style enforcement that engineering defaults were never hand-edited; it's a convention the skill supports, not a technical guarantee like the DB guard.
- "Autonomous mode" only ever relaxes re-confirmation on phases 1-4; there is no setting, including this one, that skips the human gate on review/security/release. If you want full unattended runs, this isn't built for that.
- Reverting a released feature is a documented checklist the orchestrator walks through with you, not an automated rollback command - `knowledge-graph` proposes what to remove, it never deletes on its own.
- `COVERAGE_THRESHOLD` is carried through to `CLAUDE.md`/`AGENTS.md`/`ci.yml` as a real number, but actually enforcing it is `devops-docs`'s job once the stack's coverage tool is chosen - the scaffolded `ci.yml` step is a placeholder it replaces, not a working gate out of the box.
- The `docs/specs/STATUS.md` index reduces the two-people-same-file collision risk with an explicit lease convention (set a `Lease: owner @ timestamp` field before writing a row, clear it after - stale leases older than 15 minutes are ignored) but doesn't eliminate it - there's no actual file lock or atomic test-and-set, just a convention agents are told to follow.
- Re-running `scaffold.py` without any flag on an already-scaffolded project adds new files (e.g. a newly-added agent) correctly, since existing files are skipped by default. For `.claude/settings.json` and `.mcp.json` specifically, use `--merge-settings` (not `--overwrite`) to pick up new deny rules/hooks/MCP servers by key - covered by `scripts/test_scaffold.py::test_merge_settings_unions_deny_rules_without_clobbering_custom_keys` (a custom top-level key survives the merge untouched) and `::test_merge_settings_preserves_other_servers_in_existing_mcp_json` (your own MCP servers, and a customized `knowledge-graph` entry, survive it too). For changing `MODEL_PRIORITY`/`COVERAGE_THRESHOLD` specifically (a standing default, not a one-off override), use `scripts/retune.py` via `/amend-constitution` instead of re-scaffolding or hand-editing - it edits only the lines that hold the old value.
