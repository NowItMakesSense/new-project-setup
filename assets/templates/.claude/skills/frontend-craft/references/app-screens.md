# App screens

For screens people work in: dashboards, admin, analytics, settings, lists and inboxes, editors and builders, the detail of one object, viewers. Distilled from a measured study of real product screens (taste-skill); the numbers are those measurements.

## What separates a real screen from a generated one
1. **Colour goes on data, not chrome.** Most screens stay at or under ~3-5% coloured pixels. Many have no filled primary button at all; a primary is usually near-black (light) or an inverted white pill (dark).
2. **KPIs are type, not tiles.** No icon in a coloured circle, no sparkline on a KPI.
3. **Surfaces are flat.** Separation is a 1px line or one tone step - a border or a shadow, never both.
4. **No hero header.** A noun title at 18-32px (median 24), never a landing-page headline or a figure at 48px+.
5. **Charts carry almost no chrome.** One series has no legend; 3-5 faint gridlines or none; one hue per chart.
6. **Navigation recedes.** The active item is a neutral grey pill or a brighter label; a coloured left bar is rare.
7. **Tables are rules and alignment.** No zebra, no header bands, 12px grey sentence-case headers, numbers right-aligned in tabular figures.
8. **Data states are honest.** Zeros print as zeros, missing values as a grey dash, an empty section keeps its frame.

Quiet is the starting point, not the goal: a screen people trust shows more of the product than a template does - its people, its objects, its numbers and the one thing to do next.

## The run
1. **Inventory the data and the jobs** (8-12 lines): the objects and their fields with units; realistic magnitudes (including how small a new account really is); who opens the screen and how often; the jobs they do next and which comes up most; the product's own things (name, mark, workspace, people, recognisable objects). Write a small dataset the screen renders from; totals are computed from rows, never typed separately.
2. **Name the one question.** It decides what is biggest, what comes first and what is left out. The largest figure answers the title row's sentence.
3. **Choose a style.** With `design-taste-frontend` installed: `draw.mjs --app --kind <kind> --brief "<product>" --screens <screens> [--theme dark] --options 3`, then deal the chosen one with `--style <id>`. Keep the style's one move intact; take other values from the defaults below.
4. **Give it a face** before markup: the data hue taken from the product's world, a ground with the product's temperature, or a signature element only this product has. Plus the product's mark and name in the shell, and words of the trade in every label ("Waiting on the customer", not "Status").
5. **Build the shell empty** (sidebar or top bar, canvas, title row) and look at it at 1440 and 390. Write the grid arithmetic in a comment.
6. **Put in the data**, formatted: separators, fixed decimals per metric, a sign on every change, units as small grey suffixes, tabular figures, right alignment in columns. A fact shown twice is one variable. Every relative figure names its baseline.
7. **Build every state** (below) and every row/control state: hover, selected, focus, disabled.
8. **Check and look.** `inspect.mjs --app <page>` when available; then read the screenshots and answer: is the question answered by the biggest thing? Does every block share the screen's edges? Is colour only on data/status/one action? Do numbers add up and line up? Does the phone fold the navigation?

App screens have no motion floor. Motion is feedback: press, hover, focus, a menu or sheet opening, a row arriving. Nothing performs an entrance.

## Defaults when the style does not set a value
- **Type:** one grotesk; title 18-24px/600, section 16px, body 14px, labels 12px, nothing under 11px; weights 400/500/600 (700 for one job at most); tracking 0 except -0.02em on large type.
- **Light:** ground `#f9fafb`, surface `#fff`, border `#e8e8e8`, rule `#f2f2f2`, control border `#d1d5db`, text `#111`, secondary `#5f6368`, faint `#6b6b6b` (every text tier reaches 4.5:1).
- **Dark:** ground `#000`/`#111` (never navy or slate), surface one step up (`#111` on `#000`, nested `#222`-`#2a2a2a`), lines `#1a1a1a`-`#2e2e2e`, text `#fff`, secondary `#b4b4b4`, meta `#949494`.
- **Status:** pale tint with dark ink of the same hue for pills; a darker green such as `#247b50` when green is text on light.
- **Radius:** tight (4-8px) or soft (16-24px), chosen once; nested radii step down; at most three panel radii.
- **Spacing:** 4px base; card gap ~16px, card padding ~20px, control height ~32-36px.

## States
- **Zero:** printed in the normal style ("0", "$0.00"). **Missing:** a grey dash, never a dash at value size.
- **Empty section:** keeps its frame and header plus one sentence spanning the block; an empty chart draws its zero line.
- **First run:** keep the frame and title; put the first action where the data will appear.
- **Loading:** the final layout with each value replaced by a flat grey bar at its real size; no shimmer gradient, no layout shift.
- **Error:** inside the block that failed - what failed, when data was last good, a Retry text button.

## Banned on app screens, and what replaces it
| Banned | Instead |
| --- | --- |
| Gradients on grounds, buttons, cards, text, KPI tiles | Flat fills (an area fade under one line chart is the one exception) |
| Glows, glass, backdrop blur | Opaque surfaces one tone step from the ground |
| An icon in a coloured circle on every KPI or card | A label and a number |
| Rainbow charts, a hue per bar, one subject in two hues | One hue per chart, neutrals for the rest, four hues at most per screen |
| A dark or saturated sidebar on a light screen; a navy/slate dark theme | The page ground for the sidebar; true neutral darks |
| The accent on chrome (tinted nav row, coloured tab pills, brand fill on every button) | The accent on data and at most one control |
| "Welcome back, Alex 👋", a hero header, an illustrated banner | A noun title at ~24px |
| Uppercase tracked table headers, zebra rows, left-aligned numbers | 12px grey headers, rules or space, right-aligned tabular figures |
| Pagination under a five-row list | Capped rows, "View all", the total |
| Lorem, Acme, John Doe, vanity totals, growth on a week-old account | Believable sample data computed from rows, listed for replacement |
| A screen that names no product and offers no action | The product's mark and scope in the shell; its main job one click away |
