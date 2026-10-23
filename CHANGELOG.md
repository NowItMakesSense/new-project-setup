# Changelog

This is this skill's own changelog (not shipped to generated projects).

## 2026-10-23 (2)

**Database access control is now part of the generated design, not left implicit.** In a real project, a review of the database rules found no roles or privileges defined anywhere: nothing said which user the application connects as, who applies migrations, or what each component may do. The Docker Compose file an agent then wrote connected the API as the cluster superuser (`POSTGRES_USER`), because nothing in the scaffold asked for anything else.

- **New `Database/roles/` folder** (generated with the rest of `Database/`):
  - its `README.md` sets the convention: one file per role, plus a project-wide `privilege-matrix.md`;
  - it also carries the baseline every project starts from: bootstrap superuser for administration only; NOLOGIN owner plus a human-run migrator for DDL; a least-privilege runtime app role with no DDL and no migrations at startup; hardening (revoke PUBLIC, default privileges, fixed `search_path`); per-role timeouts and connection limits; TLS outside local dev; an explicit row-level-security decision; role scripts generated only as files, with passwords from the environment.
- **`Database/README.md`:** lists `roles/` and adds the non-negotiable that access control is part of the schema.
- **`architect`:** owns roles and the matrix, writes a new "Database access control" section in `design.md`, and reviews local-dev topology (Compose) against it.
- **`design.md` template:** gains that section. The threat-model section names the database threats to cover: compromised app process, runtime DDL, no TLS, long queries, and backups keeping deleted personal data.
- **`security` agent and `security-report.md`:** gain a "Database access control" check, done by static review only.
- **`docs/security-policy.md` (template) and `references/security-policy.md`:** new section "System database access control". It also states that `.env.example` is written by a human, because the guard's deny rules cover every `.env*` path, including the example.
- **`verify_setup.py`:** requires `Database/roles/README.md` when the project has a database.
- **Tests:** one new test checks that the baseline is generated, substituted and wired into the design template, the policy, the security report and both agents. The existing `Database/` test now covers `roles/`. The new test fails without the template changes. The suite has 65 tests, all passing.
- **Projects scaffolded before this change:** they don't get the folder automatically. Render `assets/templates/Database/roles/README.md.tmpl` into `Database/roles/README.md`, then copy the changed sections of the other templates listed above.

## 2026-10-23

**`render-graph.py` also writes `graph.md` as an export of `graph.jsonl`.** In a real project, the stale fallback `graph.md` kept looking like a second source of truth next to `graph.jsonl`. The user asked for it to be regenerated from the graph, but nothing in the scaffold could do that, so the agent wrote a one-off script that would leave the file stale again after the next graph change.

- **Export from `graph.jsonl`:** when `graph.jsonl` exists, every render now also rewrites `docs/knowledge-graph/graph.md`.
  - It has a generated-file header and the same Entities and Relations tables the fallback reader parses.
  - Observations are joined with `<br>`, and `|` is escaped as `&#124;`.
  - The output has no timestamp, so an unchanged graph produces no diff.
- **Fallback mode:** with no `graph.jsonl`, `graph.md` is the source of truth. The script still only reads it and never writes it.
- **Docs:** the generated `docs/knowledge-graph/README.md`, the `knowledge-graph` agent, `SKILL.md` and `README.md` describe the export. The agent is told never to write the export itself.
- **Tests:** two new tests. One checks that the export replaces a stale file, escapes pipes and newlines, is byte-identical on re-render, and round-trips through the fallback reader. The other checks that fallback mode never overwrites `graph.md`. The suite has 64 tests, all passing.

## 2026-10-22 (8)

**Fix: generated projects now get `docs/security-policy.md`.** Two generated files pointed at a security policy that was never generated. `docs/specs/_templates/requirements.md` said "see `security-policy.md`" and `Database/README.md` said "see `references/security-policy.md`", but that file only existed inside the skill's own `references/`. Found in a real project, where `planner` hit the dangling reference while writing a feature's requirements and had to remove it.

- New template `assets/templates/docs/security-policy.md.tmpl`, adapted from `references/security-policy.md` for the generated project. It records the project's `COMPLIANCE` regime.
- Both dangling references now point to `docs/security-policy.md`.
- `security` starts its review from the policy. `architect` uses it as the threat-model baseline. `CLAUDE.md`/`AGENTS.md` list it next to the test-strategy guide and the debugging protocol.
- `verify_setup.py` requires the file.
- Three new tests: the policy is generated with `COMPLIANCE` substituted; no generated `.md` references any `security-policy.md` other than `docs/security-policy.md`; the `security` agent cites it. The suite has 62 tests, all passing.
- Projects scaffolded before this fix don't get the file automatically. Render `assets/templates/docs/security-policy.md.tmpl` alone into `docs/` and fix the same two references. Re-running `scaffold.py` would also add every other file introduced since.

## 2026-10-22 (7)

**KG view: minimal controls in the bottom-right corner.** These changes came from reviewing the layout live with the user.

- **Types menu:** the menu gets `margin-bottom: 1rem`, so it sits 28px above the bottom edge, and the same 1rem comes off its `max-height`.
- **View controls:**
  - They are back in the bottom-right corner, on the same baseline as the Types menu, and the detail sheet stops above them again.
  - They are now three icons in a small glass pill. Each name appears as a quiet tooltip on hover (after a 350ms delay, and it leaves at once) or on keyboard focus; the last one is right-aligned so it stays on screen.
  - Keycaps are gone from the UI. L/R/C still work and are exposed through `aria-keyshortcuts`.
  - Auto-rotate's on state is now a subtle fill instead of the inverted white button.
