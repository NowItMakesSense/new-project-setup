#!/usr/bin/env python3
"""Render the domain knowledge graph as an interactive 3D HTML page.

Reads `docs/knowledge-graph/graph.jsonl` (the MCP memory server's storage: one JSON object per
line, `"type": "entity"` or `"type": "relation"`) or, in fallback mode, the "Entities" and
"Relations" markdown tables of `docs/knowledge-graph/graph.md`, and writes a single self-contained
`docs/knowledge-graph/graph.html` (data embedded inline; the 3d-force-graph library is loaded from
a pinned CDN URL, so viewing it needs network access). The HTML is a generated view - never edit
it by hand, re-run this script instead.

Usage: render-graph.py [--graph-dir docs/knowledge-graph] [--out <path>]
Exit code 0 when the page was written (an empty graph still produces a page). Standard library only.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

LIB_URL = "https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js"
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


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --bg:#0b0f17; --panel:rgba(17,24,39,.92); --fg:#e5e7eb; --muted:#9ca3af; --line:#374151; --accent:#60a5fa; }
  html, body { margin:0; height:100%; background:var(--bg); color:var(--fg);
               font:14px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; overflow:hidden; }
  #graph { position:fixed; inset:0; }
  .panel { position:fixed; background:var(--panel); border:1px solid var(--line); border-radius:10px;
           padding:12px 14px; max-width:min(340px, calc(100vw - 32px)); box-sizing:border-box; }
  #top { top:16px; left:16px; }
  #top h1 { font-size:15px; margin:0 0 4px; }
  #top .meta { color:var(--muted); font-size:12px; margin-bottom:8px; }
  #search { width:100%; box-sizing:border-box; padding:6px 8px; border-radius:6px; border:1px solid var(--line);
            background:#0f172a; color:var(--fg); }
  #legend { margin-top:10px; display:flex; flex-wrap:wrap; gap:6px 12px; font-size:12px; }
  #legend span { display:inline-flex; align-items:center; gap:5px; cursor:pointer; user-select:none; }
  #legend span.off { opacity:.35; }
  #legend i { width:10px; height:10px; border-radius:50%; display:inline-block; }
  #info { right:16px; top:16px; max-height:calc(100vh - 32px); overflow:auto; }
  #info h2 { font-size:15px; margin:0 0 2px; }
  #info .type { color:var(--muted); font-size:12px; margin-bottom:8px; }
  #info h3 { font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); margin:10px 0 4px; }
  #info ul { margin:0; padding-left:18px; }
  #info a { color:var(--accent); cursor:pointer; }
  #empty { top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; }
  [hidden] { display:none !important; }
</style>
</head>
<body>
<div id="graph"></div>
<div id="top" class="panel">
  <h1>__TITLE__</h1>
  <div class="meta">__SUMMARY__ &middot; drag to rotate, scroll to zoom, click a node for details</div>
  <input id="search" list="names" placeholder="Find an entity...">
  <datalist id="names"></datalist>
  <div id="legend"></div>
</div>
<div id="info" class="panel" hidden></div>
<div id="empty" class="panel" hidden>The knowledge graph is empty - nothing to render yet.</div>
<script src="__LIB_URL__"></script>
<script>
const DATA = __DATA__;
const PALETTE = ["#60a5fa","#f472b6","#34d399","#fbbf24","#a78bfa","#f87171","#22d3ee","#a3e635","#fb923c","#e879f9"];
const types = [...new Set(DATA.nodes.map(n => n.type))].sort();
const color = t => t === "undeclared" ? "#6b7280" : PALETTE[types.filter(x => x !== "undeclared").indexOf(t) % PALETTE.length];
const hidden = new Set();
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const degree = {};
DATA.links.forEach(l => { degree[l.source] = (degree[l.source] || 0) + 1; degree[l.target] = (degree[l.target] || 0) + 1; });

if (!DATA.nodes.length) document.getElementById("empty").hidden = false;

const legend = document.getElementById("legend");
types.forEach(t => {
  const s = document.createElement("span");
  s.innerHTML = `<i style="background:${color(t)}"></i>${esc(t)}`;
  s.onclick = () => { hidden.has(t) ? hidden.delete(t) : hidden.add(t); s.classList.toggle("off"); refresh(); };
  legend.appendChild(s);
});
document.getElementById("names").innerHTML = DATA.nodes.map(n => `<option value="${esc(n.id)}">`).join("");

let selected = null;
const Graph = ForceGraph3D()(document.getElementById("graph"))
  .backgroundColor("#0b0f17")
  .graphData(DATA)
  .nodeLabel(n => `<b>${esc(n.id)}</b><br><small>${esc(n.type)}</small>`)
  .nodeColor(n => selected && n !== selected && !isNeighbor(n) ? "#374151" : color(n.type))
  .nodeVal(n => 2 + (degree[n.id] || 0) * 1.5)
  .nodeOpacity(0.95)
  .nodeVisibility(n => !hidden.has(n.type))
  .linkVisibility(l => !hidden.has(l.source.type) && !hidden.has(l.target.type))
  .linkLabel(l => esc(l.label))
  .linkColor(l => selected && (l.source === selected || l.target === selected) ? "#f9fafb" : "#4b5563")
  .linkWidth(l => selected && (l.source === selected || l.target === selected) ? 1.2 : 0.4)
  .linkDirectionalArrowLength(4)
  .linkDirectionalArrowRelPos(1)
  .linkDirectionalParticles(l => selected && (l.source === selected || l.target === selected) ? 3 : 0)
  .onNodeClick(focus)
  .onBackgroundClick(() => { selected = null; document.getElementById("info").hidden = true; refresh(); });

function isNeighbor(n) {
  return DATA.links.some(l => (l.source === selected && l.target === n) || (l.target === selected && l.source === n));
}
function refresh() {
  // Accessors read `selected`/`hidden` lazily; refresh() re-evaluates them for every node/link.
  Graph.refresh();
}
function focus(n) {
  selected = n;
  const d = 90, r = 1 + d / Math.hypot(n.x || 1, n.y || 1, n.z || 1);
  Graph.cameraPosition({x: (n.x || 1) * r, y: (n.y || 1) * r, z: (n.z || 1) * r}, n, 1200);
  const out = DATA.links.filter(l => l.source === n), inc = DATA.links.filter(l => l.target === n);
  const link = m => `<a data-id="${esc(m.id)}">${esc(m.id)}</a>`;
  const info = document.getElementById("info");
  info.innerHTML = `<h2>${esc(n.id)}</h2><div class="type">${esc(n.type)}</div>`
    + (n.observations.length ? `<h3>Observations</h3><ul>${n.observations.map(o => `<li>${esc(o)}</li>`).join("")}</ul>` : "")
    + (out.length ? `<h3>Outgoing</h3><ul>${out.map(l => `<li>${esc(l.label)} &rarr; ${link(l.target)}</li>`).join("")}</ul>` : "")
    + (inc.length ? `<h3>Incoming</h3><ul>${inc.map(l => `<li>${link(l.source)} ${esc(l.label)} &rarr;</li>`).join("")}</ul>` : "");
  info.querySelectorAll("a[data-id]").forEach(a => a.onclick = () => focus(DATA.nodes.find(x => x.id === a.dataset.id)));
  info.hidden = false;
  refresh();
}
document.getElementById("search").addEventListener("change", e => {
  const n = DATA.nodes.find(x => x.id.toLowerCase() === e.target.value.trim().toLowerCase());
  if (n) focus(n);
});
window.addEventListener("resize", () => Graph.width(innerWidth).height(innerHeight));
</script>
</body>
</html>
"""


