#!/usr/bin/env python3
"""Retune an already-scaffolded project in place: change MODEL_PRIORITY and/or
COVERAGE_THRESHOLD after the initial scaffold, without touching anything else.

Usage:
  retune.py --target DIR [--model-priority cost|balanced|quality] [--coverage-threshold N]
            [--answers answers.json] [--dry-run]

At least one of --model-priority/--coverage-threshold is required. This is the companion script
`/amend-constitution` uses when the user wants model tiers or the coverage gate changed after
scaffold time: it edits only the specific lines that hold that value (agent `model:` frontmatter,
the "MODEL_PRIORITY for this project" mention in CLAUDE.md, the coverage number in
CLAUDE.md/AGENTS.md/ci.yml) - the same "never silently touch anything else" rule scaffold.py
follows for --merge-settings. Pass --answers to also update the stored answers.json so a later
verify_setup.py run checks against the new values instead of the stale ones.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scaffold import TIER_PRESETS  # noqa: E402

AGENT_ROLES = ["planner", "architect", "domain", "test", "qa", "implementer", "reviewer",
               "security", "devops-docs", "knowledge-graph", "debug", "designer"]


def retune_models(target: Path, priority: str, dry_run: bool) -> list[str]:
    tiers = TIER_PRESETS[priority]
    changed = []
    for role in AGENT_ROLES:
        p = target / ".claude" / "agents" / f"{role}.md"
        if not p.is_file():
            continue
        tier = tiers[role.upper().replace("-", "_")]
        text = p.read_text(encoding="utf-8")
        new_text, n = re.subn(r"(?m)^model: .*$", f"model: {tier}", text, count=1)
        if n == 0:
            sys.exit(f"no 'model:' line found in {p} - refusing to guess, fix manually")
        if new_text != text:
            changed.append(str(p))
            if not dry_run:
                p.write_text(new_text, encoding="utf-8", newline="\n")

    claude_md = target / "CLAUDE.md"
    if claude_md.is_file():
        text = claude_md.read_text(encoding="utf-8")
        new_text = re.sub(r"`(?:cost|balanced|quality)` for this project",
                           f"`{priority}` for this project", text)
        if new_text != text:
            changed.append(str(claude_md))
            if not dry_run:
                claude_md.write_text(new_text, encoding="utf-8", newline="\n")
    return changed


def retune_coverage(target: Path, threshold: str, dry_run: bool) -> list[str]:
    changed = []
    file_subs = {
        target / "CLAUDE.md": [(r"(Coverage threshold: `)[^`]*(`)", rf"\g<1>{threshold}\g<2>")],
        target / "AGENTS.md": [(r"(Coverage threshold: `)[^`]*(`)", rf"\g<1>{threshold}\g<2>")],
        target / ".github" / "workflows" / "ci.yml": [
            (r"(Coverage threshold \()[^)]*(%\))", rf"\g<1>{threshold}\g<2>"),
            (r"(fail under )\S*(%)", rf"\g<1>{threshold}\g<2>"),
        ],
    }
    for path, subs in file_subs.items():
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new_text = text
        for pattern, repl in subs:
            new_text = re.sub(pattern, repl, new_text)
        if new_text != text:
            changed.append(str(path))
            if not dry_run:
                path.write_text(new_text, encoding="utf-8", newline="\n")
    return changed


def retune_answers(answers_path: Path, priority: str | None, threshold: str | None, dry_run: bool) -> bool:
    if not answers_path.is_file():
        return False
    data = json.loads(answers_path.read_text(encoding="utf-8"))
    changed = False
    if priority is not None and data.get("MODEL_PRIORITY") != priority:
        data["MODEL_PRIORITY"] = priority
        changed = True
    if threshold is not None and str(data.get("COVERAGE_THRESHOLD")) != threshold:
        data["COVERAGE_THRESHOLD"] = threshold
        changed = True
    if changed and not dry_run:
        answers_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--model-priority", choices=sorted(TIER_PRESETS))
    ap.add_argument("--coverage-threshold")
    ap.add_argument("--answers", help="also update MODEL_PRIORITY/COVERAGE_THRESHOLD in this answers.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.model_priority and not a.coverage_threshold:
        sys.exit("nothing to do: pass --model-priority and/or --coverage-threshold")

    target = Path(a.target).resolve()
    changed: list[str] = []
    if a.model_priority:
        changed += retune_models(target, a.model_priority, a.dry_run)
    if a.coverage_threshold:
        changed += retune_coverage(target, a.coverage_threshold, a.dry_run)
    if a.answers:
        if retune_answers(Path(a.answers), a.model_priority, a.coverage_threshold, a.dry_run):
            changed.append(a.answers)

    deduped = list(dict.fromkeys(changed))  # CLAUDE.md can be touched by both passes above
    verb = "Would update" if a.dry_run else "Updated"
    print(f"{verb} {len(deduped)} file(s):")
    for p in deduped:
        print(f"  ~ {p}")
    if not deduped:
        print("Nothing changed - values already matched.")


if __name__ == "__main__":
    main()
