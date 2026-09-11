# Task Plan: Integrate and Rebrand huashu-slides

## Goal
Audit the upstream `huashu-slides` skill, fill all required dependencies/content, integrate a fully rebranded copy into this project, and verify it without retaining unintended references to the original repository or user.

## Current Phase
Complete — delivery review finished

## Phases

### Phase 1: Repository and Upstream Audit
- [x] Inspect this project's conventions, skill layout, metadata, validation, and dependency patterns
- [x] Inventory every upstream file and reference
- [x] Classify runtime, package, binary, font, template, and cross-skill dependencies
- [x] Locate all original repository/author/user/name references
- **Status:** complete

### Phase 2: Finalize Migration Design
- [x] Choose proposed name `subaru-slides` and destination `skills/subaru-slides/` (workspace `.agents/` is read-only)
- [x] Define file-by-file keep/adapt/replace/remove mapping
- [x] Define dependency completion strategy and acceptance checks
- **Status:** complete

### Phase 3: Import and Rebrand (GPT-5.6 Terra)
- [x] Add the skill under the project's expected directory
- [x] Vendor or declare every required dependency and missing supporting resource
- [x] Rename folder, frontmatter, UI metadata, prompts, scripts, examples, paths, and internal references
- [x] Remove or replace original repository/user attribution where requested, while preserving legally required license notices
- [x] Update the project README with the new skill entry and project-local invocation path
- **Status:** complete

### Phase 4: Validation and Behavioral Testing (GPT-5.6 Terra)
- [x] Run structural/frontmatter validation
- [x] Run script and dependency smoke tests
- [x] Search for stale upstream identifiers and broken relative links
- [x] Exercise at least one realistic invocation/output flow
- **Status:** complete

### Phase 5: Delivery
- [x] Review diff and report imported files, dependency decisions, rebranding coverage, tests, and residual caveats
- **Status:** complete

## Key Questions
1. What naming and layout conventions does this project use for skills?
2. Which upstream dependencies are declared, implicit, missing, remote-only, or environment-specific?
3. What new name should replace `huashu-slides`, and which related author/repository identifiers must be rewritten?
4. Does upstream licensing require retaining any copyright/license notice despite the requested rebrand?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Separate audit/planning from implementation | User explicitly requested the plan before execution |
| Execute implementation with GPT-5.6 Terra | User explicitly selected that model for the execution stage |
| Preserve legally required notices | Rebranding should not silently violate upstream license obligations |
| Default new identity to `subaru-slides` / Subaru Skills / LesBit / `qqc0821/subaru-skills` | These are the current repository, license, and Git remote identities; the user can override them before execution |
| Install at `skills/subaru-slides/` | Workspace permissions make `.agents/` read-only; this remains a project-local discoverable skill directory |
| Replace image-generation instructions with Codex `imagegen` routing | Removes Gemini key, `nano-banana-pro`, and sibling `huashu-wechat-image` dependencies |
| Use the bundled Presentations workflow for editable PPTX assembly | Removes hard-coded user-home `html2pptx.js` paths while retaining editable output support |
| Retain and repair local `create_slides.py` for image-PPTX fallback | It is small, deterministic, and already declares its Python requirements inline |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| ego-browser bootstrap unavailable in default sandbox | 1 | Retried with approved full access; succeeded |
| Shallow clone `master` resolved to `49a55ba8a975ebda6bb55ea5ca4388942e3f6f18`, not audited baseline | 1 | Fetch and checkout audited commit `791450a2594a3506144917517ff5533c344a62b0` before copying |
| Workspace denied writes under `.agents/` | 1 | Use writable project-local `skills/subaru-slides/` and update all references |
| System Python had missing `python-pptx` and an x86_64 Pillow binary incompatible with arm64 | 1 | Used `uv run` with the script's declared dependencies for a clean compatible test environment |

## Scope Guard
- The requested import/rebrand and validation are complete; no unrelated project files were changed.
- Temporary test outputs and dependency caches were kept outside the project tree.
- Upstream baseline: commit `791450a2594a3506144917517ff5533c344a62b0` (latest commit affecting the directory as of 2026-09-11).
- Upstream has no root `LICENSE` at that revision; redistribution licensing remains an explicit caveat.

---

## Session 2 — Optimization Plan & Pre-P0 Harness

- **Status:** In progress
- **Goal:** 按 `optimization-plan.md` 把 subaru-slides 升级为"最好的 PPT 制作 skill"，先建设仓库级 Harness 约束 AI 辅助开发。
- **Plan of record:** `optimization-plan.md`
- **Current phase:** Pre-P0 H1–H7 完成；已开始 P0（P0-3/P0-4 完成）

### H1 deliverable
- [x] 新建 `AGENTS.md`（222 行）：仓库结构、Must/Must Not、skill 包规范、风格系统约定、依赖与能力策略、Git 约定、质量门、协作工作流、出处与许可。
- [x] 新建 `CLAUDE.md`（5 行）：通过 `@AGENTS.md` 导入，不重复规则。
- [x] 执行 `AGENTS.md` §8.2 过渡期手动检查，确认命令有效（外部依赖扫描命中已知 P0-2）。

### H2–H4 deliverable（Harness 工具链）
- [x] H2 `schemas/`：skill.frontmatter / openai-agent / styles.index / style.preset。
- [x] H3 `tools/`：validate_skills / check_links / check_consistency / check_assets / check_style_system / doctor + `_common.py` + `consistency-rules.json`。
- [x] H4 `Makefile`（check/test/doctor/baseline）+ `.github/workflows/ci.yml`。
- [x] 基线机制：`tools/baseline.json` 记录 9 条已知债务，`make check` 通过；新 finding 会使 check 失败。

### H5–H6 deliverable
- [x] H5：`docs/templates/{task_plan,findings,progress}.md`、`docs/definition-of-done.md`、`.github/PULL_REQUEST_TEMPLATE.md`、`tools/new_task.sh`、`make new-task`。
- [x] H6：`evals/`（3 个 case + README）、`tools/pptx_inspect.py`、`tools/run_evals.py`、`make eval`。
- [x] `.gitignore` 增加构建/评测产物忽略项。

### H7 + 早期 P0 deliverable
- [x] H7：`tools/install-hooks.sh` + `make hooks` + `.pre-commit-config.yaml` + `docs/lessons-learned.md`（10 条）。
- [x] H3 强化：baseline 改为"按 check 替换 + stale 提示"，已自动清理 2 条已修复债务。
- [x] P0-4：修复 Snoopy NOT 约束矛盾、统一图像分辨率为 2048x1152。
- [x] P0-3：`skills/subaru-slides/scripts/detect_capabilities.py` 能力探测与路径推荐。

### Next
- [ ] P0-1 / P0-2 / P0-5：SKILL.md 路由器、路径重构（含 Path B'）、风格系统机读化。
