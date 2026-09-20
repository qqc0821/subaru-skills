# Render and Validate

## Render every slide to an image
Goal: inspect real pixels, not geometry.

### Native builder (Path A / B')
- If the builder exposes an export API (e.g. `presentation.export({ slide, format: "png" })`), use it - one PNG per slide.
- Also export a montage/contact sheet for deck-level flow.

### PPTX files (any path)
Use a renderer if available:
```
soffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
# re-render a single page: pdftoppm -f 5 -l 5 ...
```
If neither `soffice` nor `pdftoppm` is installed (see `../../scripts/detect_capabilities.py`), say so;
do not claim visual verification you did not perform.

### HTML deck (Path C)
```
npx playwright screenshot "file:///abs/path/slide.html" preview.png --viewport-size=960,540 --wait-for-timeout=1000
```

## Validate
- Pixels: run the skill's own detector over the renders -
  `python3 scripts/detect_pixel_artifacts.py <renders>/ --detail`.
  It flags wrapped numeric groups, oversized shrink-to-fit glyphs and thin bands
  crossing a colour boundary. See `pixel-artifacts.md` for thresholds and fixes,
  and for the defects it deliberately does **not** claim to detect.
- Structural: report slides, charts, tables, images, text, fonts and placeholders from the
  built file itself (the host's own inspection capability, when available).
- Layout heuristics: if the host provides a layout validator, run it and fix blocking findings.
- Automated checks are **estimates**: treat layout heuristics as warnings, not verdicts.
  State what was **not** verified (e.g. "not opened in real PowerPoint").

## If this skill is used from its development repository
<!-- repo-only -->
The commands below ship with the **subaru-skills development repository**, not with the
installed skill package. Use them only when you are working inside that repository;
otherwise rely on the host's own tooling and the renderer commands above.

- `python3 tools/validate_pptx.py deck.pptx` - structural errors (blank slide, out-of-bounds,
  placeholder text) plus heuristic warnings (text overflow, mixed fonts).
- `make validate PPTX=...` / `make render PPTX=... [OUT=dir]` / `make montage DIR=slides/ [OUT=file]`.
- `python3 tools/pptx_inspect.py deck.pptx` - raw structural metrics (slides, charts, tables, images, fonts).
<!-- /repo-only -->

## Contact sheet
Generate a montage for deck-level rhythm and consistency. Never use it to judge a single slide.
