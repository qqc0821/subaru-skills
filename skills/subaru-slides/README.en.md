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

`scripts/detect_pixel_artifacts.py` (stdlib-only, read-only, offline) checks each rendered slide PNG for three defects visible only in pixels: an orphaned numeral after a wrapped group, a glyph blown up by shrink-to-fit, and a thin band crossing a colour boundary. Thresholds and build-time prevention: [references/qa/pixel-artifacts.md](references/qa/pixel-artifacts.md).

Minimum fallback when only uv is available:

~~~bash
uv run scripts/create_slides.py a.webp b.webp --layout fullscreen --output out.pptx
~~~

Supported layouts: fullscreen, title_above, title_below, title_left, center, and grid. This path performs image assembly only.

## Styles

`styles/index.json` is the single source of truth for style data (IDs, Chinese/English names, theme recommendations, formality, allowed paths, sample mappings, proven status); `styles/router.md` is a generated selection digest of it (the only style file an agent reads when picking a direction); each style also has a `styles/<id>.md` preset, and sample images live in `assets/style-samples/`.

## More

- Runtime rules, workflow, and checkpoints: [SKILL.md](SKILL.md)
- Workflow and path details: [references/workflow.md](references/workflow.md)
- Design and QA: [references/qa/checklist.md](references/qa/checklist.md)
- Redistribution: this skill contains third-party documents and sample images; confirm each licensing boundary before redistribution.

## Versions, updates, and stable releases

Read `metadata.version` in the installed `SKILL.md` for the package version. A `-dev.N` suffix marks unpublished development content, which may change before release; use CLI source records or a Git commit for exact revision tracking.

The default installation fetches the latest content from `main`, including unpublished changes. This differs from the latest stable release.

For [skills CLI](https://github.com/vercel-labs/skills#skills-update) installations, run project updates from the original project directory, or select global scope:

~~~bash
npx skills update subaru-slides -p
npx skills update subaru-slides -g
~~~

Updates use recorded sources and content, rather than selecting a stable Release from `metadata.version`. If an older CLI lacks the command or source records are missing, reinstall with the original `npx skills add` command, choosing the same agent and scope (add `--global` for global installations). Back up customizations first; reload the skill or start a new session as required by your host afterward.

For manually downloaded ZIPs or copied folders, download the desired branch or release again, back up the old folder, and replace the entire installed folder with the corresponding `skills/<name>/` folder to avoid retaining deleted files. Pulling the downloaded repository does not synchronize copied installations, and manual copies are not guaranteed to be tracked by the CLI.

Stable versions: [GitHub Releases](https://github.com/qqc0821/subaru-skills/releases). As of 2026-10-06, the remote has no Release or tag, so no stable version is available for installation. The historical `0.1.0` record does not establish a published stable release.

Once a release exists, choose an actual tag containing the desired skill:

~~~bash
# Template: replace <release-tag> with an existing tag from the Release page
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>" --skill subaru-slides
~~~

A fixed tag installation retains that version and does not automatically switch to newer stable tags. Read the target release notes and reinstall using the new tag URL to upgrade. Reinstall without a tag to return to the default branch.