- **Preview note:** a stale render seen in an earlier round turned out to be Chrome's heuristic cache on `python -m http.server`. The scratchpad preview server now sends `Cache-Control: no-store`. This affected only the preview; nothing shipped changed for it.
- **Verified live in Chrome:**
  - the tooltips on hover;
  - the sheet ending above the controls;
  - the legend and controls sharing a 28px baseline;
  - the CDP interaction checks and the 59 regression tests pass.

## 2026-10-22 (6)

**KG view: controls always on screen, and the Types menu ends on a whole row.** Changes requested after a second look at the layout in the user's browser.

- **View controls:** Hide/Show labels, Auto-rotate and Center moved from a bottom-centre pill into the top bar, next to the search, at the same 48px height. They now sit with the other global controls and can't fall below the visible area. As the window narrows, the bar sheds detail in a fixed order: keycaps (≤1500px), then the question sentence (≤1280px), then a narrower search (≤1000px), then the control names, leaving icons with an `aria-label` and a tooltip (≤900px). The controls themselves never go. With no bottom band left to reserve, the detail sheet now reaches the bottom edge.
- **Types menu:** the list now holds exactly five whole rows (`max-height: 184px`) with 10px below the last one, instead of a half-cut row pressed against the pane's bottom edge. The scroll thumb and the edge fade signal that there's more.
- **Verified live in Chrome** (claude-in-chrome MCP) at 1370×637 and 500×637:
  - scrolling the menu to its last kind;
  - the sheet down to the bottom edge;
  - icon-only controls in the top bar on a phone;
  - no console errors.
- `inspect.mjs --app --allow glass` reports 0 FAIL and 1 WARN, `hero-void`. The headless capture lands while the page still shows "Loading the 3D view…", before the canvas has drawn, and with the controls no longer at the bottom, the lower half of that frame is empty stage. The live render fills it. The CDP interaction checks and the 59 tests pass.

## 2026-10-22 (5)

**KG view: a compact Types menu and explicit view controls**, from reviewing the glass layout in the user's own browser.

- **Types menu:** the row list now stops at about 5.5 rows (`max-height: 200px`) and scrolls inside the glass pane, and the half-visible row signals that there's more. Before, it grew to the window height and got cut off on short screens. Below 1100px it sits above the toolbar instead of beneath it.
- **Toolbar:** now centred at the bottom, with an icon, an explicit name and a keycap on every control.
  - **Hide labels / Show labels** (`L`): an action whose name says what it will do, with a struck icon once labels are off.
  - **Auto-rotate** (`R`): a real toggle.
  - **Center** (`C`, and `F` as before).
  - On phones the keycaps drop, and below 480px only the icons remain.
- **Auto-rotate under reduced motion:** the control stays available even with `prefers-reduced-motion` (for example, Windows animation effects off), just slower (0.2 instead of 0.5). Hiding it made the control look missing, and rotation only ever starts on an explicit click.
- **Fix:** the labels-off icon toggles the SVG `hidden` attribute with `toggleAttribute`, because SVG elements have no `.hidden` property.
- **Verified live in Chrome** (claude-in-chrome MCP), by mouse and with the L/R/C shortcuts:
  - scrolling the Types menu to its last kind, including the top fade;
  - Hide/Show labels, Auto-rotate on/off and Center;
  - the 500px layout.
- `inspect.mjs --app --allow glass` reports 0 FAIL / 0 WARN, and the CDP interaction script passes (its Labels and reduced-motion checks were updated for the new behaviour).

## 2026-10-22 (4)

**The KG view goes glass, and glass becomes a standard material in `frontend-craft`.** Asked for: a better search field, a transparent Types menu whose scrollbar stopped breaking the layout, and a modern glass look applied consistently to every component.

- **The rule, researched in the installed skills:**
  - taste-skill bans glass on app screens (`glass` is a FAIL in `inspect.mjs`).
  - apple-design (§12, materials and depth) prescribes it for chrome floating over live content: weights that encode hierarchy, a light edge, never glass on glass, vibrancy, scroll-edge fades, and a reduced-transparency fallback.
  - The prototype skill's picker gives a concrete dark-glass recipe.
  - `frontend-craft` now settles the conflict with a **Glass material** section in `references/materials-type.md`. Glass is allowed only for chrome over live content (a canvas, map, media or 3D scene) when `design.md` chooses it, never as cards on an ordinary dashboard and never glass on glass.
  - The section defines three weights (thin/regular/thick, with fill and backdrop values), one edge, fills rather than blur inside panes, the `-webkit-` twin, solid fallbacks, the cost rules (never animate `backdrop-filter`; no blur on a full-screen scrim or on moving labels) and how to scroll inside glass.
  - The short rules, the banned tables, the review checklist and the `frontend` agent all point to it, and `inspect.mjs --allow glass` is the documented way to measure an approved glass screen.
