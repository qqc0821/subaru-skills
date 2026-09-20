# subaru-skills

A Chinese-first [Agent Skills](https://agentskills.io/) repository for turning topics, source material, or existing documents into clear, visually controlled presentation decks.

[中文](README.md) · [Changelog](CHANGELOG.md) · [Provenance and licensing](PROVENANCE.md)

The repository currently contains one installable skill: **subaru-slides**. It covers the full flow from content structuring and visual direction to PPTX / HTML deck construction and delivery QA. The repository root also contains a development harness that is not installed with the skill package.

## Quick start

### Install

Install the repository with the [skills CLI](https://github.com/vercel-labs/skills):

~~~bash
# Install into the current project
npx skills add qqc0821/subaru-skills

# Install into the user-level skill directory
npx skills add qqc0821/subaru-skills --global

# Install only subaru-slides
npx skills add qqc0821/subaru-skills --skill subaru-slides

# List available skills without installing
npx skills add qqc0821/subaru-skills --list
~~~

After installation, invoke $subaru-slides explicitly. Host Agents may also select it implicitly for requests involving PPTs, slides, presentations, Keynote, pitches, reports, or training material.

Without the CLI, copy skills/subaru-slides/ into the skill directory used by your Agent:

~~~bash
git clone https://github.com/qqc0821/subaru-skills.git
cp -R subaru-skills/skills/subaru-slides <your-agent-skill-directory>/
~~~

Only skills/subaru-slides/ is needed for installation. tools/, schemas/, evals/, tests/, and docs/ support repository development and regression checks.

### Use it

~~~text
Use $subaru-slides to turn this market analysis into a 10-slide executive presentation.
~~~

Guided collaboration is the default: the Agent asks for confirmation at the outline, style direction, and key-slide preview checkpoints. You can also specify:

- collaboration mode: Full Auto, Guided, or Collaborative;
- output form: editable PPTX, visual PPTX, or a single-file HTML deck;
- audience, duration, goal, tone, brand rules, and an existing template.

## How it works

subaru-slides is a thin router. Detailed methods are loaded on demand from references/:

1. **Probe capabilities**: run scripts/detect_capabilities.py before making promises.
2. **Choose a path**: select the best execution path for the available capabilities and desired output.
3. **Confirm settings**: confirm collaboration mode and output form, then fill in audience, duration, and tone as needed.
4. **Structure content**: produce assertion titles, key points, and visual types slide by slide; review the outline at Checkpoint 1.
5. **Choose a style**: match theme, formality, and path, then review three differentiated directions at Checkpoint 2.
6. **Build and preview**: create native objects or visual bases and review key slides at Checkpoint 3.
7. **QA and deliver**: render per slide when possible, inspect structure and readability, and provide the file path, receipt, and claim boundary.

The core contract is editable-by-default content, explicit capability degradation, Chinese-first slide copy, and no claim that an unperformed visual or application-compatibility check was completed.

## Execution paths and editability boundaries

The selection order is: A native editable → B' hybrid → C HTML deck → B full AI visual → fallback.

| Path | Product | Main capability | Editability boundary |
|---|---|---|---|
| A | Native editable PPTX | Native builder | Text, tables, and charts remain editable |
| B' | AI text-free base + native text/charts | Image generation + native builder | Base imagery is not editable; text, tables, and charts are |
| C | Single-file HTML deck | Deck runtime; PPTX export also needs a converter | HTML stays statically editable; no converter means no PPTX promise |
| B | Full AI visual PPTX | Image generation | Each slide is a complete image; text is generally not editable |
| fallback | Image-only PPTX | scripts/create_slides.py | Image assembly only; it does not restore native editability |

Without a native builder, the image-only PPTX fallback must not be presented as Path A. Without a renderer, only structural checks are performed and visual QA is disclosed as not performed. Chinese text inside AI images can also contain errors, so short titles and native text overlays are preferred when possible.

## Capabilities and optional dependencies

The skill has no hard dependency on another Agent skill. Host capabilities are detected as optional enhancers, with graceful degradation when they are absent:

| Capability | Enables | When absent |
|---|---|---|
| Native builder | Path A / B' | Use HTML, full visual, or image fallback; do not promise editable PPTX |
| Image generation | Visual bases for Path B / B' | Use native graphics and layout, or a path without AI imagery |
| HTML runtime / HTML-to-PPTX converter | Path C and optional PPTX export | Deliver HTML; explicitly state when PPTX export is unavailable |
| LibreOffice + Poppler | Per-slide PPTX rendering and visual QA | Run structural checks only and disclose the missing visual check |
| uv | Bundled fallback helper and its PEP 723 dependencies | The fallback cannot run in that environment |

The bundled create_slides.py declares python-pptx>=1.0.0 and Pillow>=10.0.0, resolved on demand only for the fallback. HTML presentation or export may also need Chrome / Chromium and the relevant runtime; none of these is a hard subaru-slides install dependency.

### Probe the environment

From the repository root:

~~~bash
python3 skills/subaru-slides/scripts/detect_capabilities.py
# Machine-readable output
python3 skills/subaru-slides/scripts/detect_capabilities.py --json
~~~

If the skill is installed elsewhere, replace the path with its actual location. The probe describes the current machine; it is not an installation prerequisite.

### Minimal fallback example

The checked-in WebP samples can be assembled into an image-only PPTX:

~~~bash
uv run skills/subaru-slides/scripts/create_slides.py \
  skills/subaru-slides/assets/style-samples/warm-comic-strip.webp \
  skills/subaru-slides/assets/style-samples/bauhaus.webp \
  skills/subaru-slides/assets/style-samples/blueprint.webp \
  --layout fullscreen \
  --output output.pptx
~~~

Supported layouts are fullscreen, title_above, title_below, title_left, center, and grid. The fallback validates image assembly only; it does not establish editable text, native data charts, or AI image-generation quality.

## Style system

The single source of truth for style data is [skills/subaru-slides/styles/index.json](skills/subaru-slides/styles/index.json):

- it owns style IDs, Chinese and English names, theme recommendations, formality, allowed paths, sample mappings, and proven status;
- each preset lives at skills/subaru-slides/styles/<id>.md and carries its palette, typography, Base Style Prompt, layout blocks, and pitfalls;
- sample images use assets/style-samples/<style-id>.webp, with presence defined by the registry;
- when adding or changing a style, update the registry and preset together instead of copying counts, palettes, or recommendation tables into other documents.

The catalog spans comics and illustration, education, technical blueprints, Eastern cultural references, data narratives, editorial systems, vintage advertising, pixel art, and other native-building directions. For formal business and industry analysis, start with the Path A styles; for creative, training, and brand work, choose visual styles after probing capabilities.

## Design and delivery conventions

- One core idea per slide; prefer verifiable assertion titles.
- Keep density under control, usually no more than four key points and no long run of text-heavy slides.
- Tables, data charts, and text that may be edited later must be native objects; raster images are for decorative visuals.
- Use Chinese-first slide copy and a documented CJK font fallback stack; disclose font differences or embedding strategy for cross-machine delivery.
- Describe mood and world-view in AI image prompts rather than over-specifying coordinates, color ratios, or character poses; Path B' base images contain no text.
- Render every slide when possible and check overflow, contrast, cropping, placeholders, fonts, and data units.
- A delivery receipt should include file path, size or hash, slide count, fonts, native chart/table counts, performed checks, and the claim boundary.

See [skills/subaru-slides/SKILL.md](skills/subaru-slides/SKILL.md) and its references/ for detailed rules; see [styles/index.json](skills/subaru-slides/styles/index.json) for style selection data.

## Repository structure

~~~text
subaru-skills/
├── README.md / README.en.md        # User entrypoints, Chinese / English
├── skills/subaru-slides/           # Independently installable skill package
│   ├── SKILL.md                    # Thin router: rules, paths, checkpoints
│   ├── references/                 # Workflow, paths, design, QA, and more
│   ├── styles/                     # Style registry and presets
│   ├── scripts/                    # Capability probe and image-PPTX fallback
│   └── assets/                     # WebP style samples
├── tools/                          # Harness validators and helper scripts
├── schemas/                        # Machine-readable metadata/style contracts
├── evals/                          # Fixed briefs, assertions, and environment matrix
├── tests/                          # Harness unit tests
├── docs/                           # DoD, templates, and lessons learned
├── Makefile                        # Shared command entrypoint (local, agent, or self-hosted CI)
├── AGENTS.md                       # Single source of engineering rules
└── PROVENANCE.md                   # Upstream and licensing boundary
~~~

Consumers only need skills/subaru-slides/; the other directories support maintenance, quality gates, and regression testing.

## Development and quality gates

Read [AGENTS.md](AGENTS.md) before changing the repository. Per the project workflow, start a task with make new-task; it creates the .gitignored task_plan.md, findings.md, and progress.md. These working files must not be committed.

Common commands:

~~~bash
make check       # frontmatter / links / consistency / assets / styles / installability
make test        # tool smoke tests and Harness unit tests
make doctor      # probe the current machine
make eval        # local fixed cases and coverage gate
make eval-clean  # rebuild fixtures on a clean checkout and run the independent gate
make new-task    # create the three task-tracking files
make help        # list all commands
~~~

For a specific deck:

~~~bash
make validate PPTX=deck.pptx
make render PPTX=deck.pptx OUT=preview/
make montage DIR=preview/ OUT=montage.webp
make lint-copy SRC=outline.md
make new-style ID=my-style NAME="My Style"
~~~

make check is the only mandatory quality gate. The repository ships no CI workflow; local runs, agents, and any self-hosted CI call the same entrypoint. make eval classifies results as PASS / FAIL / SKIP / BLOCKED based on both policy and environment; an unexecuted case is not a pass. make eval-clean claims deterministic fixture structure only, not external image-model quality, HTML runtime behavior, or Office rendering quality.

## License and provenance

Original repository content is released under the [MIT License](LICENSE). skills/subaru-slides is derived from huashu-slides; the upstream audit baseline had no root LICENSE. Read [PROVENANCE.md](PROVENANCE.md) before redistribution to confirm the licensing boundary for third-party documents, scripts, and sample images.
