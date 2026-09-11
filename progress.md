# Progress Log

## Session: 2026-09-11

### Phase 1: Repository and Upstream Audit
- **Status:** complete
- Actions taken:
  - Captured the user's three requirements and model handoff requirement.
  - Loaded the planning, skill-authoring, and browser-operation guidance.
  - Initialized persistent planning files before implementation work.
  - Audited the local root and opened the upstream GitHub skill directory in ego-browser task space 1.
  - Enumerated the complete upstream skill tree and scanned all upstream text files for dependencies, paths, cross-skill references, URLs, and identity markers.
  - Recorded upstream baseline commit `791450a2594a3506144917517ff5533c344a62b0`.
  - Inspected local identity: `subaru-skills`, GitHub owner `qqc0821`, MIT copyright holder `LesBit`.
- Files created/modified:
  - `task_plan.md` (created)
  - `findings.md` (created)
  - `progress.md` (created)

### Phase 2: Finalize Migration Design
- **Status:** complete
- Actions taken:
  - Proposed `subaru-slides` under `skills/subaru-slides/`.
  - Defined dependency replacement, file mapping, rebrand scope, and acceptance checks.
  - Flagged the missing upstream license as a distribution caveat.
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

### Phase 3: Import and Rebrand
- **Status:** complete; executed with GPT-5.6 Terra
- Actions taken:
  - Started implementation from the audited plan and fixed upstream commit.
  - The initial `.agents/` destination was rejected by workspace permissions; redirected to writable `skills/subaru-slides/`.
  - Copied 1 entrypoint, 5 original references plus `dependencies.md`, 1 helper script, and 17 PNG style samples; excluded `.DS_Store`.
  - Rebranded frontmatter/UI metadata, removed original identity and personal paths, routed image generation to `imagegen`, and routed editable assembly to `presentations`.
  - Added a project README entry and local runtime dependency notes.
- Files created/modified:
  - `task_plan.md` (updated)
  - `progress.md` (updated)

### Phase 4: Validation and Behavioral Testing
- **Status:** complete
- Actions taken:
  - Ran `quick_validate.py`; skill package is valid.
  - Parsed `agents/openai.yaml` as YAML.
  - Ran the helper with `uv`; dependencies resolved and `--help` rendered.
  - Generated a temporary 1-slide PPTX from two bundled sample images; ZIP integrity and 16:9 dimensions passed.
  - Verified all 17 PNGs decode, local Markdown references resolve, stale identity/path scan is clean, and `.DS_Store` is absent.
  - Verified missing-image handling returns a clear error and exit code 1.
- Files created/modified:
  - No project files added by tests; temporary outputs are under `/private/tmp`.

### Phase 5: Delivery
- **Status:** complete
- Actions taken:
  - Reviewed the final project status and diff check.
  - Moved the generated uv cache out of the project tree.
- Files created/modified:
  - `README.md`
  - `skills/subaru-slides/`
  - `task_plan.md`
  - `findings.md`
  - `progress.md`

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Planning scope | Current turn | No implementation changes | Only planning artifacts created so far | Pass |
| Upstream inventory | GitHub recursive tree | Complete payload identified | 1 SKILL, 1 script, 5 references, 17 PNGs, 1 `.DS_Store` | Pass |
| Local identity | Git metadata/LICENSE | Rebrand target inferable | `subaru-skills`, `qqc0821`, `LesBit` | Pass |
| Structural validation | `quick_validate.py skills/subaru-slides` | Valid skill package | `Skill is valid!` | Pass |
| Dependency help | `uv run .../create_slides.py --help` | Helper starts with declared deps | Usage rendered; uv installed 5 packages | Pass |
| PPTX smoke | 2 bundled PNGs, grid layout | 1-slide valid 16:9 PPTX | `unzip -t` clean; 1 slide; 12191695×6858000 EMU | Pass |
| Asset integrity | 17 PNG samples | All decode | 17 PNGs valid; sizes 960×535 or 1200×669 | Pass |
| Identity scan | Rebranded skill and README | No stale upstream identity/path | No matches | Pass |
| Local reference scan | All Markdown references | No broken local links | 0 broken links after path fix | Pass |
| Missing-image handling | Nonexistent image path | Clear warning/error and exit 1 | Passed | Pass |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-09-11 | None | 1 | N/A |
| 2026-09-11 | ego-browser could not connect inside the default sandbox | 1 | Retried with approved full access; GitHub loaded successfully |
| 2026-09-11 | Clone `master` was at `49a55ba8a975ebda6bb55ea5ca4388942e3f6f18`, not the audited `791450a…` | 1 | Will fetch and checkout the fixed audited commit before copying |
| 2026-09-11 | Permission denied creating `.agents/` | 1 | Redirected implementation to `skills/subaru-slides/` |
| 2026-09-11 | System Python lacked `python-pptx` and had an incompatible x86_64 Pillow binary | 1 | Used `uv run` with the script's PEP 723 dependencies for a clean compatible environment |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Complete; ready for delivery |
| Where am I going? | User can review or commit the scoped changes |
| What's the goal? | Integrate a dependency-complete, fully rebranded version of the upstream skill |
| What have I learned? | Complete payload, dependency gaps, identity markers, local branding, and license caveat |
| What have I done? | Imported, rebranded, dependency-documented, and tested the skill |

