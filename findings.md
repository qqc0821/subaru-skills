# Findings & Decisions

## Requirements
- Audit `https://github.com/alchaincyf/huashu-skills/tree/master/huashu-slides` and identify all dependencies and missing content.
- Add the skill to `/Users/nicolas/Projects_app/subaru-skills`.
- Rename the skill and all related metadata/content, including references to the original repository and original user.
- Produce the implementation plan first; use GPT-5.6 Terra for execution.

## Research Findings
- Local repository currently contains only `.gitignore`, `LICENSE`, and a minimal `README.md`; it has no established skill directory, manifest, validator, or dependency convention to inherit.
- Upstream `huashu-slides` contains `SKILL.md` plus `assets/`, `references/`, and `scripts/` directories. The repository root also has `skills.json`, which may contain registration metadata that must be evaluated separately from the skill folder.
- The upstream repository contains multiple sibling `huashu-*` skills, so cross-skill references are a likely hidden dependency and must be searched explicitly.
- Upstream skill payload is 1 `SKILL.md` (642 lines), 1 Python script, 5 Markdown references, 17 PNG style samples, and an unwanted `.DS_Store`. The PNG assets total roughly 13.9 MB and are functional visual references, not placeholders.
- `scripts/create_slides.py` is a PEP 723 inline-metadata Python 3.10+ script with two declared Python dependencies: `python-pptx>=1.0.0` and `Pillow>=10.0.0`. It creates image-based 16:9 PPTX files and supports fullscreen, title-above/below/left, center, grid, background/title colors, margins, and an optional PPTX template.
- Path A (editable HTML to PPTX) depends on Node.js, `pptxgenjs`, an external `html2pptx.js` currently hard-coded at `$HOME/.agents/skills/pptx/scripts/html2pptx.js`, and Playwright (`npx playwright screenshot`) for preview rendering.
- Path B depends on an image-generation capability. Upstream names the external `nano-banana-pro` skill and falls back to sibling `huashu-wechat-image/scripts/generate_image.py`; neither is bundled in `huashu-slides`, so the current skill is not self-contained.
- The skill also references an external `design-philosophy` skill for deeper style guidance; this appears optional but must be removed, bundled, or clearly downgraded to an optional enhancement.
- Current paths are Claude-oriented (`~/.claude/skills/...`) and conflict with a project-local Codex integration. All executable examples must use skill-relative or project-resolved paths.
- The upstream repository has no root `LICENSE` at the queried `master` revision (raw request returned 404). Before copying, execution must record the exact upstream commit and treat licensing/provenance as a release caveat; the local repository's MIT license does not automatically license third-party copied content.
- Root `README.md` and `skills.json` are upstream catalog/install metadata, not required runtime payload. They contain extensive `huashu`, `alchaincyf`, source-repository, and update-check metadata and should not be copied wholesale.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Treat dependencies as more than package manifests | Skills often rely on scripts, binaries, fonts, sibling skills, templates, and implicit tools |
| Scan both text and filenames for upstream identity | Rebranding must include paths, metadata, prompts, examples, comments, and generated UI metadata |
| Exclude `.DS_Store` | It is OS metadata and not a skill asset |
| Avoid preserving the upstream updater metadata | `.huashu-skill-meta.json` would intentionally retain the original repo/user identity and is unnecessary for a forked/rebranded project copy |
| Make primary workflows locally resolvable | Hard-coded home-directory and sibling-skill paths are brittle and violate the request to complete dependencies |
| Proposed folder/frontmatter name: `subaru-slides` | Natural namespace match for the current `subaru-skills` repository |
| Proposed destination: `skills/subaru-slides/` | `.agents/` is read-only in this workspace; a writable project-local skill directory is required |
| Add `agents/openai.yaml` | Supplies rebranded Codex UI metadata and a `$subaru-slides` default prompt |
| Route illustration generation to `$imagegen` | Uses the native image capability and removes external Gemini scripts/API-key handling |
| Route editable deck creation to `$presentations` | Uses the verified PPTX workflow instead of a hard-coded helper path |
| Keep all 17 style samples | They materially guide style selection; verify them and omit only `.DS_Store` |

## Planned File Mapping
| Upstream item | Planned treatment |
|---------------|-------------------|
| `huashu-slides/SKILL.md` | Rewrite as `skills/subaru-slides/SKILL.md`; preserve the useful workflow, replace identity/dependency/path references, and trim project-specific claims |
| `scripts/create_slides.py` | Copy and repair examples to use skill-relative paths; retain PEP 723 dependencies and add smoke coverage |
| `references/*.md` | Copy and scan; repair internal wording/links and remove original-author project claims while retaining third-party citations |
| `assets/style-samples/*.png` | Copy all 17 and verify decodability/dimensions; omit `.DS_Store` |
| `agents/openai.yaml` | Create Codex UI metadata for `$subaru-slides` |
| Root `README.md` | Add local catalog/install/invocation entry for `subaru-slides` |
| Upstream `skills.json`, README, updater metadata | Do not copy; they belong to the original ecosystem and are not runtime dependencies |

## Acceptance Checks
- `quick_validate.py skills/subaru-slides` passes.
- Every Markdown relative link and referenced local file resolves.
- A stale-identity scan finds no unintended `huashu`, `花叔`, `alchaincyf`, `huashu-skills`, `nano-banana-pro`, `huashu-wechat-image`, `~/.claude`, hard-coded `pptx` skill path, or `image-to-slides` references.
- The Python helper runs with `--help`, rejects missing images cleanly, and creates a smoke-test PPTX from generated test images.
- The smoke PPTX has the expected slide count and 16:9 dimensions; all 17 style samples decode successfully.
- No secrets, `.DS_Store`, upstream updater metadata, temporary outputs, or dependency caches are committed.
- `git diff --check` passes and the final diff remains scoped to this integration and its planning artifacts.

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| None | N/A |
| Upstream has no visible license file | Flag licensing explicitly; user confirmed authorization for this integration, but future redistribution should retain that authorization record |

## Resources
- Upstream skill: https://github.com/alchaincyf/huashu-skills/tree/master/huashu-slides
- Local project: /Users/nicolas/Projects_app/subaru-skills

## Visual/Browser Findings
- GitHub successfully loaded the public `master/huashu-slides` tree. Visible top-level skill entries are `assets`, `references`, `scripts`, and `SKILL.md`.
- The GitHub recursive tree confirms there are no other files inside the skill beyond the listed script, references, images, and `.DS_Store`.
