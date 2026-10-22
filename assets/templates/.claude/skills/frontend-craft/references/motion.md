# Motion

Decide in this order before writing any animation code. Most bad motion fails at step 1 or 3.

## 1. Should it animate at all?
| How often the user sees it | Decision |
| --- | --- |
| 100+ times a day (keyboard shortcuts, command palette toggle) | No animation. Ever. |
| Tens of times a day (hover, list navigation) | Remove or drastically reduce |
| Occasionally (modals, drawers, toasts, sheets) | Standard animation |
| Rarely / first time (onboarding, celebrations) | Can add delight |

**Never animate keyboard-initiated actions** - repeated hundreds of times, they feel slow and disconnected.

## 2. What is it for?
Valid purposes: spatial consistency (enters and exits the same way), state indication, explanation, feedback on press, preventing a jarring change. "It looks cool" on something seen often is not a purpose.

## 3. Easing
- Entering or exiting → **ease-out** (starts fast, feels responsive).
- Moving or morphing on screen → **ease-in-out**.
- Hover / colour change → **ease**.
- Constant motion (marquee, progress) → **linear**.
- **Never ease-in for UI** - it delays the first movement, exactly when the user is watching.
- The built-in curves are too weak; use strong custom ones as tokens:
```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

## 4. Duration
| Element | Duration |
| --- | --- |
| Button press feedback | 100-160ms |
| Tooltips, small popovers | 125-200ms |
| Dropdowns, selects | 150-250ms |
| Modals, drawers, sheets | 200-500ms |
| Marketing / explanatory | Can be longer |

UI animation stays under 300ms. **Exits are faster than entrances** (a sheet in at 240ms, out at 180ms): slow where the user is deciding, fast where the system is responding.

## 5. Physicality
- Never animate from `scale(0)`; start at `scale(0.95-0.97)` with `opacity: 0`.
- Pressable elements: `:active { transform: scale(0.97) }` with `transition: transform 160ms ease-out`.
- Popovers scale from their trigger (`transform-origin` at the trigger); modals stay centred.
- Tooltips: delay the first one, then open neighbours instantly with no animation.
- Stagger groups by 30-80ms; never block interaction while a stagger plays.
- A crossfade that still looks like two objects swapping: add `filter: blur(2px)` during it (keep blur under 20px).

## 6. Springs and interruption
- For anything a user can grab or redirect (drag, sheets, gestures), prefer springs: they keep velocity when interrupted and start from the current value. Default to critically damped (no bounce); add a little bounce (~0.1-0.2) only when the gesture itself carried momentum.
- Hand the release velocity to the spring so there is no seam between drag and animation.
- For dynamic UI triggered rapidly (toasts, toggles), use CSS **transitions**, which retarget mid-flight; `@keyframes` restart from zero.
- Every move must be interruptible; read the live on-screen value when a new move starts.

## 7. Performance
- Animate **only `transform` and `opacity`** (and, in current engines, `filter`/`clip-path`). Never `width`, `height`, `top`, `left`, `margin`, `padding`.
- Never `transition: all` - name the properties.
- Do not drive per-frame motion through an inherited CSS variable on a parent; set `transform` on the element.
- CSS and the Web Animations API run off the main thread; `requestAnimationFrame`-driven JS (and Framer Motion's `x`/`y` shorthands) drop frames while the page is busy - use the full `transform` string or WAAPI.
- In React, never animate through state per frame; write to the element's style via a ref.
- `will-change: transform` only once you see a 1px shift or jank, not everywhere.

## 8. Reduced motion
`prefers-reduced-motion: reduce` means gentler, not none: keep opacity and colour changes that aid comprehension, drop movement, parallax, springs and overshoot, cut camera moves. Build the fallback with the animation, not after.

## The motion spec in design.md
| Element | Trigger | Property | Easing | Duration | Reduced motion |
| --- | --- | --- | --- | --- | --- |
| Detail sheet | open / close | transform, opacity | `--ease-out` | 240ms in / 180ms out | opacity only |
| Command palette | `/`, Ctrl+K | - | - | none (keyboard) | none |
| Primary button | press | transform | ease-out | 160ms | unchanged |
