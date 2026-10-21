---
name: spec-writer
description: Write or update spec-driven artifacts for a feature - requirements (EARS + Gherkin), design (DDD/Clean Architecture/threat model) and tasks (TDD-sized) under docs/specs/<feature>/. Use after discovery or whenever a feature needs a spec, when the user says "spec", "especificação", "requirements", "design doc" or "tasks".
---

# spec-writer

1. Confirm the feature name and read `docs/specs/discovery.md`, `docs/glossary.md`, existing ADRs. If anything needed is unknown, **ask** - do not invent.
2. Copy templates from `docs/specs/_templates/` into `docs/specs/<feature-slug>/` and fill them in the project's docs language.
3. Produce in order, getting user approval between each:
   - `requirements.md`: REQ-IDs in EARS form, Gherkin scenarios per requirement, NFRs, out-of-scope. Open questions must be empty before approval.
   - `design.md`: bounded context, domain model, UX (if the feature has a UI - owned by `designer`), ports & adapters, layer map, system design (capacity/scale, data flow, caching/queues, deployment topology, resilience - owned by `architect`), contracts, error handling, STRIDE-lite threat model, test strategy using fakes/in-memory/disposable infra (never the system DB, see `docs/test-strategy.md`).
   - `tasks.md`: ordered TDD tasks; each lists REQ-IDs, the failing test first, minimal implementation, refactor notes, definition of done.
4. Set the status header (Draft -> Approved) with date and approver only after explicit user approval.
5. Record architectural decisions as ADRs in `docs/adr/` using the template.
6. Keep `docs/specs/STATUS.md` updated.
