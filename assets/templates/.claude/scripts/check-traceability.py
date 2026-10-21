#!/usr/bin/env python3
"""Spec traceability check: every REQ-ID defined in a feature's requirements.md must have a
Gherkin scenario and be covered by at least one task in tasks.md; every REQ-ID referenced from
tasks.md must actually be defined in requirements.md (catches typos/drift between the two files).

This only checks REQ-ID linkage between requirements.md/tasks.md - it does not (and, since the
project's STACK varies, cannot generically) check that a real test file exists for each one.
That's still `qa`'s job to confirm by reading actual test output before reporting phase 6 done.

Usage: check-traceability.py [--specs-dir docs/specs] [--feature <slug>]
Exit code 0 only if every feature checked has no gaps. Standard library only.
"""
import argparse
import re
import sys
from pathlib import Path

REQ_DEF = re.compile(r"^-\s*(REQ-\d+)\s*:", re.M)
REQ_SCENARIO_HEADER = re.compile(r"^###\s*(REQ-\d+)\s*$", re.M)
REQ_COVERS = re.compile(r"Covers:\s*(.+)$", re.M)
REQ_ID = re.compile(r"REQ-\d+")
SKIP_DIRS = {"_templates"}
failures = []


def check(ok: bool, msg: str) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        failures.append(msg)


def check_feature(feature_dir: Path) -> None:
    name = feature_dir.name
    req_path = feature_dir / "requirements.md"
    tasks_path = feature_dir / "tasks.md"
    if not req_path.is_file() or not tasks_path.is_file():
        print(f"INFO  {name}: skipping (requirements.md/tasks.md not written yet)")
        return

    req_text = req_path.read_text(encoding="utf-8")
    tasks_text = tasks_path.read_text(encoding="utf-8")

    defined = set(REQ_DEF.findall(req_text))
    if not defined:
        print(f"INFO  {name}: no REQ-IDs defined yet in requirements.md")
        return

    scenarios = set(REQ_SCENARIO_HEADER.findall(req_text))
    covered = set()
    for m in REQ_COVERS.finditer(tasks_text):
        covered |= set(REQ_ID.findall(m.group(1)))
    referenced_anywhere = set(REQ_ID.findall(tasks_text))

    for req in sorted(defined):
        check(req in scenarios, f"{name}: {req} has a Gherkin scenario in requirements.md")
        check(req in covered, f"{name}: {req} is covered by a task in tasks.md")

    for req in sorted((covered | referenced_anywhere) - defined):
        check(False, f"{name}: tasks.md references {req}, which is not defined in requirements.md")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs-dir", default="docs/specs")
    ap.add_argument("--feature", help="check only this feature slug instead of every feature found")
    args = ap.parse_args()

    specs_dir = Path(args.specs_dir)
    if not specs_dir.is_dir():
        sys.exit(f"{specs_dir} not found")

    if args.feature:
        feature_dirs = [specs_dir / args.feature]
    else:
        feature_dirs = sorted(p for p in specs_dir.iterdir() if p.is_dir() and p.name not in SKIP_DIRS)

    if not feature_dirs:
        print("INFO  no feature directories found - nothing to check")
        sys.exit(0)

    for feature_dir in feature_dirs:
        check_feature(feature_dir)

    print(f"\n{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
