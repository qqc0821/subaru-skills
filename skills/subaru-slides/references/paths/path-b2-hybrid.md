# Path B' - Hybrid (recommended default)

**Product:** AI-generated, text-free visual bases with native editable text and charts on top.
**Use when:** you want maximum visual quality **and** editable text - most real decks.
**Requires:** image generation **and** a native builder. If the builder is missing, fall back to Path B or C.

## Why this is the default
Path B looks great but bakes text into pixels (not editable, Chinese may misrender).
Path A is editable but visually plain. Path B' takes the visual richness of B and the editability of A.

## Method
1. For each slide, generate a **text-free** visual base: "no text in image", 2048x1152, base style appended.
   Describe scene + mood only (see `../illustrations.md`).
2. Build the PPTX with the native builder (Path A mechanics):
   - add the AI image as the background (cover/contain),
   - add native title/body/chart/table on top, choosing a readable zone of the image.
3. If a slide's base image leaves no clean text area, add a scrim (semi-transparent solid/gradient rectangle)
   behind the native text, then re-check contrast.
4. Export, render, and inspect every slide.

## Checks specific to B'
- No text rendered inside the AI image (otherwise editability is lost).
- Native text contrast over the image is sufficient.
- One shared style block so the imagery stays consistent across slides.
- Charts/tables remain native, not baked into the image.
