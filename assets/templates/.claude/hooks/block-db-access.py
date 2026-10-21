#!/usr/bin/env python3
"""PreToolUse guard: agents must never access the system database or read secrets.

Reads the hook JSON from stdin. Exit 0 = allow, exit 2 = block (stderr is shown to the agent).
Fails closed on malformed input, and on a missing/invalid db_patterns.json. Standard library only.

The DB/secret-access rule set lives in the sibling db_patterns.json, not in this file - review or
extend the rules there instead of editing this script's logic.
"""
import json
import re
import sys
from pathlib import Path

PATTERNS_FILE = Path(__file__).resolve().parent / "db_patterns.json"


def block(reason: str) -> None:
    sys.stderr.write(
        f"BLOCKED by project security policy: {reason}.\n"
        "Agents must never access the system database or secrets. "
        "Do not work around this guard. Tell the user what you need and let a human run it.\n"
    )
    sys.exit(2)


def load_patterns() -> dict:
    try:
        data = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
        return {
            "cmd": [(re.compile(p["pattern"], re.I), p["label"]) for p in data["cmd_patterns"]],
            "path": re.compile(data["path_pattern"], re.I),
            "safe": re.compile(data["safe_path"], re.I),
        }
    except Exception as e:
        block(f"could not load {PATTERNS_FILE.name} ({e}) - failing closed")


def main() -> None:
    patterns = load_patterns()

    try:
        data = json.load(sys.stdin)
    except Exception:
        block("could not parse hook input (failing closed)")
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}

    if tool == "Bash":
        cmd = inp.get("command", "") or ""
        for rx, label in patterns["cmd"]:
            if rx.search(cmd):
                block(label)
        return

    for key in ("file_path", "path", "notebook_path", "pattern", "glob"):
        val = inp.get(key)
        if isinstance(val, str) and patterns["path"].search(val) and not patterns["safe"].search(val):
            block(f"access to secret/credential path ({val})")


if __name__ == "__main__":
    main()