## Session: 2026-09-11 (Optimization & Pre-P0 Harness)

### H1: AGENTS.md + CLAUDE.md
- **Status:** complete
- Actions:
  - 新建 `AGENTS.md`（222 行）作为仓库单一事实源：仓库结构、硬性 Must/Must Not、skill 包规范（frontmatter/行数/scripts/assets/openai.yaml）、风格系统约定、依赖与能力策略、Git 约定、质量门与手动检查、协作工作流、出处与许可。
  - 新建 `CLAUDE.md`（5 行），以 `@AGENTS.md` 导入方式指向单一事实源，避免规则漂移。
  - 记录 Harness 建设状态表（H1 完成，H2–H7 待建）。
  - 执行 `AGENTS.md` §8.2 的过渡期手动检查，验证命令可用。
- Files created:
  - `AGENTS.md`
  - `CLAUDE.md`

### H1 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| AGENTS.md 存在与规模 | 文件 | 单一事实源、含硬性规则 | 222 行，含全部章节 | Pass |
| CLAUDE.md 导入 | `@AGENTS.md` | 指向单一事实源 | 命中 | Pass |
| 外部依赖/用户路径扫描 | `skills/` | 命中已知 P0-2 | 命中 `dependencies.md:17`、`SKILL.md:520,563` | Pass（暴露待修项） |
| `.DS_Store` 扫描 | repo | 无 | 无 | Pass |
| 单文件 >1MB 扫描 | `skills/` | 无 | 无（最大样图 984KB） | Pass |
| skill 体积 | `skills/*` | 记录 | 14M（P2-1 待压缩） | Pass（记录） |

## Session: 2026-09-11 (Pre-P0 H2–H4)

### H2–H4: Harness 工具链
- **Status:** complete
- Actions:
  - H2：新增 `schemas/`（skill.frontmatter / openai-agent / styles.index / style.preset）。
  - H3：新增 `tools/`：`_common.py`、`validate_skills.py`、`check_links.py`、`check_consistency.py`、`check_assets.py`、`check_style_system.py`、`doctor.py`、`consistency-rules.json`、`check.sh`（纯标准库，零第三方依赖）。
  - H4：新增 `Makefile`（check/test/doctor/baseline）与 `.github/workflows/ci.yml`，CI 与本地共用 `make check`。
  - 引入 baseline 机制：`tools/baseline.json` 记录 9 条已知债务；`make check` 通过；新阻塞项会失败。
  - 更新 `AGENTS.md` §8：统一入口、辅助检查、Harness 状态表与 baseline 说明。
- Files created/modified:
  - `schemas/*.json`、`tools/*`、`Makefile`、`.github/workflows/ci.yml`、`AGENTS.md`

### H2–H4 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| `make test` | tools/ | 编译 + doctor | compileall OK / doctor OK | Pass |
| `make check`（无 baseline） | 全库 | 报出已知问题且非 0 | 9 条 findings，exit 1 | Pass |
| `make baseline` | 全库 | 记录已知债务 | 9 known | Pass |
| `make check`（有 baseline） | 全库 | 无新 finding，exit 0 | PASS，9 suppressed | Pass |
| 失败路径 | 空 baseline | 非 0 | validate_skills exit 1 | Pass |
| 坏链自检 | 临时 md | 报坏链且非 0 | 命中 does-not-exist-xyz，exit 1 | Pass |
| consistency 规则 | skills/ | 命中矛盾/分辨率不一致 | Snoopy 矛盾 + 1920/2048 混用 | Pass |