def render(graph: dict, title: str, source: str) -> str:
    # "</" is escaped so an observation containing "</script>" cannot close the data block.
    data = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    summary = f"{len(graph['nodes'])} entities, {len(graph['links'])} relations, from {source}"
    return (PAGE.replace("__TITLE__", html.escape(title))
                .replace("__SUMMARY__", html.escape(summary))
                .replace("__LIB_URL__", LIB_URL)
                .replace("__DATA__", data))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-dir", default="docs/knowledge-graph")
    ap.add_argument("--out", help="output file (default: <graph-dir>/graph.html)")
    ap.add_argument("--title", default="Domain knowledge graph")
    args = ap.parse_args()

    graph_dir = Path(args.graph_dir)
    jsonl, md = graph_dir / "graph.jsonl", graph_dir / "graph.md"
    if jsonl.is_file():
        entities, relations = load_jsonl(jsonl)
        source = jsonl.name
    elif md.is_file():
        entities, relations = load_markdown(md)
        source = md.name
    else:
        entities, relations, source = [], [], "no graph file yet"
        print(f"INFO  neither {jsonl} nor {md} exists - writing an empty graph page")

    graph = build_graph(entities, relations)
    out = Path(args.out) if args.out else graph_dir / "graph.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(graph, args.title, source), encoding="utf-8", newline="\n")
    undeclared = sum(1 for n in graph["nodes"] if n["type"] == "undeclared")
    print(f"Wrote {out} ({len(graph['nodes'])} entities, {len(graph['links'])} relations)")
    if undeclared:
        print(f"WARN  {undeclared} node(s) appear only as a relation endpoint, with no entity declared")


if __name__ == "__main__":
    main()
