# Changelog

本文件记录 `subaru-skills` 的版本变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## Unreleased

### 变更

- 降低 `subaru-slides` 的上下文成本：选风格时改读自动生成的 `styles/router.md`（约 1 137 token），
  不再读整个 `styles/index.json`（约 2 947 token）；入口明确"只读选中的 1 个 preset"、
  `references/design-movements.md` 降为按需读取。
- 瘦身 `references/design-principles.md`（2 209 → 537 token）与 `references/design-movements.md`
  （2 016 → 793 token）：删除与本 skill 风格系统重复的通用色板与 2026 趋势、全库零引用的
  Viral Deck 框架，以及与 `styles/foundation.json` 冲突的"正文 ≥24pt"规则。
- 移除 CI：仓库不再附带 `.github/workflows/ci.yml`，质量门由 `make check` 承担，本地、Agent
  或使用者自建的 CI 都调用同一入口。
- `make eval-ci` 更名为 `make eval-clean`，`evals/policy-ci.json` / `evals/environment-ci.json`
  相应更名为 `policy-clean.json` / `environment-clean.json`，避免名字继续暗示一个已不存在的
  CI 环境；闸门语义不变（在干净检出上重建固定输入产物，要求至少 2 PASS、0 FAIL、0 SKIP）。

## 0.1.0 - 2026-09-12

首个发布版本。仓库可作为 Agent Skill 被安装使用。

### 新功能

- `subaru-slides` skill：从源内容到成品 PPTX 的端到端流程，含内容结构化、风格选择、
  原生可编辑构建、AI 视觉构建、HTML deck 与图片兜底五条执行路径。
- 风格系统：23 个风格 preset，`styles/index.json` 作为计数、命名、推荐与样例映射的唯一事实源。
- 能力探测与降级：`scripts/detect_capabilities.py` 先探测环境再推荐路径，
  任一能力缺失都会明确告知并降级，不做静默换路。
- 内置兜底脚本 `scripts/create_slides.py`：PEP 723 内联依赖，图片型 PPTX 零安装可用。
- 可安装性：支持 `npx skills add qqc0821/subaru-skills`，仓库结构通过 skills CLI 校验。

### 工程与质量

- Harness 质量门：`validate_skills` / `check_links` / `check_consistency` / `check_assets` /
  `check_style_system` / `gen_style_router` / `check_context_budget` / `check_installability`，
  由 `make check` 统一入口驱动，本地与 CI 一致。
- 机读契约 `schemas/`：skill frontmatter、openai-agent 元数据、style preset 与 index。
- 回归基准 `evals/`：固定 brief + 结构断言，`make eval` 强制覆盖率闸门。
- 单元测试 `tests/`：28 个用例覆盖路径路由、渲染器探测、安装边界与校验器行为。
- 安装边界护栏：`check_installability` 确保发布出去的 skill 包自包含
  （目录名可安装、frontmatter 与目录一致、不引用 `tools/`、`schemas/`、`AGENTS.md`
  或仓库专有的 `make` 目标）；CI 另有一条任务用 skills CLI 枚举本仓库，防止结构漂移。
- `make doctor` 环境自检；`make new-task` / `make new-style` 脚手架。
- 渲染器探测修复：`soffice` / `pdftoppm` 现在按
  `SOFFICE_BIN`/`PDFTOPPM_BIN` → `PATH` → 常见安装路径 → 运行时 glob 的顺序查找，
  不再依赖 PATH 中恰好包含宿主的 `bin/override` 目录。

### 文档

- `README.md` 重写为面向使用者：安装方式、Agent 目录约定、能力降级、依赖清单、质量门入口。
- 新增 `PROVENANCE.md`：记录上游出处与再分发授权边界。
- `AGENTS.md` 明确任务过程三件套（`task_plan.md` / `findings.md` / `progress.md`）不入库。

### 变更

- 移除根目录开发过程日志与已落地的优化方案文档，仓库只保留用户可见内容。
- 6 个缺少对照样例图的风格 preset（`fathom-data`、`muller-brockmann-grid`、
  `pentagram-editorial`、`neo-brutalism`、`build-luxury-minimal`、`takram-speculative`）
  的 `proven` 由 `true` 修正为 `false`，不再声称已验证。

[0.1.0]: https://github.com/qqc0821/subaru-skills/releases/tag/v0.1.0
