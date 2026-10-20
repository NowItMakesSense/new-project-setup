# Interview (required before scaffolding)

Ask one topic at a time. Skip only what the user already stated explicitly. Never fill gaps with guesses; if an answer is "I don't know", record `TBD` and flag it for the planning phase (`/plan-grill`).

## Required questions

| Key | Question | Notes |
|---|---|---|
| `PROJECT_NAME` | Project name (slug-friendly)? | |
| `PROJECT_DESCRIPTION` | One-paragraph description / problem it solves? | |
| `DOC_LANGUAGE` | Language for docs and specs? (e.g. pt-BR, en) | Agent instructions stay in English |
| `DOMAIN` | Business domain / industry? | May be TBD until planning |
| `PROJECT_TYPE` | Web app, API, CLI, library, mobile, data pipeline, other? | |
| `STACK` | Language(s), frameworks, runtime? | Never assume; TBD allowed |
| `TEST_CMD` | Command to run the test suite? | TBD allowed; filled after stack is known |
| `LINT_CMD` | Lint/format command? | |
| `BUILD_CMD` | Build command? | |
| `DB_ENGINE` | Does the system use a database? Which engine? | Used ONLY to extend deny rules. Agents never connect to it. |
| `TEST_DB_STRATEGY` | How should tests handle persistence? (in-memory/fakes, disposable container started by a human, other) | Must not be the system DB |
| `CI_PROVIDER` | GitHub Actions, GitLab CI, other, none? | Only GitHub Actions has a template |
| `VCS_BRANCHING` | Branch/commit conventions? (default offered: trunk-based + Conventional Commits) | Ask, do not assume |
| `ENGINEERING_PRINCIPLES` | Keep defaults (Clean Code, Clean Architecture, TDD, DDD, SOLID) or override/remove any? | Default = keep all |
| `COMPLIANCE` | Regulatory/security constraints (LGPD, GDPR, PCI, HIPAA, none)? | |
| `TEAM` | Solo or team? Review process? | |
| `PYTHON_CMD` | Python command available for the hook (`python`, `python3`, `py`)? | Detect with the user; hook needs Python 3 |
| `EXTRA_DENY` | Extra commands/paths agents must never touch? | Optional |

## Confirmation
Show a table of all answers (including `TBD`s) and get explicit approval before running `scaffold.py`.

## Answers JSON schema
```json
{
  "PROJECT_NAME": "my-app",
  "PROJECT_DESCRIPTION": "...",
  "DOC_LANGUAGE": "pt-BR",
  "DOMAIN": "TBD",
  "PROJECT_TYPE": "api",
  "STACK": "TBD",
  "TEST_CMD": "TBD",
  "LINT_CMD": "TBD",
  "BUILD_CMD": "TBD",
  "DB_ENGINE": "postgresql",
  "TEST_DB_STRATEGY": "in-memory fakes",
  "CI_PROVIDER": "github-actions",
  "VCS_BRANCHING": "trunk-based + Conventional Commits",
  "ENGINEERING_PRINCIPLES": "defaults",
  "COMPLIANCE": "none",
  "TEAM": "solo",
  "PYTHON_CMD": "python",
  "EXTRA_DENY": []
}
```
All keys are required (use `"TBD"` for unknown). `EXTRA_DENY` is a list of Bash patterns (e.g. `"Bash(terraform apply:*)"`).
