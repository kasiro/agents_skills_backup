# Diversification rules

Central home for every "no two outputs may look the same" rule. Loaded at Step 2 (macrostructure pick) and Step 2.5 (project memory). Per-rule detail lives in the linked files; this is the enforcement summary.

## Macrostructure diversification

Before picking, look for an existing `/* Hallmark · macrostructure: <name> · ... */` stamp in any CSS file in the codebase; if found, pick a *different* macrostructure. If you produced Hallmark output earlier this session, your pick must differ from the last one. Full rule in [`macrostructures.md`](macrostructures.md) § Diversification rule.

**The Specimen macrostructure is no longer a default** — reach for it only when the brief is explicitly editorial, foundry-adjacent, or the user named it.

## Theme diversification (mandatory) — the three axes

Picking a different macrostructure isn't enough: two consecutive outputs can share a theme and still read as repetition. **Two consecutive themes must differ on at least one of three axes:**

- **Paper band** — dark (L < 30 %) / mid (30–85 %) / light (> 85 %), per the theme's `--color-paper` lightness.
- **Display style** — high-contrast-serif (Specimen, Studio, Atelier) / roman-serif (Newsprint) / classical-serif (Lumen) / geometric-sans (Manifesto) / grotesk-sans (Cobalt) / rounded-sans (Hum) / mono (Terminal) / display-condensed (Sport) / display-heavy (Brutal, Carnival) / risograph-bold (Riso). All display is roman — italic headers are banned globally.
- **Accent hue** — warm (red/orange/amber 10–60°) / cool (blue/indigo/cyan 200–300°) / neutral (no chromatic accent) / chromatic-other (green: Studio · leaf-green: Garden · phosphor: Terminal).

If the previous output was Specimen (light · high-contrast-serif · warm), the next can be Studio (light · high-contrast-serif · chromatic-green) — the accent hue differs. It can't be Newsprint (light · roman-serif · warm), which differs only on display style and shares both other axes.

The per-theme axis values live as comments at the top of each theme's tokens block in [`../../site/css/tokens.css`](../../site/css/tokens.css). When in doubt, name your candidate theme out loud and identify its three axis values; if two of three match the previous output, redirect.

## Nav + footer diversification

Across consecutive Hallmark runs in the same project session (per `.hallmark/log.json`) and across multiple test builds of the same theme, **no two outputs may share the same nav archetype OR the same footer archetype.** Before writing any nav markup, state one line: *"Previous nav: <X>. This build: <Y>, because <reason>."* Rotate deliberately through the routing tables' "Acceptable also" column — e.g. Hum across Curio/Sprout/Tally/Mixtape: N5 → N1b → N12 → N13. Default away from **N1a** (wordmark + links + button-right) and **Ft3** (4 columns + social row + copyright) — the most-recognised AI fingerprints. Full routing in [`component-cookbook.md`](component-cookbook.md) § Navigation and § Footers.

## Enrichment diversification

The enrichment archetype should not repeat the last run's (`E1 clipped` twice in a row reads as templated even with different content). See [`hero-enrichment.md`](hero-enrichment.md).

## State your pick

Before writing any code, say in plain text: *"Macrostructure: <name>. Theme: <name>. Differs from the last on: <axes>."* This accountability step — picking on the page, not in your head — is what prevents default-attractor sameness. If the brief is genuinely vague, offer three macrostructures from *categorically different* groups (grid-led like Bento, document-led like Long Document, poster-led like Manifesto) — three concrete choices, not seven abstract tones.

Custom runs are theme-route-blind: a custom theme must differ from the previous entry on at least one of the three axes, same as catalog-vs-catalog. Custom entries record their axes explicitly into `.hallmark/log.json` (see [`custom-theme.md`](custom-theme.md) § F). Studied-DNA runs suspend diversification (see [`study.md`](study.md)).
