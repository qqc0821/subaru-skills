# Design Systems and Custom Styles

A style is not just a color palette: it is a visual philosophy - typography ratios, composition rules,
and emotional intent. There are three ways to get one.

## 1. Pick a proven preset (default)
Read `../styles/index.json`, match `theme_recommendations`, then `formality` and `path`.
Each preset `../styles/<id>.md` carries palette, typography, base style prompt, layout blocks, and pitfalls.

## 2. Derive a custom style from a reference (e.g. "Ghibli", "Doraemon")
Treat the reference as **style DNA**, not a request to draw copyrighted characters.
Extract, then write a preset with `tools/new_style.py`:
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
```bash
python3 tools/new_style.py my-style --name "我的风格" --name-en "My Style" --tier 3 --themes "创意/艺术" --register
```
Keep the base style prompt short (<=5 lines). Registering updates `styles/index.json` atomically
(and its `count`), so the registry stays the single source of truth.