- **KG view:**
  - **Stage:** the graph now fills the whole viewport. A transparent WebGL canvas sits over a faint fixed ambient light (two blurred colour fields, plain fills rather than gradients, never animated), so the glass has something to refract.
  - **Top:** two floating islands. One holds the title with the question sentence and the undeclared pill. The other is a 48px thin-glass **search pill** with an icon, placeholder and a `Ctrl K` / `⌘ K` keycap that matches the platform.
  - **Command palette:** thick glass, still opening with no animation because it's keyboard-driven. It has a 52px input well with an `Esc` keycap, a results header with the match count ("8 of 12"), names with the typed part in `<mark>` (built from text nodes), a selected row as a white-alpha fill, and a hint footer.
  - **Types menu:** regular glass with a header (total, plus "Show all" once a kind is hidden). Its rows scroll in their own container with a thin overlay thumb inside the radius, `scrollbar-gutter: stable` and edge fades, so counts no longer shift and the native scrollbar no longer cuts the corner. The same treatment applies to the sheet body, the palette results and the fallback list.
  - **Detail sheet:** regular glass, sticky head, observations as one inset group. Opening it shifts the camera's view offset with the sheet (same 240/180ms ease-out) so the selected concept centres in the free space: left of the sheet on desktop, above it on a phone.
  - **Other components:**
    - The toolbar is a regular-glass pill, compact and centred on phones (it used to stretch full width).
    - 3D labels are semi-transparent chips with the same edge but no per-label blur.
    - `fit()` frames the band the floating panes leave free.
  - **New loading state:** a quiet glass status ("Loading the 3D view of 23 concepts…") replaces the blank screen while the engine loads; the taste-skill inspector caught that blank.
  - **Fallbacks:** without `backdrop-filter`, with reduced transparency, or with more contrast, every weight becomes a solid surface. Reduced motion is unchanged.
- **Verified:**
  - Live in Chrome through the claude-in-chrome MCP at 1370×637, 1370×409 (where the Types menu scrolls) and 500×637:
    - the palette: typing, highlight, arrow keys, Enter;
    - the sheet and its view-offset centring on desktop and on a phone;
    - hiding two kinds and then "Show all";
    - the legend scroll thumb and its fades;
    - the empty state and the 1,500-node graph;
    - no console errors.
  - `inspect.mjs --app --allow glass` reports 0 FAIL / 0 WARN.
  - The real-input CDP script passes all 16 checks.
  - The regression suite gained two tests (the template's glass material, fallbacks, prefixed twins and scroll treatment; `frontend-craft` documenting the material).

## 2026-10-22 (3)

**Bug fix: the KG view greyed out kinds that carry a qualifier.** Found re-rendering Deckloom's graph: its agent records kinds like `Value Object (imutável)`, `Entity (aggregate root)` and `Actor / Entity (aggregate root)`, and `graph-view.html`'s `kindKey` only matched the bare word, so 13 of 16 concepts fell through to neutral grey and no aggregate got the accent hue.

- `kindKey` now treats any kind mentioning "aggregate" as an aggregate, drops parenthetical notes, and keeps the part after the last `/`. Legend labels still show the project's own wording.
- `test_scaffold.py` gained `test_graph_view_maps_qualified_kinds_to_ddd_hues`, which runs the template's own `kindKey` in Node (skipped when Node isn't installed). 57 tests pass.

## 2026-10-22 (2)

**A front-end team for projects with a UI, and the knowledge-graph view rebuilt with it.** The first `graph.html` looked generic (stock spheres, floating boxes, hover-only labels), and the cause was general: nothing in a generated project carried design-engineering taste past the UX `designer`. Both are now built on two MIT-licensed skill collections - Emil Kowalski's skills (motion, polish, worst-case data, Apple's fluid-interface principles) and Leonxlnx's taste-skill (art direction, app-screen rules from measured product screens, a real-browser inspector).

