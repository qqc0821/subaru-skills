# Optional Integrations

These are **enhancers, never requirements**. Detect them with `scripts/detect_capabilities.py`
and use them only when present; otherwise fall back per `dependencies.md`.

| Integration | Adds | Used by |
|---|---|---|
| Native builder (e.g. `@oai/artifact-tool`) | native editable text/charts/tables + validators | Path A / B' |
| Anthropic `pptx`-style skill | OOXML editing, template following, layout validation | Path A |
| `python-pptx` (+ Pillow) | pure-Python native fallback and image assembly | Path A / fallback |
| Image generation | AI visual bases | Path B / B' |
| `deck-stage`-style runtime | HTML deck with navigation + notes | Path C |
| HTML->editable-PPTX converter | native PPTX from an HTML deck | Path C export |
| `render_preview` (LibreOffice + Poppler) | per-slide PNG for visual QA | QA |

## Principle
A deck must still be producible when every integration above is absent: the bundled
`scripts/create_slides.py` (Python 3.10+, `uv run`) is the floor.
