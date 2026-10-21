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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scaffold import TIER_PRESETS  # noqa: E402

AGENTS = ["planner", "architect", "domain", "test", "qa", "implementer", "reviewer", "security",
          "devops-docs", "knowledge-graph", "debug"]
OPTIONAL_AGENTS = ["designer"]
SKILLS = ["orchestrate", "plan-grill", "spec-writer", "amend-constitution"]
DATABASE_OBJECT_KINDS = ["tables", "indexes", "foreign-keys", "primary-keys", "packages", "functions"]
MUST_DENY = ["Bash(psql:*)", "Bash(mysql:*)", "Bash(mongosh:*)", "Bash(redis-cli:*)", "Bash(sqlite3:*)",
             "Bash(docker exec:*)", "Bash(aws secretsmanager get-secret-value:*)",
             "Read(./.env)", "Read(./.env.*)"]
BLOCKED = [
    ("Bash", {"command": "psql -h localhost -U app db"}),
    ("Bash", {"command": "bash -c \"mysql -e 'select 1'\""}),
    ("Bash", {"command": "npx prisma migrate deploy"}),
    ("Bash", {"command": "docker exec db sqlite3 x.db"}),
    ("Bash", {"command": "aws secretsmanager get-secret-value --secret-id prod/db"}),
    ("Bash", {"command": "vault read secret/prod/db"}),
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
    ap.add_argument("--answers")
    args = ap.parse_args()
    t = Path(args.target).resolve()
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8")) if args.answers else None
    priority = str(answers.get("MODEL_PRIORITY", "balanced")).strip().lower() if answers else "balanced"
    if priority not in TIER_PRESETS:
        priority = "balanced"
    if answers is None:
        print(f"INFO  no --answers given; checking model tiers against the '{priority}' preset as a guess")
    model_tier = {role.lower().replace("_", "-"): model for role, model in TIER_PRESETS[priority].items()}

    for f in ["CLAUDE.md", "AGENTS.md", "docs/glossary.md", "docs/specs/README.md",
              "docs/adr/0000-template.md", "docs/knowledge-graph/README.md",
              "docs/test-strategy.md", "docs/debugging-protocol.md"]:
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

            mcp = s.get("mcpServers", {})
            node_expected = answers is not None and str(answers.get("NPX_CMD", "")).strip().lower() not in ("none", "tbd", "")
            if node_expected:
                check("knowledge-graph" in mcp, "mcpServers.knowledge-graph declared (NPX_CMD set)")
            if "knowledge-graph" in mcp:
                kg = mcp["knowledge-graph"]
                well_formed = (
                    bool(kg.get("command"))
                    and kg.get("args") == ["-y", "@modelcontextprotocol/server-memory"]
                    and kg.get("env", {}).get("MEMORY_FILE_PATH", "").endswith("docs/knowledge-graph/graph.jsonl")
                )
                check(well_formed, "mcpServers.knowledge-graph well-formed")
            elif answers is None:
                print("INFO  mcpServers.knowledge-graph not present (pass --answers to verify this was expected)")
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

    guard = t / ".claude" / "hooks" / "verify-guard.py"
    check(guard.is_file(), "exists: verify-guard.py (CI guard-rail check)")
    if guard.is_file():
        r = subprocess.run([sys.executable, str(guard)], cwd=t, capture_output=True, text=True)
        check(r.returncode == 0, "verify-guard.py passes against this scaffold (self-check)")

    for a in AGENTS:
        p = t / ".claude" / "agents" / f"{a}.md"
        check(p.is_file(), f"agent exists: {a}")
        if p.is_file():
            fm = frontmatter(p)
            check(fm.get("name", "").strip() == a and bool(fm.get("description", "").strip()),
                  f"agent frontmatter valid: {a}")
            check(fm.get("model", "").strip() == model_tier[a], f"agent model tier: {a} = {model_tier[a]}")
            body = p.read_text(encoding="utf-8")
            check("NEVER access the system database" in body, f"agent carries DB rule: {a}")
    for a in OPTIONAL_AGENTS:
        p = t / ".claude" / "agents" / f"{a}.md"
        if answers is not None and str(answers.get("HAS_UI", "")).strip().lower() == "yes" and a == "designer":
            check(p.is_file(), f"agent exists: {a} (HAS_UI=yes)")
        if p.is_file():
            fm = frontmatter(p)
            check(fm.get("name", "").strip() == a and bool(fm.get("description", "").strip()),
                  f"agent frontmatter valid: {a}")
            check(fm.get("model", "").strip() == model_tier[a], f"agent model tier: {a} = {model_tier[a]}")
            body = p.read_text(encoding="utf-8")
            check("NEVER access the system database" in body, f"agent carries DB rule: {a}")
    for sk in SKILLS:
        p = t / ".claude" / "skills" / sk / "SKILL.md"
        check(p.is_file() and frontmatter(p).get("name", "").strip() == sk, f"skill valid: {sk}")

    if answers is not None:
        db_engine = str(answers.get("DB_ENGINE", "")).strip().lower()
        has_db = db_engine not in ("none", "nenhum", "tbd", "")
        if has_db:
            check((t / "Database" / "README.md").is_file(), "exists: Database/README.md")
            check((t / "Database" / "er-diagram.md").is_file(), "exists: Database/er-diagram.md")
            for kind in DATABASE_OBJECT_KINDS:
                check((t / "Database" / kind / "README.md").is_file(), f"exists: Database/{kind}/README.md")
        else:
            check(not (t / "Database").exists(), "Database/ omitted (DB_ENGINE indicates no database)")
    else:
        print("INFO  no --answers given; skipping Database/ checks (pass --answers to verify this was expected)")

    leftovers = [str(p.relative_to(t)) for p in t.rglob("*")
                 if p.is_file() and ".git" not in p.parts and p.suffix in {".md", ".json", ".yml", ".py"}
                 and re.search(r"\{\{[A-Z_]+\}\}", p.read_text(encoding="utf-8", errors="ignore"))]
    check(not leftovers, f"no unresolved template variables {leftovers}")

    print(f"\n{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
