# Design Systems and Custom Styles

A style is not just a color palette: it is a visual philosophy - typography ratios, composition rules,
and emotional intent. There are three ways to get one.

## 1. Pick a proven preset (default)
Read `../styles/index.json`, then `../styles/foundation.json`, and match `theme_recommendations`,
`formality` and `path`. `foundation.json` is the single source for readable type scales,
CJK font resolution, spacing and diagram grammar. Each preset carries palette, visual character,
base style prompt, layout blocks and pitfalls; it must not lower the foundation's content-text floor.

## 2. Derive a custom style from a reference (e.g. "Ghibli", "Doraemon")
Treat the reference as **style DNA**, not a request to draw copyrighted characters.
Extract, then write a preset (see "Adding a style" below):
- shape language: round / angular / geometric / organic
- line quality: thin uniform / thick varied / sketchy / brushwork
- palette: specific colors from that aesthetic
- character style: proportions, expressiveness
- background treatment: detailed / minimal / abstract
- emotional tone: warm / energetic / philosophical / surreal

## 3. Import a brand / design system
When the user provides brand guidelines, a UI kit, or a design-system folder:
1. Extract tokens: colors, type scale, spacing, logotype rules, component grammar.
2. Treat the system's prompt as a **binding visual constraint** for the whole deck.
3. Record the binding (source path + a hash) so it can be verified later.
4. For a deck that must follow a template, use `template-following.md`.

## Adding a style
Write the preset by hand: copy an existing `styles/<id>.md`, then register it in
`styles/index.json` (`styles` array + `count`). Keep both in sync in the same change, so the
registry stays the single source of truth.

```yaml
id: my-style
name: 我的风格
name_en: My Style
tier: 3
themes: [创意/艺术]
formality: low
path: A_or_B2
sample: null
proven: false          # set true only after a reference sample exists
palette: { background: "#FFFFFF", text: "#1A1A1A", accent: ["#D4480B"] }
typography: { heading: "heavy sans", body: "regular sans", cjk_tone: "neutral sans" }
```

Keep the base style prompt short (<=5 lines).
<!-- repo-only -->
> In the **subaru-skills development repository** there is a helper for this:
> `python3 tools/new_style.py my-style --name "我的风格" --register`. It is not part of the
> installed skill package, so do not call it from an installed copy.
<!-- /repo-only -->
