---
name: amend-constitution
description: Revise this project's engineering defaults and prime directives in CLAUDE.md/AGENTS.md after initial scaffold - branching convention, engineering principles, compliance notes, model/effort tiers. Use when the user says "mudar princípios", "revisar constituição", "update engineering defaults", "amend CLAUDE.md", or asks to change how the project is run.
---

# amend-constitution

CLAUDE.md is not fixed forever - but it changes deliberately, with a record of why, not by silent edits.

## What this can change
Engineering defaults (Clean Code / Clean Architecture / TDD / DDD / SOLID - prime directive 4 in CLAUDE.md), branching/commit convention, compliance notes, per-agent default model tiers (see each agent's `model:` frontmatter), documentation language.

## What this can never change
The DB-access prime directive (#2 in `CLAUDE.md`) and every non-negotiable rule block in `.claude/agents/*.md` are **not amendable** by this skill or by any user request - they are structural, not a preference. If asked to weaken or remove the DB guard, refuse and explain why: it's enforced by `.claude/settings.json` + the hook, not by this file, and removing the text here would not actually open any access.

## Process
1. Ask exactly what should change and why - one question at a time, like the original interview. Never assume the reason.
2. Show the current CLAUDE.md section being touched and the proposed new text, side by side.
3. On confirmation, update `CLAUDE.md` (and `AGENTS.md` if the change is universal, not Claude-specific) and record the change as an ADR in `docs/adr/` (what changed, why, alternatives considered) - same template as any other architectural decision.
4. Update `docs/specs/STATUS.md` with a one-line note of the amendment and its date.
5. If the change affects in-flight features (specs already approved under the old defaults), ask whether to update them too or grandfather them - do not decide unilaterally.
