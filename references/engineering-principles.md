# Engineering principles (defaults)

Apply these only when the user has not specified otherwise in the interview or planning. User choices always win; record deviations as ADRs.

- **Clean Code**: intention-revealing names, small functions, one level of abstraction, no dead code, comments explain *why*, errors are explicit.
- **Clean Architecture**: layers `domain` -> `application` -> `interface`/`infrastructure`; dependencies point inward only; frameworks, DB and IO live at the edges behind ports.
- **DDD**: ubiquitous language in `docs/glossary.md`; bounded contexts; entities, value objects, aggregates, domain events, repositories as ports; domain has no framework imports.
- **SOLID**: SRP, OCP, LSP, ISP, DIP - flagged by the reviewer agent.
- **TDD (Iron Law): NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.** red (failing test that captures a spec scenario) -> green (minimal code) -> refactor (tests stay green). If code was written before its test, delete it and redo it properly - do not retrofit a test around existing code. Test pyramid: many unit, some integration (against fakes/disposable infra, see `test-strategy.md`), few e2e.
- **Rationalization red flags** - if you catch yourself thinking any of these, stop and follow the Iron Law instead: "it's just this one case", "I'll add the test after", "this is too simple to need a test first", "the test would be trivial anyway", "I already know this works".
- **Debugging**: never patch a failure you haven't understood. Follow `debugging-protocol.md` (reproduce -> root cause -> minimal hypothesis -> fix + regression test) instead of guessing.
- **Specs-first**: every feature has requirements -> design -> tasks before code; tests trace back to Gherkin scenarios.
- **Git**: small PRs; Conventional Commits and trunk-based unless the user chose otherwise.
- **Quality gates**: lint, tests, coverage threshold agreed with the user, security checks in CI.
