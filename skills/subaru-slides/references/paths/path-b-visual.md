# Path B - Full AI Visual

**Product:** every slide is a complete AI-generated image; assembled into a PPTX.
**Use when:** maximum visual impact, artistic/quick drafts, or the host has image generation but no native builder.
**Trade-off:** text is baked into the image - not editable; Chinese may occasionally misrender.

## Method
1. Define one base style (from `../styles/<id>.md`), short (<=5 lines).
2. Write per-slide prompts using the structure in `../illustrations.md`; include all text verbatim.
   Keep Chinese titles <=8 characters and body lines <=30 characters.
3. Generate in parallel batches of 3-5; save as `slide-NN-name.png` (16:9, @2048x1152).
4. Verify every slide image for text accuracy and style consistency; regenerate wrong ones.
5. Assemble with the bundled helper:
```
uv run scripts/create_slides.py slide-01.png slide-02.png ... --layout fullscreen -o output.pptx
```

## Layouts (create_slides.py)
| Layout | Use case |
|---|---|
| `fullscreen` | AI full-page slides (Path B default) |
| `title_above` / `title_left` | image + editable title (small hybrid) |
| `center` | centered image with padding |
| `grid` | multiple images per slide |

## Quality check after generation
1. Text accuracy - verify all Chinese/English text.
2. Layout - elements positioned as described.
3. Style consistency across slides.
4. If text is wrong, regenerate with shorter text (do not try to patch the image).
