#!/usr/bin/env python3
"""Verify a scaffolded project: guard rails present and working, agents valid, no unresolved variables.

Usage: verify_setup.py --target DIR
Exit code 0 only if every check passes.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

AGENTS = ["planner", "architect", "domain", "test", "implementer", "reviewer", "security", "devops-docs"]
SKILLS = ["orchestrate", "plan-grill", "spec-writer"]
MUST_DENY = ["Bash(psql:*)", "Bash(mysql:*)", "Bash(mongosh:*)", "Bash(redis-cli:*)", "Bash(sqlite3:*)",
             "Bash(docker exec:*)", "Read(./.env)", "Read(./.env.*)"]
BLOCKED = [
    ("Bash", {"command": "psql -h localhost -U app db"}),
    ("Bash", {"command": "bash -c \"mysql -e 'select 1'\""}),
    ("Bash", {"command": "npx prisma migrate deploy"}),
    ("Bash", {"command": "docker exec db sqlite3 x.db"}),
    ("Bash", {"command": "cat .env"}),
    ("Bash", {"command": "echo postgres://u:p@h/db"}),
    ("Bash", {"command": "printenv"}),
    ("Read", {"file_path": "/proj/.env.production"}),
    ("Read", {"file_path": "/proj/secrets/key.pem"}),
]
ALLOWED = [
    ("Bash", {"command": "npm test"}),
    ("Bash", {"command": "pytest -q"}),
    ("Bash", {"command": "git status"}),
    ("Read", {"file_path": "/proj/src/app.py"}),
    ("Read", {"file_path": "/proj/.env.example"}),
]
failures = []


def check(ok: bool, msg: str) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        failures.append(msg)


def run_hook(py: str, hook: Path, tool: str, tool_input: dict) -> int:
    p = subprocess.run([py, str(hook)], input=json.dumps({"tool_name": tool, "tool_input": tool_input}),
                       capture_output=True, text=True)
    return p.returncode


def frontmatter(path: Path) -> dict:
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return {}
    return dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    t = Path(ap.parse_args().target).resolve()

    for f in ["CLAUDE.md", "AGENTS.md", "docs/glossary.md", "docs/specs/README.md", "docs/adr/0000-template.md"]:
        check((t / f).is_file(), f"exists: {f}")

    sp = t / ".claude" / "settings.json"
    check(sp.is_file(), "exists: .claude/settings.json")
    if sp.is_file():
        try:
            s = json.loads(sp.read_text(encoding="utf-8"))
            deny = s.get("permissions", {}).get("deny", [])
            for rule in MUST_DENY:
                check(rule in deny, f"deny rule: {rule}")
            hooks = s.get("hooks", {}).get("PreToolUse", [])
            check(any("block-db-access.py" in h.get("command", "") for e in hooks for h in e.get("hooks", [])),
                  "PreToolUse hook registered")
        except json.JSONDecodeError as e:
            check(False, f"settings.json is valid JSON ({e})")

    hook = t / ".claude" / "hooks" / "block-db-access.py"
    check(hook.is_file(), "exists: block-db-access.py")
    if hook.is_file():
        py = sys.executable
        for tool, inp in BLOCKED:
            check(run_hook(py, hook, tool, inp) == 2, f"hook blocks {tool}: {list(inp.values())[0]}")
        for tool, inp in ALLOWED:
            check(run_hook(py, hook, tool, inp) == 0, f"hook allows {tool}: {list(inp.values())[0]}")
        check(subprocess.run([py, str(hook)], input="not json", capture_output=True, text=True).returncode == 2,
              "hook fails closed on malformed input")

    for a in AGENTS:
        p = t / ".claude" / "agents" / f"{a}.md"
        check(p.is_file(), f"agent exists: {a}")
        if p.is_file():
            fm = frontmatter(p)
            check(fm.get("name", "").strip() == a and bool(fm.get("description", "").strip()),
                  f"agent frontmatter valid: {a}")
            body = p.read_text(encoding="utf-8")
            check("NEVER access the system database" in body, f"agent carries DB rule: {a}")
    for sk in SKILLS:
        p = t / ".claude" / "skills" / sk / "SKILL.md"
        check(p.is_file() and frontmatter(p).get("name", "").strip() == sk, f"skill valid: {sk}")

    leftovers = [str(p.relative_to(t)) for p in t.rglob("*")
                 if p.is_file() and ".git" not in p.parts and p.suffix in {".md", ".json", ".yml", ".py"}
                 and re.search(r"\{\{[A-Z_]+\}\}", p.read_text(encoding="utf-8", errors="ignore"))]
    check(not leftovers, f"no unresolved template variables {leftovers}")

    print(f"\n{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
