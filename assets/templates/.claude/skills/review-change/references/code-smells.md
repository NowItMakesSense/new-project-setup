# Code-smell baseline (Fowler)

Generic baseline for the Standards pass. The project's own documented standards override it. Smells are **judgement calls**, not violations: flag them with the concrete cost in this code, and don't flag a smell the project knowingly accepts (see ADRs).

| Smell | What to look for | Usual fix |
|---|---|---|
| Mysterious Name | Name doesn't say what or why; differs from `docs/glossary.md` | Rename to the ubiquitous-language term |
| Duplicated Code | Same logic in 2+ places that must change together | Extract function/class (after the second copy proves the shape) |
| Long Function | Needs comments to separate steps; several abstraction levels | Extract Function; Replace Temp with Query |
| Large Class / God Object | Many unrelated fields or methods | Extract Class; split by responsibility |
| Long Parameter List | 4+ params, flag params | Introduce Parameter Object; split by flag |
| Global / Mutable Data | Shared state changed from many places | Encapsulate; pass as a dependency |
| Divergent Change | One module changed for many unrelated reasons | Split along reasons to change |
| Shotgun Surgery | One change needs edits in many files | Move Function/Field together |
| Feature Envy | Method uses another object's data more than its own | Move Function to that object |
| Data Clumps | The same 3+ fields travel together | Introduce a value object (DDD) |
| Primitive Obsession | Money/ids/emails as raw strings and numbers | Value objects with invariants |
| Repeated Switches | Same type-switch in several places | Replace Conditional with Polymorphism |
| Speculative Generality | Hooks, params, abstractions nobody uses (YAGNI) | Remove |
| Dead Code | Unreachable or unused code, commented-out blocks | Delete (git remembers) |
| Message Chains / Middle Man | `a.b().c().d()` / class that only delegates | Hide Delegate / Remove Middle Man |
| Insider Trading / Inappropriate Intimacy | Modules reaching into each other's internals | Move behavior; narrow the interface |
| Comments as deodorant | Comment explains confusing code | Fix the code; keep comments for *why* |
| Test smells | Mock-heavy assertions on call order, no assertion, shared mutable fixtures, tests that pass when the code is deleted | Assert on observable behavior; isolate fixtures |

## Layering checks (Clean Architecture / DDD)
- Domain imports nothing from frameworks, ORM, HTTP or UI.
- Adapters translate; they hold no business rules.
- An aggregate is changed only through its root; invariants live in the domain, not in handlers.
- A new cross-bounded-context call goes through a published interface, and appears in `design.md`.
