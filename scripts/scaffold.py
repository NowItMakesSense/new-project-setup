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
    "VCS_BRANCHING", "ENGINEERING_PRINCIPLES", "COMPLIANCE", "TEAM", "PYTHON_CMD", "EXTRA_DENY",
]
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
    return values


def render(text: str, values: dict, name: str) -> str:
    def sub(m):
        if m.group(1) not in values:
            sys.exit(f"Unknown template variable {m.group(0)} in {name}")
        return values[m.group(1)]
    return VAR.sub(sub, text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    values = load_answers(Path(a.answers))
    target = Path(a.target).resolve()
    created, skipped = [], []

    for src in sorted(p for p in TEMPLATES.rglob("*") if p.is_file()):
        rel = src.relative_to(TEMPLATES)
        if rel.as_posix().startswith(".github/") and values["_CI"] != "github-actions":
            continue
        is_tmpl = src.suffix == ".tmpl"
        dest = target / (rel.with_suffix("") if is_tmpl else rel)
        if dest.exists() and not a.overwrite:
            skipped.append(dest)
            continue
        if not a.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            text = src.read_text(encoding="utf-8")
            if is_tmpl:
                text = render(text, values, rel.as_posix())
            dest.write_text(text, encoding="utf-8", newline="\n")
        created.append(dest)

    verb = "Would create" if a.dry_run else "Created"
    print(f"{verb} {len(created)} file(s):")
    for p in created:
        print(f"  + {p.relative_to(target)}")
    if skipped:
        print(f"Skipped {len(skipped)} existing file(s) (use --overwrite only with user approval):")
        for p in skipped:
            print(f"  = {p.relative_to(target)}")


if __name__ == "__main__":
    main()
