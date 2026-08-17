# Component-scope flow

Run this instead of the full Design flow when the brief is a component, not a page. Most day-to-day dev requests are component-shaped, and the page-level apparatus (macrostructure, hero enrichment, footer archetype, project memory) is wrong for them.

## Component-scope signals

- The brief names a single UI element: *a button · an input · a card · a modal · a dropdown · a tooltip · a select · a checkbox · a switch · a tab strip · a chip · a badge · a banner · a snackbar · a popover · a slider · a date picker · an avatar*.
- The brief is short (≤ 30 words) and refers to one element.
- The target file is a single component (e.g. `./Button.tsx`, `./components/Input.css`, `app/components/Card.vue`).
- The user explicitly says *"just the X"*, *"only the Y"*, *"this one element"*, *"a single ___"*.

**If two signals fire → route component.** If only the page flow fires (multi-section brief, "build me a landing page") → stay in Design flow.

## Keeps from the page flow

- **Step 0 · Pre-flight scan** — same. Read existing tokens, fonts, framework, microinteraction stance. A button on a Geist-bodied Tailwind project must adopt those tokens, not invent new ones. See [`preflight.md`](preflight.md).
- **Step 1 · Genre detection** — same. Editorial / modern-minimal / atmospheric / playful; the component inherits its surroundings' genre (silent default to editorial when unknown).
- **Step 2.6 · Theme route** — same. If a `tokens.css` or `design.md` exists, the component uses those tokens. Otherwise ask "is there a system to follow, or should I pick one?" — default *catalog* on silence.
- **2+1 font discipline** — same.
- **State discipline — STRICTER.** Every interactive component MUST ship code for **all 8 states**: default · hover · `:focus-visible` · `:active` · disabled · loading · error · success. The 8-state checklist in [`interaction-and-states.md`](interaction-and-states.md) is mandatory, not advisory.
- **Slop test — universal-only subset.** Run the visual / microinteraction / contrast (gates 40–41) / a11y / typography gates. Skip the diversification gates (no `.hallmark/log.json` entry — components don't rotate) and the layout-safety gates that assume a full page.

## Skips

- **Step 2 · Macrostructure pick** — components don't have macrostructures. State explicitly: *"Component-scope: skipping macrostructure."*
- **Nav and footer archetype picks** (N1–N13, Ft1–Ft8) — page-scope only; a component has no nav or footer.
- **Hero polish patterns (HP1–HP4)** — page-scope only.
- **Step 4 · Enrichment** — no hero illustration, no demo video, no abstract background. The component IS the artifact.
- **Step 5 · Multi-section preview** — replaced by the 8-state demo wrapper (below).
- **Project-memory append** — no `.hallmark/log.json` entry for component runs; the diversification rule doesn't apply.

## Emits — two files, side by side

1. **The component artifact** — a single self-contained file matching the project's conventions:
   - React / Vue / Svelte: `Button.tsx` / `Button.vue` / `Button.svelte`
   - Vanilla web: `button.css` + `button.html`
   - Tailwind: a `.tsx` with `className` chains AND a `tokens.css` if missing
   - Consumes Hallmark tokens by name (`var(--color-accent)`), never inline OKLCH values.

2. **An 8-state demo wrapper** — `<ComponentName>.preview.html` (or `.preview.tsx`): a small standalone page rendering the component in **all 8 states** stacked vertically, each labelled. The user opens it once, sees the component working, then deletes it. Not part of production code.

   ```
   ┌──── Button — 8 states ────────────────────────┐
   │ default       [ Click me                  ]   │
   │ hover         [ Click me                  ]   │  ← .is-hover forces :hover styling
   │ focus         [ Click me                  ]   │  ← .is-focus forces :focus-visible
   │ active        [ Click me                  ]   │  ← .is-active forces :active
   │ disabled      [ Click me                  ]   │  ← disabled attr
   │ loading       [ ⌛ Working…                ]   │  ← data-state="loading"
   │ error         [ ⚠ Try again               ]   │  ← data-state="error"
   │ success       [ ✓ Saved                   ]   │  ← data-state="success"
   └────────────────────────────────────────────────┘
   ```

   Each labelled row uses a class (e.g. `.is-hover`) that the component's CSS targets in addition to the real pseudo-class, so all 8 states render at once:

   ```css
   .btn:hover, .btn.is-hover { background: var(--color-paper-3); }
   .btn:focus-visible, .btn.is-focus { outline: 2px solid var(--color-focus); }
   .btn:active, .btn.is-active { transform: translateY(1px); }
   ```

## Stamp format for component output

```css
/* Hallmark · component: <type> · genre: <genre> · theme: <theme>
 * states: default · hover · focus · active · disabled · loading · error · success
 * contrast: pass (46–50)
 */
```

The `component:` prefix tells future Hallmark runs this artifact is component-scoped and shouldn't trigger page-level diversification. The `states:` line is a checklist — every state listed must have actual styling in the file.

## When in doubt — ask once

If the brief is ambiguous between component and page (e.g. *"design a pricing section"* — one card or a whole page), ask one short question: *"One pricing card, or the whole pricing page?"* Default to **component** if the user doesn't engage — single-artifact output is cheaper to redirect than a multi-section page.
