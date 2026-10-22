# Art direction for pages

For pages that are read and scrolled. App screens follow `app-screens.md` instead.

## The run
1. **Read what is real.** The subject, the audience, the one thing the page must get someone to do, the stack, any existing brand (colours, fonts, logo), and above all which imagery truly exists: the project's own photographs or product, a real interface that can be shown, an image tool, or nothing. Do not plan around pictures you do not have.
2. **Inventory the subject.** Write 8-12 things that belong to this client and to no competitor: its name and what the name means, its place (street, materials, light, signage), its numbers (seats, minutes, price, year), the constraint it lives with, its rituals and hours, the printed things of its world (a ticket, a label, a timetable). This list is where the idea comes from, and it is the picture search.
3. **Write the argument.** List the page as claims with their proof, one line per section. The claims decide which sections exist and their order; delete any section with no claim. This is how you avoid the stock sequence of hero, logos, three features, testimonial, pricing, call to action.
4. **Choose a direction** (a way of composing: type system, palette proportions, hero and section compositions). With `design-taste-frontend` installed, deal three with `draw.mjs --options 3` and pick the one that can carry something only this client has. Adopt it whole; do not blend it with the layout you would have made anyway.
5. **Find the idea.** Fill both blanks from the inventory: *On this page, [something that belongs to the subject] becomes [the device the direction calls for].* Test it against the nearest competitor: if the sentence still works for them, it belongs to the category, not to this client. "Clean and modern" is not an idea.
6. **One live thing.** One thing the visitor can do with the subject's real content (set the loan and read the real monthly figure; pick a wood and see the chair in it). Works with a thumb, has a plain fallback, never blocks reading.
7. **Write the words before markup.** Headlines fit two lines at every width (about 32 characters is safe). One supporting sentence directly under the headline. One primary action named for what it does. Every section the visitor came for delivers its information completely - thin sections lose to busier pages.
8. **Build it still, then look, then move.** Tokens first, then the hero at desktop and phone width, then each section. Look at screenshots at 1440, 768 and 390 and fix the worst three problems; repeat up to three rounds. Only then add motion (`motion.md`).

## House rules (pages)
| Rule | Instead |
| --- | --- |
| Headlines two lines or fewer at every width | Cut words, then widen the measure, then size |
| A clear `h1` title on the first screen, a heading on every section | Say what this is: name + what it does, event + date and place |
| Equal outer margins; no section huddled on one side | Close every void with the section's picture, a second column or a figure |
| No blank stretch taller than about half a screen | The normal section gap; one deliberate rest per page at most |
| No eyebrows, pills or "New ·" chips above headings | Put the information in the heading or the first sentence |
| No monospace outside real code | The text face, tabular figures where numbers align |
| No index numbering (01 / 02 / 03, "Step 2") | Order by position, size or words; a real `<ol>` if order matters |
| No hairline dividers, outlined boxes, grid lines or crop marks | Space, a tone step, a change of scale, a filled shape |
| No gradients (backgrounds, buttons, text) | Flat colour or a real photograph; a neutral scrim under text on a photo is the one exception |
| No shadows on things at rest, no glows, no ad-hoc glass | A tone step; shadows only on menus and dialogs; the glass material (`materials-type.md`) only for chrome floating over live content |
| No violet/indigo accents, no cream-with-terracotta "assistant palette" | The direction's palette, checked against the subject's own colours |
| No icon-topped feature cards in identical rows | The direction's section compositions |
| No emoji, gradient blobs, decorative shapes or fake dashboards of grey bars | A real picture, a real interface fragment, or nothing |
| No styled accent word in a headline (italic, coloured, underlined) | One face, one colour; the words carry the emphasis |
| Two typefaces at most, usually one | The direction's type system |

## Imagery, in order of preference
The project's own; generated if an image tool exists; real pictures of the subject's world from open collections (with licence and credit, never presented as the client's own product or people); drawn in code from the subject itself; type and colour alone. Software shows its own interface built in HTML, never grey placeholder bars.

## Tells of a generated page
A centred headline with a small label above it; a soft gradient or blob behind the hero; three icon cards; a logo strip of invented customers; a testimonial from "Sarah, CEO"; thin rules and a monospace caption; every section the same width and rhythm; a dark mode that is navy. Each one is a default that was not chosen.