- **New `frontend-craft` project skill** (only when `HAS_UI` is yes): a short `SKILL.md` plus six references (`art-direction`, `app-screens`, `materials-type`, `motion`, `worst-case`, `review`), distilled in this project's own words with credits. It is self-contained, so teammates don't need a global install; when the original skills are installed globally it defers to them, including taste-skill's `draw.mjs` (deals a direction/app style) and `inspect.mjs` (measures the page in headless Chrome at 1440/768/390).
- **Two new agents, one upgraded** (all gated on `HAS_UI`, all preloading `frontend-craft` through the subagent `skills:` frontmatter - a listed skill that isn't installed is skipped by Claude Code, not an error):
  - `designer` now also owns the art direction in `design.md` → UX: screen kind and its one question, direction/style and "face", tokens, a motion spec table, worst-case states, and any deliberate house-rule exception with its reason.
  - `frontend` builds tasks marked `Owner: frontend` in phase 5, under the same Iron Law as `implementer`, and renders the worst-case fixtures (plus `inspect.mjs` when available) before reporting done.
  - `ui-reviewer` reviews the rendered UI in phase 6 and logs **Before | After | Why** findings in the shared ledger with the usual Open/Confirmed/Retracted flow; Write is limited to that ledger.
- **Routing:** `tasks.md` tasks carry `- Owner: implementer | frontend` (set by `planner`/`spec-writer`); the orchestrator routes phase 5 by owner and adds `ui-reviewer` to phase 6 when any task had `Owner: frontend`. The `design.md` template's UX section lists the new art-direction fields.
- **Tiers:** `FRONTEND`/`UI_REVIEWER` are in `TIER_PRESETS` (cost sonnet/sonnet, balanced sonnet/opus, quality opus/opus); `retune.py` covers both. `verify_setup.py` requires the three agents and the skill with its six references when `HAS_UI=yes`, and checks each UI agent preloads `frontend-craft`.
- **KG view rebuilt** as an app screen, using taste-skill's dealt style `true-black-flat` (seed 331266591) with a cool near-black ground as its face:
  - The page now lives in a template, `.claude/scripts/graph-view.html`, which `render-graph.py` fills. The data moved into a `<script type="application/json">` block, with `</` escaped.
  - **The stage:** a full-viewport canvas whose top bar answers the screen's question ("23 concepts in 3 bounded contexts · 28 relations"). The four DDD kinds that carry the model get the only hues; bounded contexts are drawn as rings, other kinds are neutral, and undeclared endpoints are grey wireframes.
  - **Glow:** sits only on the data marks, as an additive halo texture rather than a bloom pass. This is the one deliberate exception to taste's "no glows" app rule.
  - **Labels:** HTML (CSS2D) in Inter, shown only on hubs, the selection and the hover, with a collision pass.
  - **Interactions:**
    - Hover isolates a concept's neighbourhood.
    - Clicking flies the camera (700ms ease-in-out, interruptible, starting from where the camera is) and opens a detail sheet (in 240ms / out 180ms, ease-out, CSS transitions).
    - `/` and `Ctrl/⌘+K` open a command palette with no animation, since it's keyboard-driven. Esc closes the palette, then the sheet; F fits the view.
    - Legend rows hide a kind; the toolbar toggles labels and auto-rotate.
  - **Other states and modes:** reduced motion, higher contrast, a designed empty state, and an offline fallback that lists every concept.
  - **Libraries:** pinned to three 0.186.1 and 3d-force-graph 1.80.1 (with three-forcegraph 1.43.6 and three-render-objects 1.43.0) via esm.sh `?external=three`, so the page loads exactly one three.js instance. jsDelivr's `+esm` builds mixed three r164/r168/r185, so they weren't usable.
  - `knowledge-graph` now passes `--title "{{PROJECT_NAME}}"`.
- **Two library problems found and worked around while testing:**
  - 3d-force-graph's node drag-end handler calls an OrbitControls internal that throws on a plain click with three r186, so node dragging is off. It isn't needed for exploring.
  - The library keeps hit-testing its last pointer position after the pointer moves onto an overlay, which left the hover stuck. Hover now only counts while the pointer is over the canvas.
- **Verified:**
  - 56 regression tests pass. The new tests cover the UI team gating, verify with `HAS_UI=yes`, a missing UI agent, tiers per preset, retune, task routing, the escaped data block parsed back as JSON, exact version pins, and `--title` escaping.
  - taste-skill's `inspect.mjs --app` reports 0 FAIL / 0 WARN on a 23-concept fixture. Two earlier rounds fixed a `text-shadow` FAIL (now a scrim behind labels) and too-small label text.
  - A real-input CDP script covering hover, click, relation navigation, Esc, `/`, typing, arrow keys, Enter, Ctrl+K, legend, Rotate, Labels and F reported no page errors. It also checked reduced motion and the offline fallback (esm.sh blocked).
  - Screenshots were reviewed for the empty, single, long-name/HTML-injection and 1,500-node fixtures.
- **Not verified:** a hands-on session in a regular browser. The Claude in Chrome extension wasn't reachable, so all browser checks ran in headless Chrome.

## 2026-10-22

**The knowledge graph now has an interactive 3D view.** New `.claude/scripts/render-graph.py`, generated into every project, turns the graph into `docs/knowledge-graph/graph.html`: entities as spheres coloured by `entityType` and sized by degree, relations as labelled directional arrows, a search box, a clickable legend that hides a type, and a side panel listing the selected entity's observations and its incoming/outgoing relations (click a neighbour to jump to it).

- Reads `graph.jsonl` (the MCP memory server's format) or, in fallback mode, the "Entities"/"Relations" tables of `graph.md`, so both setups get the same view. Standard library only, like the other generated scripts.
- Self-contained except for the rendering library: the data is embedded inline (with `</` escaped so an observation can't close the script block), and `3d-force-graph` loads from a pinned unpkg URL - viewing needs network access.
- Relation endpoints with no declared entity are drawn grey as `undeclared` and reported with a `WARN` line, so a missing `create_entities` call is visible instead of silently dropped.
- `knowledge-graph` re-runs the script after every graph change (its `tools:` gained `Bash` for this; the DB-guard hook still covers every Bash call). `verify_setup.py` checks the script exists and renders the fresh scaffold (into a temp dir, never into the project); `test_scaffold.py` gained 3 tests (JSONL input incl. the script-injection case and the undeclared warning, markdown fallback, agent wiring).
- Not verified: an actual browser render. The page's inline JS passes `node --check`, but it was not opened in a browser during this change.

## 2026-10-21 (7)

**Bug fix: the knowledge-graph MCP server was written to a file Claude Code never reads.** Found while bootstrapping a real project (Deckloom): the `knowledge-graph` agent fell back to markdown, and the previous "unverified" note in README's known-limits turned out to be hiding an actual defect, not just an unknown.

- **`mcpServers` moved from `.claude/settings.json` to a new `.mcp.json` at the repo root.** Claude Code reads project-scoped MCP server definitions **only** from `.mcp.json`; `settings.json` supports `enabledMcpServers`/`disabledMcpServers` toggles but not server definitions. The old placement meant the server was never registered at all - `claude mcp list` didn't list it, no approval was ever prompted, and no `mcp__knowledge-graph__*` tools existed, in every project this skill has scaffolded with `NPX_CMD` set. Node.js/`npx` was never the cause (the previously-suspected explanation, which the generated agent instructions actively suggested).
- **`MEMORY_FILE_PATH` is now a literal absolute path**, resolved from `--target` at scaffold time, because it cannot be made portable. Two compounding reasons, both verified by running the server directly rather than reasoned about: `@modelcontextprotocol/server-memory` resolves a *relative* path against **its own module directory in the npx cache** (writes fail with `ENOENT` on a lock file under the package's `dist/`, which is exactly how this surfaced), and Claude Code substitutes `$CLAUDE_PROJECT_DIR` into hook *commands* but does **not** export it into an MCP server's environment, so every variable form expands to nothing there. Worth recording the wrong turn: the first attempt at this fix used `${CLAUDE_PROJECT_DIR:-.}`, which made `claude mcp list`'s "Missing environment variables" warning disappear while silently producing a relative `.` path - a strictly worse failure than the warning it silenced. The trade-off accepted instead: a committed `.mcp.json` carries one machine's path, so a teammate on a different path must edit that line (`verify_setup.py` warns when the path's parent doesn't exist), or register the server at user scope instead.
- **`--merge-settings` now also merges `.mcp.json`** (new `merge_mcp_json`), adding only servers the project doesn't already declare and never overwriting an existing entry - so a retrofit can't clobber a user's own MCP servers. `merge_settings` no longer merges `mcpServers` into settings.json; a legacy dead block there is preserved untouched rather than extended.
- **`verify_setup.py` checks `.mcp.json`** (existence when `NPX_CMD` is set, server well-formedness, and that the brace-expansion form is used), and **warns** when it finds a legacy `mcpServers` key still in `.claude/settings.json`.
- **Generated `knowledge-graph` agent instructions now say how to diagnose a missing MCP tool** instead of pointing at Node/`npx` as the presumed cause: check `claude mcp list` (`pending approval` vs. absent entirely), check the brace syntax, and verify `npx` before blaming it. This defect survived as long as it did partly because the agent's own fallback text told it the wrong answer.
- Documented in the generated `docs/knowledge-graph/README.md`, `references/security-policy.md`, `SKILL.md`'s generated-files table and README that **a project-scoped server requires a one-time approval** before its tools exist - so the first knowledge-graph delegation in a fresh project legitimately lands on the markdown fallback until someone approves it.
- **Generated `.claude/settings.json` now pre-approves the server** with `"enabledMcpjsonServers": ["knowledge-graph"]` (omitted when `NPX_CMD` is `none`), so a fresh project doesn't need a manual per-server approval at all. `verify_setup.py` checks it. Two limits worth knowing: the key is **ignored in an untrusted folder**, so each user still has to accept the workspace-trust dialog on first run in a clone; and MCP connections are established when the session starts, so a server added to a *running* session is only picked up after restarting Claude Code - approval alone doesn't attach the tools mid-session.

## 2026-10-21 (6)

Two small infrastructure fixes, both motivated by things observed directly in this session's own work rather than external comparison:

- **CI now runs on Windows too, not just Ubuntu**: `.github/workflows/test.yml`'s `test` job gained a `strategy.matrix` over `[ubuntu-latest, windows-latest]`. `block-db-access.py`'s pattern set has real Windows-specific logic (`get-content`/`gci` PowerShell matching, `\\` path separators in `SECRET_PATH`) that until now was only ever exercised locally on a Windows dev machine, never in CI - a regression there could have shipped unnoticed.
- **Added `.gitattributes`** (`* text=auto eol=lf`): every git command this session printed an "LF will be replaced by CRLF" warning, because nothing in the repo normalized line endings - they depended entirely on each contributor's local `core.autocrlf` setting. Now the repository's own text files stay LF on checkout regardless of that local setting.

## 2026-10-21 (5)

Measured this skill against Anthropic's own official skill-authoring conventions (the `skill-creator`/`skill-development` meta-skills, installed locally as a plugin) and fixed every gap found:

- **Generated `orchestrate` skill split via progressive disclosure**: its `SKILL.md.tmpl` body was 2,398 words with zero bundled resources - exactly the guide's named "Mistake 2: Too Much in SKILL.md". Moved the four least-frequently-needed procedures (parallel implementation, context hygiene, archiving, the revert checklist) into a new `references/` subfolder under `.claude/skills/orchestrate/`, leaving a short pointer stub (same heading, 1-2 sentences, "full procedure: `references/<file>.md`") in place of each in `SKILL.md.tmpl`. Body is now 1,974 words - inside the guide's 1,500-2,000 "ideal" band. Added a new `## Additional Resources` section listing all four reference files. `verify_setup.py` checks all four exist; `test_scaffold.py` gained a test.
- **Second-person phrasing removed from generated skills**: `orchestrate/SKILL.md.tmpl` had 16 "you"/"your" instances (e.g. "You coordinate..."), `plan-grill/SKILL.md` had 1 - both now 0, rewritten in imperative/neutral voice to match this skill's own top-level `SKILL.md` (already compliant) and the guide's explicit style rule.
- **"Additional Resources" section added to this skill's own `SKILL.md`**: replaced the single unlabeled `References: references/workflow.md, ...` line with a proper bulleted list, one line per file, naming what each covers - matching the guide's canonical format (an unreferenced/under-described bundled file is its named "Mistake 4").
- **New `examples/answers.example.json`**: a fully filled-in, realistic 22-key `answers.json` (a small team web-app scenario) to adapt instead of building one from scratch - the guide's third resource tier ("copy-and-adapt starting points"), which this skill had none of. Referenced from `SKILL.md`'s Step 1 and the new Additional Resources section; used directly in this round's own scaffold+verify smoke test.

Deliberately not changed: the 5 skills' frontmatter `description` fields already carry concrete, quoted trigger phrases (the substantive requirement) even though they don't literally open with the guide's "This skill should be used when..." template - rewording live trigger text everywhere for template-letter conformity risked changing real auto-trigger behavior for a cosmetic gain, so left alone.

## 2026-10-21 (4)

Two more gaps, specifically about using this for both small and large projects:

- **Change-size tiering (Trivial vs Standard)**: `/orchestrate`'s Start now asks the user to classify each change before choosing a path. Trivial (typo, dependency bump, one-line fix, no new `REQ-ID` needed) skips the whole spec-directory ceremony - no `discovery.md`/`requirements.md`/`design.md`/`tasks.md` - and goes straight to a regression test, a quick `reviewer` pass, and abbreviated security/docs passes, logged as one row in the index instead of its own feature directory. Standard is the unabridged 8-phase workflow, unchanged. The DB guard and every agent's non-negotiable rules apply identically regardless of tier - this only trims which *spec artifacts* get produced, never a guard rail or a human gate. New "Change size" section in `orchestrate/SKILL.md.tmpl`; "Phases"/"Done criteria" now say explicitly they describe the Standard path.
- **`docs/specs/STATUS.md` archiving**: new `docs/specs/STATUS-archive.md`, generated alongside it. The moment a feature's row reaches `Released` or `Reverted`, it moves out of the live index into the archive (newest at the top) instead of accumulating there forever - a long-lived, large project's index stays small for every orchestrator session's first read, instead of growing across years of shipped features. Only the index row moves; the feature's own `docs/specs/<feature>/STATUS.md`/`retro.md`/specs/ADRs never do. New "Archiving" section in `orchestrate/SKILL.md.tmpl`; `verify_setup.py` checks the archive file exists; `test_scaffold.py` gained 2 tests.

## 2026-10-21 (3)

Five more gaps found comparing against BMAD-METHOD/Spec Kit/moai-adk again, all implemented:

- **Requirement traceability is now verified, not just asserted**: new `.claude/scripts/check-traceability.py`, generated into every project. Checks that every `REQ-ID` defined in a feature's `requirements.md` has a Gherkin scenario and is covered by a task in `tasks.md`, and flags any `tasks.md` reference to a `REQ-ID` that was never defined (typo/drift). Stack-agnostic by design (only parses the two markdown files, never the real test files, since `STACK` varies) - `qa` runs it before the phase 6 gate (`qa.md.tmpl`), `spec-writer` self-checks after writing `tasks.md`, and it's wired into `ci.yml.tmpl` as a real step. `verify_setup.py` checks it exists and runs clean against a fresh scaffold; `test_scaffold.py` gained 3 tests (clean scaffold, a constructed gap+orphan fixture, a constructed fully-linked fixture).
- **Context-hygiene guidance for the orchestrator session**: `orchestrate/SKILL.md` gained a "Context hygiene" section making explicit what was already true structurally (every phase persists its output to disk, so a fresh session can always resume safely) - recommends starting a new session between features always, and mid-feature once the transcript has gotten long enough that re-reading `STATUS.md` would recover the same state a fresh session gets for free. This is the BMAD-METHOD-style "context engineering" idea, applied to the one session (the orchestrator) that previously had no such guidance - subagent delegations already had scoped context by design.
- **Agents are told to treat external content as data, not instructions**: a new non-negotiable rule, worded identically, added to all 12 agent templates, plus a matching prime directive in `CLAUDE.md.tmpl`/`AGENTS.md.tmpl` and a new section in `security-policy.md`. Covers a prompt-injection surface (a fetched page, a dependency README, scraped search results) that's distinct from the DB-guard's threat model and wasn't addressed anywhere before. `verify_setup.py` checks every agent carries it; `test_scaffold.py` gained a test.
- **Parallel implementation via git worktree isolation, documented as opt-in**: `orchestrate/SKILL.md` gained a "Parallel implementation (optional, phase 5 only)" section - for tasks confirmed independent, delegate with `isolation: "worktree"` instead of relying on "don't touch the same file" as a bare convention; merging a worktree branch back gets the same human confirmation as any other outward-facing action. Falls back to sequential the moment independence turns out to be wrong.
- **Monorepo/multi-service limitation made explicit instead of silently assumed**: `references/interview.md`'s `PROJECT_TYPE` row and the README's "Limits, honestly" now say plainly that one scaffold run assumes one deployable unit (one `CLAUDE.md`/`Database/`), and the interview is told to ask the user whether to scaffold once per service or once at the root rather than guessing. No multi-package overlay was built - this is the "document the limit now, build the real thing only if demand shows up" choice, same as the security-single-agent limit earlier.

Also fixed in passing: `orchestrate/SKILL.md` and `spec-writer/SKILL.md` had to become `.md.tmpl` (were plain `.md`) once they started referencing `{{PYTHON_CMD}}` for the traceability-check command - caught by this repo's own `verify_setup.py` "no unresolved template variables" check before it shipped.

## 2026-10-21 (2)

Addressed five gaps found in a self-review comparing this skill against similar tooling:

- **`scripts/retune.py`**: a new companion script for changing `MODEL_PRIORITY` or `COVERAGE_THRESHOLD` on an already-scaffolded project without hand-editing generated files or re-scaffolding. It surgically edits only the lines that hold the old value (each agent's `model:` frontmatter, the `MODEL_PRIORITY` mention in `CLAUDE.md`, the coverage number in `CLAUDE.md`/`AGENTS.md`/`ci.yml`), optionally updates a kept `answers.json` too, and supports `--dry-run` - same discipline as `scaffold.py --merge-settings`. `/amend-constitution` now documents this as the supported path for retuning these two values, and for adding a new specialist subagent later (e.g. splitting `security`). Covered by 7 new tests in `test_scaffold.py`.
- **DB-guard patterns extracted to `db_patterns.json`**: `block-db-access.py`'s regex rule set (DB CLIs, migrators, container exec, cloud secret-manager CLIs, connection strings, secret-file access, env dumps) now lives in a sibling `db_patterns.json`, reviewable/extendable on its own instead of buried in the script's logic. Generated byte-exact from the previous inline patterns (verified by round-tripping and recompiling every pattern before replacing the file) - no behavior change. The hook now fails closed (blocks everything) if this file is missing or not valid JSON, same philosophy as failing closed on malformed stdin. `verify_setup.py` and the generated `verify-guard.py` both check the file exists and parses. New tests cover the missing- and corrupt-file cases.
- **`PYTHON_CMD` is now actually verified, not just shaped-checked**: `verify_setup.py` resolves `PYTHON_CMD` against `PATH` (`shutil.which`) when `--answers` is given and fails the check if it doesn't resolve, instead of only validating that it looks like a plain command name. `references/interview.md` and the README's "Limits, honestly" now spell out that the DB-guard hook is Python-only by construction and needs a working Python 3 even on projects whose own stack has none.
- **`docs/specs/STATUS.md` gained an explicit lease convention**: a new `Lease (who @ when)` column - set it before writing a row, clear it after, treat someone else's lease under 15 minutes old as mid-update. Still not a real lock (documented as such), but narrower than "just re-read before writing." `orchestrate/SKILL.md`'s two STATUS.md-writing steps now point to this section instead of restating weaker advice inline.
- **`security`-as-single-agent limit given a documented escape hatch**: `/amend-constitution` now has an "Adding a specialist agent" section (copy an existing agent file, keep its non-negotiable rules block verbatim, register it in the orchestrate phase table and CLAUDE.md) for when one exhaustive-checklist `security` agent isn't enough depth for a project - a manual, deliberate path, not a default change.

## 2026-10-21

- **Feature-scoped diagram in `design.md`**: a new "Feature diagram" section, right after "Domain model" - entities/tables/screens touched by *that feature only*, never the whole project's schema. Mirrored in `spec-writer`'s `SKILL.md`, `references/spec-format.md`, and owned by `architect` (screens contributed by `designer` when present).
- **New `Database/` folder, generated when `DB_ENGINE` indicates a database** (inferred from the existing interview answer - `none`/`nenhum`/`tbd`/empty omits it, no new question needed): the project's complete, authoritative ER diagram (`er-diagram.md`) plus one file per DB object under `tables/`, `indexes/`, `foreign-keys/`, `primary-keys/`, `packages/`, `functions/`. Owned by `architect`; every feature that touches the database updates it (never silently replaces it) once `design.md` is approved. Static design artifacts only - same non-negotiable as the rest of the DB guard: never a live connection, real dump, or credentials.
- **Per-feature `overview.html`** (conditional: only when a feature touches UI screens and/or the database): a single self-contained, static HTML/inline-SVG file - no CDN, no external dependency - summarizing affected screens, the feature's scoped diagram, and affected `Database/` objects, so a non-technical stakeholder can open it and understand the change at a glance.
- `scaffold.py` gained `_HAS_DB` (derived from `DB_ENGINE`) and skips `Database/` templates when there's no database; `verify_setup.py` checks `Database/` existence (or absence) when `--answers` is given; `test_scaffold.py` covers both branches.
- `knowledge-graph.md.tmpl` gained a line distinguishing `Database/er-diagram.md` (physical schema, owned by `architect`) from the knowledge graph (conceptual domain entities) - related but not the same artifact, never merged.

## 2026-10-20

- **Model/effort selection**: `/orchestrate` asks once for the orchestrator's and each subagent's model (and, where supported, effort), records it in `docs/specs/STATUS.md`. Every agent file's frontmatter gained an explicit `model:` field (later retuned to role-tiered defaults - see below).
- **Knowledge graph**: new `knowledge-graph` agent, MCP-backed (`@modelcontextprotocol/server-memory`, gated by the `NPX_CMD` interview answer) with a markdown fallback when Node/npx isn't available. Seeds from discovery/design, extracts a proposal on retrofit onto an existing codebase, always checks before creating. Verified for real against the actual npm package: all 9 tool names, the duplicate-name skip behavior, and the on-disk `.jsonl` format.
- **Superpowers-inspired corrections**: TDD Iron Law + rationalization red flags (`engineering-principles.md`, `test.md`, `implementer.md`); 4-phase systematic debugging protocol (`docs/debugging-protocol.md`).
- **Test strategy guide**: `docs/test-strategy.md` (pyramid ownership, fixture/test-double conventions) - reference only, no code generation.
- **Team expansion**: `security` rewritten with an exhaustive ASVS-based checklist (authN/authZ, injection, secrets/supply-chain, infra, API, business-logic abuse, compliance); new `qa` agent (integration/e2e/edge-case/regression, phase 6 alongside `reviewer`); new `designer` agent (UI/UX), generated only when the new `HAS_UI` interview answer is yes.
- **Adaptive documentation**: `devops-docs` now tailors depth/structure to the project's actual scenario instead of a generic template.
- **System design**: `design.md` gained a "System design" section (capacity/scale, data flow, caching/queues, deployment topology, resilience); `requirements.md`'s NFR section is now structured (latency/throughput, SLO, compliance, accessibility, observability) instead of a one-line list. `architect` owns this explicitly.
- **Security report template**: `docs/specs/_templates/security-report.md`, written by `security` per feature/release instead of only a free-text chat report.
- **Guard-rail CI check**: generated projects now ship `.claude/hooks/verify-guard.py` and a real CI step that re-runs it on every push/PR, so a weakened deny-list or disabled hook is caught automatically instead of drifting silently.
- **Settings merge on upgrade**: `scaffold.py --merge-settings` does a key-level JSON merge of `.claude/settings.json` (deny-list union, new `mcpServers`/hook entries added) instead of forcing a full skip-or-overwrite choice.
- **Test suite for this skill**: `scripts/test_scaffold.py` covers the full answer matrix (HAS_UI, NPX_CMD, CI_PROVIDER, EXTRA_DENY, missing keys, overwrite, merge-settings) plus `verify_setup.py` pass/fail behavior; `.github/workflows/test.yml` runs it on every push/PR to this repo.

Researched comparable tools (GitHub Spec Kit, BMAD-METHOD, the Claude Code `spec-driven-dev` plugin) and adopted four improvements they do better:

- **Role-tiered model defaults**: every agent's `model:` frontmatter changed from a uniform `inherit` to a role-appropriate default - `opus` for `architect`/`security`/`reviewer`, `sonnet` for the rest of the delivery team, `haiku` for `devops-docs`. `/orchestrate` Start step 4 now asks whether to keep or override these, instead of asking for "one default for all." `verify_setup.py` checks the tier on every agent.
- **Shared findings ledger with one-time dispute**: `docs/specs/_templates/findings-ledger.md`, written jointly by `reviewer`, `qa` and `security` instead of each keeping separate findings. A Critical/High row starts `Open`; the orchestrator relays it to `implementer` for a fix or a dispute, and the agent that raised it makes the final `Confirmed`/`Retracted` call before it can block phase 6/7. `security-report.md`'s own Findings section now points to the ledger instead of duplicating it.
- **`/amend-constitution` skill**: a deliberate, ADR-recorded way to revise `CLAUDE.md`'s engineering defaults after scaffold time, instead of silent hand-edits or never revisiting them. It explicitly refuses to touch the DB-access prime directive or any agent's non-negotiable rules.
- **Retro after release**: `docs/specs/_templates/retro.md`, written with the user once phase 8 is confirmed - what went well, what to adjust, and what should carry into `discovery.md`/`CLAUDE.md`/the "Models & effort" table before the next feature's `/plan-grill`.

Fixed a bug found while making the model-tier change: `knowledge-graph.md.tmpl` had a stray `</content>` line left over from an earlier edit, after the frontmatter rules block. Removed.

Compared again (moai-adk this time, plus re-checking Spec Kit/spec-driven-dev) and read the actual guard code/templates critically instead of just comparing externally. Fixed everything found, in both rounds:

- **Cloud secret-manager CLI coverage**: the guard previously covered DB CLIs and local secret files but not cloud secret-manager calls (`aws secretsmanager get-secret-value`, `aws ssm get-parameter --with-decryption`, `gcloud secrets versions access`, `az keyvault secret show/download`, `vault read`/`kv get`, `op read`/`item get`, `doppler secrets get`/`run`, `pass show`, `kubectl get secret`) - the same class of exfiltration risk the guard already treats as critical, just a channel it didn't enumerate. Added to both `.claude/settings.json.tmpl` deny rules and `block-db-access.py`'s patterns, with matching test coverage in `verify-guard.py`, `verify_setup.py`, and `scripts/test_scaffold.py`.
- **Configurable model tiers**: `MODEL_PRIORITY` (`cost`/`balanced`/`quality`) is now a real interview answer. All 10 remaining agent files were converted from plain `.md` to `.md.tmpl` (`knowledge-graph` already was) so `scaffold.py` can compute each role's tier from `TIER_PRESETS` and substitute it - no more one-size-fits-all `balanced` default baked into every project regardless of budget. `verify_setup.py` now checks tiers dynamically from the answers instead of a hardcoded expectation.
- **New `debug` agent**: escalation point when one pass of `docs/debugging-protocol.md` by `implementer`/`qa` doesn't find the root cause - a fresh agent without the failed first attempt's anchoring bias, instead of the same agent retrying the same approach.
- **Structural self-check before human gates**: `planner`, `architect` and `security` now re-read their own drafts (no blank required section, no leftover open questions) before reporting them ready for approval, and the orchestrator is told to enforce this - fewer human review cycles spent on incomplete drafts.
- **Real coverage threshold**: `COVERAGE_THRESHOLD` is a new interview answer, carried into `CLAUDE.md`/`AGENTS.md`, wired as a named CI step in `ci.yml.tmpl`, and reported by `qa` (not just "looks good") before the phase 6 gate.
- **STATUS.md split into index + per-feature file**: the old single `docs/specs/STATUS.md` had one singular "current feature" field, even though the interview explicitly allows `TEAM: team` - a real contradiction, since two people on two features would collide on the same file. Now `docs/specs/STATUS.md` is a project-wide index (one row per feature, plus the global Models & effort table) and each feature gets its own `docs/specs/<feature>/STATUS.md` (template: `feature-status.md`). The orchestrator re-reads the index before writing to it.
- **Rollback checklist**: `orchestrate/SKILL.md` gained an explicit "If a released feature needs reverting" section - git-revert the code (human-confirmed), update the feature's status + index row, record an ADR, and have `knowledge-graph` propose (never auto-apply) removing entities that came only from that feature.
- **Knowledge-graph consolidation**: `knowledge-graph` now proposes (never auto-merges) likely-duplicate entities at the start of each feature's phase 3, instead of the graph only ever growing.
- **Limited autonomous mode**: an opt-in, asked once at Start - phases 1-4 stop re-confirming each gate individually, but phases 6-8 (review/security/release) are always human-gated regardless, since those are the outward-facing/irreversible ones.
- **Claude Code version-drift note**: `docs/knowledge-graph/README.md` now documents the two Claude-Code-internals this setup depends on (`mcp__knowledge-graph__<tool>` naming, `$CLAUDE_PROJECT_DIR` expansion in `mcpServers.env`) and what it looks like when they drift, instead of leaving that only in this repo's own README.
