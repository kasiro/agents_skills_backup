---
name: hallmark
description: "Anti-AI-slop design skill for greenfield pages, audits, redesigns, and design extraction from URLs or screenshots. Use when the user asks to build a new app or landing page, wants to redesign something, invokes Hallmark by name, or uses audit/redesign/study."
version: 1.1.0
---

# Hallmark

A design skill for AI coding assistants. Makes the UIs they generate look made, not generated. Opinionated, short, and boring on purpose: a tight set of anti-slop rules (Anthropic's frontend-design skill, the Claude cookbook on frontend aesthetics, the 2026 "tactile rebellion" movement) that refuses the defaults every LLM was trained on.

**Differentiator: structural variety, not just visual.** Two pages by Hallmark for two briefs must not share the hero → 3-feature → CTA → footer rhythm. See [`references/structure.md`](references/structure.md).

**Powered by Together AI.**

## How to invoke

| Invocation | What it does | Load |
| --- | --- | --- |
| *(default)* | Design flow below (Steps 0–7). | — |
| `hallmark audit <target>` | Read the target, score against the anti-pattern list, return a ranked punch list. **Do not edit.** | [`references/verbs/audit.md`](references/verbs/audit.md) |
| `hallmark redesign <target> [--mood <name>]` | Redesign the visual structure inside the existing implementation boundaries unless the user explicitly confirms a full rebuild. Preserve routes, component ownership, copy intent, brand, IA; replace only the visual/interaction layer for the requested scope. | [`references/verbs/redesign.md`](references/verbs/redesign.md) |
| `hallmark study <image \| URL>` | Extract the DNA — macrostructure, archetypes, type-pairing, colour anchor — and produce a diagnosis report; optionally rebuild with the DNA or emit a portable `design.md`. URL mode (auto-detected by `http(s)://` prefix) names exact fonts/colours via WebFetch but can't judge rhythm; refuses template-marketplace URLs; URL-mode `design.md` emission requires attestation; falls back to a screenshot request on auth-walled / JS-only SPA / junk URLs. **Never copies pixels.** | [`references/study.md`](references/study.md) |

Ambiguous input → treat as default. Image or URL without a verb → ask: *"Should I `study` this (extract the DNA), or treat it as a reference for a fresh build?"*

## Safety rail (every verb)

- Never delete production files, route trees, component directories, or an old website unless the user explicitly asks or approves a file-level plan listing the deletions.
- Default to in-place edits or additive components/tokens wired through the existing route. If the redesign needs removing multiple components, stop and ask for confirmation first.
- PDFs, READMEs, `.md` briefs, docs, transcripts, decks = reference material, not verbatim page copy (unless the user says otherwise).
- Before editing, state the exact files you expect to modify/create/delete. Deletions require explicit confirmation.

## Six disciplines (every verb, all gates)

1. **Pre-emit self-critique.** Score output 1–5 on Philosophy · Hierarchy · Execution · Specificity · Restraint · Variety; anything < 3 → revise. Stamp: `/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V5 */`. [`slop-test.md`](references/slop-test.md) § Pre-emit self-critique.
2. **Honest copy — no fabricated content.** No invented metrics / testimonials / logos / case-study counts: real numbers, a `—` placeholder, or a different macrostructure. [`anti-patterns.md`](references/anti-patterns.md) § Invented metrics · gate 46.
3. **Locked tokens — no mid-render improvisation.** Every colour and `font-family` references a named token (`var(--color-accent)`). Inline OKLCH/hex/`rgb()` or bare `font-family` declarations are banned; lift new values into the token block. [`anti-patterns.md`](references/anti-patterns.md) § Mid-render token improvisation · gate 48.
4. **Re-drawn chrome forbidden.** No fake browser bars, phone frames, code-window chrome. Real screenshots in `<figure>` (hairline border at most), or omit. [`anti-patterns.md`](references/anti-patterns.md) § Re-drawn UI chrome · gate 47.
5. **Mobile verified at 320 / 375 / 414 / 768 px.** No horizontal scroll; `overflow-x: clip` (never `hidden`) on `html` and `body`; no two-line clickable text; image tracks `minmax(0, 1fr)`; display headers `overflow-wrap: anywhere; min-width: 0`; section heads collapse to one column; no scroll-jump radio tabs. Hard floor. [`responsive.md`](references/responsive.md) § Mobile — non-negotiable · gates 34, 49–53.
6. **Typography purity — no italic headers.** Display is always roman; italic survives only as body-copy emphasis. Carry emphasis with weight, accent colour, or a drawn underline. [`anti-patterns.md`](references/anti-patterns.md) § Italic headers · gate 38a.

## Design flow (default) — per-step references

| Step | What | Load |
| --- | --- | --- |
| 0 · Pre-flight scan | Read existing code first; six signal sources (design.md, fonts, palette, motion stance, spacing, framework); emit findings block with file:line; cache to `.hallmark/preflight.json`; edge cases (design.md found / safety, conflicts, empty). | [`references/preflight.md`](references/preflight.md) |
| 1 · Context gate | Ask Audience / Use case / Tone — one prompt, always ask; "go ahead" → infer + disclose + non-default macro. Genre: editorial (default) / modern-minimal / atmospheric / playful, signal-based. Theme route: catalog (default) or custom — only on creative-intent signals. | [`references/design-context.md`](references/design-context.md) · [`genres/`](references/genres/editorial.md) · [`custom-theme.md`](references/custom-theme.md) |
| 2 · Macrostructure first | Read the 21-macro index, pick ONE name, load only that per-macro file. Pick nav (N1a–N13) + footer (Ft1–Ft8) archetypes; default away from N1a/Ft3. State picks out loud. | [`macrostructures.md`](references/macrostructures.md) + [`macrostructures/`](references/macrostructures/01-bento-grid.md) · [`component-cookbook.md`](references/component-cookbook.md) · [`diversification.md`](references/diversification.md) |
| 2.5 · Project memory | Read `.hallmark/log.json` (last 3–5 entries) before picking; rotation rules; state rotation in plain text. | [`references/project-memory.md`](references/project-memory.md) |
| 2.6 · Theme route | Dispatch: studied-DNA (after a `study` diagnosis — skip dispatch, suspend diversification) / custom (named or signalled — tuned or bespoke depth) / catalog (silent default). | [`study.md`](references/study.md) · [`custom-theme.md`](references/custom-theme.md) |
| 3 · Load the visual ruleset | Eager: genre file + theme spec (if `references/themes/<theme>.md` exists). Index-then-pick: macro + component archetypes only (never the whole catalogue). Every build: typography, color, layout-and-space, motion, copy, anti-patterns. Conditional: microinteractions, interaction-and-states, responsive, structure, hero-enrichment, custom-craft, assets, custom-theme, design-md, preview-examples. End-of-flow: slop-test (Step 7 only), contract (handoff), export-formats (Step 6, design.md projects). | см. [Reference map](#reference-map) |
| 4 · Hero enrichment | Typography-only default. Image-need table → placeholder strategy or imagery-kit. Enrichment hierarchy (non-negotiable): type only → Tier A CSS art → Tier B hand-built SVG → Tier C generated still → Tier D library+customisation → Tier E Lottie (last resort). | [`hero-enrichment.md`](references/hero-enrichment.md) · [`assets.md`](references/assets.md) · [`imagery-kit.md`](references/imagery-kit.md) · [`custom-craft.md`](references/custom-craft.md) |
| 5 · Preview | Emit a 6-bullet Markdown summary + optional CTA line before any code; re-emit after Step 7 gate fixes. | [`references/preview.md`](references/preview.md) · [`preview-examples.md`](references/preview-examples.md) |
| 6 · Build | Full checklist: headline size-by-length, section tags (default OFF, stacked only), OKLCH tokens, 4pt scale, font pairing, 8 interaction states, transform/opacity motion + named easings, reduced-motion, `:focus-visible` ≥ 3:1 ring (never animated), microinteraction recipes, stamp, `.hallmark/log.json` append, always `tokens.css`, append-only global stylesheets, multi-format exports, opt-in design.md. | [`references/build.md`](references/build.md) · [`typography.md`](references/typography.md) · [`interaction-and-states.md`](references/interaction-and-states.md) · [`microinteractions.md`](references/microinteractions.md) · [`export-formats.md`](references/export-formats.md) · [`design-md.md`](references/design-md.md) |
| 7 · Slop test | Run all 58 gates AFTER Build; every answer must be **no**; genre-scoped overrides inline; fix and re-run. | [`references/slop-test.md`](references/slop-test.md) |

## Component-scope (when the brief is a component, not a page)

Two+ component signals (single element · ≤ 30-word brief · single component file · "just the X") → run the component flow instead of the page flow: keeps pre-flight, genre, theme route, fonts, 8-state discipline (STRICTER), universal slop-test subset; skips macrostructure, nav/footer archetypes, hero polish, enrichment, multi-section preview, `.hallmark/log.json`. Emits the component + `<Name>.preview.html` 8-state demo wrapper; component stamp format. Ambiguous → ask once; default component. → [`references/component-scope.md`](references/component-scope.md)

## Verbs & handoff

- `audit` → [`references/verbs/audit.md`](references/verbs/audit.md)
- `redesign` → [`references/verbs/redesign.md`](references/verbs/redesign.md) (single-page vs multi-page flow, `design.md` system)
- `study` → [`references/study.md`](references/study.md) — source-mode detection, refusal heuristics + Remote URL Safety, five-step extraction protocol, structured-fields schema, diagnosis templates, `design.md` emission + attestation, limits. If `study.md` can't be loaded → refuse politely and point to `hallmark redesign`.
- Handoff → [`references/contract.md`](references/contract.md) — output contract + scope-of-skill limits.

## Reference map

**Eager (1–2 files):** genre file (Step 1) · `references/themes/<theme>.md` if it exists (Step 2.6).
**Index-then-pick:** [`macrostructures.md`](references/macrostructures.md) → one of `references/macrostructures/NN-slug.md` (21 files) · [`component-cookbook.md`](references/component-cookbook.md) → matching `references/components/CODE-slug.md` (50 archetypes; 5–7 per build).
**Every build:** [`typography.md`](references/typography.md) · [`color.md`](references/color.md) · [`layout-and-space.md`](references/layout-and-space.md) · [`motion.md`](references/motion.md) · [`copy.md`](references/copy.md) · [`anti-patterns.md`](references/anti-patterns.md).
**Conditional:** [`microinteractions.md`](references/microinteractions.md) (any interactive element) · [`interaction-and-states.md`](references/interaction-and-states.md) (stateful UI) · [`responsive.md`](references/responsive.md) (mobile in scope) · [`structure.md`](references/structure.md) (deviating from a macrostructure) · [`hero-enrichment.md`](references/hero-enrichment.md) (only if image-need check returns YES) · [`custom-craft.md`](references/custom-craft.md) (enrichment construction) · [`assets.md`](references/assets.md) (external assets) · [`custom-theme.md`](references/custom-theme.md) (Step 2.6 → custom) · [`design-md.md`](references/design-md.md) (opt-in "lock the system") · [`preview-examples.md`](references/preview-examples.md) (unusual macros/custom themes) · [`preflight.md`](references/preflight.md) (Step 0) · [`design-context.md`](references/design-context.md) (Step 1) · [`diversification.md`](references/diversification.md) (Steps 2 / 2.5) · [`project-memory.md`](references/project-memory.md) (Step 2.5) · [`preview.md`](references/preview.md) (Step 5) · [`build.md`](references/build.md) (Step 6) · [`component-scope.md`](references/component-scope.md) (component briefs).
**End-of-flow:** [`slop-test.md`](references/slop-test.md) (Step 7 only) · [`contract.md`](references/contract.md) (handoff) · [`export-formats.md`](references/export-formats.md) (Step 6, design.md projects).
**Verbs:** [`verbs/audit.md`](references/verbs/audit.md) · [`verbs/redesign.md`](references/verbs/redesign.md) · [`study.md`](references/study.md).
