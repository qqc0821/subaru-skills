# subaru-skills

面向 AI Agent 的 **Agent Skills** 集合：把源内容变成结构清晰、视觉可控的演示文稿。

当前包含 1 个 skill：**`subaru-slides`**（端到端 PPTX / 幻灯片制作）。

---

## 安装

### 方式一：skills CLI（推荐）

```bash
# 安装到当前项目
npx skills add qqc0821/subaru-skills

# 或安装到用户级（所有项目可用）
npx skills add qqc0821/subaru-skills --global
```

安装后可直接用 `$subaru-slides` 显式调用；当任务涉及做 PPT / 幻灯片 / 演示文稿 / 路演 / 课件时，Agent 也会自动选中它。

只装其中一个 skill：

```bash
npx skills add qqc0821/subaru-skills --skill subaru-slides
```

查看仓库里有哪些 skill 而不安装：

```bash
npx skills add qqc0821/subaru-skills --list
```

### 方式二：手动 clone

```bash
git clone https://github.com/qqc0821/subaru-skills.git
cp -R subaru-skills/skills/subaru-slides <你的 skill 目录>
```

各 Agent 的 skill 目录约定：

| Agent | 用户级目录 | 项目级目录 |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| DSH / Codex / 其他 | `~/.agents/skills/` | `.agents/skills/` |

> `skills-cli` 的做法是把包放在 `~/.agents/skills/<name>/`，再在各 Agent 目录建软链。
> 手动安装时按你的 Agent 约定放即可，skill 本身不依赖具体路径。

---

## 使用

安装后对 Agent 说需求即可，例如：

```
用 $subaru-slides 把这份市场分析做成 10 页管理层汇报 PPT
```

skill 会依次完成：**能力探测 → 选择执行路径 → 内容结构化 → 选择视觉风格 → 构建 → 逐页渲染质检 → 交付**，
并在关键节点（大纲、风格、关键页）向你确认。

### 它会问你的两件事

1. **合作模式**：Full Auto / Guided（默认）/ Collaborative
2. **输出形态**：可编辑 PPTX / 视觉型 PPTX / HTML deck

### 能力与降级

`subaru-slides` 是 **capability-portable** 的：先探测环境，再选路径；任何能力缺失都会**明确告知你**并降级，
不会静默换路或假装端到端。

| 能力 | 缺了会怎样 |
|---|---|
| 原生可编辑构建器 | 无法做 A / B'；改用 HTML deck 或纯视觉方案，且文字不可编辑 |
| 图片生成 | 跳过 AI 配图，只用原生图形与排版 |
| 渲染器（LibreOffice + poppler） | 只做结构校验，并声明**未做**视觉检查 |
| 以上都没有 | 退回 `create_slides.py`：只能生成图片型 PPTX |

执行顺序：`A 原生可编辑 → B' 混合 → C HTML deck → B 全 AI 视觉 → create_slides.py 兜底`。

### 环境自检

```bash
# 从仓库根目录
make doctor

# 或直接探测（会输出推荐路径）
python3 skills/subaru-slides/scripts/detect_capabilities.py
```

`make doctor` 的结论是**本机探测结果**，不是依赖要求——缺哪项就降级，不会导致安装失败。

---

## 依赖

**运行 skill 本身零依赖。** 以下都是可选增强，按需安装：

| 用途 | 需要 | 安装 |
|---|---|---|
| 图片→PPTX 兜底脚本 | Python 3.10+ 与 `uv`（依赖由 PEP 723 内联声明） | `uv` 见 [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| PPTX 逐页渲染质检 | LibreOffice（`soffice`）+ poppler（`pdftoppm`） | `brew install --cask libreoffice poppler` |
| HTML deck 导出 PPTX | Chrome / Chromium | 按系统安装 |

### 最小可用验证

只装了 skill、没有任何可选依赖时，下面两条都能跑通：

```bash
# 1) 看看这台机器有什么能力、推荐走哪条路径
python3 .agents/skills/subaru-slides/scripts/detect_capabilities.py

# 2) 把若干张图直接合成 PPTX（首次运行会自动拉取 PEP 723 声明的依赖）
uv run .agents/skills/subaru-slides/scripts/create_slides.py \
  slide-01.png slide-02.png slide-03.png \
  --layout title_below -t "第一页" "第二页" "第三页" \
  -o output.pptx
```

预期输出（实测）：

```
Presentation saved: .../output.pptx
  3 images, 3 slides, layout: title_below
```

> 路径按你的安装位置调整：`npx skills add` 默认装到 `.agents/skills/`，
> 从仓库内使用时则是 `skills/subaru-slides/scripts/`。

---

## 仓库结构

```
subaru-skills/
├── skills/subaru-slides/    # skill 包本体（安装时只需这一个目录）
│   ├── SKILL.md             # 薄入口：路由 + 铁律 + 流程
│   ├── references/          # 按需加载的设计原则、路径细节、QA 清单
│   ├── styles/              # 23 个风格 preset + index.json（风格数据唯一事实源）
│   ├── scripts/             # 能力探测与兜底构建脚本
│   └── assets/              # 风格样例图
├── tools/                   # 质量门校验器
├── schemas/                 # 机读契约（frontmatter / preset / index）
├── evals/                   # 回归基准：固定 brief + 结构断言
├── tests/                   # harness 单元测试
├── docs/                    # Definition of Done、模板、经验沉淀
└── Makefile                 # 统一入口
```

安装 skill 时只需要 `skills/subaru-slides/`；其余目录是**开发这个 skill 用的 Harness**。

---

## 开发与质量门

```bash
make check     # 全部门禁：frontmatter / 链接 / 一致性 / 资产 / 风格系统
make test      # 脚本冒烟 + 单元测试
make doctor    # 环境能力自检
make eval      # 回归基准与覆盖率闸门
make help      # 全部命令
```

针对具体 deck：

```bash
make validate PPTX=deck.pptx        # 结构错误 + 启发式警告
make render   PPTX=deck.pptx OUT=d  # 逐页 PNG/PDF
make montage  DIR=slides/ OUT=m.webp # 联系表
make lint-copy SRC=deck.pptx        # 文案初筛
make new-style ID=x NAME="..."      # 新建风格 preset
```

本地、Agent、CI 使用**同一个入口**（`make check`），避免"我本地过了"。

改动前请先读 **`AGENTS.md`**（本仓库的工程规范与单一事实源）。
贡献者与来源说明见 **`PROVENANCE.md`**。

---

## 许可

仓库原创内容采用 MIT（见 `LICENSE`）。
`skills/subaru-slides` 派生自上游 `huashu-slides`，**再分发前请先阅读 `PROVENANCE.md`**——
MIT 声明不自动覆盖第三方内容。
