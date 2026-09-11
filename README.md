# subaru-skills

Project-local Agent Skills.

## Included skills

### `subaru-slides`

`skills/subaru-slides/` provides an end-to-end workflow for turning source content into a polished PPTX deck, including content structuring, visual-system selection, optional bitmap illustration generation, editable HTML-based assembly through the available presentations workflow, and a bundled image-to-PPTX fallback.

Use it explicitly as `$subaru-slides`, or let the skill be selected automatically when the task is about making slides, presentations, or PPTX files.

The bundled fallback script declares its Python requirements inline (Python 3.10+, `python-pptx>=1.0.0`, `Pillow>=10.0.0`) and can be run from the repository root:

```bash
uv run skills/subaru-slides/scripts/create_slides.py slide-01.png slide-02.png --layout fullscreen -o output.pptx
```
