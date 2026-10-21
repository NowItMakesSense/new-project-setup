# Spec format

Per feature: `docs/specs/<feature-slug>/{requirements,design,tasks}.md`. Templates live in `docs/specs/_templates/`.

- **requirements.md**: context, actors, functional requirements in EARS (`WHEN <trigger> THE SYSTEM SHALL <response>`), structured non-functional requirements (latency/throughput, availability/SLO, security, compliance, accessibility, observability - each marked N/A if it doesn't apply), Gherkin scenarios (Given/When/Then) per requirement, out-of-scope, open questions (must be empty before approval).
- **design.md**: bounded context, domain model (entities/VOs/aggregates/events), **feature diagram** (entities/tables/screens touched by *this* feature only - the complete, cross-feature schema lives only in `Database/er-diagram.md`), UX (IA/flows/design-system/WCAG, only for features with a UI, owned by `designer`), ports & adapters, layer map, **system design** (capacity/scale, data flow, caching/queues, deployment topology, resilience - owned by `architect`), data contracts, error handling, threat model (STRIDE-lite), test strategy (no system DB), **visual overview** (`overview.html`, self-contained static HTML/SVG, only if the feature touches UI and/or the database), ADR links. If the feature touches the database, `architect` updates `Database/er-diagram.md` and the relevant `Database/<kind>/` files once design.md is approved.
- **tasks.md**: ordered tasks, each: requirement IDs covered, failing test to write first, minimal implementation, refactor notes, definition of done. Each task small enough for one red-green-refactor cycle.
- **security-report.md**: written by `security` per feature/release - ASVS checklist by category, severity-ranked findings with file:line and remediation, DB-guard integrity check, sign-off (no open High/Critical before Approved).
- Requirement IDs (`REQ-001`) are referenced from tests and tasks for traceability.
- Status header in each file: `Draft | Approved | Implemented`, with date and approver.
