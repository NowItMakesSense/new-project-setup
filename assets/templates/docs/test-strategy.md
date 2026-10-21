# Test strategy guide

Guides how `architect`, `test` and `qa` set up and grow the test suite for this project.

## Test pyramid
- **Unit (many)**: one behavior at a time, no IO, fast. Owned by `test` during the TDD red phase.
- **Integration (some)**: real collaborators within a bounded context, persistence via fakes/in-memory/disposable infra per `TEST_DB_STRATEGY` - never the system database. Owned by `qa` after implementation.
- **End-to-end (few)**: full flow through the real interface (API/UI/CLI), still never against the system database or production services. Owned by `qa`.

## Fixtures and test doubles
- Prefer fakes/in-memory implementations of ports over mocks where behavior matters; use mocks/stubs only to verify interaction, not state.
- Name test doubles by role (`InMemoryUserRepository`, not `FakeThing1`); keep them next to the port they implement so they evolve together.
- `TEST_DB_STRATEGY` (see `CLAUDE.md`) decides how persistence-dependent tests run: in-memory fakes, or a disposable container a human starts - never the live system DB.

## Where tests live
Follow the stack's own convention (mirror source layout, e.g. `tests/` or co-located `*_test`/`*.spec` files) - `architect` records the chosen layout as a decision in the feature's `design.md` the first time it matters, so later features stay consistent.

## Coverage breadth (for `qa`)
Beyond the happy path each `test`-authored unit test covers, `qa` is responsible for: edge cases and boundary values, invalid/malicious input, concurrency/race conditions where relevant, error-handling and failure-mode paths, and regression scenarios tied to past bugs. Record new scenarios as Gherkin in the feature's `requirements.md` if they reveal a gap in the original spec (then get it approved) rather than only adding ad-hoc test code.
