# Proven Styles Gallery

> **The single source of truth for style data is `../styles/index.json`** (23 presets,
> one `../styles/<id>.md` each). This file keeps only the cross-style **selection strategy**
> and the **rationale for the tiers**. Palette / typography / prompt live in the presets.

## Core finding
Illustration/comic styles generate far better than "professional minimal" styles: comics have an explicit
visual language (lines, characters, color blocks), while minimal dark-background styles lack visual elements
and come out empty and flat.

## Tiers
- **Tier 1 (best results):** `warm-comic-strip`, `manga-educational`, `ligne-claire`, `neo-pop-magazine`
- **Tier 2 (specific scenes):** `whiteboard-sketch`, `soviet-constructivism`, `dunhuang-mural`, `ukiyo-e`, `oatmeal-comic`, `neo-brutalism`
- **Tier 3 (needs the right scene):** `warm-narrative`, `risograph`, `isometric`, `bauhaus`, `blueprint`, `vintage-ad`, `dada-collage`, `pixel-art`
- **Path A editorial systems:** `pentagram-editorial`, `fathom-data`, `muller-brockmann-grid`, `build-luxury-minimal`, `takram-speculative`

## How to choose
1. Read `../styles/router.md` (generated from `../styles/index.json`) and match the theme recommendations.
2. Filter by `formality` and the `path` allowed by the capability probe.
3. Offer 3 candidates that differ in direction; show each `../styles/<id>.md` one-liner + sample.
4. 17 styles have sample images; the 6 Path A styles have `sample: null` (to be added).

## Per-style details
Everything lives in `../styles/<id>.md`. For the Snoopy method, see `proven-styles-snoopy.md`.
