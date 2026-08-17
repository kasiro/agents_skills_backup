# Step 6 · Build

Loaded at Build time in the default Design flow. Emit code that satisfies the tone and structural fingerprint — match the complexity of the code to the ambition of the tone (a brutalist page needs raw, heavy CSS; an austere page needs restraint).

## Always

- **Hero headline — match font-size to copy length.** When you write the headline yourself, aim for **≤ 7 words and ≤ 50 chars** from the start. For longer headlines use the size-by-length brackets in [`typography.md`](typography.md) § Hero headline sizing: 21–50 chars → `--text-display`; 51–90 chars → cap at `--text-display-s`; > 90 chars → rewrite shorter or cap at `--text-4xl`. Aggressive-display themes (Brutal, Riso, Manifesto) auto-step down one rung past 50 chars — their 6.5–9rem ceiling is for short statements only.
- **Section tags / eyebrows — default OFF.** Do NOT emit `01 · THE TOUR`, `02 / FEATURES`, `Chapter Three`, or any uppercase mono-cap section number / kicker / label unless (a) the user explicitly asked for numbering, OR (b) the macrostructure is Long Document / Manifesto / Catalogue numbered AND the content is genuinely ordinal. Cap at 1–2 per page. **When a tag IS used, stack it vertical — tag above, heading directly underneath in the same column.** The tag-left / heading-right two-column pattern (hanging header, left-margin label) is banned outright — the single most reliable templated-editorial tell; slop-test gate **54** auto-fails it.
- **OKLCH everywhere.** Tokens as CSS custom properties at `:root`.
- **4pt spacing scale** with semantic names (`--space-sm`, `--space-md`, …).
- **Distinctive display face + refined body face.** Pairings, not single-font pages — unless the single-font choice IS the design (a true terminal-aesthetic page is monospace-only on purpose).
- **Design every interactive element for its full eight states** — see [`interaction-and-states.md`](interaction-and-states.md).
- **Animate `transform` and `opacity` only** — never layout properties. Use the three named easings (`--ease-out`, `--ease-in`, `--ease-in-out`) — never the browser default `ease`, never bounce/overshoot on UI state.
- **`prefers-reduced-motion: reduce`** — spatial motion collapses to ≤ 150 ms opacity crossfade.
- **`:focus-visible` with a visible ring at ≥ 3:1 contrast. Never animate the ring's appearance** — it must show instantly on focus.
- **Microinteraction recipes** — for each interaction (button, input, modal, toast, drag, copy) apply [`microinteractions.md`](microinteractions.md). Silent success over celebratory toasts. Optimistic update + Undo over confirmation dialogs. Delay 800 ms on hover tooltips, 0 ms on focus tooltips.
- **Cut motion before adding it.** If removing an animation wouldn't lose the user information, remove it.

## Stamp the output

The first non-empty line of the produced CSS (or top of `<style>`) MUST be:

`/* Hallmark · macrostructure: <name> · tone: <tone> · anchor hue: <hue> */`

The next Hallmark run reads this stamp and picks a *different* macrostructure. **Custom themes** carry a fuller multi-line stamp (vibe, paper + accent OKLCH, fonts, three axes) — [`custom-theme.md`](custom-theme.md) § E. **Studied-DNA builds** stamp `theme: studied-DNA (source: <URL or "image">)` plus the paper/accent OKLCH and fonts from the diagnosis; diversification stays suspended for the run.

## Append to project memory

After the stamp, update (or create) `.hallmark/log.json` at the project root — append a new entry at the **front** of the array: `{ "date": "<YYYY-MM-DD>", "macrostructure": "<name>", "theme": "<name>", "enrichment": "<E# name or 'none'>", "brief": "<one-line summary>" }`. Custom entries add `"theme": "custom"`, `"theme_axes"`, optional `"vibe"` (see [`custom-theme.md`](custom-theme.md) § F). Trim to the last 20 entries. Create `.hallmark/` if needed; respect any existing `.gitignore`. This file is what Step 2.5 reads next run.

## Stylesheet hygiene

- **Never clobber an existing global stylesheet.** `app/globals.css`, `src/index.css`, `src/styles/global.css` are **append-only**: keep their `@tailwind` / `@import "tailwindcss"` directives in place, add Hallmark's `:root` block and base rules below, keep new `@import` at the very top, reuse the project's own token names where they exist. Overwrite only on explicit user request. See [`contract.md`](contract.md).
- **Always emit `tokens.css`.** After the page CSS, write `tokens.css` at the project root containing every `--color-*`, `--font-*`, `--space-*`, `--text-*`, `--ease-*`, `--dur-*`, `--rule-*`, `--radius-*` token used. The page CSS imports it (or the framework entry-point includes it); the page CSS references tokens by name, never inline raw values. Even single-page builds get one.
- **Multi-format exports on `design.md` projects.** If `design.md` exists at the root, append all four export formats — `tokens.css`, Tailwind v4 `@theme`, DTCG `tokens.json`, shadcn/ui CSS variables — into its `## Exports` section. Load [`export-formats.md`](export-formats.md) for the canonical mapping. Single-page projects get only `tokens.css`.
- **Opt-in `design.md` (lock-the-system flow).** Only when the user explicitly asks (*"lock the system"*, *"give me a design.md"*, *"make this portable"*): load [`design-md.md`](design-md.md) and follow it. Page-scope only; the default verb does NOT auto-emit `design.md`; if it exists, refresh its `## Exports` instead of overwriting. The Step 5 preview carries the CTA surfacing this.
