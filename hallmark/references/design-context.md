# Step 1 · Design-context gate

Loaded in the default Design flow before any code. Covers: the three questions, the inference protocol, genre detection, and the catalog/custom theme-route signals.

## The three questions

Hallmark works best knowing three things: **Audience** (who will use this, what do they know), **Use case** (the one job / one action the page drives), **Tone** (pick an extreme — editorial · brutalist · soft · utilitarian · luxury · playful · technical · austere; "clean and modern" is not a tone).

**Always ask — answering is optional.** Send the prompt **once**, in one message, bold the three labels, no laddered follow-ups:

> *Before I build, I need three things:*
> *1. **Audience** — Who will use this? What do they care about?*
> *2. **Use case** — What's the one action the page should drive? (Sign up? Subscribe? Read? Buy?)*
> *3. **Tone** — Pick an extreme: editorial · brutalist · soft · utilitarian · luxury · playful · technical · austere. "Clean and modern" isn't a tone.*
> *Or say **"go ahead"** and I'll infer from the brief — I'll tell you what I picked.*

No exceptions for complete briefs or short briefs — the default is to ask; the cost of asking is one message, the cost of guessing wrong is a whole rebuild.

**One exception where the gate is silent:** `audit`, `study`, or `redesign --mood` — those read context from the target, not the user.

## Inference protocol (opt-out)

If the user says "go ahead" / "you pick" / "just build it" / "don't ask", or skips fields, or doesn't engage after one prompt:

- Infer audience, use case, tone from the brief, domain, and visible context (filename, framework, surrounding code is fair game *now* — only because the user delegated).
- **State the inferences in one sentence at the top of your reply:** *"Going with: audience = X · use = Y · tone = Z. If any of those is wrong, tell me and I'll redirect."*
- Stamp them in the CSS comment alongside the macrostructure (Step 4).
- Pick a **non-default** macrostructure — Specimen fall-through is banned even on inferred briefs.

**Do not skip the inference disclosure** — the opt-out is a courtesy, not an excuse to be opaque.

## Genre — pick before themes

Four genres: **editorial** (default, canonical anti-slop voice), **modern-minimal** (Stripe/Linear/ElevenLabs), **atmospheric** (Suno/Runway/dark-AI-tool), **playful** (post-Linear soft). Detection is signal-based — silent default to editorial unless the brief fires one of these:

- *AI tool, generative, music, video, voice, late-night, dark mode, atmospheric* → **atmospheric** → load [`genres/atmospheric.md`](genres/atmospheric.md)
- *SaaS, enterprise, API, platform, developer tool, infra, B2B, dev experience* → **modern-minimal** → load [`genres/modern-minimal.md`](genres/modern-minimal.md)
- *fun, consumer, casual, friendly, onboarding, family, community* → **playful** → load [`genres/playful.md`](genres/playful.md)

Two non-default signals firing (rare) → ask one short follow-up naming the two candidates. Default with no signal: silent **editorial** → load [`genres/editorial.md`](genres/editorial.md). The chosen genre file loads eagerly (it scopes everything downstream); other genre files stay on disk. State the genre out loud at Step 2.5 alongside macrostructure and theme.

## Theme route — catalog vs custom (signal detection)

Two routes: **catalog** (20 named themes — Specimen, Atelier, Brutal, Newsprint, Studio, Manifesto, Terminal, Midnight, Almanac, Garden, Riso, Sport, Bloom, Coral, Cobalt, Aurora, Editorial, Carnival, Lumen, Hum) and **custom** (made-to-measure OKLCH palette + free-font pairing). **Catalog is the default.** Catalog rotation is scoped to the genre's theme cluster. Do **not** offer the user a choice on every prompt.

Surface the catalog/custom fork **only** when the brief carries one of these signals:

- User explicitly says **custom theme** / **tailored to our brand** / **make it ours** / **something unique** / **play with the colors and fonts**.
- User names a **specific brand colour** as anchor ("use our terracotta", "the brand red is hex #c0392b").
- User describes a **multi-attribute aesthetic** that doesn't map to a single catalog theme — 3+ vibe words ("moss, lichen, soft pink, herbal"). One adjective is a tone, not a custom signal.
- User attaches a **brand-mood reference** (swatch, moodboard, Pantone chip) without asking to study a screenshot.

If a signal fires, ask one short follow-up: *"This brief reads like a custom palette would fit better than the catalog. Want me to construct a custom OKLCH palette + free-font pairing tuned to <one-line vibe>, or stay on the catalog for variety + speed?"* Silence routes to catalog.

**Custom has two depths** — *tuned* (palette + fonts on Hallmark's structures) and *bespoke* (own structure too, for "no theme / from scratch / fully bespoke" or a page-shape no catalog macrostructure fits). Both fire the one fork above, default to catalog on silence, and pass every slop-test gate. See [`custom-theme.md`](custom-theme.md) § Bespoke depth.

If no signal fires: **proceed with catalog silently. Do not mention the fork.**
