# Path A - Native Editable

**Product:** a PPTX in which every text, table, and chart is a native, editable object.
**Use when:** the deck must be edited later, follow a corporate template, or carry accurate data.
**Requires:** a native builder - Codex `@oai/artifact-tool`, the Anthropic `pptx` skill, or plain `python-pptx` (bundled fallback).
**Not:** screenshots of slides, or a single image per page.

## Rule: editable by default, raster by exception
Any text/table/chart that may be edited must be native. Only decorative visuals may be bitmaps.

## How to build
1. Resolve a font available on the host; if none, fall back to a web-safe family and say so.
2. Declare slide size in EMU (16:9 = `12192000 x 6858000`).
3. Use the builder API to add native objects:
```
slide = presentation.slides.add()
shape  = slide.shapes.add(geometry, position, fill, line)
text   = slide.shapes.add({ geometry: "textbox", position }); text.text = "..."
chart  = slide.charts.add("bar", { categories, series, ... })
table  = slide.tables.add({ rows, columns, position })
slide.speakerNotes.textFrame.setText("...")
```
4. A reference implementation of the whole flow (cover, chart, cards, footer, notes, export,
   finalize with validators) lives in the project history: `.codex-build/ev-trends/build.mjs`.

## Native evidence guardrails
See `../native-evidence.md` (P1 - being expanded). Until then:
- Charts: set units/signs/precision explicitly; show 31% as `0.31`, not `31@@; remove placeholder "Chart Title";
  stacked labels use `inEnd`/`center`; set the chart font explicitly.
- Tables: compute each total once and reuse it in table, title, and notes; keep template alignment.
- Bullets: use the native paragraph API; never fake bullets with characters or multiple text boxes.

## Unit guardrails
- Shape geometry: EMU (914400 per inch).
- Paragraph `marginLeft` / `indent@@: EMU (1pt = 12700).
- `spaceBefore` / `spaceAfter`: hundredths of a point (100 = 1pt).
Do not double-convert imported paragraphs.

## Assembly and preview
- Export to PPTX; if the host provides a finalizer with validators, run it (structure, charts, tables, layout).
- Render every slide to PNG and inspect (see `../qa/render-and-validate.md`).
- The fallback (no native builder) is `../paths/path-b-visual.md` with `scripts/create_slides.py`.
