#!/usr/bin/env python3
"""Keeps the project graph in front of the agent. Two modes, both advisory - this hook never blocks
anything and fails open (any error means: print nothing, exit 0).

  graph-hook.py nudge     PreToolUse on Grep|Glob. Reads the hook JSON from stdin and adds a short
                          reminder to the model's context to ask the graph first (and to build it if
                          it doesn't exist yet). Shown on the first search of a session and then on
                          every 4th one, so it informs without nagging.
  graph-hook.py refresh   SessionStart. If the graph is missing or stale (`build-graph.py check`),
                          rebuilds it, then prints one status line that lands in the session context.

It only runs .claude/scripts/build-graph.py (read-only on the project's files; writes
docs/knowledge-graph/). It never touches the database, credentials or the network.
Standard library only.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
BUILD = ROOT / ".claude" / "scripts" / "build-graph.py"
GRAPH = ROOT / "docs" / "knowledge-graph" / "graph.json"
EVERY = 4


def emit(event: str, text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def project_name() -> str:
    try:
        first = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()[0]
        return re.sub(r"^#\s*", "", first).strip() or ROOT.name
    except (OSError, IndexError):
        return ROOT.name


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(BUILD), "--root", str(ROOT), *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=90)


def nudge() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        event = {}
    session = re.sub(r"[^\w-]", "", str(event.get("session_id") or "nosession"))[:60]
    counter = Path(tempfile.gettempdir()) / f"claude-graph-nudge-{session}"
    try:
        n = int(counter.read_text()) if counter.is_file() else 0
        counter.write_text(str(n + 1))
    except (OSError, ValueError):
        n = 0
    if n % EVERY:
        return
    if GRAPH.is_file():
        emit("PreToolUse", "Project graph: before searching files, ask it. "
             "`python .claude/scripts/build-graph.py query <terms>` ranks the files and their neighbours; "
             "`explain <file>` shows what a file points to and what points to it; `path <a> <b>` how two files relate. "
             "Use Grep/Glob only if the graph has no match (and say so). INFERRED edges are leads to verify.")
    else:
        emit("PreToolUse", "The project graph has not been built yet: run "
             "`python .claude/scripts/build-graph.py` once, then use its `query` / `explain` / `path` commands "
             "instead of searching files blind.")


def refresh() -> None:
    if not BUILD.is_file():
        return
    if GRAPH.is_file() and run("check").returncode == 0:
        emit("SessionStart", "Project graph is up to date (docs/knowledge-graph/GRAPH_REPORT.md). "
             "Query it before grepping: python .claude/scripts/build-graph.py query <terms>.")
        return
    r = run("--title", project_name())
    if r.returncode == 0:
        emit("SessionStart", "Project graph rebuilt: " + (r.stdout.strip().splitlines() or ["done"])[-1]
             + ". Read docs/knowledge-graph/GRAPH_REPORT.md, then query it before grepping.")
    else:
        emit("SessionStart", "The project graph could not be rebuilt (" + (r.stderr.strip().splitlines() or ["unknown error"])[-1][:200] + ").")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "nudge":
            nudge()
        elif mode == "refresh":
            refresh()
    except Exception:   # advisory hook: never get in the way of the session
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
