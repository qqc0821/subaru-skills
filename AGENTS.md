# AGENTS.md — subaru-skills 工程与 AI 协作规范

> 本文件是本仓库对 **AI 编码代理**（Claude Code / Codex / Cursor / DSH 等）与人类贡献者的
> **单一事实源（single source of truth）**。开始任何修改前，请先完整阅读。
> `CLAUDE.md` 只是指向本文件的入口，不重复规则。
>
> 冲突时的优先级：**仓库工程约定以本文件为准；某个 skill 的运行时行为以该 skill 的 `SKILL.md` 为准。**

---

## 1. 仓库是什么

- `subaru-skills` 是一个**项目级 Agent Skill 仓库**，当前包含 `skills/subaru-slides/`（从内容到成品 PPTX 的演示文稿制作）。
- 每个 `skills/<name>/` 子目录是一个可被 Agent 直接加载的 skill 包。
- 仓库同时维护一套 **Harness**（校验器、CI、模板、回归基准），用于约束 AI 辅助开发，见第 8 节。

当前 / 目标目录结构：

```
subaru-skills/
├── AGENTS.md                  # 本文件（单一事实源）
├── CLAUDE.md                  # → 指向本文件
├── README.md                  # 面向使用者：安装、能力、依赖
├── PROVENANCE.md              # 上游出处与再分发授权记录
├── VERSION / CHANGELOG.md     # 发布版本与变更记录
├── LICENSE                    # MIT（LesBit）；不自动覆盖第三方内容
├── skills/
│   └── subaru-slides/         # 一个 skill 包，见第 3 节
├── schemas/                   # (H2) 机读契约：skill frontmatter / openai-agent / styles.*
├── tools/                     # (H3) 校验器：validate_skills / check_links / check_consistency / ...
├── docs/                      # (H5) definition-of-done / templates / lessons-learned
├── evals/                     # (H6) 回归基准：固定 brief + 结构断言
├── tests/                     # harness 单元测试
└── .github/workflows/         # (H4) CI
```

> `(Hx)` 标注对应 Pre-P0 Harness 建设项；H2–H6 已落地，状态见第 8.3 节。

---

## 2. 硬性规则（Must / Must Not）

### Must（必须）

1. **过闸**：任何 skill 改动提交前必须通过 `make check`；CI 使用同一入口。
2. **薄入口**：一个 skill 的 `SKILL.md` ≤ **200 行**，超出部分下沉到 `references/`。
3. **零外部依赖为默认**：需要外部能力时先做**能力探测**，并提供**降级路径**；外部 skill 只能"检测到则增强"，不能设为必需。
4. **语言**：用户可见文案**中文优先**（保留必要英文术语）；代码、路径、文件名、JSON key、commit message 用**英文**。
5. **任务留痕**：开任务前用 `make new-task` 生成 `task_plan.md` / `findings.md` / `progress.md` 三件套并边做边更新；**这三个文件不入库**（发布仓库只保留用户可见内容），结项时把结论固化成 `docs/lessons-learned.md` 或代码注释。
6. **改名即修链**：改路径/重命名后，必须同步检查并修复所有相对链接与交叉引用。
7. **新依赖先说明**：新增依赖、脚本或二进制资产前，先说明必要性，并记录到本文件或该 skill 的依赖文档。

### Must Not（禁止）

1. 提交 **>1MB 的二进制**；样例图必须压缩为 WebP，并遵守体积预算。
2. 提交 **secrets / token / API key**、`.DS_Store`、临时产物、依赖缓存（`node_modules/`、`.venv/` 等）。
3. 硬编码用户主目录或机器相关绝对路径（`~/.claude`、`/Users/<name>`、`$HOME/.agents` 等）。一律用"skill 相对路径 + 运行时探测"。
4. 把外部 skill 名写死为必需依赖（如 `$presentations`、`imagegen`）。
5. 在 `SKILL.md` 里堆长文；或把同一份信息（风格计数、色板、推荐表）重复维护到多处。
6. **文档说 A、实现做 B**；改实现必须同步改文档。

---

## 3. Skill 包规范

### 3.1 目录结构

