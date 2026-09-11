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

- **Status:** Complete
- **Goal:** 按 `optimization-plan.md` 把 subaru-slides 升级为"最好的 PPT 制作 skill"，先建设仓库级 Harness 约束 AI 辅助开发。
- **Plan of record:** `optimization-plan.md`
- **Current phase:** Pre-P0 + P0 + P1 + P2 全部完成

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

### P0 deliverable
- [x] P0-1：`SKILL.md` 瘦身为 99 行路由器。
- [x] P0-2：新增 `references/paths/{path-a-native,path-b2-hybrid,path-b-visual,path-c-html}.md`；`dependencies.md` 重写为能力矩阵；新增 `workflow.md`、`content-structure.md`、`illustrations.md`、`qa/{checklist,render-and-validate,delivery}.md`；`proven-styles-gallery.md` 精简为策略页；`prompt-templates.md` 去重。
- [x] P0-5：`styles/index.json` + 23 个 `styles/<id>.md`；`check_style_system` 转绿。
- [x] 基线从 9 条降到 3 条（仅剩 P2 资产压缩债务）。

### P1 deliverable
- [x] P1-1 模板/品牌跟随：`references/template-following.md`。
- [x] P1-2 原生证据 + 单位护栏：`references/native-evidence.md`。
- [x] P1-3 质检工具：`tools/validate_pptx.py`、`tools/render_preview.py`、`tools/make_montage.py` + `make validate/render/montage`。
- [x] P1-4 内容质量闸：`references/writing-quality.md` + `tools/lint_copy.py` + `make lint-copy`。
- [x] P1-5 中文排版：`references/typography-cjk.md`。
- [x] P1-6 演讲备注/动画：`references/speaker-notes.md`。
- [x] 真实 deck 验证：validate 0 error/3 warn；lint-copy 2 命中。

### P2 deliverable
- [x] P2-1 设计系统/自定义风格：`references/design-system.md` + `tools/new_style.py` + `make new-style`。
- [x] P2-2 资产压缩：17 张 PNG -> WebP，13.66 MB -> 1.04 MB；skill 14MB -> 1.3MB；**baseline 归零**。
- [x] P2-3 测试与 CI：`tests/test_harness.py`（8 个用例）+ CI 增加 `make eval`。
- [x] P2-4 跨 harness：`references/harnesses.md`。
- [x] P2-5 生态联动：`references/integrations.md`。

### Next
- [ ] 可选项：为 6 个 Path A 风格补样例图；扩展 evals 断言（validate/lint 纳入）；更多 harness 适配。

---

## Session 3 — subaru-slides 覆盖测试闭环

- **Status:** Complete
- **Goal:** 只对 `subaru-slides` 建立可审计的测试闭环，避免把未执行或环境阻塞误报为通过。
- **Scope for this change:** 先完成覆盖率闸门与环境可执行矩阵，再依据矩阵选择可运行案例。

### Phase 1: Baseline and environment evidence
- [x] 记录 git SHA、静态检查、单测、eval 基线
- [x] 记录 `doctor --json` 与 `detect_capabilities --json`
- [x] 落地环境可执行矩阵（RUNNABLE / BLOCKED + reason）
- **Status:** complete

### Phase 2: Coverage gate
- [x] 将案例状态拆为 PASS / FAIL / SKIP / BLOCKED
- [x] 增加最小 PASS 数、零 FAIL、BLOCKED 必须有 reason 的覆盖率策略
- [x] 增加单元测试，验证零覆盖不再返回成功
- **Status:** complete

### Phase 3: Runnable cases
- [x] 根据环境矩阵只执行可运行路径；不可执行路径保留 BLOCKED 证据
- [x] 决定不在本轮把图片装配 helper 冒充 Path A；原生 schema/布局器/对象契约留作独立建设项
- **Status:** complete

### Phase 4: Iterate and verify
- [x] 每个确认问题记录最小复现命令与产物片段
- [x] 最小修复后重跑失败案例与全量质量门
- [x] 达到覆盖率策略且无明显 P0/P1 问题
- **Status:** complete

### Session 3 acceptance
- [x] `make eval` 在 0 个 PASS 时非 0
- [x] BLOCKED 不等同 FAIL，但缺 reason 会使覆盖率闸门失败
- [x] 环境矩阵记录 git SHA、能力证据、路径可执行性和 claim boundary
- [x] 路由覆盖落到 frontmatter 静态断言与路径决策表单测
- [x] 时间戳 ledger 记录每轮模型、prompt 版本、参数与运行时 git SHA
- [x] `make check` 与 `make test` 通过

### Session 3 errors
| Error | Attempt | Resolution |
|---|---:|---|
| 添加 fallback case 的首个补丁因 README 标题上下文不匹配而失败 | 1 | 检查文件实际内容后改用稳定的列表行作为补丁锚点 |
| `uv run` 无法初始化默认缓存（只读用户缓存目录） | 1 | 改用 `/private/tmp/subaru-skills-uv-cache` 作为任务专用缓存后重试 |
| fallback 无法把仓库 WebP 样例写入 PPTX：`unsupported image format ... WEBP` | 1 | P0：在 `create_slides.py` 内存转换不受 python-pptx 支持的格式为 PNG，再用原命令回归 |
| fallback 结构校验报每页图片越界 | 1 | P1：fullscreen 改为画布内图片对象 + OOXML crop，保持 cover 效果且不越界 |
| 能力探测器在 native + image 同时存在时返回 B2，与 A→B2 的仓库顺序冲突 | 1 | P1：`recommend()` 改为原生构建器优先，并用合成能力矩阵单测锁定顺序 |
| Path C 首次浏览器截图中标题/流程文字继承 deck-stage 白色前景，在浅色背景上对比度不足 | 1 | P1：在固定 HTML 源中显式设置 `.slide`、标题与正文前景色；新增 inspector 断言后复验 `#1 -> #2 -> #3`，控制台 0 错误/告警 |
| 沙箱不允许本地 HTTP 服务绑定 4312 端口 | 1 | 获得仅限 `python3 -m http.server` 的授权后启动临时本地服务完成浏览器验证 |
