# Knowledge graph

This project keeps a **domain knowledge graph** - entities, value objects, aggregates, bounded contexts and the relationships between them - separate from any application/business data.

## Where it lives
- Backed by the MCP memory server (`@modelcontextprotocol/server-memory`), configured as `mcpServers.knowledge-graph` in `.claude/settings.json` (requires Node.js/`npx` - this is why).
- Storage file: `docs/knowledge-graph/graph.jsonl` (git-committed, JSON Lines - one entity/relation per line). Safe to read directly; it holds only domain-model metadata, never credentials or production data.
- If Node.js/`npx` wasn't available when this project was scaffolded, there is no `mcpServers` entry and no `graph.jsonl`; see "Fallback" below.

## Who maintains it
The `knowledge-graph` subagent (`.claude/agents/knowledge-graph.md`) is the only agent that calls the memory-server tools (`read_graph`, `search_nodes`, `open_nodes`, `create_entities`, `create_relations`, `add_observations`, `delete_entities`, `delete_relations`, `delete_observations`). It collaborates with (and never contradicts) the `domain` agent, which identifies the concepts in prose during design; `knowledge-graph` persists and links them.

## Idempotency rule
Every run checks before it writes: read the current graph first, then only add what's missing or extend existing entities with new observations. Nodes/relations are never silently deleted - only on explicit user confirmation that something is wrong or obsolete.

## How it grows
- **New project:** seeded from `docs/specs/discovery.md` and `docs/glossary.md` after `/plan-grill`, then extended from each feature's approved `design.md` (phase 3).
- **Retrofit onto an existing codebase:** on the project's first `/orchestrate` run, if source code already exists but no graph does, the orchestrator asks `knowledge-graph` to analyze existing code/docs and propose an initial graph. The proposal is shown to the user for confirmation before anything is persisted.

## If you don't have the MCP tool connected
This README and `docs/glossary.md` are the human-readable views. For the full graph with relationships, connect an MCP client to the `knowledge-graph` server, or read `graph.jsonl` directly (plain JSON Lines).

## Fallback (no Node.js/npx)
Without Node, the graph cannot be MCP-backed. In that case `knowledge-graph` maintains `docs/knowledge-graph/graph.md` (plain markdown tables) instead, and `docs/glossary.md` stays the primary human-readable artifact. Install Node.js and re-run the scaffold with `--overwrite` on `.claude/settings.json` to upgrade later.

## Compatibility note
This setup depends on two Claude Code internals that can change between versions: the `mcp__knowledge-graph__<tool>` naming convention used in `.claude/agents/knowledge-graph.md`'s `tools:` allowlist, and `$CLAUDE_PROJECT_DIR` expanding inside `mcpServers.*.env` in `.claude/settings.json`. If `knowledge-graph` ever reports a tool it should have access to as unavailable, or the memory server can't find `MEMORY_FILE_PATH`, that's the likely cause - check both against your installed Claude Code version's current docs rather than assuming the graph itself is broken.
