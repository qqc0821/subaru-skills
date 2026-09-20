# subaru-slides

A Chinese-first presentation skill that turns a topic, source material, or existing document into a clear PPTX or HTML deck with explicit editability boundaries.

## Invocation

Copy this directory into your Agent's skill directory, or install it:

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-slides
~~~

~~~text
Use $subaru-slides to turn this market analysis into a 10-slide executive presentation.
~~~

Invoke `$subaru-slides` explicitly, or let the host Agent select it implicitly for PPTs, slides, presentations, Keynote, pitches, reports, or training material.

Guided collaboration is the default: the Agent asks for confirmation at the outline, style direction, and key-slide preview checkpoints. You can also choose Full Auto or Collaborative, pick the output form (editable PPTX / visual PPTX / single-file HTML deck), and supply audience, duration, tone, and brand rules.

## Execution paths and editability

Probe host capabilities first, then pick a path in this order: **A native editable → B' hybrid → C HTML deck → B full AI visual → fallback**; editable content uses native objects by default.

| Path | Product | Editability boundary |
|---|---|---|
| A | Native editable PPTX | Text, tables, and charts stay editable |
| B' | AI base + native text/charts | Base image is not editable; text and charts are |
| C | Single-file HTML deck | HTML stays statically editable; no converter means no PPTX promise |
| B | Full AI visual PPTX | Each slide is one image; text is generally not editable |
| fallback | Image-only PPTX | Image assembly only; native editability is not restored |

## Capabilities and degradation

`scripts/detect_capabilities.py` probes the native builder, image generation, the HTML runtime, and renderers. All of them are optional enhancers: when one is missing, execution moves to the next path and says so explicitly — nothing is silently rerouted, and an image-only PPTX is never presented as editable.

Minimum fallback when only uv is available:

~~~bash
uv run scripts/create_slides.py a.webp b.webp --layout fullscreen --output out.pptx
~~~

Supported layouts: fullscreen, title_above, title_below, title_left, center, and grid. This path performs image assembly only.

## Styles

`styles/index.json` is the single source of truth for style data (IDs, Chinese/English names, theme recommendations, formality, allowed paths, sample mappings, proven status); each style also has a `styles/<id>.md` preset, and sample images live in `assets/style-samples/`.

## More

- Runtime rules, workflow, and checkpoints: [SKILL.md](SKILL.md)
- Workflow and path details: [references/workflow.md](references/workflow.md)
- Design and QA: [references/qa/checklist.md](references/qa/checklist.md)
- Redistribution: this skill contains third-party documents and sample images; confirm each licensing boundary before redistribution.
