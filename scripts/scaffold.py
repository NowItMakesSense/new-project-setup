#!/usr/bin/env python3
"""Scaffold the new-project-setup templates into a target project.

Usage: scaffold.py --target DIR --answers answers.json [--dry-run] [--overwrite]

- Every answer key is required (use "TBD" for unknown). Nothing is guessed.
- Existing files are skipped unless --overwrite is given.
- *.tmpl files get {{VARIABLES}} substituted and the suffix removed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "PROJECT_NAME", "PROJECT_DESCRIPTION", "DOC_LANGUAGE", "DOMAIN", "PROJECT_TYPE", "STACK",
    "TEST_CMD", "LINT_CMD", "BUILD_CMD", "DB_ENGINE", "TEST_DB_STRATEGY", "CI_PROVIDER",
    "VCS_BRANCHING", "ENGINEERING_PRINCIPLES", "COMPLIANCE", "TEAM", "PYTHON_CMD", "NPX_CMD",
    "HAS_UI", "MODEL_PRIORITY", "COVERAGE_THRESHOLD", "EXTRA_DENY",
]
KG_MCP_TOOLS = [
    "read_graph", "search_nodes", "open_nodes", "create_entities", "create_relations",
    "add_observations", "delete_entities", "delete_relations", "delete_observations",
]
# Role-tiered model defaults per MODEL_PRIORITY. "balanced" is the recommended default.
TIER_PRESETS = {
    "cost": {
        "PLANNER": "sonnet", "ARCHITECT": "sonnet", "DOMAIN": "sonnet", "TEST": "sonnet",
        "IMPLEMENTER": "sonnet", "QA": "sonnet", "REVIEWER": "sonnet", "SECURITY": "sonnet",
        "DEVOPS_DOCS": "haiku", "KNOWLEDGE_GRAPH": "sonnet", "DESIGNER": "sonnet", "DEBUG": "sonnet",
        "FRONTEND": "sonnet", "UI_REVIEWER": "sonnet",
    },
    "balanced": {
        "PLANNER": "sonnet", "ARCHITECT": "opus", "DOMAIN": "sonnet", "TEST": "sonnet",
        "IMPLEMENTER": "sonnet", "QA": "sonnet", "REVIEWER": "opus", "SECURITY": "opus",
        "DEVOPS_DOCS": "haiku", "KNOWLEDGE_GRAPH": "sonnet", "DESIGNER": "sonnet", "DEBUG": "opus",
        "FRONTEND": "sonnet", "UI_REVIEWER": "opus",
    },
    "quality": {
        "PLANNER": "sonnet", "ARCHITECT": "opus", "DOMAIN": "opus", "TEST": "sonnet",
        "IMPLEMENTER": "sonnet", "QA": "sonnet", "REVIEWER": "opus", "SECURITY": "opus",
        "DEVOPS_DOCS": "sonnet", "KNOWLEDGE_GRAPH": "opus", "DESIGNER": "sonnet", "DEBUG": "opus",
        "FRONTEND": "opus", "UI_REVIEWER": "opus",
    },
}
# Generated only when HAS_UI is yes: the front-end team and the house rules they share.
UI_ONLY_FILES = {
    ".claude/agents/designer.md.tmpl", ".claude/agents/frontend.md.tmpl", ".claude/agents/ui-reviewer.md.tmpl",
}
UI_ONLY_PREFIX = ".claude/skills/frontend-craft/"
TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"
VAR = re.compile(r"\{\{([A-Z_]+)\}\}")


def load_answers(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in data or data[k] in (None, "")]
    if missing:
        sys.exit(f"Missing answers (ask the user, do not assume): {', '.join(missing)}")
    if not isinstance(data["EXTRA_DENY"], list):
        sys.exit("EXTRA_DENY must be a list of permission patterns")
    if not re.fullmatch(r"[A-Za-z0-9_./-]+", str(data["PYTHON_CMD"])):
        sys.exit("PYTHON_CMD must be a plain command name such as python, python3 or py")
    values = {k: str(data[k]) for k in REQUIRED if k != "EXTRA_DENY"}
    values["EXTRA_DENY_ITEMS"] = "".join(",\n      " + json.dumps(x) for x in data["EXTRA_DENY"])
    values["_CI"] = str(data["CI_PROVIDER"]).strip().lower()
    values["_HAS_UI"] = str(data["HAS_UI"]).strip().lower()
    db_engine = str(data["DB_ENGINE"]).strip().lower()
    values["_HAS_DB"] = "no" if db_engine in ("none", "nenhum", "tbd", "") else "yes"

    priority = str(data["MODEL_PRIORITY"]).strip().lower()
    if priority not in TIER_PRESETS:
        sys.exit(f"MODEL_PRIORITY must be one of {sorted(TIER_PRESETS)}, got {priority!r}")
    for role, model in TIER_PRESETS[priority].items():
        values[f"MODEL_{role}"] = model

    npx_cmd = str(data["NPX_CMD"]).strip()
    node_available = npx_cmd.lower() not in ("none", "tbd", "")
    if node_available:
        if not re.fullmatch(r"[A-Za-z0-9_./-]+", npx_cmd):
            sys.exit("NPX_CMD must be a plain command name such as npx, or 'none'")
        values["KG_MCP_TOOLS"] = "".join(f", mcp__knowledge-graph__{t}" for t in KG_MCP_TOOLS)
        # Pre-approves the .mcp.json server so the knowledge-graph agent isn't blocked by the
        # per-server trust prompt. Each user must still trust the folder itself on first run -
        # this key is ignored in an untrusted folder.
        values["MCP_ENABLED_BLOCK"] = '"enabledMcpjsonServers": ["knowledge-graph"],\n  '
    else:
        values["KG_MCP_TOOLS"] = ""
        values["MCP_ENABLED_BLOCK"] = ""
    # The server DEFINITION lives in `.mcp.json` at the repo root, NOT in `.claude/settings.json`:
    # Claude Code reads project-scoped server definitions only from `.mcp.json`. Only the
    # enable/disable toggle lists belong in settings.json.
    values["_HAS_MCP"] = "yes" if node_available else "no"
    return values


def render(text: str, values: dict, name: str) -> str:
    def sub(m):
        if m.group(1) not in values:
            sys.exit(f"Unknown template variable {m.group(0)} in {name}")
        return values[m.group(1)]
    return VAR.sub(sub, text)


def merge_mcp_json(old: dict, new: dict) -> dict:
    """Key-level merge of .mcp.json: add server definitions `old` doesn't already have,
    never overwrite or remove a server the project already declares."""
    merged = dict(old)
    merged_servers = dict(old.get("mcpServers", {}))
    for key, value in new.get("mcpServers", {}).items():
        merged_servers.setdefault(key, value)
    merged["mcpServers"] = merged_servers
    return merged


def merge_settings(old: dict, new: dict) -> dict:
    """Key-level merge of .claude/settings.json: union deny rules, add new hook entries,
    never touch or remove anything already in `old` that `new` doesn't mention.

    Note: MCP servers are NOT merged here. They belong in `.mcp.json` (see merge_mcp_json);
    a legacy `mcpServers` block left in settings.json by an older version of this skill is
    dead config - it is preserved untouched rather than extended."""
    merged = dict(old)

    old_deny = old.get("permissions", {}).get("deny", [])
    new_deny = new.get("permissions", {}).get("deny", [])
    merged["permissions"] = dict(old.get("permissions", {}))
    merged["permissions"]["deny"] = old_deny + [d for d in new_deny if d not in old_deny]

    old_hooks = old.get("hooks", {}).get("PreToolUse", [])
    new_hooks = new.get("hooks", {}).get("PreToolUse", [])

    def hook_commands(entries):
        return {h.get("command", "") for e in entries for h in e.get("hooks", [])}

    existing_cmds = hook_commands(old_hooks)
    merged_hooks = list(old_hooks)
    for entry in new_hooks:
        if not any(h.get("command", "") in existing_cmds for h in entry.get("hooks", [])):
            merged_hooks.append(entry)
    if old_hooks or new_hooks:
        merged["hooks"] = dict(old.get("hooks", {}))
        merged["hooks"]["PreToolUse"] = merged_hooks

    return merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--merge-settings", action="store_true",
                     help="For .claude/settings.json and .mcp.json only: merge new deny rules/hooks "
                          "(settings.json) and new MCP servers (.mcp.json) into the existing file by "
                          "key instead of skipping or fully overwriting it.")
    a = ap.parse_args()

    values = load_answers(Path(a.answers))
    target = Path(a.target).resolve()
    # MEMORY_FILE_PATH must be ABSOLUTE: @modelcontextprotocol/server-memory resolves a relative
    # path against its own module directory (inside the npx cache), not the project - a relative
    # path makes writes fail with ENOENT on a lock file under the package's dist/. And it cannot
    # be expressed portably: Claude Code substitutes $CLAUDE_PROJECT_DIR into hook *commands*, but
    # does not export it into an MCP server's environment, so `${CLAUDE_PROJECT_DIR}` there expands
    # to nothing. Hence the concrete path, resolved at scaffold time. See docs/knowledge-graph/README.md.
    values["MCP_MEMORY_PATH"] = (target / "docs" / "knowledge-graph" / "graph.jsonl").as_posix()
    created, skipped, merged_files = [], [], []

    for src in sorted(p for p in TEMPLATES.rglob("*") if p.is_file()):
        rel = src.relative_to(TEMPLATES)
        if rel.as_posix().startswith(".github/") and values["_CI"] != "github-actions":
            continue
        if rel.as_posix() in UI_ONLY_FILES or rel.as_posix().startswith(UI_ONLY_PREFIX):
            if values["_HAS_UI"] != "yes":
                continue
        if rel.as_posix().startswith("Database/") and values["_HAS_DB"] != "yes":
            continue
        if rel.as_posix() == ".mcp.json.tmpl" and values["_HAS_MCP"] != "yes":
            continue
        is_tmpl = src.suffix == ".tmpl"
        dest = target / (rel.with_suffix("") if is_tmpl else rel)
        text = src.read_text(encoding="utf-8")
        if is_tmpl:
            text = render(text, values, rel.as_posix())

        if dest.exists():
            mergers = {
                ".claude/settings.json.tmpl": merge_settings,
                ".mcp.json.tmpl": merge_mcp_json,
            }
            merger = mergers.get(rel.as_posix())
            if a.merge_settings and merger is not None:
                old = json.loads(dest.read_text(encoding="utf-8"))
                new = json.loads(text)
                merged = merger(old, new)
                if not a.dry_run:
                    dest.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8", newline="\n")
                merged_files.append(dest)
                continue
            if not a.overwrite:
                skipped.append(dest)
                continue
        if not a.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8", newline="\n")
        created.append(dest)

    verb = "Would create" if a.dry_run else "Created"
    print(f"{verb} {len(created)} file(s):")
    for p in created:
        print(f"  + {p.relative_to(target)}")
    if merged_files:
        verb2 = "Would merge" if a.dry_run else "Merged"
        print(f"{verb2} {len(merged_files)} file(s) by key (deny rules/hooks/mcpServers union):")
        for p in merged_files:
            print(f"  ~ {p.relative_to(target)}")
    if skipped:
        print(f"Skipped {len(skipped)} existing file(s) (use --overwrite or --merge-settings only with user approval):")
        for p in skipped:
            print(f"  = {p.relative_to(target)}")


if __name__ == "__main__":
    main()
