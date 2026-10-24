#!/usr/bin/env python3
"""Where is each feature, really? Reads docs/specs/<feature>/ and reports what already exists, what is
approved, task progress, the frontier of unblocked tasks, open blocking findings and the next phase -
so `/orchestrate` resumes from the files on disk instead of from memory or a guess.

The result is evidence, not a decision: the orchestrator shows it to the user and confirms before acting.

Usage: spec-state.py [--specs-dir docs/specs] [--feature <slug> | --spec <path-or-slug>] [--json]
  --spec accepts a feature slug, a directory, or a path to any file inside the feature's directory
  (e.g. docs/specs/billing/prd.md). Standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252

SKIP_DIRS = {"_templates"}
ARTIFACTS = ["prd.md", "requirements.md", "design.md", "tasks.md", "findings-ledger.md", "security-report.md", "retro.md"]
STATUS_LINE = re.compile(r"^\s*Status:\s*([A-Za-z-]+)", re.I | re.M)
TASK_SPLIT = re.compile(r"^(?=##\s*T-\d+)", re.M)
TASK_HEAD = re.compile(r"^##\s*(T-\d+)\s*:?\s*(.*)$", re.M)
TASK_STATUS = re.compile(r"^\s*-?\s*Status:\s*([A-Za-z-]+)", re.I | re.M)
TASK_ID = re.compile(r"T-\d+")
BLOCKED_BY = re.compile(r"Blocked by:\s*(.+)$", re.M)
PHASE_WORDS = re.compile(r"Phase:\s*(.+)$", re.I | re.M)


def header_status(path: Path) -> str:
    """Draft | Approved | Implemented from the file's first Status line ('' if absent/templated)."""
    if not path.is_file():
        return "missing"
    m = STATUS_LINE.search(path.read_text(encoding="utf-8"))
    word = (m.group(1).lower() if m else "")
    return {"draft": "draft", "approved": "approved", "implemented": "implemented"}.get(word, "draft")


def parse_tasks(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    tasks = []
    for sec in TASK_SPLIT.split(path.read_text(encoding="utf-8")):
        head = TASK_HEAD.match(sec)
        if not head:
            continue
        st = TASK_STATUS.search(sec)
        bb = BLOCKED_BY.search(sec)
        tasks.append({"id": head.group(1), "title": head.group(2).strip(),
                      "status": (st.group(1).lower() if st else "todo"),
                      "blocked_by": sorted(set(TASK_ID.findall(bb.group(1)))) if bb else []})
    return tasks


def blocking_findings(path: Path) -> int:
    """Open/Confirmed Critical/High rows in the findings ledger."""
    if not path.is_file():
        return 0
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0].startswith("f-") and cells[2] in ("critical", "high") and cells[5] in ("open", "confirmed"):
            n += 1
    return n


