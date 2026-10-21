#!/usr/bin/env python3
"""PreToolUse guard: agents must never access the system database or read secrets.

Reads the hook JSON from stdin. Exit 0 = allow, exit 2 = block (stderr is shown to the agent).
Fails closed on malformed input for tools it inspects. Standard library only.
"""
import json
import re
import sys

DB_CLIS = (
    r"psql|pg_dump|pg_restore|pg_dumpall|mysql|mysqldump|mysqladmin|mariadb|mongosh|mongo|mongodump|mongorestore|"
    r"redis-cli|sqlite3|sqlcmd|cqlsh|clickhouse-client|influx|isql|sqlplus|usql|pgcli|mycli|litecli"
)
MIGRATORS = (
    r"prisma|alembic|flyway|liquibase|knex|sequelize|typeorm|sequelize-cli|dbmate|goose|atlas|"
    r"(?:rake|rails)\s+db:|manage\.py\s+(?:migrate|dbshell|shell|flush|loaddata|sqlmigrate)|"
    r"artisan\s+(?:migrate|db:)|ef\s+database|dotnet\s+ef\s+database"
)
CONTAINER_EXEC = r"(?:docker|podman|kubectl|nerdctl)(?:\s+compose)?\s+(?:exec|run|attach)|docker-compose\s+exec"
SECRET_MANAGER_CLI = (
    r"aws\s+secretsmanager\s+get-secret-value|aws\s+ssm\s+get-parameter(?:s(?:-by-path)?)?\b[^|;&]*--with-decryption|"
    r"gcloud\s+secrets\s+versions\s+access|az\s+keyvault\s+secret\s+(?:show|download)|"
    r"vault\s+(?:read|kv\s+get)|op\s+(?:read|item\s+get)|doppler\s+(?:secrets\s+get|run)|"
    r"pass\s+show|kubectl\s+get\s+secrets?\b"
)
CONN_URL = r"(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|rediss|mssql|sqlserver|oracle|cassandra|clickhouse)://"
SECRET_READ = r"(?:cat|type|less|more|head|tail|bat|get-content|gc|grep|rg|awk|sed|cp|mv|curl)\b[^|;&]*"
SECRET_PATH = r"(?:^|[\\/\s\"'])\.env(?:\.[\w.-]+)?(?:$|[\s\"'])|secrets?[\\/]|\.pem\b|\.key\b|id_rsa|id_ed25519|credentials(?:\.json)?\b|\.pgpass|\.my\.cnf|\.netrc|\.aws[\\/]"
ENV_DUMP = r"(?:^|[;&|]\s*)(?:printenv|env|set|export\s+-p|declare\s+-x|get-childitem\s+env:|gci\s+env:)\s*(?:$|[;&|])"

CMD_PATTERNS = [
    (re.compile(rf"(?:^|[\s;&|`(\"'/\\])(?:{DB_CLIS})(?:\.exe)?(?=$|[\s;&|`)\"'])", re.I), "database CLI"),
    (re.compile(rf"(?:^|[\s;&|`(\"'/\\])(?:{MIGRATORS})", re.I), "database migration/ORM runner"),
    (re.compile(CONTAINER_EXEC, re.I), "container exec (can reach the database)"),
    (re.compile(SECRET_MANAGER_CLI, re.I), "cloud secret-manager CLI call"),
    (re.compile(CONN_URL, re.I), "database connection string"),
    (re.compile(SECRET_READ + SECRET_PATH, re.I), "secret/credential file access"),
    (re.compile(ENV_DUMP, re.I), "environment dump (may expose credentials)"),
]
PATH_PATTERN = re.compile(SECRET_PATH, re.I)
SAFE_PATH = re.compile(r"\.env\.(?:example|sample|template)$", re.I)


def block(reason: str) -> None:
    sys.stderr.write(
        f"BLOCKED by project security policy: {reason}.\n"
        "Agents must never access the system database or secrets. "
        "Do not work around this guard. Tell the user what you need and let a human run it.\n"
    )
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        block("could not parse hook input (failing closed)")
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}

    if tool == "Bash":
        cmd = inp.get("command", "") or ""
        for rx, label in CMD_PATTERNS:
            if rx.search(cmd):
                block(label)
        return

    for key in ("file_path", "path", "notebook_path", "pattern", "glob"):
        val = inp.get(key)
        if isinstance(val, str) and PATH_PATTERN.search(val) and not SAFE_PATH.search(val):
            block(f"access to secret/credential path ({val})")


if __name__ == "__main__":
    main()
