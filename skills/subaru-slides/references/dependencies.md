# Runtime and dependency notes

`subaru-slides` is designed to work in a project-local Codex skill directory.

## Core image-to-PPTX path

- Python 3.10 or newer
- `uv` for isolated execution
- `python-pptx>=1.0.0`
- `Pillow>=10.0.0`
- Entry point: `scripts/create_slides.py`

The helper uses PEP 723 inline metadata, so a separate virtual environment or committed dependency cache is not required. Run it with `uv run` from the project root.

## Editable HTML path

Use the available `$presentations` skill to convert HTML slides into editable PPTX files and to preview them. The helper paths and Node.js packages for this path are owned by that workflow; do not hard-code a home-directory path here. If `$presentations` is unavailable, switch to the core image-to-PPTX path rather than guessing an installation path.

## Optional illustration path

Use the native `imagegen` capability when bitmap illustrations are useful. No Gemini key, provider-specific CLI, sibling repository, or external image skill is required by this skill.

## Local resources

- `../assets/style-samples/` contains the bundled visual references.
- `references/` contains the design framework and prompt templates.
- No secret files, generated outputs, font downloads, or dependency caches belong in this skill directory.
