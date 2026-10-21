---
name: spec-writer
description: Write or update spec-driven artifacts for a feature - requirements (EARS + Gherkin), design (DDD/Clean Architecture/threat model) and tasks (TDD-sized) under docs/specs/<feature>/. Use after discovery or whenever a feature needs a spec, when the user says "spec", "especificação", "requirements", "design doc" or "tasks".
---

# spec-writer

1. Confirm the feature name and read `docs/specs/discovery.md`, `docs/glossary.md`, existing ADRs. If anything needed is unknown, **ask** - do not invent.
2. Copy templates from `docs/specs/_templates/` into `docs/specs/<feature-slug>/` and fill them in the project's docs language.
3. Produce in order, getting user approval between each:
   - `requirements.md`: REQ-IDs in EARS form, Gherkin scenarios per requirement, NFRs, out-of-scope. Open questions must be empty before approval.
   - `design.md`: bounded context, domain model, **feature diagram** (entities/tables/screens touched by *this* feature only - never the whole project's schema), UX (if the feature has a UI - owned by `designer`), ports & adapters, layer map, system design (capacity/scale, data flow, caching/queues, deployment topology, resilience - owned by `architect`), contracts, error handling, STRIDE-lite threat model, test strategy using fakes/in-memory/disposable infra (never the system DB, see `docs/test-strategy.md`).
   - `tasks.md`: ordered TDD tasks; each lists REQ-IDs, the failing test first, minimal implementation, refactor notes, definition of done.
4. If this feature touches UI screens and/or the database, also produce `docs/specs/<feature>/overview.html` - a single self-contained static HTML (inline SVG, no CDN/external dependency) showing affected screens, this feature's entity/relationship diagram, and the affected `Database/` objects, so a non-technical stakeholder can grasp the change at a glance. Get the same approval as the rest of `design.md`.
5. If this feature touches the database, once `design.md` is approved, update (never silently replace) `Database/er-diagram.md` and the relevant per-object file(s) under `Database/<kind>/` - that folder is the only place the complete, cross-feature schema lives (owned by `architect`).
6. Set the status header (Draft -> Approved) with date and approver only after explicit user approval.
7. Record architectural decisions as ADRs in `docs/adr/` using the template.
8. Keep `docs/specs/STATUS.md` updated.