## Session: 2026-09-11 (Pre-P0 H5–H6)

### H5: 任务模板 + DoD + PR 模板
- **Status:** complete
- Files: `docs/templates/{task_plan,findings,progress}.md`、`docs/definition-of-done.md`、`.github/PULL_REQUEST_TEMPLATE.md`、`tools/new_task.sh`、`make new-task`。

### H6: Eval 回归基准
- **Status:** complete
- Files: `tools/pptx_inspect.py`（纯标准库 OOXML 指标）、`tools/run_evals.py`（`--pptx/--case/--compare`）、`evals/`（3 个 case + README）、`make eval`。
- 机制：无产物的 case SKIP；有产物按 `expect.json` 断言；结果写 `evals/results/latest.json`（gitignored）。

### H5–H6 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| `make eval`（无产物） | 3 cases | 全 SKIP、exit 0 | 0 validated / 3 skipped | Pass |
| 真实 deck 回归 | `subaru-ev-trends-candidate.pptx` | 通过 cn-industry-analysis 断言 | 10 slides / 3 charts / 1325 CJK / 1 font | Pass |
| 终版 deck | `output/subaru-ev-trends.pptx` | 同上 | PASS | Pass |
| `--compare` | 上一次 FAIL | 显示 FAIL -> PASS | 命中 chart_count 0 -> 3 | Pass |
| `make test` | tools/ | 编译通过 | compileall OK / doctor OK | Pass |
| `make check` | 全库 | 无新 finding | PASS, exit 0 | Pass |

## Session: 2026-09-11 (Pre-P0 H7 + P0-3/P0-4)

### H7: pre-commit + 经验沉淀
- **Status:** complete
- Files: `tools/install-hooks.sh` + `make hooks`（安装 `.git/hooks/pre-commit`，`SKIP_HARNESS=1` 可跳过）、`.pre-commit-config.yaml`（local hook）、`docs/lessons-learned.md`（L-01..L-10）。

### H3 强化: baseline stale 检测
- `_common.py`：`--update-baseline` 改为"按 check 前缀替换"；`make check` 对失效条目输出 stale 提示。
- 结果：修好 Snoopy 矛盾与分辨率不一致后，`make baseline` 自动清理 2 条（9 -> 7 known）。

### P0-3: 能力探测
- 新增 `skills/subaru-slides/scripts/detect_capabilities.py`：探测 python/uv/node/soffice/chrome/python-pptx/artifact-tool/deck-stage/html2pptx/imagegen，并输出推荐路径 `A -> B2 -> C -> B -> fallback`。

### P0-4: 修复矛盾
- `proven-styles-gallery.md`：删除"始终指定 NOT Snoopy"，统一为"不写反向约束"。
- `prompt-templates.md`：`1920x1080` -> `2048x1152`（4 处）。

### H7 + P0-3/P0-4 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| `make check` | 全库 | 报出 stale 提示 | 2 stale，exit 0 | Pass |
| `make baseline` | 全库 | 清理 stale | -2 stale，7 known | Pass |
| 能力探测 | 本机 | 输出推荐路径 | 推荐 C（deck-stage + imagegen） | Pass |
| `make hooks` | git hooks | 安装 hook | 安装 `pre-commit` | Pass |

## Session: 2026-09-11 (P0-1 / P0-2 / P0-5)

### P0-5: 风格系统机读化
- **Status:** complete
- 新增 `styles/index.json`（23 个风格、13 条主题推荐）与 23 个 `styles/<id>.md` preset。
- `proven-styles-gallery.md` 精简为选择策略页，数据以 index 为准。
- `check_style_system` 转绿。

### P0-1 / P0-2: 薄路由器 + 路径重构

## Session: 2026-09-11 (P1)

### P1 deliverable
- [x] P1-1 模板/品牌跟随：`references/template-following.md`。
- [x] P1-2 原生证据 + 单位护栏：`references/native-evidence.md`。
- [x] P1-3 质检工具：`tools/validate_pptx.py`、`tools/render_preview.py`、`tools/make_montage.py` + `make validate/render/montage`。
- [x] P1-4 内容质量闸：`references/writing-quality.md` + `tools/lint_copy.py` + `make lint-copy`。
- [x] P1-5 中文排版：`references/typography-cjk.md`。
- [x] P1-6 演讲备注/动画：`references/speaker-notes.md`。
- [x] 更新 `SKILL.md`（Step 6 + 参考索引）、`qa/render-and-validate.md`、`AGENTS.md` §8.1。