```
skills/<name>/
├── SKILL.md               # 薄入口：路由 + 铁律 + 流程 + 检查点（≤200 行）
├── agents/openai.yaml     # UI 元数据（见 3.5）
├── references/            # 按需加载的长文（设计原则、路径细节、QA 清单…）
├── scripts/               # 可执行辅助脚本（见 3.4）
├── assets/                # 样例图等静态资产（见 3.6）
└── styles/                # （可选）机读风格系统（见第 4 节）
```

### 3.2 `SKILL.md` frontmatter

```yaml
---
name: <skill-name>        # 必须与目录名完全一致，小写连字符
description: <一句话>      # 必须写清"当用户……时使用"，包含中英文触发词与同义词
---
```

### 3.3 行数与体积预算

- `SKILL.md` ≤ 200 行。
- 单个 reference 文件 ≤ 600 行；超出需拆分。
- 一个 skill 包总量 ≤ 5MB。

### 3.4 `scripts/`

- 优先 Python 3.10+，使用 **PEP 723 内联依赖**，用 `uv run` 可直接执行。
- 每个脚本必须有 `--help`、清晰的错误信息与明确的退出码。
- 依赖环境的脚本提供 `--doctor` 自检（缺什么、怎么装）。
- 不写死路径；默认不联网（除非用户明确要求）。

### 3.5 `agents/openai.yaml`

```yaml
interface:
  display_name: "<显示名>"
  short_description: "<一句话，说明能力>"
  brand_color: "#RRGGBB"
  default_prompt: "Use $<name> to <目标>. <关键约束>."
policy:
  allow_implicit_invocation: true
```

### 3.6 `assets/`

- 样例图使用 **WebP**；文档中声明的体积/尺寸必须与实际一致。
- 命名使用稳定的风格 id（英文小写连字符），不要用中文或空格。

---

## 4. 风格系统约定

- 若 skill 提供多风格，`styles/index.json` 是**风格数量、命名、主题推荐、样例映射的唯一事实源**。
- `SKILL.md`、gallery 文档、样例目录**不得各自维护**一份可能漂移的计数；只引用 index。
- 每个风格一个 `styles/<id>.md` preset（字段定义见 P0-5）。
- 风格 base prompt 保持**简短**（≤5 行），描述情绪与世界观；不微操构图、不写 NOT 约束。

---

## 5. 依赖与能力策略

- 执行能力分四类：**原生可编辑构建器** / **图片生成** / **HTML deck 运行时** / **渲染器**（LibreOffice 等）。
- 选择顺序（详见 `skills/subaru-slides/references/dependencies.md`）：
  `A 原生可编辑 → B' 混合 → C HTML deck → B 全 AI 视觉 → create_slides.py 兜底`。
- 任一能力缺失必须**明确告知用户**，不得静默换路或假装端到端。
- 外部 skill 仅作为增强，必须可选、可降级。

---

## 6. Git / 提交 / PR

- 分支：`<type>/<scope>-<short-desc>`（如 `feat/subaru-slides-styles-index`）。
- 提交信息：`<type>(<scope>): <subject>`；`type ∈ {feat, fix, docs, chore, refactor, test, ci}`。
- 一个提交只做一件事；不夹带无关格式化或重排。
- 不 force-push 主分支；不提交生成物（`.codex-build/`、`output/`、`.chart-data-*/` 等应进 `.gitignore`，由 H4 的 `check_assets` 兜底）。
- PR 逐项勾选 Definition of Done（H5 的 PR 模板）。

---

## 7. 常见任务的正确做法

- **改某个 skill 的文档/脚本**：先读该 skill 的 `SKILL.md` 与其 `references/`，再改；改完跑第 8 节质量门。
- **加一个新风格**：在 `styles/index.json` 与 `styles/<id>.md` 同步登记；补样例图；不要只改 SKILL.md 的描述。
- **改路径 / 重命名**：全库搜索旧路径与引用，修完再校验。
- **引入新能力**：走"能力探测 + 降级"，不要新增硬依赖。
- **开新任务**：运行 `make new-task` 从 `docs/templates/` 生成三件套（已存在时跳过，`--force` 覆盖）。

---

## 8. 校验与质量门

### 8.1 统一入口（已落地）

