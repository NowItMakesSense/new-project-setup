# Requirements: <feature>

Status: Draft | Date: | Approved by:

## Context and goal

## Actors

## Functional requirements (EARS)
- REQ-001: WHEN <trigger> THE SYSTEM SHALL <response>.

## Scenarios (Gherkin)
### REQ-001
```gherkin
Scenario: <name>
  Given <context>
  When <action>
  Then <outcome>
```

## Non-functional requirements
- **Performance**: target latency (p50/p95/p99), expected throughput.
- **Availability**: SLO/uptime target, acceptable downtime.
- **Security**: see `security-policy.md` and the `security` agent's checklist.
- **Privacy/compliance**: per the project's `COMPLIANCE` answer.
- **Accessibility**: WCAG level, if `HAS_UI`.
- **Observability**: what must be logged/traced/alerted on for this feature.
Mark any of these "N/A" explicitly rather than leaving it blank.

## Out of scope

## Open questions (must be empty before approval)
