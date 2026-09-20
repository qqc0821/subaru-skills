# Dependencies and Capabilities

`subaru-slides` is **capability-portable**: it probes the host and degrades gracefully.
No external skill is a hard dependency; any detected capability is an optional enhancer.

## Capabilities
| Capability | Detected by | Enables |
|---|---|---|
| Native editable builder | host-native artifact tool / available `python-pptx` workflow | Path A / B' |
| Image generation | the host's image-generation capability | Path B / B' |
| HTML deck runtime | `deck-stage.js` | Path C |
| HTML→PPTX converter | an html2pptx-style converter | Path C export |
| Renderer | `soffice` + `pdftoppm` | visual QA |
| Bundled fallback | `scripts/create_slides.py` (PEP 723) | image-only PPTX |

Run `scripts/detect_capabilities.py` (human or `--json`) to detect all of the above.
For Chinese or cross-platform delivery, also run `scripts/detect_fonts.py --locale zh-CN`.
It has no external Python dependency; without Fontconfig it reports the font result as unverified.

## Selection order
`A 原生可编辑 → B' 混合 → C HTML deck → B 全 AI 视觉 → fallback`

## Degrade rules
- **No native builder** → cannot do A/B'; use C or B and state that text will not be editable. `scripts/create_slides.py` remains available only for the image-only PPTX fallback; it does not restore native editability.
- **No image generation** → skip AI imagery; A/C use native visuals only.
- **No renderer** → run structural checks only and state that visual verification was not performed.
- **Optional skills absent** → no action needed; the probe simply reports them as unavailable.

## Bundled helper
`scripts/create_slides.py`: Python 3.10+, PEP 723 dependencies `python-pptx>=1.0.0` and `Pillow>=10.0.0`.
Run with `uv run`. Layouts: `fullscreen` / `title_above` / `title_below` / `title_left` / `center` / `grid`.

在干净检出上重建固定输入的 eval 产物需要 `uv`，用于解析 `create_slides.py` 已声明的 PEP 723 依赖。它属于测试 Harness 依赖，不是 skill 端到端运行的必需能力；缺少 uv 时应把 fallback 标为 BLOCKED，而不是静默通过。

## Local resources
- `../styles/index.json` - style registry (single source of truth).
- `references/` - design framework, paths, QA.
- No secrets, generated outputs, font downloads, or dependency caches belong in this skill directory.
