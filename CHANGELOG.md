# Changelog

This is this skill's own changelog (not shipped to generated projects).

## 2026-10-20

- **Model/effort selection**: `/orchestrate` asks once for the orchestrator's and each subagent's model (and, where supported, effort), records it in `docs/specs/STATUS.md`. Every agent file's frontmatter gained an explicit `model:` field (later retuned to role-tiered defaults - see below).
- **Knowledge graph**: new `knowledge-graph` agent, MCP-backed (`@modelcontextprotocol/server-memory`, gated by the `NPX_CMD` interview answer) with a markdown fallback when Node/npx isn't available. Seeds from discovery/design, extracts a proposal on retrofit onto an existing codebase, always checks before creating. Verified for real against the actual npm package: all 9 tool names, the duplicate-name skip behavior, and the on-disk `.jsonl` format.
- **Superpowers-inspired corrections**: TDD Iron Law + rationalization red flags (`engineering-principles.md`, `test.md`, `implementer.md`); 4-phase systematic debugging protocol (`docs/debugging-protocol.md`).
- **Test strategy guide**: `docs/test-strategy.md` (pyramid ownership, fixture/test-double conventions) - reference only, no code generation.
- **Team expansion**: `security` rewritten with an exhaustive ASVS-based checklist (authN/authZ, injection, secrets/supply-chain, infra, API, business-logic abuse, compliance); new `qa` agent (integration/e2e/edge-case/regression, phase 6 alongside `reviewer`); new `designer` agent (UI/UX), generated only when the new `HAS_UI` interview answer is yes.
- **Adaptive documentation**: `devops-docs` now tailors depth/structure to the project's actual scenario instead of a generic template.
- **System design**: `design.md` gained a "System design" section (capacity/scale, data flow, caching/queues, deployment topology, resilience); `requirements.md`'s NFR section is now structured (latency/throughput, SLO, compliance, accessibility, observability) instead of a one-line list. `architect` owns this explicitly.
- **Security report template**: `docs/specs/_templates/security-report.md`, written by `security` per feature/release instead of only a free-text chat report.
- **Guard-rail CI check**: generated projects now ship `.claude/hooks/verify-guard.py` and a real CI step that re-runs it on every push/PR, so a weakened deny-list or disabled hook is caught automatically instead of drifting silently.
- **Settings merge on upgrade**: `scaffold.py --merge-settings` does a key-level JSON merge of `.claude/settings.json` (deny-list union, new `mcpServers`/hook entries added) instead of forcing a full skip-or-overwrite choice.
- **Test suite for this skill**: `scripts/test_scaffold.py` covers the full answer matrix (HAS_UI, NPX_CMD, CI_PROVIDER, EXTRA_DENY, missing keys, overwrite, merge-settings) plus `verify_setup.py` pass/fail behavior; `.github/workflows/test.yml` runs it on every push/PR to this repo.

Researched comparable tools (GitHub Spec Kit, BMAD-METHOD, the Claude Code `spec-driven-dev` plugin) and adopted four improvements they do better:

- **Role-tiered model defaults**: every agent's `model:` frontmatter changed from a uniform `inherit` to a role-appropriate default - `opus` for `architect`/`security`/`reviewer`, `sonnet` for the rest of the delivery team, `haiku` for `devops-docs`. `/orchestrate` Start step 4 now asks whether to keep or override these, instead of asking for "one default for all." `verify_setup.py` checks the tier on every agent.
- **Shared findings ledger with one-time dispute**: `docs/specs/_templates/findings-ledger.md`, written jointly by `reviewer`, `qa` and `security` instead of each keeping separate findings. A Critical/High row starts `Open`; the orchestrator relays it to `implementer` for a fix or a dispute, and the agent that raised it makes the final `Confirmed`/`Retracted` call before it can block phase 6/7. `security-report.md`'s own Findings section now points to the ledger instead of duplicating it.
- **`/amend-constitution` skill**: a deliberate, ADR-recorded way to revise `CLAUDE.md`'s engineering defaults after scaffold time, instead of silent hand-edits or never revisiting them. It explicitly refuses to touch the DB-access prime directive or any agent's non-negotiable rules.
- **Retro after release**: `docs/specs/_templates/retro.md`, written with the user once phase 8 is confirmed - what went well, what to adjust, and what should carry into `discovery.md`/`CLAUDE.md`/the "Models & effort" table before the next feature's `/plan-grill`.
