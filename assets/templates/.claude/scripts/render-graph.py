#!/usr/bin/env python3
"""Render the domain knowledge graph as an interactive 3D HTML page.

Reads `docs/knowledge-graph/graph.jsonl` (the MCP memory server's storage: one JSON object per
line, `"type": "entity"` or `"type": "relation"`) or, in fallback mode, the "Entities" and
"Relations" markdown tables of `docs/knowledge-graph/graph.md`, and writes a single self-contained
`docs/knowledge-graph/graph.html`: a full-screen 3D explorer built from the sibling template
`graph-view.html` (data embedded inline; three.js and 3d-force-graph load from pinned esm.sh URLs,
so viewing it needs network access - without it the page lists the concepts instead). The HTML is a
generated view - never edit it by hand, re-run this script instead.

When the graph comes from `graph.jsonl`, the script also rewrites `graph.md` as a human-readable
markdown export of it (same "Entities"/"Relations" tables the fallback reads), so the two never drift.
In fallback mode (no `graph.jsonl`) `graph.md` is the source of truth and is left untouched.

If `docs-index.json` (written by index-docs.py) sits next to the graph, its documents are drawn too, as
`document` nodes linked to the concepts they mention (view only; the graph files are untouched).

Usage: render-graph.py [--graph-dir docs/knowledge-graph] [--out <path>]
Exit code 0 when the page was written (an empty graph still produces a page). Standard library only.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).with_name("graph-view.html")
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
SEPARATOR_ROW = re.compile(r"^\s*\|?\s*:?-{3,}")


def load_jsonl(path: Path) -> tuple[list, list]:
    entities, relations = [], []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            sys.exit(f"{path}:{n}: invalid JSON ({e})")
        if item.get("type") == "entity":
            entities.append({"name": item.get("name", ""), "entityType": item.get("entityType", ""),
                             "observations": list(item.get("observations", []))})
        elif item.get("type") == "relation":
            relations.append({"from": item.get("from", ""), "to": item.get("to", ""),
                              "relationType": item.get("relationType", "")})
    return entities, relations


def parse_tables(text: str) -> dict:
    """Map each markdown heading to the list of row dicts (lower-cased headers) in its tables."""
    tables, heading, header = {}, "", None
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            heading, header = line.strip("# ").strip().lower(), None
            continue
        m = TABLE_ROW.match(line)
        if not m:
            header = None
            continue
        if SEPARATOR_ROW.match(line):
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        tables.setdefault(heading, []).append(dict(zip(header, cells)))
    return tables


def pick(row: dict, *keys: str) -> str:
    for k in keys:
        for col, value in row.items():
            if k in col:
                return value
    return ""


def load_markdown(path: Path) -> tuple[list, list]:
    entities, relations = [], []
    for heading, rows in parse_tables(path.read_text(encoding="utf-8")).items():
        if "entit" in heading:
            for row in rows:
                obs = pick(row, "observ", "note", "descri")
                entities.append({"name": pick(row, "name", "entity"), "entityType": pick(row, "type", "kind"),
                                 "observations": [o.strip() for o in re.split(r"<br\s*/?>|;", obs) if o.strip()]})
        elif "relation" in heading:
            for row in rows:
                relations.append({"from": pick(row, "from", "source"), "to": pick(row, "to", "target"),
                                  "relationType": pick(row, "relation", "type", "label")})
    return entities, relations


def build_graph(entities: list, relations: list) -> dict:
    nodes = {e["name"]: {"id": e["name"], "type": e["entityType"] or "unknown",
                         "observations": e["observations"]} for e in entities if e["name"]}
    links = []
    for r in relations:
        if not r["from"] or not r["to"]:
            continue
        for end in (r["from"], r["to"]):
            # A relation pointing at an entity that was never created is still shown, flagged.
            nodes.setdefault(end, {"id": end, "type": "undeclared", "observations": []})
        links.append({"source": r["from"], "target": r["to"], "label": r["relationType"]})
    return {"nodes": list(nodes.values()), "links": links}


def add_documents(graph: dict, index_path: Path) -> int:
    """Overlay the document index (index-docs.py) on the view: one `document` node per file, linked by
    `mentions` to the domain concepts it names. View-only - graph.jsonl/graph.md never get these."""
    if not index_path.is_file():
        return 0
    try:
        docs = json.loads(index_path.read_text(encoding="utf-8")).get("docs", [])
    except (json.JSONDecodeError, OSError):
        return 0
    known = {n["id"] for n in graph["nodes"]}
    for d in docs:
        doc_id = f"doc:{d['path']}"
        obs = [f"{d['kind']}{' - ' + d['status'] if d.get('status') else ''}", d.get("summary", "")]
        graph["nodes"].append({"id": doc_id, "type": "document", "observations": [o for o in obs if o]})
        graph["links"] += [{"source": doc_id, "target": m, "label": "mentions"} for m in d.get("mentions", []) if m in known]
    return len(docs)


def render(graph: dict, title: str) -> str:
    if not TEMPLATE.is_file():
        sys.exit(f"{TEMPLATE} not found - it ships next to this script; re-run the scaffold to restore it")
    # The data sits in a JSON <script> block; "</" is escaped so an observation containing
    # "</script>" cannot close it ("<\/" is still valid JSON).
    data = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    return (TEMPLATE.read_text(encoding="utf-8")
            .replace("__TITLE__", html.escape(title))
            .replace("__DATA__", data))


def md_cell(text: str) -> str:
    # "|" would split the cell and a newline would end the row; "&#124;" still renders as "|".
    return " ".join(text.split()).replace("|", "&#124;")


def render_markdown(entities: list, relations: list) -> str:
    """The human-readable export of graph.jsonl. Deterministic (no timestamp), so an unchanged graph
    produces no diff, and readable back by load_markdown() should graph.jsonl ever go missing."""
    lines = ["# Domain knowledge graph (generated export)", "",
             "> Generated from `graph.jsonl`, the source of truth, by `.claude/scripts/render-graph.py` - "
             "never edit it by hand; it is rewritten every time the graph is rendered.", "",
             f"{len(entities)} entities, {len(relations)} relations", "",
             "## Entities", "", "| Name | Type | Observations |", "|---|---|---|"]
    lines += [f"| {md_cell(e['name'])} | {md_cell(e['entityType'])} | "
              f"{'<br>'.join(md_cell(o) for o in e['observations'])} |" for e in entities]
    lines += ["", "## Relations", "", "| From | Relation | To |", "|---|---|---|"]
    lines += [f"| {md_cell(r['from'])} | {md_cell(r['relationType'])} | {md_cell(r['to'])} |" for r in relations]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-dir", default="docs/knowledge-graph")
    ap.add_argument("--out", help="output file (default: <graph-dir>/graph.html)")
    ap.add_argument("--title", default="Domain knowledge graph", help="shown in the top bar; pass the project name")
    args = ap.parse_args()

    graph_dir = Path(args.graph_dir)
    jsonl, md = graph_dir / "graph.jsonl", graph_dir / "graph.md"
    if jsonl.is_file():
        entities, relations = load_jsonl(jsonl)
        # graph.md is only a generated export when graph.jsonl exists; in fallback mode it is the
        # source of truth and is never written here.
        md.write_text(render_markdown(entities, relations), encoding="utf-8", newline="\n")
        print(f"Wrote {md} (markdown export of {jsonl.name})")
    elif md.is_file():
        entities, relations = load_markdown(md)
    else:
        entities, relations = [], []
        print(f"INFO  neither {jsonl} nor {md} exists - writing an empty graph page")

    graph = build_graph(entities, relations)
    n_docs = add_documents(graph, graph_dir / "docs-index.json")
    out = Path(args.out) if args.out else graph_dir / "graph.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(graph, args.title), encoding="utf-8", newline="\n")
    undeclared = sum(1 for n in graph["nodes"] if n["type"] == "undeclared")
    docs_note = f", {n_docs} documents drawn" if n_docs else ""
    print(f"Wrote {out} ({len(graph['nodes']) - n_docs} entities, {len(graph['links'])} relations{docs_note})")
    if undeclared:
        print(f"WARN  {undeclared} node(s) appear only as a relation endpoint, with no entity declared")


if __name__ == "__main__":
    main()