def feature_state(fdir: Path) -> dict:
    present = {a: (fdir / a).is_file() for a in ARTIFACTS}
    status = {a: header_status(fdir / a) for a in ARTIFACTS if present[a]}
    tasks = parse_tasks(fdir / "tasks.md")
    done = {t["id"] for t in tasks if t["status"] in ("done", "implemented")}
    frontier = [t["id"] for t in tasks if t["status"] in ("todo", "in-progress") and set(t["blocked_by"]) <= done]
    blocked = [t["id"] for t in tasks if t["status"] == "todo" and not set(t["blocked_by"]) <= done]
    blocking = blocking_findings(fdir / "findings-ledger.md")
    feature_phase = ""
    sp = fdir / "STATUS.md"
    if sp.is_file():
        m = PHASE_WORDS.search(sp.read_text(encoding="utf-8"))
        feature_phase = m.group(1).strip() if m else ""

    def ok(a):
        return status.get(a) in ("approved", "implemented")

    if re.search(r"released|reverted", feature_phase, re.I):
        phase, why = "done", f"feature STATUS.md says: {feature_phase}"
    elif not present["prd.md"] and not present["requirements.md"]:
        phase, why = "2 Requirements (start with /to-spec)", "no prd.md or requirements.md yet"
    elif not ok("prd.md") and present["prd.md"] and not present["requirements.md"]:
        phase, why = "2 Requirements (finish /to-spec)", "prd.md not approved"
    elif not ok("requirements.md"):
        phase, why = "2 Requirements", "requirements.md missing or not approved"
    elif not ok("design.md"):
        phase, why = "3 Architecture & domain", "design.md missing or not approved"
    elif not ok("tasks.md"):
        phase, why = "4 Tasks (/to-tickets)", "tasks.md missing or not approved"
    elif any(t["status"] != "done" for t in tasks):
        phase, why = "5 TDD loop", f"{sum(t['status'] == 'done' for t in tasks)}/{len(tasks)} tasks done"
    elif not present["findings-ledger.md"] or blocking:
        phase, why = "6 Review & QA", (f"{blocking} blocking Critical/High finding(s)" if blocking else "no findings ledger yet")
    elif not ok("security-report.md"):
        phase, why = "7 Security", "security-report.md missing or not approved"
    elif not present["retro.md"]:
        phase, why = "8 CI/CD & docs", "all gates passed; not released yet"
    else:
        phase, why = "done", "retro.md written"
    return {"feature": fdir.name, "artifacts": status, "missing": [a for a in ARTIFACTS if not present[a]],
            "tasks": {"total": len(tasks), "done": len(done), "frontier": frontier, "blocked": blocked},
            "blocking_findings": blocking, "feature_status_phase": feature_phase,
            "next_phase": phase, "why": why}


def resolve(specs_dir: Path, spec: str) -> Path | None:
    p = Path(spec)
    for cand in (specs_dir / spec, p):
        if cand.is_dir() and cand.resolve().parent == specs_dir.resolve():
            return cand
    if p.exists():
        for parent in [p.resolve()] + list(p.resolve().parents):
            if parent.parent == specs_dir.resolve():
                return parent
    return None


def show(s: dict) -> None:
    print(f"== {s['feature']}  ->  next: {s['next_phase']}  ({s['why']})")
    arts = ", ".join(f"{a}[{st}]" for a, st in s["artifacts"].items()) or "nothing yet"
    print(f"   artifacts: {arts}")
    t = s["tasks"]
    if t["total"]:
        print(f"   tasks: {t['done']}/{t['total']} done; frontier (ready now): {', '.join(t['frontier']) or 'none'}; "
              f"blocked: {', '.join(t['blocked']) or 'none'}")
    if s["blocking_findings"]:
        print(f"   blocking findings (Open/Confirmed Critical/High): {s['blocking_findings']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs-dir", default="docs/specs")
    ap.add_argument("--feature")
    ap.add_argument("--spec")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    specs_dir = Path(args.specs_dir)
    if not specs_dir.is_dir():
        sys.exit(f"{specs_dir} not found")
    if args.feature or args.spec:
        fdir = resolve(specs_dir, args.feature or args.spec)
        if fdir is None:
            sys.exit(f"No feature directory for {args.feature or args.spec!r} under {specs_dir}. "
                     "Known: " + (", ".join(sorted(p.name for p in specs_dir.iterdir() if p.is_dir() and p.name not in SKIP_DIRS)) or "none"))
        dirs = [fdir]
    else:
        dirs = sorted(p for p in specs_dir.iterdir() if p.is_dir() and p.name not in SKIP_DIRS)
    states = [feature_state(d) for d in dirs]
    discovery = (specs_dir / "discovery.md").is_file()
    if args.json:
        print(json.dumps({"discovery": discovery, "features": states}, indent=1))
        return
    print(f"discovery.md: {'present' if discovery else 'MISSING (run /plan-grill)'}")
    if not states:
        print("No features yet.")
    for s in states:
        show(s)


if __name__ == "__main__":
    main()
