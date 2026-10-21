# Design: <feature>

Status: Draft | Date: | Approved by:

## Bounded context and ubiquitous language

## Domain model
Entities, value objects, aggregates (invariants), domain events.

## UX (if this feature has a UI)
Information architecture, user flows/wireframes (text/Mermaid), design-system tokens/components used, accessibility (WCAG) criteria. Owned by `designer`; omit this section for UI-less features.

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

## ADRs
Links to `docs/adr/`.
