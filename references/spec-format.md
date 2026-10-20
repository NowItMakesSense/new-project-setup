# Spec format

Per feature: `docs/specs/<feature-slug>/{requirements,design,tasks}.md`. Templates live in `docs/specs/_templates/`.

- **requirements.md**: context, actors, functional requirements in EARS (`WHEN <trigger> THE SYSTEM SHALL <response>`), non-functional requirements (perf, security, accessibility, observability), Gherkin scenarios (Given/When/Then) per requirement, out-of-scope, open questions (must be empty before approval).
- **design.md**: bounded context, domain model (entities/VOs/aggregates/events), ports & adapters, layer map, data contracts, error handling, threat model (STRIDE-lite), test strategy (no system DB), ADR links.
- **tasks.md**: ordered tasks, each: requirement IDs covered, failing test to write first, minimal implementation, refactor notes, definition of done. Each task small enough for one red-green-refactor cycle.
- Requirement IDs (`REQ-001`) are referenced from tests and tasks for traceability.
- Status header in each file: `Draft | Approved | Implemented`, with date and approver.
