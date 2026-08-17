# Step 5 · Preview

Loaded before emitting any code in the default Design flow. The preview is the user's TL;DR — scannable in five seconds so they can redirect *before* you write 500 lines of CSS that don't match their intent.

## Format

Markdown bullets, not ASCII boxes (they render reliably across every chat client and terminal):

```markdown
**Hallmark · v1.1.0**

- **Macrostructure** · Stat-Led
- **Theme** · Plain (#fff paper · cool greys · ink-blue accent)
- **Enrichment** · none (typography only)
- **Sections** · Hero · Logos · Stats · Features · Testimonials · Pricing · FAQ · CTA · Footer
- **Motion** · counter · pricing-lift · pulse-once
- **Slop test** · 58 / 58 ✓ (run after Build)
- **Diversification** · differs from Newsprint on display style + accent hue
```

## The bullets

1. **Macrostructure** — the named pick from [`macrostructures.md`](macrostructures.md).
2. **Theme** — catalog: name + one-line palette summary (paper colour band · accent hue · display style). Custom: `custom (vibe: "<4–8 words>" · paper oklch(<L%> <C> <H>) · accent oklch(<L%> <C> <H>) <one-word hue label> · <display face> + <body face>)`.
3. **Enrichment** — the chosen archetype + tier, or *none (typography only)*.
4. **Sections** — section names separated by ` · `, in DOM order.
5. **Motion** — microinteraction primitives separated by ` · `, or *none — typography only*. Always under three primitives per the [`microinteractions.md`](microinteractions.md) hard rules.
6. **Slop test** — `58 / 58 ✓` if all gates pass, or `N / 58 — fails: <gate numbers>`. Run the slop test BEFORE writing this row (it's Step 7).
7. **Diversification** *(optional — only when `.hallmark/log.json` has prior entries)* — what axes differ vs the previous run.

## CTA line

One quiet, italicised line after the bullets: *"System portable? Say `lock the system` to extract this build's tokens + voice into a `design.md`."*

**Skip the CTA when** (a) the build is component-scope, or (b) `design.md` already exists at the project root (the system is already locked). See [`design-md.md`](design-md.md) for the full opt-in flow.

## After Step 7

If any slop-test gate fails at Step 7, return to the relevant Build step, fix it, and **re-emit the preview block** with the corrected slop-test row. The preview is the durable summary; it's wrong to ship if it lies.

Four worked sample preview blocks (Long Document, Bento Grid, Manifesto, Custom) live in [`preview-examples.md`](preview-examples.md) — load only when picking unusual macrostructures / custom themes and this spec isn't enough scaffolding.
