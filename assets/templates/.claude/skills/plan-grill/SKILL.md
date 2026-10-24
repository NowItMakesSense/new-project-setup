---
name: plan-grill
description: Planning interview in the style of grill-me - relentlessly question the user, one question at a time, walking every branch of the decision tree until nothing is ambiguous, then record the result as a discovery spec. Use at project start, before any feature, when the user says "plan", "planejar", "grill me", "vamos planejar", or whenever requirements are unclear.
---

# plan-grill

If a skill named `grill-me` is installed (check the available skills list), invoke it for the interview and then continue at "Record" below. Otherwise run the interview yourself as follows.

## Interview rules
1. **One question at a time.** For each, offer a recommended answer and the reasoning; the user may accept or change it.
2. **Never assume.** Do not fill gaps with defaults. "I don't know" -> record as open question and revisit.
3. **Walk the decision tree.** Resolve dependencies between decisions in order; revisit earlier answers when a later one contradicts them.
4. **Look before asking.** If the answer is in the repo or docs, read it instead of asking (then confirm briefly). Find it through the project graph first (`.claude/scripts/build-graph.py query <term>`), not by opening every file.
5. Be relentless but respectful: challenge vague words ("fast", "secure", "simple", "users"), ask for examples and edge cases, ask "what happens when this fails?".
6. User-stated preferences (architecture, tools, methods) override the engineering defaults (Clean Code, Clean Architecture, TDD, DDD, SOLID).
7. Never request or touch database contents or credentials; ask about the data *model* only.

## Topics to cover (adapt order to dependencies)
Problem & goals -> users/actors & jobs-to-be-done -> scope & non-goals -> core use cases & flows -> domain language & bounded contexts -> data (entities, volume, retention, privacy, compliance) -> integrations -> non-functional (performance, availability, security, accessibility, observability, cost) -> stack & infra constraints -> test strategy (no system DB) -> deployment & environments -> team, timeline, milestones -> risks & unknowns -> success metrics.

## Record
Write `docs/specs/discovery.md` (in the project's docs language) with: decisions (with rationale), assumptions explicitly confirmed by the user, out-of-scope, glossary terms (also add to `docs/glossary.md`), open questions, proposed feature list. Present a summary and get explicit confirmation. Then ask `knowledge-graph` to rebuild the project graph so the new files are findable. Then hand off to `/to-spec`, which turns the discovery and this conversation into the feature's spec (`docs/specs/<feature>/prd.md`) without a second interview, and suggest `/orchestrate` to carry it through the remaining phases.
