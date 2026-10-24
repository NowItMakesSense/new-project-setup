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
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "PROJECT_NAME", "PROJECT_DESCRIPTION", "DOC_LANGUAGE", "DOMAIN", "PROJECT_TYPE", "STACK",
    "TEST_CMD", "LINT_CMD", "BUILD_CMD", "DB_ENGINE", "TEST_DB_STRATEGY", "CI_PROVIDER",
    "VCS_BRANCHING", "ENGINEERING_PRINCIPLES", "COMPLIANCE", "TEAM", "PYTHON_CMD",
    "HAS_UI", "MODEL_PRIORITY", "COVERAGE_THRESHOLD", "EXTRA_DENY",
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

    return values


def render(text: str, values: dict, name: str) -> str:
    def sub(m):
        if m.group(1) not in values:
            sys.exit(f"Unknown template variable {m.group(0)} in {name}")
        return values[m.group(1)]
    return VAR.sub(sub, text)


def merge_settings(old: dict, new: dict) -> dict:
    """Key-level merge of .claude/settings.json: union deny rules, add new hook entries,
    never touch or remove anything already in `old` that `new` doesn't mention.

    Anything else already in `old` (including a legacy `mcpServers` / `enabledMcpjsonServers` block left
    by an older version of this skill, which nothing reads any more) is preserved untouched."""
    merged = dict(old)

    old_deny = old.get("permissions", {}).get("deny", [])
    new_deny = new.get("permissions", {}).get("deny", [])
    merged["permissions"] = dict(old.get("permissions", {}))
    merged["permissions"]["deny"] = old_deny + [d for d in new_deny if d not in old_deny]

    def hook_commands(entries):
        return {h.get("command", "") for e in entries for h in e.get("hooks", [])}

    old_hooks, new_hooks = old.get("hooks", {}), new.get("hooks", {})
    if old_hooks or new_hooks:
        merged["hooks"] = dict(old_hooks)
        for event in sorted(set(old_hooks) | set(new_hooks)):
            entries = list(old_hooks.get(event, []))
            existing = hook_commands(entries)
            for entry in new_hooks.get(event, []):
                if not any(h.get("command", "") in existing for h in entry.get("hooks", [])):
                    entries.append(entry)
            merged["hooks"][event] = entries

    return merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--merge-settings", action="store_true",
                     help="For .claude/settings.json only: merge new deny rules/hooks into the existing "
                          "file by key instead of skipping or fully overwriting it.")
    a = ap.parse_args()

    values = load_answers(Path(a.answers))
    target = Path(a.target).resolve()
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
        is_tmpl = src.suffix == ".tmpl"
        dest = target / (rel.with_suffix("") if is_tmpl else rel)
        text = src.read_text(encoding="utf-8")
        if is_tmpl:
            text = render(text, values, rel.as_posix())

        if dest.exists():
            mergers = {
                ".claude/settings.json.tmpl": merge_settings,
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

    build = target / ".claude" / "scripts" / "build-graph.py"
    if not a.dry_run and build.is_file():
        # Build the project graph now so it exists from the first session; the SessionStart hook keeps it current.
        r = subprocess.run([sys.executable, str(build), "--root", str(target), "--title", values["PROJECT_NAME"]],
                           capture_output=True, text=True, encoding="utf-8")
        print(("Built the project graph: " + r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip()
              else f"WARN  could not build the project graph ({r.stderr.strip()[-200:]}); run .claude/scripts/build-graph.py")

    verb = "Would create" if a.dry_run else "Created"
    print(f"{verb} {len(created)} file(s):")
    for p in created:
        print(f"  + {p.relative_to(target)}")
    if merged_files:
        verb2 = "Would merge" if a.dry_run else "Merged"
        print(f"{verb2} {len(merged_files)} file(s) by key (deny rules/hooks union):")
        for p in merged_files:
            print(f"  ~ {p.relative_to(target)}")
    if skipped:
        print(f"Skipped {len(skipped)} existing file(s) (use --overwrite or --merge-settings only with user approval):")
        for p in skipped:
            print(f"  = {p.relative_to(target)}")


if __name__ == "__main__":
    main()
