# Reviewing UI

## Format (required)
Every UI finding is a row in one markdown table with **Before | After | Why** columns - never "Before:"/"After:" on separate lines.

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms` | `transition: transform 200ms var(--ease-out)` | Name exact properties; `all` animates things you didn't mean to |
| `transform: scale(0)` on enter | `transform: scale(0.96); opacity: 0` | Nothing appears from nothing |
| `ease-in` on a dropdown | `--ease-out` | ease-in delays the first movement, so it feels sluggish |
| No `:active` state on a button | `:active { transform: scale(0.97) }` | The press must be answered |
| Navy `#0f172a` dark ground | `#0c0d0f` with surfaces one step up | Dark themes are true neutrals |

In this project the rows go into `docs/specs/<feature>/findings-ledger.md` with a severity, the `file:line`, and the usual Open/Confirmed/Retracted status - the same ledger and flow as `reviewer`.

## Severity
- **Critical/High:** content or a primary action unreachable or unreadable (overflow hides the action, contrast under 4.5:1 on essential text, keyboard trap, no focus indicator, a motion with no reduced-motion fallback that moves large areas, an injected-HTML path for user data).
- **Medium:** a house-rule violation a user would notice (gradient/glow on chrome, glass outside the glass material or over a static page, glass on glass, a glass surface with no reduced-transparency/no-blur fallback, an animated `backdrop-filter`, a native scrollbar cutting a glass pane, accent on chrome, rainbow chart, animation on a keyboard action, UI motion over 300ms, a missing empty/error state, numbers not tabular in a table).
- **Low:** polish (easing curve, a stagger, tracking on a heading, a radius that doesn't step down).

## Checklist
**Against the spec**
- Does it match `design.md`'s direction/style, tokens, motion spec and worst-case states? Anything built that the spec doesn't describe?
- Does the biggest thing on the screen answer the screen's one question?

**House rules** (`app-screens.md` or `art-direction.md`)
- Colour only on data/status/one control; at most four hues; no gradients, glows, resting shadows; border or shadow, never both (the glass material's edge + float shadow is the one sanctioned pair).
- Glass only as the glass material (`materials-type.md`): the right weight per surface, one edge, fills not blur inside panes, `-webkit-` twin, solid fallbacks, thin overlay scrollbars with edge fades.
- One typeface (two with separate jobs); sentence case; no eyebrows, index numbers, emoji, lorem, invented proof.
- Numbers: tabular, formatted, right-aligned in columns, plurals correct, totals add up from rows.

**Motion** (`motion.md`)
| Issue | Fix |
| --- | --- |
| `transition: all` | Name the properties |
| `scale(0)` entry | `scale(0.95-0.97)` + opacity |
| `ease-in` on UI | `--ease-out` or a custom curve |
| Animation on a keyboard action | Remove it |
| UI duration over 300ms | 150-250ms |
| Same speed in and out | Exit faster than enter |
| Hover effect without the media query | `@media (hover: hover) and (pointer: fine)` |
| Keyframes on a rapidly re-triggered element | CSS transitions (interruptible) |
| Animating width/height/top/left/margin | `transform` / `opacity` |
| No reduced-motion fallback | Opacity-only or static |

**States and data** (`worst-case.md`)
- Empty, one, huge, long, missing, error and loading states exist and were looked at.
- User text is set as text, never injected as HTML.

**Accessibility**
- Real buttons/links; visible `:focus-visible`; logical focus order, focus returned after dialogs; toggles expose `aria-pressed`; 4.5:1 text contrast; nothing conveyed by colour alone; tap targets ≥ 40px.

## Evidence
Review the rendered result, not just the diff. When `design-taste-frontend` is installed, run `node <skill>/scripts/inspect.mjs <page>` (add `--app` for app screens) and read its screenshots at every width; quote its `FAIL`/`WARN` lines as evidence. Without it, say the review was code-only.
