# Project graph

A map of this project's **files and the relationships between them**, so you (or an agent) can find things and trace dependencies by asking the graph instead of grepping and opening files. It is built from the files themselves: no model, no network, no server, no extra setup - just `.claude/scripts/build-graph.py` (Python standard library).

## What is in it
- **Nodes** are project files: source, tests, specs, ADRs, docs, `Database/` design files, agents, skills, scripts, config. Each carries its kind, title, status, summary, sections, defined symbols and `REQ-ID`s.
- **Edges** are relationships between files, each tagged:
  - `EXTRACTED` - written in the files: `imports` (Python via `ast`, relative JS/TS imports), `links_to` (markdown links), `mentions` (a backticked path), `invokes` (a `/skill`), `covers` / `verifies` / `references_req` (a `REQ-ID` pointing at its `requirements.md`).
  - `INFERRED` - derived from a naming or layout convention: `derives_from` (the spec chain: requirements -> prd, design -> requirements, tasks -> design), `tests` (a test named after the source file it covers), `delegates_to` (an agent named in a prompt), a bare filename mention that matches exactly one file.
- A reference to a file that does not exist becomes a **`missing`** node: a broken link.
- **Communities** are a feature's spec files or a directory.
- Never indexed: `.env*`, keys, certificates, databases, lockfiles, binaries, `node_modules`/build output, and the graph's own outputs.

## Outputs (`docs/knowledge-graph/`, generated - never edit by hand)
| File | Purpose |
|---|---|
| `GRAPH_REPORT.md` | Read first: files by kind, most-connected files, communities, broken references, orphans |
| `graph.json` | The full graph (`schema_version`, nodes, links) that the queries read |
| `graph.html` | Full-screen interactive 3D view. Drag to orbit, scroll to zoom, hover to isolate a neighbourhood, click for a file's notes and relationships, `/` or `Ctrl/Cmd+K` to search. three.js and `3d-force-graph` (pinned versions) load from esm.sh, so viewing it needs network access; without it the page lists every file instead of going blank |

The outputs carry a content hash and no timestamp, so an unchanged project produces no diff.

## Using it
```
python .claude/scripts/build-graph.py                  # (re)build all three outputs
python .claude/scripts/build-graph.py check            # exit 1 when the outputs are stale
python .claude/scripts/build-graph.py query billing    # ranked files + neighbours for the terms
python .claude/scripts/build-graph.py explain docs/specs/billing/design.md
python .claude/scripts/build-graph.py path CLAUDE.md check-traceability.py
```
Exit codes: `0` answered, `3` ambiguous name (candidates listed), `4` no match / no graph built yet. Add `--title NAME` to set the 3D view's heading (default: the folder name).

## Keeping it in front of the agent
Three things, so it is used and current rather than just available:
1. The scaffold builds it once, so it exists in the first session.
2. A `SessionStart` hook (`.claude/hooks/graph-hook.py refresh`) rebuilds it when `check` says it is stale and puts one status line in the session context.
3. A `PreToolUse` hook on `Grep|Glob` (`graph-hook.py nudge`) adds a short reminder to ask the graph first - on the first search of a session, then every 4th. It is advisory: it never blocks or rewrites a search, and it fails open. It is not a guarantee the agent obeys; `CLAUDE.md` / `AGENTS.md` carry the same instruction in words.

## Who maintains it
The `knowledge-graph` agent rebuilds it after every phase that changes files; `/orchestrate` rebuilds it at the start of a feature. Any agent or person can run the commands above. `CLAUDE.md` / `AGENTS.md` tell agents to query the graph before grepping.

## Limits (so a missing edge isn't mistaken for "no dependency")
Only Python imports and relative JS/TS imports are resolved. Function calls, dynamic imports, path aliases, dependency injection and runtime wiring are not edges. `INFERRED` edges are leads to verify. When the graph has no answer, grep - and treat the gap as information, not proof.

## Domain language
The project's ubiquitous language lives in `docs/glossary.md` (owned by the `domain` agent). It is a document like any other: find a term with `build-graph.py query <term>`.
