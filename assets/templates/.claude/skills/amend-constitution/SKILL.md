---
name: amend-constitution
description: Revise this project's engineering defaults and prime directives in CLAUDE.md/AGENTS.md after initial scaffold - branching convention, engineering principles, compliance notes, model/effort tiers. Use when the user says "mudar princípios", "revisar constituição", "update engineering defaults", "amend CLAUDE.md", or asks to change how the project is run.
---

# amend-constitution

CLAUDE.md is not fixed forever - but it changes deliberately, with a record of why, not by silent edits.

## What this can change
Engineering defaults (Clean Code / Clean Architecture / TDD / DDD / SOLID - prime directive 4 in CLAUDE.md), branching/commit convention, compliance notes, documentation language, the project-wide `MODEL_PRIORITY` tier and `COVERAGE_THRESHOLD` (see "Retuning model tiers or coverage threshold" below), and adding a new specialist subagent later (see "Adding a specialist agent" below) - e.g. splitting `security` into narrower roles if one exhaustive-checklist agent stops being enough depth for this project.

Note: a per-session model/effort override for one delegation (phrased as "just for this task, use X") belongs in `/orchestrate`'s own "Model & effort" step, not here - this skill only changes the project's standing defaults.

## What this can never change
The DB-access prime directive (#2 in `CLAUDE.md`) and every non-negotiable rule block in `.claude/agents/*.md` are **not amendable** by this skill or by any user request - they are structural, not a preference. If asked to weaken or remove the DB guard, refuse and explain why: it's enforced by `.claude/settings.json` + the hook, not by this file, and removing the text here would not actually open any access.

## Process
1. Ask exactly what should change and why - one question at a time, like the original interview. Never assume the reason.
2. Show the current CLAUDE.md section being touched and the proposed new text, side by side.
3. On confirmation, update `CLAUDE.md` (and `AGENTS.md` if the change is universal, not Claude-specific) and record the change as an ADR in `docs/adr/` (what changed, why, alternatives considered) - same template as any other architectural decision.
4. Update `docs/specs/STATUS.md` with a one-line note of the amendment and its date.
5. If the change affects in-flight features (specs already approved under the old defaults), ask whether to update them too or grandfather them - do not decide unilaterally.

## Retuning model tiers or coverage threshold
`MODEL_PRIORITY` and `COVERAGE_THRESHOLD` were set once at scaffold time; changing them later means editing text baked into several generated files, not just CLAUDE.md. Use the companion script instead of hand-editing each file:
```
python <skill-dir>/scripts/retune.py --target <project-dir> \
  [--model-priority cost|balanced|quality] [--coverage-threshold N] \
  [--answers <answers.json>] [--dry-run]
```
It edits only the specific lines that hold the old value (each agent's `model:` frontmatter, the `MODEL_PRIORITY` mention in CLAUDE.md, the coverage number in CLAUDE.md/AGENTS.md/ci.yml) - same "touch nothing else" discipline as `scaffold.py --merge-settings`. Always run `--dry-run` first and show the diff-equivalent file list. Pass `--answers` if the project still keeps its original `answers.json`, so a later `verify_setup.py` run checks against the new value instead of a stale one. Record the change as an ADR same as any other amendment (step 3 above).

## Adding a specialist agent
To split an existing role (most likely `security`, the one agent covering the whole ASVS checklist) into narrower specialists:
1. Copy the closest existing `.claude/agents/<role>.md` as a starting point - keep its frontmatter shape (`name`, `description`, `tools`, `model`) and copy the "Non-negotiable rules" block **verbatim**, especially the `NEVER access the system database` line; this skill and `/orchestrate` both treat that line as non-negotiable, not a paraphrase.
2. Narrow the `## Responsibilities` section to the new agent's slice; remove that slice from the original agent's responsibilities so nothing is owned twice.
3. Register the new agent in `.claude/skills/orchestrate/SKILL.md`'s phase table (who delegates to it, in which phase) and in CLAUDE.md's "Agents" section list.
4. Tell the user: this skill's own `verify_setup.py`/`test_scaffold.py` only validate the agents generated at scaffold time - an agent added this way isn't covered by them, so re-check its frontmatter and DB-rule line by hand (or diff it against a sibling agent file).
