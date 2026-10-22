# Worst-case data

A screen that only works with tidy demo data is half built. Before reporting a UI task done, render it with the worst realistic data and look.

## 1. Map the surface
List every field the component shows: where it comes from, its type, its real limit (schema, form validation), whether it can be missing. A field with no limit anywhere is a finding by itself.

## 2. Build the fixtures
- **Empty:** zero items, the no-results state.
- **One:** a single item, and every count at exactly 1 (pluralisation).
- **Huge:** the realistic upper bound (1,000+ rows if unpaginated - a performance break as well as a visual one).
- **Long:** the longest real name/title/email/label, words with no break opportunity, a long translated button label.
- **Short:** one-letter names, a single-character title.
- **Missing:** every optional field absent at once.
- **Odd:** non-Latin and tall scripts (Vietnamese, Thai, Arabic), emoji-first names, markup-looking text (`<b>`, `&amp;`, `**text**`), extreme numbers (0, negative, 1,284,000.5, null).

Render them behind a "Demo data / Worst case" switch (a dev-only `?data=worst` param, or a fixture route) so the check can be repeated.

## 3. Failure signatures and their fix
| What you see | Cause | Fix |
| --- | --- | --- |
| Avatar/icon squished into an oval | Flex child shrinking | `flex-shrink: 0` on fixed-size boxes |
| Text overflows its box | Flex/grid child with `min-width: auto` | `min-width: 0` on the text column (`minmax(0, 1fr)` in grid) |
| Email or URL runs past the edge | No break opportunities | `overflow-wrap: anywhere` on that element |
| Trailing action pushed off-screen | Middle content took the space | `min-width: 0` on the middle, `flex-shrink: 0` on the action |
| Badge wraps onto two lines | Badge allowed to shrink | `white-space: nowrap; flex-shrink: 0`, decide what yields instead |
| Long word breaks mid-word in a heading | `word-break: break-all` | `overflow-wrap: anywhere` |
| "1 members", "0 member" | Hardcoded plural | `Intl.PluralRules` |
| Numbers jitter or misalign | Proportional figures | `font-variant-numeric: tabular-nums` |
| `NaN`, `undefined`, `1284.000000001` | Raw number rendered | `Intl.NumberFormat`, guard null |
| Diacritics clipped top/bottom | Tight `line-height` + `overflow: hidden` | Looser leading, no clipping on text |
| Truncated text with no way to read it | Ellipsis alone | `title`/tooltip plus the full value in the detail view |
| Raw `<b>` or `&amp;` shown, or markup executed | Wrong escaping layer | Escape once at render; set text via `textContent`; never inject user data as HTML |
| 1,000 rows stutter | Every row rendered | Virtualise or paginate, and say which |
| Last row cut mid-glyph | Fixed height, no scroll affordance | Visible scroll or a fade mask |

## 4. Truncate, wrap or clamp
- **Wrap** what the user needs in full to identify something (names, titles in a detail view).
- **Truncate at the end** secondary metadata where the start carries the meaning - always with a way to see the full value.
- **Truncate in the middle** when items differ at the end (file names, paths, hashes).
- **Clamp** multi-line previews in cards so heights stay predictable.
- **Never truncate** numbers, amounts, dates or anything the user compares.

## 5. Report
| # | Severity | Field | Worst-case value | What happens | Fix |
| --- | --- | --- | --- | --- | --- |
| 1 | Broken | `email` | `bartholomew.fitzgerald@northwind-holdings.example.com` | Pushes the menu off the row at 400px | `min-width: 0` + `overflow-wrap: anywhere`, `flex-shrink: 0` on the menu |

Severity: **Broken** (content or action unreachable), **Ugly** (visibly wrong), **Fragile** (works only because data happens to be short). Then list the decisions that need a human (what should truncate, what limit the schema should have).
