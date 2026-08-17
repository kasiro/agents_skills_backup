# Step 2.5 · Check project memory

Loaded before picking macrostructure or theme, when the project may have a `.hallmark/log.json` file (created by previous Hallmark runs).

## Schema

The file is a JSON array, newest entry first:

```json
[
  { "date": "2026-04-30", "macrostructure": "Bento Grid",   "theme": "Coral",   "enrichment": "E1 clipped-edge",  "brief": "Tracejam · SaaS observability" },
  { "date": "2026-04-28", "macrostructure": "Long Document","theme": "Garden",  "enrichment": "E5 hand-built SVG", "brief": "Maple Street Bread · bakery" },
  { "date": "2026-04-25", "macrostructure": "Manifesto",    "theme": "Manifesto","enrichment": "none",            "brief": "Meridian · studio manifesto" }
]
```

Custom entries carry `"theme": "custom"` plus `"theme_axes": "<paper-band> / <display-style> / <accent-hue>"` and optional `"vibe": "<4–8 words>"` — see [`custom-theme.md`](custom-theme.md) § F.

## Rotation rules (use the last 3–5 entries)

- **Macrostructure** must not match any of the last three.
- **Theme** must differ from the last on at least one axis (paper band / display style / accent hue — see [`diversification.md`](diversification.md)).
- **Enrichment** should not repeat the last archetype.

## Missing file / stamp-only

- No `log.json` → first Hallmark run for this project: no constraint, but the file will be created in Step 6.
- CSS stamp present but no `log.json` → infer one entry from the stamp and proceed.

## State the rotation in plain text

> *"Last 5 builds: Bento Grid (Tracejam) · Bento Grid (Foundry) · Long Document (Maple) · Manifesto (Meridian) · Quote-Led (Tide). Bento Grid used 2 of 5 — picking from {Marquee Hero, Stat-Led, Workbench, Letter} this time. I'll go with Marquee Hero."*
>
> *"Last 3 themes: Coral · Bloom · Riso. Picking from {Newsprint, Atelier, Studio, Garden} — Newsprint differs on display style and accent hue."*

## Three sample shapes

- **First-time** (no `log.json`, fresh project): no rotation block — just the pick. *"This is the first Hallmark run for this project. Picking Long Document — fits the Coffeebox brief's editorial tone."*
- **Mature project** (5+ entries): the frequency-count / exclusion-list / pick format above.
- **User overrode last run** ("use Bento Grid again, I want the same shape"): *"Last build was Bento Grid (you requested it). You've asked for it again — I'll pick different knob values. Knob deltas: tiles=8 (was 6), accent=full-bleed (was corner-only), spans=irregular (was even). Same archetype, different fingerprint."*

The rotation block keeps the user inside the discipline without making them read the rules. Skip it and the user starts thinking the diversification is theatre.
