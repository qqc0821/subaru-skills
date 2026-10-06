# Harness 使用与维护

按需查阅命令、目录职责和维护状态。任务验收要求见 [开发入口](../AGENTS.md) 与 [Definition of Done](definition-of-done.md)。

## 1. 命令入口

```
make check     # = validate_skills + check_links + check_consistency + check_assets + check_style_system + gen_style_router + check_context_budget + check_installability
make test      # 脚本冒烟 / 单元测试
make doctor    # 环境能力自检
make eval      # 本机 eval 覆盖率闸门（PASS / FAIL / SKIP / BLOCKED）
make eval-brainstorm # 固定对话案例、配对运行证据与语义审阅闸门
make eval-clean # 干净检出重建固定输入产物后执行独立覆盖率闸门
make new-task  # 从 docs/templates/ 生成任务三件套
make baseline  # 把当前 findings 记为已知债务（仅在有意接受时使用）
```

针对具体 deck 的工具：

```
make validate PPTX=deck.pptx      # 结构错误 + 启发式警告
make render   PPTX=deck.pptx OUT=d # 逐页 PNG/PDF
make montage  DIR=slides/ OUT=m.webp
make lint-copy SRC=deck.pptx      # 文案反 AI 味初筛
make pixel-qa DIR=renders/       # 渲染图像素缺陷检查
python3 tools/validate_pptx.py deck.pptx --font-policy typography-receipt.json --viewing-profile meeting-room # 角色/脚本字体声明与继承字号
make new-style ID=x NAME=...       # 新建风格 preset（可选 REGISTER=1）
```

上下文成本核算（只读，用于复核优化幅度）：

```
python3 tools/context_savings.py [--baseline HEAD]  # 必读路径 / 可选设计参考的前后对比
python3 tools/check_context_budget.py --report      # 当前必读 + 可选 + 全量合计
python3 tools/check_context_budget.py --report --skill subaru-brainstorm # 分路线成本
```

本地、Agent 与自建 CI 使用**同一个入口**，避免"我本地过了"。

仓库当前**不附带 CI workflow**（`.github/workflows/` 已移除）；`make eval-clean` 供本地、Agent 或自建 CI 在干净检出上重建不入库的固定测试产物，用 `uv` 解析内置 `create_slides.py` 已声明的 PEP 723 依赖。这不把 uv、图片生成或其他外部 skill 变成 `subaru-slides` 的强制运行时依赖。

## 2. Harness 维护状态

| 项 | 内容 | 状态 |
|---|---|---|
| **H1** | `AGENTS.md` + `CLAUDE.md` | 已完成 |
| **H2** | `schemas/` 机读契约（契约见 [schemas](../schemas/)） | 已完成 |
| **H3** | `tools/` 校验器（validate_skills / check_links / check_consistency / check_assets / check_style_system / gen_style_router / check_context_budget / check_installability / doctor） | 已完成 |
| **H4** | `Makefile` 质量门统一入口（CI workflow 已移除） | 已完成 |
| **H5** | 任务模板 `docs/templates/` + Definition of Done + PR 模板 + `make new-task` | 已完成 |
| **H6** | `evals/` 回归基准（5 个 case + `run_evals` + `pptx_inspect`） | 已完成 |
| **H7** | pre-commit（`make hooks`） | 已完成（可选启用） |
| **H8** | 上下文成本护栏：`styles/router.md` 选型摘要 + `check_context_budget`（必读路径预算与按需读取纪律） | 已完成 |
| **H9** | 对话证据护栏：brainstorm 固定案例、配对参数、原文引用与语义审阅检查 | 检查器与案例已实现；真实模型对照结果待验证 |

协作与知识维护入口见 [工程决策](decisions/README.md)；历史条目迁移结果在索引中核对。

## 3. Baseline 机制

- 历史遗留问题记录在 `tools/baseline.json`，被 suppress 的 finding **不会**让 `make check` 失败。
- 只有**新出现**的阻塞项才失败——既让存量债务不一次性阻断，又能防止回归。
- 有意接受新的债务时运行 `make baseline`（写回 baseline）；不要用它掩盖真实 bug。

## 4. 仓库目录

```
subaru-skills/
├── AGENTS.md                  # 开发协作入口
├── CLAUDE.md                  # → 指向 AGENTS.md
├── README.md                  # 面向使用者：安装、能力、依赖
├── PROVENANCE.md              # 上游出处与再分发授权记录
├── VERSION / CHANGELOG.md     # 发布版本与变更记录
├── LICENSE                    # MIT（LesBit）；不自动覆盖第三方内容
├── skills/
│   ├── subaru-slides/         # 可独立安装的演示 skill
│   └── subaru-brainstorm/     # 可独立安装的对话 skill
├── schemas/                   # (H2) 机读契约：skill frontmatter / openai-agent / styles.*
├── tools/                     # (H3) 校验器：validate_skills / check_links / check_consistency / ...
├── docs/                      # 验收清单、模板、工程规范、决策与验证缺口
├── evals/                     # (H6) 回归基准：固定 brief + 结构断言
├── tests/                     # harness 单元测试
```

`Hx` 对应上面的维护状态；目录内容以当前检出为准。

## 4. 对话行为证据

`make eval-brainstorm` 与 deck eval 分开运行，避免把对话质量混入对象计数断言。
案例、运行格式、重复次数与人工/模型/自评边界见 [brainstorm eval](../evals/brainstorm/README.md)。
检查器不调用模型。缺真实运行或缺审阅时闸门失败，不以 synthetic 单元 fixture 补覆盖率。
生成结果统一存入已有忽略目录 `evals/results/brainstorm/`，不得进入 skill 安装包或暂存区。

## Public documentation site

`make site` 使用 Python 标准库把 `site/content.json` 与样式、交互构建到忽略目录 `output/site/`。构建只复制原创公开案例，不依赖前端包、网络或宿主工具。`make check-site` 已接入统一 `make check`，在临时目录核对生成页面的本地链接、锚点、元信息、sitemap 与下载 hash；`make test` 包含缺资产、坏锚点、损坏下载与元信息的负向回归。它不检查搜索效果、外部链接或远端部署。

案例的确定性重建在 `examples/build_decks.py`，使用 PEP 723 声明 `python-pptx>=1.0.0`（现有原生构建能力，不成为 skill 硬依赖）。两份成品与 WebP 预览各小于 1MB，作为有意维护的公开样例入库；原始渲染与构建站点留在 `output/`。重建后需重新渲染并更新 receipt 与预览，不能沿用旧视觉证据。
