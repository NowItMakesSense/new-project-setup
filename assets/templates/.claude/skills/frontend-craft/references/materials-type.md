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
- Pages may use flat fields of colour; app screens keep colour off chrome (see `app-screens.md`). Glass/backdrop blur is off the table for this project's house style unless `design.md` records a deliberate exception.

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
