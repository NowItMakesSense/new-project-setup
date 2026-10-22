# Typography, colour, surfaces and feel

## Typography
- **Default to one face** - the system font or one well-made grotesk, really loaded (check it rendered; a silent fallback lands on the default look). A second face only with one job (a mono for IDs/code, a serif for one greeting).
- **Tracking is size-specific.** Negative on large display text (about -0.02em at 32px+), zero on body, slightly positive only on very small text. One letter-spacing for every size is wrong somewhere.
- **Leading tracks size inversely.** Tight on large headings (1.05-1.2), comfortable on body (1.45-1.6), tighter in dense data UI.
- **Hierarchy from weight + size + leading together**, not size alone. Emphasise with weight; it adds presence without taking space.
- **Respect the user's text size.** Spacing in `rem`/`em`, layouts that grow with the text.
- **Figures:** `font-variant-numeric: tabular-nums` on every number in a table, KPI, counter or anything that updates. Format with `Intl.NumberFormat`, plurals with `Intl.PluralRules` - never "1 items".
- **Case:** sentence case everywhere; no tracked uppercase micro-labels.

## Colour
- Define colour as **roles**, not values: ground, surface, raised, border/rule, text, secondary, faint, primary action, accent (data), positive, negative, warning. Everything downstream references roles only.
- **Every text tier reaches 4.5:1** on the surface it sits on, placeholders included.
- **One accent family** on data and at most one control. Status colours appear only where a decision is needed; grey for what is fine.
- **Light and dark** are both designed, not inverted: dark grounds are true neutrals (`#000`, `#0c0d0f`, `#111`), never navy; elevation in dark is a lightness step.
- Honour `prefers-contrast: more` (stronger borders and text) and `prefers-reduced-transparency` (solid surfaces).

## Surfaces and depth
- A border **or** a shadow, never both. Resting cards get a 1px line or a tone step; real shadows are for what floats (menus, popovers, tooltips, dialogs).
- Radius chosen once: tight (4-8px) or soft (16-24px); nested radii step down so inner corners stay concentric.
- Pages may use flat fields of colour; app screens keep colour off chrome (see `app-screens.md`). Glass/backdrop blur only as the glass material below, never improvised.

## Glass material
The one sanctioned translucent surface. Use it for chrome that floats over **live content** - a canvas, a map, media, a 3D scene - when `design.md` chooses it. Never for resting cards on an ordinary dashboard, never one glass surface on another (legibility collapses), and never improvised: every pane on the screen uses the same tokens.

**Weights encode hierarchy** - standalone controls lightest, panes in between, modal surfaces heaviest:

| Weight | Use | Fill (dark) | Backdrop |
| --- | --- | --- | --- |
| `thin` | a standalone floating control (a search pill, a chip on the canvas) | `rgba(255,255,255,.07)` | `blur(16px) saturate(160%)` |
| `regular` | panes: top bar or islands, side sheet, legend, toolbar | `rgba(17,19,23,.56)` | `blur(24px) saturate(170%)` |
| `thick` | the command palette, dialogs | `rgba(15,17,21,.78)` | `blur(32px) saturate(180%)` |

- **Edge:** every weight gets the same light edge - `inset 0 0 0 1px rgba(255,255,255,.08)` plus a top highlight `inset 0 1px 0 rgba(255,255,255,.12)` (light catching the material) - and, because it floats, one soft two-layer shadow. That is the one place border and shadow combine.
- **Inside a pane** use fills, not blur: hover/selected rows `rgba(255,255,255,.06-.10)`, input wells `rgba(0,0,0,.28)`, dividers `rgba(255,255,255,.07)`.
- **Vibrancy:** secondary text sits brighter on glass than on a solid surface (about `#c9cbd0` / `#a3a6ad` on dark), small text one weight heavier, `+0.01em` tracking at 12px. Colour goes on solid marks (swatches, data), not on the translucent foreground.
- **Something to refract:** glass over a flat ground reads as grey. The live content behind it is usually enough; a faint, fixed ambient light (two very soft blurred colour fields under 10% opacity, never animated) is acceptable behind a canvas.
- **Cost:** never animate `backdrop-filter` - enter/exit with `transform` and `opacity`; keep blur ≤ 32px; don't put a blur on a full-screen scrim or on many small moving elements over a canvas that repaints every frame (dim the scrim instead; give moving labels a semi-transparent chip with the same edge).
- **Always write the `-webkit-` twin** of `backdrop-filter` (Safari).
- **Fallbacks:** `@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)))` and `@media (prefers-reduced-transparency: reduce)` turn every weight into a solid surface (and drop the ambient light); `prefers-contrast: more` makes them solid with a stronger edge.
- **Scrolling inside glass:** the native scrollbar steals width and cuts through the radius. Use a thin overlay thumb inside the radius - `::-webkit-scrollbar { width: 10px }` with a transparent track (`margin-block: 8px`) and a thumb `rgba(255,255,255,.18)` with `border: 3px solid transparent; background-clip: padding-box` (`scrollbar-width: thin; scrollbar-color` only where `::-webkit-scrollbar` isn't supported, since Chromium ignores the pseudo-elements once the standard properties are set) - plus `scrollbar-gutter: stable` so content never shifts, and a fade mask on whichever edge still has content past it, instead of a hard cut.

## Feel: response, feedback and gestures
- **Respond on press, not on release.** Highlight on `pointerdown`; commit on release. Audit every debounce and artificial delay on the input path.
- **Feedback is continuous during an interaction** - a drag, slider or drawer tracks the pointer 1:1 the whole way, respecting where it was grabbed (Pointer Events + `setPointerCapture`).
- **Interruptible always.** Never lock input during a transition; a new move starts from the element's current on-screen value, not from its logical target.
- **Momentum:** project where a flick is going (`current + (v/1000)·d/(1−d)`, `d ≈ 0.998`) and snap to the nearest target from there; dismiss on velocity (~0.11 px/ms), not only distance.
- **Soft boundaries:** rubber-band past an edge with rising resistance instead of a hard stop.
- **Spatial consistency:** things leave the way they came; popovers and menus grow from their trigger (`transform-origin` at the trigger), modals stay centred.
- **Tap targets:** at least 40-44px, with a little hit padding; hover states only under `(hover: hover) and (pointer: fine)`.
- **Wayfinding:** every screen answers where am I, where can I go, how do I get out. Specific labels ("Invoices") beat generic ones ("Home").

## Accessibility baseline
Real `<button>`/`<a>` elements; visible `:focus-visible`; logical focus order and focus returned to the trigger when a dialog closes; `aria-pressed` on toggles, `aria-expanded` on disclosures, `role="dialog"` + `aria-modal` on dialogs; text alternatives for images and for any meaning carried by colour alone. These become explicit, testable criteria in `design.md` for `qa`.