### P1 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| `make check` | 全库 | 无新 finding | PASS（57 个 md 链接） | Pass |
| `make test` | tools/ | 5 个脚本冒烟 | 全 OK | Pass |
| `make validate` | 真实 deck | 结构错误为 0 | 0 error / 3 warn | Pass |
| `make lint-copy` | 真实 deck | 文案初筛 | 2 命中（"不是X而是Y" / "闭环"） | Pass |
| `make montage` | PNG 目录 | 生成或优雅跳过 | Pillow 缺失 -> 优雅跳过 | Pass |
| hero `make render` | 真实 deck | 无渲染器时明说 | soffice 缺失 -> 明说跳过 | Pass |
- `SKILL.md` 从 617 行降到 99 行；长文下沉到 `references/`。
- 新增 `references/paths/{path-a-native,path-b2-hybrid,path-b-visual,path-c-html}.md`（Path A 重定义为原生可编辑，新增 Path B' 混合模式，HTML 降为 Path C）。
- 新增 `workflow.md`、`content-structure.md`、`illustrations.md`、`qa/{checklist,render-and-validate,delivery}.md`。
- `dependencies.md` 重写为能力矩阵 + 降级策略；移除 `$presentations` 硬依赖。
- `prompt-templates.md` 去掉重复的 base style 模板（改为指向 styles preset）。
- 强化 `check_consistency.py`：single_value 支持捕获组，分辨率规则限定在 `CANVAS:` 行。

### P0 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| `make check` | 全库 | 无新 finding | PASS, exit 0 | Pass |
| `make baseline` | 全库 | 清理已修复债务 | 9 -> 3 known | Pass |
| SKILL.md 行数 | 文件 | ≤200 | 99 | Pass |
| `check_style_system` | styles/ | 结构/样例通过 | 1 index / 23 styles / 17 samples | Pass |
| `check_consistency` | 40 个 skill md | 无新 finding | OK | Pass |

## Session: 2026-09-11 (P2)

### P2 deliverable
- [x] P2-1 设计系统/自定义风格：`references/design-system.md` + `tools/new_style.py`（`--register` 原子更新 index）+ `make new-style`。
- [x] P2-2 资产压缩：新增 `tools/compress_assets.py`；17 张 PNG -> WebP（13.66 MB -> 1.04 MB），样例引用全部更新为 `.webp`。
- [x] P2-3 测试与 CI：`tests/test_harness.py`（8 用例）+ CI 增加 `make eval`。
- [x] P2-4 跨 harness：`references/harnesses.md`。
- [x] P2-5 生态联动：`references/integrations.md`。
- [x] `.gitignore` 增加 `.uv-cache/`。

### P2 Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| `make check` | 全库 | 无新 finding | PASS；baseline = 0 | Pass |
| `make test` | tools/ + tests | 冒烟 + 单元测试 | 5 冒烟 + 8 用例 OK | Pass |
| `make eval` | evals | exit 0 | Pass | Pass |
| 资产压缩 | 17 PNG | WebP 且 <=5MB | 1.04 MB | Pass |
| `new_style.py` | demo | 创建 + 注册 + 计数更新 | count 24，随后回滚 | Pass |
| `check_style_system` | styles/ | 样例可达 | OK | Pass |

## Session: 2026-09-12 (subaru-slides eval closure)

### Baseline
- **Status:** complete
- Recorded git SHA `788b450abb8fab0778adc5d0cf4eac90bcf89cdb` and preserved the existing dirty worktree.
- `make check`: PASS.
- `make test`: PASS, 8 tests.
- `make eval`: false green, `0 validated / 3 skipped`, exit 0.
- `python3 tools/doctor.py --json`: renderer available; system python-pptx/Pillow absent.
- `python3 skills/subaru-slides/scripts/detect_capabilities.py --json`: recommends Path C; B and fallback are also executable; A/B' lack a native builder.

### Planned edits
- Add a machine-readable environment snapshot plus a one-page execution matrix.
- Add PASS/FAIL/SKIP/BLOCKED accounting and a policy-driven coverage gate to `run_evals.py`.
- Add unit coverage for zero-pass failure and BLOCKED reason validation.