```
make check     # = validate_skills + check_links + check_consistency + check_assets + check_style_system
make test      # 脚本冒烟 / 单元测试
make doctor    # 环境能力自检
make eval      # 本机 eval 覆盖率闸门（PASS / FAIL / SKIP / BLOCKED）
make eval-ci   # CI 重建固定输入产物后执行独立覆盖率闸门
make new-task  # 从 docs/templates/ 生成任务三件套
make baseline  # 把当前 findings 记为已知债务（仅在有意接受时使用）
```

针对具体 deck 的工具：

```
make validate PPTX=deck.pptx      # 结构错误 + 启发式警告
make render   PPTX=deck.pptx OUT=d # 逐页 PNG/PDF
make montage  DIR=slides/ OUT=m.webp
make lint-copy SRC=deck.pptx      # 文案反 AI 味初筛
make new-style ID=x NAME=...       # 新建风格 preset（可选 REGISTER=1）
```

本地、Agent、CI 使用**同一个入口**，避免"我本地过了"。

CI 的 `make eval-ci` 使用 `astral-sh/setup-uv@v6`，只为解析内置 `create_slides.py` 已声明的 PEP 723 依赖并重建不入库的固定测试产物；这不把 uv、图片生成或其他外部 skill 变成 `subaru-slides` 的强制运行时依赖。

### 8.2 辅助手动检查（可选；已被 `make check` 覆盖）

```bash
# 1) 外部依赖 / 用户路径扫描（期望：无输出）
grep -rnE '\$presentations|\$imagegen|nano-banana|~/.claude|/Users/|\.agents/skills' skills/ || true

# 2) 系统垃圾文件（期望：无输出）
find . -name '.DS_Store' -not -path './.git/*' -print

# 3) 单文件体积预算（>1MB 需说明）
find skills -type f -size +1M -print

# 4) skill 包体积
du -sh skills/*

# 5) Markdown 相对链接可达性（在 check_links.py 落地前人工核对改动涉及的文件）
```

### 8.3 Harness 建设状态

| 项 | 内容 | 状态 |
|---|---|---|
| **H1** | `AGENTS.md` + `CLAUDE.md` | 已完成 |
| **H2** | `schemas/` 机读契约（4 个 schema） | 已完成 |
| **H3** | `tools/` 校验器（validate_skills / check_links / check_consistency / check_assets / check_style_system / doctor） | 已完成 |
| **H4** | `Makefile` + `.github/workflows/ci.yml` | 已完成 |
| **H5** | 任务模板 `docs/templates/` + Definition of Done + PR 模板 + `make new-task` | 已完成 |
| **H6** | `evals/` 回归基准（3 个 case + `run_evals` + `pptx_inspect`） | 已完成 |
| **H7** | pre-commit（`make hooks`）+ `docs/lessons-learned.md` | 已完成（可选启用） |

### 8.4 基线（baseline）机制

- 历史遗留问题记录在 `tools/baseline.json`，被 suppress 的 finding **不会**让 `make check` 失败。
- 只有**新出现**的阻塞项才失败——既让存量债务不一次性阻断，又能防止回归。
- 有意接受新的债务时运行 `make baseline`（写回 baseline）；不要用它掩盖真实 bug。

---

## 9. 任务工作流（AI 协作标准动作）

1. 读本文件 + 目标 skill 的 `SKILL.md` 与相关 `references/`。
2. `make new-task` 生成 `task_plan.md`（目标、阶段、验收、错误日志），边做边更新 `progress.md`，发现记入 `findings.md`。
3. 小步改动，保持三件套与实现同步。
4. 跑第 8 节质量门，修复所有阻塞项。
5. 更新验收结论与残余风险。
6. 结项：把可复用的结论写入 `docs/lessons-learned.md`，并确认三件套**没有被 `git add`**。
7. 按第 6 节约定提交。

---

## 10. 出处与许可

- `subaru-slides` 派生自上游 `huashu-slides`（审计基线 commit `791450a2594a3506144917517ff5533c344a62b0`）；上游当时**无根 LICENSE**。
- 再分发前须确认授权；provenance 记录见 `PROVENANCE.md`。
- 仓库根 MIT LICENSE 覆盖本仓库原创内容，**不自动覆盖**第三方复制内容。

---

## 11. 本文件的维护

- 本文件由 Pre-P0 H1 建立。
- 任何对硬性规则的增删，必须在**同一提交**内更新本文件。
- H2–H7 落地后，同步更新第 8.3 节状态表。
