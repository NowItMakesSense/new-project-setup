#!/usr/bin/env python3
"""Document index for the knowledge graph: a cheap map of every project document, so an agent looks
the answer up here first instead of grepping/reading every file.

Scans the project's markdown (docs/, Database/, README.md, CLAUDE.md, AGENTS.md) and writes, next to
the domain graph:
  docs/knowledge-graph/docs-index.json   machine-readable (path, kind, feature, title, status, summary,
                                         headings, REQ-IDs, local links, graph entities mentioned)
  docs/knowledge-graph/docs-index.md     the same as a table, grouped by feature - read this first
Both are generated: never edit them by hand, re-run this script. They carry a content hash per
document, not a timestamp, so an unchanged project produces no diff.

Usage:
  index-docs.py                       (re)write the index
  index-docs.py --find TERM [TERM..]  graph-first lookup: documents + domain entities matching the
                                      terms, ranked, with the heading to jump to. Writes nothing.
  index-docs.py --check               exit 1 if the index on disk is stale (for CI / before relying on it)
Standard library only.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True  # importing render-graph.py must not leave a __pycache__ in the project
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252

GRAPH_DIR = "docs/knowledge-graph"
ROOT_FILES = ["README.md", "CLAUDE.md", "AGENTS.md"]
SCAN_DIRS = ["docs", "Database"]
GENERATED = {"graph.md", "docs-index.md"}
SKIP_PARTS = {"_templates", "node_modules", ".git"}
HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
STATUS = re.compile(r"^\s*Status:\s*([^|\n]+)", re.I | re.M)
REQ_ID = re.compile(r"\bREQ-\d+\b")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
SPEC_KINDS = {"discovery", "prd", "requirements", "design", "tasks", "findings-ledger", "security-report",
              "retro", "STATUS", "overview"}


def load_graph_module():
    """Reuse render-graph.py's readers (graph.jsonl, or the graph.md fallback tables)."""
    path = Path(__file__).with_name("render-graph.py")
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("render_graph", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_entities(graph_dir: Path) -> list:
    mod = load_graph_module()
    jsonl, md = graph_dir / "graph.jsonl", graph_dir / "graph.md"
    if mod is None:
        return []
    if jsonl.is_file():
        return mod.load_jsonl(jsonl)[0]
    if md.is_file():
        return mod.load_markdown(md)[0]
    return []


def classify(rel: Path) -> tuple[str, str]:
    """(kind, feature) from the path alone - the layout is fixed by the scaffold."""
    parts = rel.parts
    if parts[0] == "Database":
        return "database", ""
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "specs":
        if len(parts) == 3:
            return ("spec-index" if parts[2].startswith("STATUS") or parts[2] == "README.md" else
                    ("discovery" if parts[2] == "discovery.md" else "spec"), "")
        stem = Path(parts[-1]).stem
        return (stem if stem in SPEC_KINDS else "spec"), parts[2]
    if len(parts) >= 2 and parts[0] == "docs" and parts[1] == "adr":
        return "adr", ""
    if rel.name in ROOT_FILES or rel.name == "glossary.md":
        return "project", ""
    return "doc", ""


def summarize(lines: list[str]) -> str:
    """First prose line after the title - skips headings, tables, quotes, fences and the Status line."""
    in_fence = False
    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not s or s[0] in "#|>-*<" or s.lower().startswith("status:"):
            continue
        return re.sub(r"\s+", " ", s)[:200]
    return ""


def index_doc(root: Path, path: Path, entities: list) -> dict:
    rel = path.relative_to(root)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    title, headings = "", []
    for line in lines:
        m = HEADING.match(line)
        if not m:
            continue
        if not title and len(m.group(1)) == 1:
            title = m.group(2)
        elif len(m.group(1)) >= 2:
            headings.append(m.group(2))
    kind, feature = classify(rel)
    status = STATUS.search(text)
    lowered = text.lower()
    mentions = sorted(e["name"] for e in entities
                      if len(e["name"]) >= 3 and re.search(r"(?<!\w)" + re.escape(e["name"].lower()) + r"(?!\w)", lowered))
    links = sorted({l for l in MD_LINK.findall(text) if not re.match(r"[a-z]+:", l) and not l.startswith("/")})
    return {
        "path": rel.as_posix(), "kind": kind, "feature": feature, "title": title or path.stem,
        "status": status.group(1).strip() if status else "",
        "summary": summarize(lines), "headings": headings[:40],
        "req_ids": sorted(set(REQ_ID.findall(text))), "links": links, "mentions": mentions,
        "hash": hashlib.sha1(text.encode("utf-8")).hexdigest()[:10],
    }


def collect(root: Path) -> list[Path]:
    found = [root / f for f in ROOT_FILES if (root / f).is_file()]
    for d in SCAN_DIRS:
        base = root / d
        if base.is_dir():
            found += [p for p in base.rglob("*.md")
                      if p.name not in GENERATED and not (SKIP_PARTS & set(p.relative_to(root).parts))]
    return sorted(set(found))


def build(root: Path, graph_dir: Path) -> dict:
    entities = load_entities(graph_dir)
    docs = [index_doc(root, p, entities) for p in collect(root)]
    return {"docs": docs, "entities": sorted(e["name"] for e in entities if e["name"])}


def md_cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "&#124;")


