#!/usr/bin/env python3
"""CI guard-rail check: fails the build if the DB-access guard has regressed.

Run from the repo root: python3 .claude/hooks/verify-guard.py
Exit code 0 only if every check passes - wire this into CI on every push/PR.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MUST_DENY = ["Bash(psql:*)", "Bash(mysql:*)", "Bash(mongosh:*)", "Bash(redis-cli:*)", "Bash(sqlite3:*)",
             "Bash(docker exec:*)", "Bash(aws secretsmanager get-secret-value:*)",
             "Read(./.env)", "Read(./.env.*)"]
BLOCKED = [
    ("Bash", {"command": "psql -h localhost -U app db"}),
    ("Bash", {"command": "docker exec db sqlite3 x.db"}),
    ("Bash", {"command": "aws secretsmanager get-secret-value --secret-id prod/db"}),
    ("Bash", {"command": "cat .env"}),
    ("Bash", {"command": "echo postgres://u:p@h/db"}),
    ("Read", {"file_path": str(ROOT / ".env.production")}),
]
ALLOWED = [
    ("Bash", {"command": "git status"}),
    ("Read", {"file_path": str(ROOT / "src" / "app.py")}),
]
failures = []


def check(ok: bool, msg: str) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        failures.append(msg)


def run_hook(hook: Path, tool: str, tool_input: dict) -> int:
    p = subprocess.run([sys.executable, str(hook)], input=json.dumps({"tool_name": tool, "tool_input": tool_input}),
                        capture_output=True, text=True)
    return p.returncode


def main() -> None:
    sp = ROOT / ".claude" / "settings.json"
    check(sp.is_file(), "exists: .claude/settings.json")
    if sp.is_file():
        try:
            s = json.loads(sp.read_text(encoding="utf-8"))
            deny = s.get("permissions", {}).get("deny", [])
            for rule in MUST_DENY:
                check(rule in deny, f"deny rule intact: {rule}")
            hooks = s.get("hooks", {}).get("PreToolUse", [])
            check(any("block-db-access.py" in h.get("command", "") for e in hooks for h in e.get("hooks", [])),
                  "PreToolUse hook still registered")
        except json.JSONDecodeError as e:
            check(False, f"settings.json is valid JSON ({e})")

    hook = ROOT / ".claude" / "hooks" / "block-db-access.py"
    check(hook.is_file(), "exists: block-db-access.py")
    if hook.is_file():
        for tool, inp in BLOCKED:
            check(run_hook(hook, tool, inp) == 2, f"hook still blocks {tool}: {list(inp.values())[0]}")
        for tool, inp in ALLOWED:
            check(run_hook(hook, tool, inp) == 0, f"hook still allows {tool}: {list(inp.values())[0]}")

    print(f"\n{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