### Coverage gate and environment matrix
- **Status:** complete
- Added `evals/environment.json` and `evals/environment-matrix.md` with SHA, dirty-tree flag, RUNNABLE/BLOCKED paths, reasons, and claim boundaries.
- Added `evals/policy.json` with minimum PASS, maximum FAIL/SKIP, and BLOCKED-reason rules.
- Updated `tools/run_evals.py` to classify PASS/FAIL/SKIP/BLOCKED and derive its exit code only from the coverage gate.
- Added two eval-engine unit tests; full suite is now 10 tests and passes.
- Verified the intended red state before runnable cases: `0 PASS / 0 FAIL / 1 SKIP / 2 BLOCKED`, exit 1.
- Re-ran `make check`: PASS.

### Runnable fallback case
- Added a deterministic fallback case using three bundled WebP assets and an explicit claim boundary.
- First execution did not reach the script because uv's default cache directory was not writable; next attempt uses a task-specific cache under `/private/tmp`.
- Second execution installed declared dependencies but confirmed a P0 product defect: python-pptx rejects the bundled WebP assets.
- Applied a minimal helper fix: unsupported input formats are converted to PNG in memory before insertion; source assets and temporary files are untouched.
- The same case then generated successfully and passed its initial structural assertions, but `validate_pptx.py` found 3 out-of-bounds picture errors.
- Replaced negative-offset fullscreen cover with bounded picture geometry plus symmetric crop properties.
- Regenerated the same artifact: `validate_pptx.py` now reports 0 errors / 0 warnings.
- Rendered three pages with soffice + pdftoppm and inspected each PNG; fullscreen coverage is visually correct.
- Eval state after the fix: fallback PASS, Path B SKIP, A/B2 BLOCKED; coverage gate remains red because `max_skip=0`.

### Runnable Path B case
- Converted `full-ai-visual` into a deterministic fixed-input assembly regression with an explicit claim boundary for image-model quality.
- Generated a 5-page PPTX from bundled AI visual samples.
- Structural validation: 0 errors / 0 warnings.
- Rendering: 5 PNGs produced; all pages inspected with no obvious crop, stretch, or blank-margin defect.
- Coverage gate: `2 PASS / 0 FAIL / 0 SKIP / 2 BLOCKED`, exit 0.

### Eval evidence and routing tests
- Added picture/text/graphic-frame/native-editable-object metrics to `pptx_inspect.py`.
- Integrated `validate_pptx` error/warning counts and execution-path equality into case assertions.
- Added required per-artifact run metadata and timestamped `results/runs/<run-id>.json` ledgers.
- Added static frontmatter trigger coverage and synthetic path-routing tests.
- Fixed path-order drift: native capability now recommends A before B2, matching repository policy.

### Path C browser loop
- Added a tracked three-slide `fixture.html` and evaluated the runtime copy with deck-stage in a real browser.
- Initial navigation worked, but the screenshots confirmed a P1 readability defect: host styles made headings and labels white on the light slide background.
- Added an explicit slide text-color contract to both the fixture and `html_deck_inspect.py`; the new expect assertion fails if that rule regresses.
- Browser verification after the fix: `#1 -> #2 -> #3`, computed heading/slide color `rgb(21, 32, 43)`, 0 console warnings, 0 console errors, no remaining obvious visual issue.

### Clean-checkout CI coverage
- Added `prepare_eval_artifacts.py` to rebuild only fixed-input B/fallback cases from repository WebP assets.
- Added isolated `environment-ci.json` / `policy-ci.json`; `make eval-ci` uses a gitignored CI artifact directory so local Path C output cannot expand the CI claim.
- Added `astral-sh/setup-uv@v6` to CI; official GitHub release tag was checked before pinning the major version.
- `make eval-ci`: `2 PASS / 0 FAIL / 0 SKIP / 3 BLOCKED`, exit 0.

### Final closure evidence
- `make check`: PASS; no new findings.
- `make test`: PASS; 19 tests, including zero-case and zero-pass false-green guards.
- Local `make eval` ran twice consecutively with identical model, prompt version, parameters, git SHA and counts: `3 PASS / 0 FAIL / 0 SKIP / 2 BLOCKED`.
- Timestamp ledgers: `20260911T173223485545Z.json` and `20260911T173225699768Z.json`.
- A and B' remain explicitly BLOCKED; installing `python-pptx` alone was rejected as a false Path A because there is no native content/layout/object contract yet.
- `git diff --check`: PASS. No baseline suppression was added and no commit was created in the pre-existing dirty worktree.