def render_markdown(index: dict) -> str:
    docs = index["docs"]
    out = ["# Documents index (generated)", "",
           "> Generated by `.claude/scripts/index-docs.py` - never edit by hand. **Look here first**: find the "
           "document (and heading) that answers your question, then read only that, instead of opening every file. "
           "Terms: `python .claude/scripts/index-docs.py --find <term>`.", "",
           f"{len(docs)} documents, {len(index['entities'])} domain entities in the graph", ""]
    groups: dict[str, list] = {}
    for d in docs:
        key = f"Feature `{d['feature']}`" if d["feature"] else {
            "discovery": "Project specs", "spec-index": "Project specs", "adr": "Decisions (ADRs)",
            "database": "Database", "project": "Project"}.get(d["kind"], "Other docs")
        groups.setdefault(key, []).append(d)
    for key in sorted(groups, key=lambda k: (k.startswith("Feature"), k)):
        out += [f"## {key}", "", "| Document | Kind | Status | Summary | REQ-IDs | Mentions |", "|---|---|---|---|---|---|"]
        for d in groups[key]:
            reqs = ", ".join(d["req_ids"][:6]) + (" ..." if len(d["req_ids"]) > 6 else "")
            ments = ", ".join(d["mentions"][:6]) + (" ..." if len(d["mentions"]) > 6 else "")
            out.append(f"| `{d['path']}` ({md_cell(d['title'])}) | {d['kind']} | {md_cell(d['status'])} | "
                       f"{md_cell(d['summary'])} | {reqs} | {md_cell(ments)} |")
        out.append("")
    return "\n".join(out)


def write_outputs(root: Path, graph_dir: Path, index: dict) -> tuple[str, str]:
    return (json.dumps(index, ensure_ascii=False, indent=1) + "\n", render_markdown(index))


def find(index: dict, entities: list, terms: list[str]) -> None:
    terms = [t.lower() for t in terms]
    hits = []
    for d in index["docs"]:
        score, why = 0, []
        for t in terms:
            for label, hay, w in (("path", d["path"], 3), ("title", d["title"], 4), ("req", " ".join(d["req_ids"]), 4),
                                  ("mentions", " ".join(d["mentions"]), 2), ("summary", d["summary"], 1)):
                if t in hay.lower():
                    score += w
                    why.append(label)
            for h in d["headings"]:
                if t in h.lower():
                    score += 3
                    why.append(f"section: {h}")
        if score:
            hits.append((score, d, why))
    ents = [e for e in entities if any(t in (e["name"] + " " + " ".join(e["observations"])).lower() for t in terms)]
    if ents:
        print("DOMAIN ENTITIES")
        for e in ents[:10]:
            print(f"  {e['name']} [{e['entityType']}]  {' | '.join(e['observations'])[:160]}")
    if hits:
        print("DOCUMENTS (best first)")
        for score, d, why in sorted(hits, key=lambda h: (-h[0], h[1]["path"]))[:15]:
            print(f"  {d['path']}  [{d['kind']}{', ' + d['status'] if d['status'] else ''}]  match: {', '.join(dict.fromkeys(why))}")
    if not hits and not ents:
        print("No match in the index. If the document is new, re-run this script without --find to refresh it; "
              "otherwise fall back to grep.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--graph-dir", default=GRAPH_DIR)
    ap.add_argument("--find", nargs="+", metavar="TERM")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    graph_dir = root / args.graph_dir
    index = build(root, graph_dir)
    j_path, m_path = graph_dir / "docs-index.json", graph_dir / "docs-index.md"

    if args.find:
        find(index, load_entities(graph_dir), args.find)
        return
    j_text, m_text = write_outputs(root, graph_dir, index)
    if args.check:
        stale = not (j_path.is_file() and m_path.is_file()
                     and j_path.read_text(encoding="utf-8") == j_text and m_path.read_text(encoding="utf-8") == m_text + "\n")
        print("STALE docs index - run: python .claude/scripts/index-docs.py" if stale else "PASS docs index is current")
        sys.exit(1 if stale else 0)
    graph_dir.mkdir(parents=True, exist_ok=True)
    j_path.write_text(j_text, encoding="utf-8", newline="\n")
    m_path.write_text(m_text + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {m_path} and {j_path.name} ({len(index['docs'])} documents)")


if __name__ == "__main__":
    main()
