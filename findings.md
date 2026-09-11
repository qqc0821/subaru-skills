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

## Session 2 - Optimization / Pre-P0 / P0

### Key findings
- Path A 文档与实现脱节：真实产物用原生构建器（`.codex-build/ev-trends/build.mjs`），SKILL.md 却写 HTML→html2pptx。
- 硬依赖外部 skill（`@presentations` / imagegen）破坏可移植性；本机 DSH 技能目录并不包含它们。
- Snoopy 风格 NOT 约束自相矛盾；图像分辨率 1920/2048 混用；风格计数 18/23/17 漂移。
- 图表部件实际位于 `ppt/slides/charts/`，eval 首次漏检（已修）。

### Decisions
| Decision | Rationale |
|---|---|
| 风格数据单一事实源 `styles/index.json` + 每风格 preset | 消除多处计数/命名漂移 |
| 能力探测优先，外部 skill 仅增强 | 可移植 |
| SKILL.md ≤ 200 行路由器，长文下沉 `references/` | harness 规则 + 上下文效率 |
| baseline 按 check 替换 + stale 提示 | 债务只减不增 |

## Visual/Browser Findings
- GitHub successfully loaded the public `master/huashu-slides` tree. Visible top-level skill entries are `assets`, `references`, `scripts`, and `SKILL.md`.
- The GitHub recursive tree confirms there are no other files inside the skill beyond the listed script, references, images, and `.DS_Store`.

## Session 3 — Eval closure findings

- Baseline commit: `788b450abb8fab0778adc5d0cf4eac90bcf89cdb` (`feat(subaru-slides): add skill harness and evaluation suite`). The working tree contains uncommitted user changes; do not commit or rewrite them without explicit authorization.
- Baseline `make check` and `make test` pass.
- Baseline `make eval` reports `0 validated, 3 skipped` and exits 0. This is a confirmed false-green coverage defect.
- Host capability evidence: `soffice` and `pdftoppm` are available; `deck_stage`, `imagegen`, `uv`, and bundled `create_slides.py` are detected. System `python-pptx`, Pillow, Chrome, artifact-tool, and html2pptx are absent.
- Path decision: A and B' are BLOCKED by the missing native editable builder; C is RUNNABLE as HTML but PPTX export is BLOCKED without html2pptx; B is RUNNABLE because image generation is available; fallback is RUNNABLE through `uv run` despite system Python lacking python-pptx/Pillow.
- Visual QA is executable through soffice + pdftoppm in this environment. The earlier no-renderer claim is stale for the current runtime and must not be repeated.
- The new policy gate correctly returns exit 1 for `0 PASS / 0 FAIL / 1 SKIP / 2 BLOCKED`; zero coverage can no longer pass silently.
- BLOCKED status is determined only when the case has no artifact and its declared path is BLOCKED in `evals/environment.json`. Supplying an artifact still evaluates the case, so the matrix cannot hide a real result.
- Policy is explicit in `evals/policy.json`: `min_pass=1`, `max_fail=0`, `max_skip=0`, and every BLOCKED case requires a reason.
- P0 confirmed: `create_slides.py` accepted WebP during input validation through Pillow, but passed the original path to python-pptx, which rejects WebP. This made the bundled fallback incompatible with every newly compressed style sample. Minimal reproduction is the command in `evals/cases/fallback-image-pptx/brief.md`; failure fragment: `ValueError: unsupported image format ... got 'WEBP'`.
- P1 confirmed after the WebP fix: fallback PPTX structurally passed the narrow eval assertions but `validate_pptx.py` reported one out-of-bounds picture on every slide. Root cause was fullscreen cover implemented with negative offsets. The rendered deck succeeded, so this is both a product-cleanliness issue and evidence that eval did not include validator errors.
- After the crop fix, the same fallback artifact validates with 0 errors / 0 warnings and renders to three PNGs. Manual page-by-page inspection found all three images fill the slide without distortion, blank margins, or clipped primary content.
- Current gate state is intentionally still red: fallback is PASS, A/B2 are reasoned BLOCKED, and runnable Path B remains SKIP. The remaining red state is coverage debt, not a fallback product failure.
- Path B fixed-input regression now passes: 5 slides / 5 images, 0 validator errors, 0 validator warnings, and successful 5-page rendering. Page-by-page inspection found no obvious crop, stretch, blank-margin, or primary-text readability defect.
- With fallback and fixed-input B executed, the coverage gate reaches `2 PASS / 0 FAIL / 0 SKIP / 2 BLOCKED` and exits 0.
- P1 routing contract mismatch: `detect_capabilities.recommend()` selected B2 when native + image were both present, while AGENTS.md, SKILL.md, and dependencies.md define A before B2. The detector now returns A and treats image generation as an optional enhancement; synthetic capability-table tests cover A, C, B, and fallback.
- P1 browser finding: Path C loaded and navigated correctly, but deck-stage host styles made unqualified headings and step labels white on the light paper background. The fixed fixture now sets an explicit ink color on the slide wrapper/headings/body; the HTML inspector treats that contract as required. Browser recheck reached `#1 -> #2 -> #3` with 0 console warnings/errors and no remaining obvious readability defect.
- CI reproducibility finding: because `evals/artifacts/` is intentionally gitignored, running `make eval` in a clean checkout would correctly fail the local 3-PASS policy. CI now rebuilds only the two repository-owned fixed-input PPTX cases with `uv` and evaluates them against a separate honest matrix/policy; optional Path C and visual QA remain BLOCKED there.
- Path A decision: do not add a nominal `python-pptx` dependency and call the existing image assembler a native builder. A maintainable Path A still needs a content schema, layout engine, native chart/table/text contracts, and dedicated cases; until then A/B2 remain explicitly BLOCKED.
- Final false-green boundary: `run_evals.py` also returned success when no case directory existed. It now exits non-zero before artifact evaluation, with a dedicated regression test; both “no cases” and “cases but no runnable artifact” are covered.
