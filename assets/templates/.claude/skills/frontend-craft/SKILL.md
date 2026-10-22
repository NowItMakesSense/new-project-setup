---
name: frontend-craft
description: House rules for front-end work in this project - art direction, app-screen layout, typography, colour, motion, worst-case data and the UI review format. Preloaded by the designer, frontend and ui-reviewer agents; load it whenever a task designs, builds, restyles, animates or reviews a screen, component, page or style, or when something "looks generic", "AI-made" or "not polished".
---

# Front-end craft

Generated interfaces look like the average of every interface: a centred headline over a gradient, icon cards in a row, a navy sidebar with a coloured pill, `transition: all 300ms`, a spinner that fades in from `scale(0)`. Nothing in them is wrong and none of it was decided. This skill replaces those defaults with decisions, and gives every UI agent the same rules so design, build and review agree.

## First, decide what kind of thing this is
- **A page** is read and scrolled: landing, marketing, product, portfolio, event, docs home. Follow `references/art-direction.md`.
- **An app screen** is worked in: dashboard, admin, settings, list/inbox, editor, builder, the detail of one object, a viewer. Follow `references/app-screens.md`.
- A product page that shows its app is a page; the interface fragments on it follow the app-screen rules inside.

Then, for either kind, write down before any markup:
1. **The one question** the screen answers first ("Did today's orders come in?", "Which deploy broke?"). The biggest thing on the screen answers it.
2. **The direction** (page) or **style** (app screen), and one line on why it suits this subject, not the category.
3. **The face**: one thing only this product has (its own data, object, place or vocabulary), and where it shows on the first screen.
4. **Tokens**: type scale, palette roles, spacing, radii (`references/materials-type.md`).
5. **The motion spec**: a table of element, trigger, easing, duration and reduced-motion behaviour (`references/motion.md`).
6. **The worst-case states**: empty, one, huge, long, missing, error, loading (`references/worst-case.md`).

`designer` writes these into the feature's `design.md` (UX section); `frontend` builds to them; `ui-reviewer` checks the result against them.

## The short form of the rules
- Colour goes on data, status and at most one control, never on chrome. At most four hues on a screen.
- No gradients on surfaces, buttons or text; no glows, no glass/backdrop blur, no shadows on things at rest. Separate surfaces by a lightness step or a single 1px line, never both. If a design really needs one of these (a glow on data marks in a visualisation, say), name it as a deliberate exception in `design.md` with its reason.
- No eyebrow labels above headings, no tracked uppercase micro-labels, no index numbering (01/02/03), no emoji, no lorem, no "Acme"/"John Doe", no invented proof or vanity numbers.
- One typeface (two at most, each with one job). Tabular figures on every number that aligns or updates. Sentence case.
- Animate only `transform` and `opacity`, under 300ms for UI, with strong ease-out curves; never animate keyboard-initiated actions; never from `scale(0)`; exits faster than entrances; every motion has a `prefers-reduced-motion` fallback.
- Every pressable element answers the press (`:active { transform: scale(0.97) }`); hover effects only under `@media (hover: hover) and (pointer: fine)`; visible `:focus-visible`.
- Every block has its empty, zero, loading and error state, built and looked at, not imagined.

## References
- `references/art-direction.md` - the run for pages: inventory, argument, direction, idea, house rules, tells.
- `references/app-screens.md` - the run for app screens: question, style, shell, data, states, banned list.
- `references/materials-type.md` - typography, colour roles, surfaces, depth, gesture and feedback details.
- `references/motion.md` - whether to animate, purpose, easing, duration, springs, interruption, performance.
- `references/worst-case.md` - the worst-case fixtures and the failure-signature table.
- `references/review.md` - the mandatory Before/After/Why review format and the checklist.

## Deeper tooling, when installed
These rules are distilled from two MIT-licensed skill collections. When their full versions are installed (globally with `npx skills@latest add emilkowalski/skills -g` and `npx skills@latest add Leonxlnx/taste-skill -g`), load the relevant one with the Skill tool for depth:
- `design-taste-frontend` - deals researched directions and app styles with `node <skill>/scripts/draw.mjs` (add `--app` for app screens) and measures the built page in a real browser with `node <skill>/scripts/inspect.mjs <page>` (screenshots at 1440/768/390, `--app` for app rules). Requires Node 22+ and an installed Chrome/Edge/Chromium. Run `inspect.mjs` before reporting a UI task done and fix every `FAIL`.
- `emil-design-eng`, `animate`, `review-animations`, `animation-performance`, `apple-design`, `break-ui` - the motion, polish, performance and worst-case detail behind `references/motion.md`, `references/review.md` and `references/worst-case.md`.

Without them, work from these references alone and say so in your report - never claim a browser check you did not run.

## Credits
Distilled, in this project's own words, from Emil Kowalski's skills (github.com/emilkowalski/skills, MIT) - including his `apple-design` translation of Apple's WWDC design talks - and from Leonxlnx's taste-skill (github.com/Leonxlnx/taste-skill, MIT).
