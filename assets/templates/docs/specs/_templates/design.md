# Design: <feature>

Status: Draft | Date: | Approved by:

## Bounded context and ubiquitous language

## Domain model
Entities, value objects, aggregates (invariants), domain events.

## Feature diagram
Scope: only entities/tables/screens touched by *this* feature - never the whole project's schema (that lives in `Database/er-diagram.md`).
- Entity/relationship diagram covering just this feature's entities (plain text/table notation - no external rendering dependency).
- If this feature adds/changes UI screens: a simple flow/wireframe description of just the affected screens (owned by `designer`).
- If this feature touches the database: list of affected `Database/` objects (new or modified tables/indexes/foreign-keys/primary-keys/packages/functions), linked into `Database/`.

## UX (if this feature has a UI)
Information architecture, user flows/wireframes (text/Mermaid), design-system tokens/components used, accessibility (WCAG) criteria. Owned by `designer` (rules: `.claude/skills/frontend-craft/`); omit this section for UI-less features. Also record, per screen:
- **Kind and question:** page or app screen; the one question it answers first.
- **Direction / style:** name (and `draw.mjs` seed if dealt), why it suits this subject, and **the face** (the one thing only this product has).
- **Tokens:** type scale, colour roles, spacing, radii (or a link to `docs/design-system.md`).
- **Motion spec:** | Element | Trigger | Property | Easing | Duration | Reduced motion |
- **Worst-case states:** empty, one, huge, long, missing, loading, error - what each shows.
- **Exceptions:** any deliberate break of the house rules, with its reason.

## Architecture
Layer map (domain / application / infrastructure / interface), ports and adapters, dependency direction (inward).

## System design
Macro view, beyond code layering:
- **Capacity & scale**: expected load (requests/sec, data volume, growth rate), read/write ratio.
- **Data flow**: how data moves between components/services (Mermaid sequence or flow diagram).
- **Caching & queues**: what's cached, invalidation strategy, async/queue usage if any.
- **Deployment topology**: how this runs in practice (single instance, horizontally scaled, serverless, etc.) and why.
- **Resilience**: timeouts, retries, circuit breakers, idempotency for anything that can fail partially.
- **Scaling approach**: vertical vs horizontal, stateless vs stateful, bottlenecks anticipated.
Skip sub-points that genuinely don't apply (e.g. a CLI tool has no deployment topology) - say so explicitly rather than leaving it blank.

## Contracts
APIs, events, schemas.

## Error handling and observability

## Threat model (STRIDE-lite)
| Threat | Asset | Mitigation |
|---|---|---|

## Test strategy
Unit / integration / e2e. Persistence in tests: fakes, in-memory or disposable infra. NEVER the system database.

## Visual overview (only if this feature touches UI screens and/or the database)
A single self-contained `overview.html` next to this file - static HTML/inline SVG, no external dependency (no CDN) - rendering: affected screens (if any), this feature's entity/relationship diagram, and the list of affected `Database/` objects. Built so a non-technical stakeholder can open it in a browser and understand the change at a glance.

## ADRs
Links to `docs/adr/`.
