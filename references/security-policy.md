# Security policy

## Non-negotiable: agents never access the system database
No agent or orchestrator may, by any means, query, inspect, connect to, migrate, seed, dump or otherwise run commands against the system's database (dev, staging or prod). This includes reading credentials or connection strings.

### Layers (defense in depth)
1. **`permissions.deny`** in `.claude/settings.json`: DB CLIs (`psql`, `mysql`, `mariadb`, `mongosh`, `mongo`, `redis-cli`, `sqlite3`, `sqlcmd`, `cqlsh`, `influx`, `clickhouse-client`), ORM/migration runners that hit a live DB (`prisma migrate|db|studio`, `alembic`, `flyway`, `liquibase`, `knex migrate`, `typeorm migration:run`, `rails db:`, `rake db:`, `django manage.py migrate|dbshell|shell`, `sequelize db:`), `docker exec`/`docker compose exec`, and reads/edits of `.env*`, keys, credentials, `secrets/`.
2. **PreToolUse hook** (`.claude/hooks/block-db-access.py`): inspects Bash commands and file paths with broader patterns (connection-string URLs such as `postgres://`, wrapper invocations like `npx prisma`, `bash -c "psql ..."`, `cat .env`). Exit code 2 blocks the call.
3. **Textual rules** in `CLAUDE.md`, `AGENTS.md` and every agent prompt.
4. **Structural**: no agent is given credentials; tests use in-memory/fakes or disposable containers started by a human; migrations are only **generated as files** for a human to review and apply.

### If a task seems to require DB access
Stop and tell the user. Propose a human-run command or a fixture/fake instead. Never work around the guard (no scripts, no base64, no alternate clients).

## General security practices
- Least privilege: each agent gets the minimum tools it needs.
- No secrets in the repo; `.env.example` with placeholders only. Secret scanning in CI.
- Threat model (STRIDE-lite) in the design phase; OWASP ASVS checklist in the security review.
- Input validation at boundaries, parameterized queries only, output encoding, authN/authZ explicit per use case.
- Dependency audit + SAST in CI; pin versions; review new dependencies.
- Destructive or outward-facing actions (deleting data, pushing, deploying, publishing, sending messages) require explicit human confirmation.
- Log without PII/secrets; document data retention per `COMPLIANCE` answer.

## Limits
Hook and deny rules are enforced only by Claude Code. `AGENTS.md` is advisory for other tools. Tell the user this.
