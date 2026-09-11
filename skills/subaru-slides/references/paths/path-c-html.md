# Path C - HTML Deck

**Product:** a self-contained HTML slide deck (can be presented in a browser; may export to PPTX/PDF).
**Use when:** web presentation, speaker mode, animations, or social distribution are wanted.
**Requires:** a deck runtime (e.g. `deck-stage.js`) or an HTML->editable-PPTX converter.

## Rules
- Fixed canvas: one element per slide, 16:9 (1280x720 or 1920x1080).
- Write slide content as **static HTML**, not script-generated DOM, so text stays directly editable.
- Use a shared type scale and spacing via CSS custom properties.
- Do not use the slide root for animations; put animation attributes on inner elements.

## Export to editable PPTX
If a converter is available (e.g. an HTML->native-PPTX tool), route CSS like this:
| HTML / CSS | Becomes |
|---|---|
| text, rich text, color, size, alignment | native editable text box |
| background, border, radius, lines | native geometry |
| gradient, shadow, filter, blend | local snapshot underlay; text stays native on top |
| SVG, image, canvas | embedded as-is |
Map to the converter's skill or CLI when present (detect it with `../../scripts/detect_capabilities.py`).
If no converter is available, deliver the HTML deck (and PDF) and say PPTX export is unavailable.

## Fonts
Author with the fonts that will be present at presentation time. For cross-machine CJK fidelity,
either subset-embed the fonts by used characters or stick to a documented system fallback stack
(see `../design-movements.md` and the future `typography-cjk` reference).

## Preview
Render the deck to PNG per slide (see `../qa/render-and-validate.md`) and inspect.
