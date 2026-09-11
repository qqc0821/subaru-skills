# subaru-slides 优化方案（v1 · 2026-09）

> 目标：把项目内的 `skills/subaru-slides` 做成"最好的 PPT 制作 skill"。
> 方法：深度审计现状 → 对标 6 个同类顶级 skill → 取其精华 → 给出可落地的分阶段改造方案。
>
> 审计范围：`skills/subaru-slides/` 全部 9 个文本文件 + 17 张样例图 + `.codex-build/ev-trends/` 真实产物（build.mjs、validation.json、slide-01~10.png）。

---

## 0. TL;DR（一页结论）

**它已经做对了什么**
1. 端到端流程完整：内容结构化 → 设计系统 → 构建 → 装配 → 预览打磨，带 4 个检查点。
2. **风格系统是真正的护城河**：23 个风格（18 个 AI 视觉风格 + 5 个专业编辑风格），配主题推荐表、设计运动对照、17 张样例图。这是 OpenAI/Anthropic/baoyu 都没有的。
3. **"反过度约束"的 AI 出图方法论**（描述情绪而非构图、base style 保持短）来自真实踩坑，价值极高。
4. `create_slides.py` 是干净、可移植的图片→PPTX 兜底（PEP 723 内联依赖）。
5. 中文优先的语言规则。

**三个致命问题**
1. **Path A 的文档已经过时**：SKILL.md 把它写成"HTML slides → html2pptx"，但项目真实产物 `.codex-build/ev-trends/build.mjs` 用的是 Codex 原生 `@oai/artifact-tool` + `finalizePresentation`，全程没有 HTML。文档与实际实现脱节。
2. **依赖不可移植且非自包含**：Path A 依赖 `$presentations`，配图依赖 `imagegen`，两者都是 Codex 运行时专属；本 DSH 会话的技能目录里**并没有**这两个 skill。一旦宿主不同，skill 直接失效。
3. **没有质检闭环**：Path B 的 AI 图和所有文字、图表、溢出、重叠、占位符错误全靠"肉眼看"。对比 OpenAI presentations 的 13 道 finalize 闸、Anthropic pptx 的 `validate_layout.py`，差距是数量级的。

**两条主线**
> **主线 0 · Pre-P0：先给项目搭 Harness。** 让"用 AI 改这个仓库"本身有标准、有约束、有回归——`AGENTS.md` 单一事实源 + schema + `make check` 统一闸 + CI + 任务模板 + eval 基准；它是后面所有改造的地基。
> **主线 1 · P0–P2：把 skill 升级为引擎。** 从"风格百科 + 两条靠外部 skill 的路径"，升级为 **"内容闸 + 机读风格系统 + 三层可插拔执行后端 + 硬质检闭环 + 可审计交付"** 的一等公民 PPT 引擎，同时保留其独有的中文风格库与 AI 视觉方法论。

**Top 8 最高杠杆改动**
| # | 改动 | 收益 |
|---|---|---|
| 0 | **Pre-P0：给项目搭 Harness**（`AGENTS.md` + schema + `make check` + CI + 模板 + evals） | AI 开发有标准、有约束、可回归，后续改造不跑偏 |
| 1 | SKILL.md 瘦身为路由器，长文下沉 `references/` | 触发更稳、上下文更省、可维护 |
| 2 | Path A 重定义为"原生可编辑对象"，HTML 降为 Path C | 文档与真实实现一致，可编辑性成为一等公民 |
| 3 | 新增 `scripts/detect_capabilities.py` + 优雅降级 | 跨 Claude/Codex/DSH/Cursor 可移植 |
| 4 | 新增**混合模式 Path B'**：AI 无字视觉底图 + 原生可编辑文字/图表 | 同时拿到 Path B 的视觉与 Path A 的可编辑 |
| 5 | 风格系统机读化（`styles/index.json` + 每风格一个 preset） | 可路由、可扩展、可校验，消除计数混乱 |
| 6 | 新增质检脚本（render/validate/montage）与"claim boundary" | 把"看起来没问题"变成"有据可查" |
| 7 | 引入"封面三选一预览"与"模板/品牌跟随" | 选择从"读文字"变"看图"，并支持企业模板 |

---

## 1. 现状深度评估

### 1.1 真实能力盘点

| 能力 | 现状 | 证据 |
|---|---|---|
| 内容结构化 | 强（assertion-evidence、5/5/5、检查点表格） | `SKILL.md` Step 1 |
| 风格库 | 强（23 风格、主题推荐、样例图、设计运动） | `SKILL.md` Step 2、`references/proven-styles-gallery.md` |
| AI 出图方法论 | 强（短 prompt、描述情绪、base style、负面清单） | `SKILL.md` Step 3-B、`references/proven-styles-snoopy.md` |
| 图片→PPTX | 可用（6 种版式、模板支持、边界处理） | `scripts/create_slides.py` |
| 原生可编辑 PPTX | 真实可用但**文档写错**（实际走 Codex artifact-tool） | `.codex-build/ev-trends/build.mjs`、`subaru-ev-trends-validation.json` |
| HTML→PPTX | 依赖外部 `$presentations`，且指引是旧的 html2pptx 规则 | `SKILL.md:520-534`、`references/dependencies.md:17` |
| 模板/品牌跟随 | 完全没有 | 无对应文件 |
| 原生表格/图表 | 仅在真实 build 里用过，SKILL.md 未固化规则 | `build.mjs` 有 3 个原生图表，但 SKILL.md 无 native-evidence 章节 |
| 质检自动化 | 无 | 无任何校验脚本 |
| 演讲者备注 | 只在最终打磨里一句"Speaker notes" | `SKILL.md` Step 5 |
| 中文排版 | 有语言规则；无字体/度量/嵌入细节 | `SKILL.md` Step 1、Typography Rules |
| 依赖自包含 | 依赖 `$presentations`/`imagegen` 两个外部 skill | `references/dependencies.md` |
| 跨 harness | 面向 Codex | frontmatter、`agents/openai.yaml` |

### 1.2 必须保留的亮点

1. **"描述情绪，不要微操构图"** 的 AI 出图第一性原理（`proven-styles-snoopy.md`），并附了反面教材（过度约束版 prompt 导致多样性骤降）。
2. **按主题自动推荐风格**的决策表，把"选风格"从审美玄学变成可执行流程。
3. **设计运动 → skill 风格对照**，为用户提供共同语言（"这个偏田中一光"）。
4. **检查点机制**（Guided 默认 3 个检查点）与合作模式分级。
5. **中文优先 + slide 内容中文、section label 可英文**的规范。
6. **法律/身份注意事项**：fork 自上游无 LICENSE，已在 `task_plan.md` 标记为 caveat（需继续保留）。

### 1.3 问题清单（按严重度）

#### P0 · 结构性 / 正确性

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| P0-1 | **Path A 定义与实现脱节**：文档说 HTML→html2pptx，真实实现是原生 JS 对象（artifact-tool），没有 HTML | `SKILL.md:29,520-534` vs `build.mjs` | 模型照文档做会走弯路、产出低质量路径 |
| P0-2 | **硬依赖外部 skill**：`$presentations`、`imagegen` 均非本仓库资产，也不是标准 skill | `dependencies.md:17,21`；本 DSH 会话技能目录无这两个 | 换宿主即失效；"端到端"是伪命题 |
| P0-3 | **内部自相矛盾**：Snoopy 风格一处要求"始终指定 NOT Snoopy"，另两处明确禁止 | `proven-styles-gallery.md:83` vs `SKILL.md:385`、`proven-styles-snoopy.md:38` | 模型无所适从，出图质量不稳定 |
| P0-4 | **风格计数混乱**：frontmatter 说 18 种，正文列 12 + "10 种"，gallery 标 18+5，样例图 17 张 | `SKILL.md:3`、`proven-styles-gallery.md:1`、`assets/style-samples/` | 用户与模型都无法确认"到底有多少风格、有没有样例" |
| P0-5 | **无质检闭环**：全流程没有一个自动校验步骤 | 全目录 | 文字错、溢出、占位符残留只能靠运气 |
| P0-6 | **无模板/品牌跟随**：企业场景最重要的能力缺失 | 无对应文件 | 无法进入正式商务/品牌场景 |
| P0-7 | **仓库无工程 Harness**：没有 `AGENTS.md`/校验器/CI/任务模板/eval，AI 改 skill 无统一标准，才会反复出现依赖漂移与文档脱节 | `task_plan.md`、无 `tools/`/CI | 每次 AI 贡献都可能引入新的不一致 |

#### P1 · 一致性 / 质量

| # | 问题 | 证据 |
|---|---|---|
| P1-1 | 分辨率不一致：`prompt-templates.md` §2 用 1920x1080，§3 用 2048x1152；SKILL.md 用 2048x1152 | grep `1920`/`2048` |
| P1-2 | 主题推荐表重复且不一致：SKILL.md 与 gallery 的"数据报告"推荐不同 | `SKILL.md` Step 2 vs `proven-styles-gallery.md` |
| P1-3 | gallery 说 Neo-Brutalism "用 HTML→PPTX 路径验证"，但既无 HTML 模板也无原生规则，样例图也缺 Neo-Brutalism | `proven-styles-gallery.md`、样例目录 |
| P1-4 | 无 CJK 字体/嵌入/度量规范；Path B 依赖 AI 渲染中文（易错） | Typography Rules 仅一句系统字体 |
| P1-5 | 5 个编辑风格（Pentagram/Fathom/Müller/Build/Takram）**无样例图** | 样例目录 |
| P1-6 | 文档引用"如果当前环境另有设计系统 skill，再按需读取"——措辞含糊，无具体路由 | `SKILL.md` Step 2 末段 |
| P1-7 | AI 文风没有约束；生成的中文文案容易"AI 味" | 无 writing-quality 章节 |
| P1-8 | Path B 文字不可编辑且易渲染错，却没有"混合模式" | `SKILL.md` Step 3-B |

#### P2 · 资产 / 维护

| # | 问题 | 证据 |
|---|---|---|
| P2-1 | 样例图 14MB、PNG、960x535 小图，文档却称"<1MB" | `du -sh assets/style-samples` = 14M |
| P2-2 | 无测试、无 CI、无版本号 | 全目录 |
| P2-3 | 无能力自检（`--doctor`） | 全目录 |
| P2-4 | 无"经验教训"沉淀文件 | 全目录 |
| P2-5 | Licensing caveat（上游无 LICENSE）未落到交付文档 | `task_plan.md` |

---

## 2. 同类 skill 对标与"取其精华"

### 2.1 对标矩阵

| 维度 | subaru-slides | OpenAI presentations | Anthropic pptx | baoyu-design | html-to-editable-pptx / html-to-pptx |
|---|---|---|---|---|---|
| 定位 | 中文风格化 PPT | 原生可编辑 PPT（Codex） | OOXML 编辑老手 | 通用 HTML 设计（含 deck） | HTML→原生 PPTX |
| 内容结构化 | 极强 | 强 | 中 | 强 | 弱 |
| 风格/审美库 | 极强 | 中 | 强 | 强 | 中 |
| AI 视觉生成 | 极强 | 中 | 中 | 强 | 弱 |
| 原生可编辑 | 弱（文档错位） | 极强 | 极强 | 强 | 极强 |
| 模板/品牌跟随 | 无 | 极强 | 极强 | 强 | 中 |
| 质检/校验 | 无 | 极强（13 闸） | 强（validate_layout） | 强 | 中（对比审计） |
| 交付/可审计 | 无 | 极强（原子发布+receipt） | 中 | 中 | 中（side-by-side audit） |
| 中文支持 | 极强 | 中 | 中 | 中 | 极强 |
| 可移植性 | 弱 | 弱 | 中 | 极强 | 极强 |
| 演讲备注/动画 | 弱 | 中 | 中 | 极强 | 中 |

### 2.2 各家的精华清单（只列值得抄的）

**OpenAI presentations — 抄"工程骨架"**
- **两阶段候选/成品 + 原子发布事务**：草稿在私有目录，成品用 `fs.link` 拒绝覆盖，发布前后 sha256/inode/mtime 三重校验，失败按 inode 精确回滚，输出 `receipt`。
- **"阻塞 finding" vs "风格 warning" 分层**：启发式的排版判断只警告，绝不因估算误报否定用户设计（`STYLE_REVIEW_KINDS`）。
- **显式声明 vs 自动推断分离**：表格算术只有显式契约才阻塞，自动发现只诊断；图表属主用"声明 ∪ 实际发现"防漏检。
- **每个校验器输出 `claim_boundary`**：写清"我验证了什么、没验证什么"（如 `native_powerpoint_verified:false`），显著抑制模型过度断言。
- **source-free 校验器**：完整性与图表闸刻意不解析 notes/workbook 内容。
- **自证禁止**：字体/模板 reference 不得等于被校验的成品，防循环校验。
- **写作质量负例库**：5 类坏文案 + 7 类 AI-isms，几乎与领域无关，可直接搬。

**Anthropic pptx — 抄"编辑与目检"**
- **`validate_layout.py` 的 8 类版式检查**：空白页、越界、重叠、表格溢出、页脚侵入、单词折行、箭头悬空、低对比度；文本 bbox 估算考虑内边距/CJK/拉丁字宽/行距/autofit。
- **inventory → replace 两阶段文本替换**：先导出每个形状的真实位置/字号/对齐/bullet，再让模型只填 `paragraphs`，脚本自动清空未用形状并**检测溢出是否恶化**。
- **先修后校验、只报新增错误**：与原始文件的 XSD 错误集合做差，避免被模板自带的历史错误淹没。
- **缩略图网格 + 子代理目检 prompt**：把视觉 QA 变成有清单、有具体图片路径的可执行步骤。
- **模板槽位 ≠ 素材条目**、**修改页号必须记录**、**layout QA 先于 content QA**。
- **pack/unpack + schema 校验**：raw OOXML 编辑的正确姿势（元素顺序、smart quotes、`xml:space`）。

**baoyu-design — 抄"HTML deck 运行时与可编辑导出"**
- **`deck-stage.js` 组件**：1920×1080 舞台、缩放、键盘/触控导航、页码 overlay、speaker-notes postMessage 契约、print-to-PDF（一页一页）。
- **`data-anim` 约定**：声明式动画，能**原样导出为 PowerPoint 原生动画**。
- **editable PPTX 导出**：HTML 静态元素 → 原生文本框/形状/图片，不是截图。
- **静态 HTML 优先**：让用户能直接点改文本（编辑模式 splice 回源文件）。
- **type scale / spacing 用 CSS 变量**，validator 拒绝 <24px，Slide wrapper fill 规则。
- **设计系统 prompt 作为绑定约束**（`_ds_prompt.md`），可导入/复用/自检。
- **title-only 可读性测试 + 反 AI-isms 标题清单 + 大纲先写出来让用户读**。

**html-to-editable-pptx / html-to-pptx — 抄"HTML→原生形状"思路**
- CSS→PPT 路由表：文本/颜色/字号/对齐→原生文本框；背景/边框/圆角/线条→原生几何；渐变/阴影/filter/blend→本地快照垫底 + 文字仍在最上层。
- **Google Fonts 按实际用字子集化 + CJK 自动种子 Noto Sans SC/Noto Serif SC**——直接解决中文跨机乱码。
- **HTML/PPT side-by-side 审计材料**：把"转得对不对"变成可对比证据。
- **`--doctor` 环境自检**、**本地 `references/lessons-learned.md` 经验沉淀**、**渲染期零出网**。

**guizang-ppt-skill / beautiful-html-templates — 抄"选择体验"**
- **不描述风格，而是渲染 3 张封面让用户选**（beautiful-html-templates 的做法）——比 subaru 现在的文字描述强得多。
- **双视觉系统 + 锁定版式库**（guizang 的 Style B 有 22 种锁定版式）：把"版式"作为可复用组件，而非每次现编。
- **演讲者模式 + 排练计时 + 每页计划时长**。
- **单文件 HTML、零构建、ESC 索引**。

### 2.3 结论：subaru 应该站在谁的肩膀上

- **工程骨架 → OpenAI presentations**：能力探测、分层校验、原子交付、claim boundary。
- **编辑与目检 → Anthropic pptx**：`validate_layout.py` 思路 + inventory/replace + 缩略图目检。
- **HTML 运行时与可编辑导出 → baoyu-design**：`deck-stage` + `data-anim` + editable PPTX。
- **HTML→原生形状 → html-to-editable-pptx**：CSS 路由表 + 字体子集化。
- **选择体验 → beautiful-html-templates/guizang**：封面三选一 + 锁定版式 + 演讲者模式。
- **subaru 自己的独占资产**：中文风格库（23 风格 + 样例 + 运动对照）、AI 视觉方法论、主题推荐决策表——这些是护城河，必须保留并机读化。

---

## 3. 目标架构

### 3.1 七条设计原则

1. **一本书的目录（router）+ 按需取用的章节（references）**：SKILL.md ≤ 200 行，只做路由和铁律；细节全部下沉。
2. **能力探测，优雅降级**：先探测宿主有什么（原生构建器 / HTML deck 运行时 / 图片生成 / LibreOffice），再选路径；缺能力时明确告知，绝不假装端到端。
3. **可编辑是默认，截图是例外**：任何会被修改的文字/表格/图表必须原生；只有装饰性视觉才允许位图。
4. **一切判断都要有证据与边界**：每个自动检查输出"通过/警告/阻塞"和 `claim_boundary`。
5. **风格是数据，不是散文**：风格 preset 机读化（`styles/*.md` + `index.json`），两条路径共享同一套 token。
6. **中文优先**：字体、度量、断行、子集嵌入、短标题、样例图都以中文场景为准。
7. **先有 Harness，再改内容（Pre-P0）**：仓库自带 `AGENTS.md`、schema、`make check`、CI 与 eval；任何 skill 改造都在闸内进行。

### 3.2 三条执行路径 + 能力探测

| 路径 | 名称 | 产物 | 依赖能力 | 何时用 |
|---|---|---|---|---|
| **A** | Native Editable（推荐默认） | 原生可编辑 PPTX（文字/表格/图表） | 原生构建器：Codex `@oai/artifact-tool` / Anthropic `pptx` skill / 纯 `python-pptx` 兜底 | 需要后期编辑、企业模板、数据准确 |
| **B** | Full AI Visual | 全页 AI 图 + 图片 PPTX | 图片生成能力 | 追求视觉冲击、艺术化、快速草稿 |
| **B'** | **Hybrid（新增，强烈推荐）** | AI 无字视觉底图 + 原生可编辑文字/图表 | 图片生成 + 原生构建器 | 既要好看又要能改，**大多数正式 deck 的最优解** |
| **C** | HTML Deck | 单文件 HTML deck（可导出 PPTX/PDF） | deck-stage / HTML→PPTX 转换器 | 网页放映、演讲者模式、动画、社交传播 |

能力探测顺序：`A → B' → C → B → create_slides.py（最低兜底）`。任一能力缺失都要给出明确的一行提示，而不是静默换路。

### 3.3 目标目录结构

**仓库根（Pre-P0 Harness）**

```
subaru-skills/
├── AGENTS.md                     # 单一事实源：目录/命名/依赖/流程/提交 约定
├── CLAUDE.md                     # 指向 AGENTS.md 的 Claude Code 兼容入口
├── Makefile                      # make check / test / doctor / new-skill / new-style
├── schemas/                      # skill.frontmatter / openai-agent / styles.index / style.preset
├── tools/                        # validate_skills / check_links / check_consistency / check_assets / check_style_system / doctor
├── docs/
│   ├── definition-of-done.md
│   ├── authoring-a-skill.md
│   └── templates/{task_plan,findings,progress}.md
├── evals/                        # 回归基准：固定 brief + 结构断言
└── .github/
    ├── workflows/ci.yml
    └── PULL_REQUEST_TEMPLATE.md
```

**skill 包（P0–P2 目标结构）**

```
skills/subaru-slides/
├── SKILL.md                     # 瘦路由器（≤200 行）：何时用、6 条铁律、流程总览、能力探测、路径选择、检查点
├── agents/openai.yaml
├── references/
│   ├── workflow.md              # 端到端 10 阶段 + 4 检查点 + 交付清单
│   ├── content-structure.md     # 内容结构化、assertion-evidence、标题、5/5/5
│   ├── writing-quality.md       # 新增：反 AI 文风负例库（中文版）
│   ├── template-following.md    # 新增：模板/品牌跟随四步法
│   ├── native-evidence.md       # 新增：原生表格/图表/bullet + 单位护栏
│   ├── illustrations.md         # 新增：imagegen 路由、短 prompt 方法论、混合模式
│   ├── speaker-notes.md         # 新增：演讲备注与排练
│   ├── design/
│   │   ├── principles.md        # 从 design-principles.md 重构
│   │   ├── movements.md         # 从 design-movements.md 重构
│   │   ├── typography-cjk.md    # 新增：中文字体/代码点/断行/嵌入
│   │   └── color-systems.md     # 新增：机读色板
│   ├── paths/
│   │   ├── path-a-native.md     # 新增：原生可编辑构建
│   │   ├── path-b-visual.md     # 新增：全 AI 视觉
│   │   ├── path-b2-hybrid.md    # 新增：混合模式
│   │   └── path-c-html.md       # 新增：HTML deck
│   ├── qa/
│   │   ├── checklist.md         # 逐页目检清单（借鉴 Anthropic 子代理 prompt）
│   │   ├── render-and-validate.md
│   │   └── delivery.md          # receipt / claim boundary / 交付话术
│   └── dependencies.md          # 重写为能力矩阵 + 降级策略
├── styles/                      # 新增：机读风格系统
│   ├── index.json               # 主题→推荐→tier→path→preset 文件
│   ├── _schema.md               # preset 字段说明
│   └── <style-id>.md            # 每个风格一个 preset（23 个）
├── scripts/
│   ├── create_slides.py         # 保留（图片兜底）
│   ├── detect_capabilities.py   # 新增：探测 artifact-tool/deck-stage/imagegen/soffice/python-pptx
│   ├── build_pptx.py            # 新增：python-pptx 原生文本/表格/图表兜底
│   ├── render_preview.py        # 新增：soffice/LibreOffice 渲染 PNG/PDF
│   ├── make_montage.py          # 新增：contact sheet
│   ├── validate_pptx.py         # 新增：边界/重叠/溢出/字体/占位符检查
│   └── inspect_deck.py          # 新增：文本 inventory 导出（供替换/校对）
├── templates/                   # 新增：可选原生 PPTX 模板/母版 + 品牌词表
│   └── README.md
├── assets/
│   ├── style-samples/           # 压缩为 webp，目标 ≤3MB
│   └── palettes.json            # 新增：机读色板
└── lessons-learned.md           # 新增：本安装的经验沉淀（gitignored 可选）
```

---

## 4. 改造清单

### Pre-P0 · 项目 Harness（必须先于一切；给 AI 辅助开发加标准与约束）

**目标**：让"用 AI 开发这个 skill 仓库"本身可复现、可校验、可回滚。任何 agent 进来先读 `AGENTS.md`，跑 `make check`，用模板开任务，用同一套闸提交。

#### H1. `AGENTS.md`（根目录，单一事实源）
- 目录约定、SKILL.md 规范、命名与语言规则、依赖政策（默认零外部 skill 依赖）、改动流程、提交/PR 约定。
- 硬性条款：① 任何 skill 改动必须 `make check` 通过、CI 绿才能合；② SKILL.md ≤ 200 行，长文进 `references/`；③ 默认不依赖外部 skill，外部能力必须能力探测 + 降级；④ 用户可见文案中文优先，代码/路径/JSON key 用英文；⑤ 不提交 >1MB 二进制（样例图用 webp）、secrets、`.DS_Store`、临时产物；⑥ 改路径/重命名必须同步跑 link + consistency 检查；⑦ 任务先建/更新 plan，结束更新验收与 progress。
- `CLAUDE.md` 指向 `AGENTS.md`，避免两份规则漂移。

#### H2. `schemas/`（机读契约）
- `skill.frontmatter.schema.json`（name/description 约束）
- `openai-agent.schema.json`（`agents/openai.yaml`）
- `styles.index.schema.json` + `style.preset.schema.json`（配合 P0-5 风格机读化）

#### H3. `tools/` 统一校验器（CI 与 agent 共用）
- `validate_skills.py`：frontmatter、name == 目录名、description 质量、`agents/openai.yaml` schema。
- `check_links.py`：所有 Markdown 相对链接可达、无死链。
- `check_consistency.py`：风格计数三处一致；**跨文件矛盾检测**（同一术语的 must/never 冲突，如 Snoopy NOT 约束）；硬编码外部依赖/用户路径扫描（`$presentations`、`imagegen`、`~/.claude`、绝对 home 路径）。
- `check_assets.py`：体积预算、格式（PNG→WebP）、尺寸、无 `.DS_Store`/secrets。
- `check_style_system.py`：`styles/index.json` 与 preset 一一对应、必填字段、样例文件存在。
- `doctor.py`：能力探测（Node/artifact-tool/deck-stage/imagegen/soffice/python-pptx/字体），供 skill 运行时复用。

#### H4. 统一入口 + CI
- `Makefile`：`make check`（H3 全部）、`make test`、`make doctor`、`make new-skill`、`make new-style`。
- `.github/workflows/ci.yml`：`make check` + 冒烟测试 + 链接检查 + 资产预算，失败阻断。
- 本地、agent、CI 跑同一入口，避免"我本地过了"。

#### H5. 任务模板与 Definition of Done
- `docs/templates/{task_plan,findings,progress}.md`：沿用本项目已有的 plan/findings/progress 三件套，固化为模板与流程。
- `docs/definition-of-done.md` + `.github/PULL_REQUEST_TEMPLATE.md`：把第 5 节验收标准变成勾选项。
- 可选 `tools/new_task.sh` 一键起任务脚手架。

#### H6. Eval Harness（回归基准，让 AI 迭代"有标准"）
- `evals/`：若干固定 brief + 期望产物的**结构断言**（页数、原生图表/表格数、字体、无占位符、0 阻塞校验、中文无乱码）。
- 每次改 skill 跑一遍并对比历史结果，防止"改 A 坏 B"。
- 先覆盖 3 个基准：① 中文行业分析（原生图表）；② 全 AI 视觉风格页（Path B）；③ 混合模式 B'。

#### H7.（可选）pre-commit 与经验沉淀
- pre-commit 挂 `make check`。
- `docs/lessons-learned.md`：agent 每次踩坑追加，形成项目级记忆。

**为什么必须最先做**：P0–P2 会大改目录、路径、schema、计数与依赖；没有 Harness，这些改动本身就会重演现在的"文档与实现脱节、计数不一致、依赖漂移"。Harness 是让后续所有改造可安全迭代的地基。

### P0 · 地基（必须先做）

#### 4.1 SKILL.md 瘦身为路由器
- 把现有 616 行拆分为：frontmatter + 何时用 + 6 条铁律 + 流程总览图 + 能力探测 + 路径选择 + 检查点 + 参考索引。
- 保留"选风格"的最关键决策表（但改为指向 `styles/index.json`）。
- 所有长文移入 `references/`。目标：新模型读 200 行就能正确开始。

#### 4.2 路径重构
- **Path A 重写**：不再写 html2pptx 规则；改为"用宿主原生构建器直接声明原生对象"，给出伪代码接口（`shapes.add / text / charts.add / speakerNotes / tables`）与"禁止用截图代替文字/表格/图表"。
- **Path B' 混合模式新增**：AI 只生成"无文字视觉底图"（明确写入 `no text in image`），再由 Path A 叠加原生标题/正文/图表。这直接解决 `SKILL.md:29` 里 Path B "文字不可编辑"的缺陷。
- **Path C 明确为可选**：若宿主有 deck-stage（baoyu-design）或 html-to-editable-pptx，则走 HTML deck/导出；否则不推荐。
- 在 `references/dependencies.md` 里画能力矩阵，逐条写降级策略。

#### 4.3 能力探测 + 依赖自包含
- 新增 `scripts/detect_capabilities.py --json`：检测 Node/artifact-tool、deck-stage、imagegen、Chrome、LibreOffice、python-pptx、字体；输出结构化能力清单。
- SKILL.md 第一步改为"先跑能力探测"，据此选路径。
- `create_slides.py` 保留为最低兜底，并加 `--doctor`。
- 目标：**不依赖任何外部 skill 也能产出可用 PPTX**。外部 skill 仅作为增强。

#### 4.4 修复全部内部矛盾
- Snoopy：统一为"描述情绪、不写 NOT 约束"（删除 `proven-styles-gallery.md:83` 的"始终指定 NOT Snoopy"）。
- 分辨率：全库统一为"图像生成目标 2048×1152（或能力允许的更高 2K），HTML 舞台 1920×1080/1280×720"，并写清换算关系。
- 计数：以 `styles/index.json` 为唯一事实源（清楚标注 23 个 preset、其中 17 个有样例图、6 个待补样例）。
- 合并两份主题推荐表为一份，放在 `styles/index.json` 与 `SKILL.md` 中同步。

#### 4.5 风格系统机读化
- 每个风格一个 `styles/<id>.md`，字段：`id/name/name_en/tier/themes/formality/path/palette{background,text,accent[]}/typography{heading,body,ratio,cjk_font}/base_style_prompt/layout_blocks/pitfalls/sample`。
- `styles/index.json`：`{ schema_version, count, styles: [...], theme_recommendations: [...] }`。
- SKILL.md 的"选 3 个风格"改为读 index.json 匹配 `themes/formality`，再**渲染 3 张封面预览**给用户选（借鉴 beautiful-html-templates）。
- 每个 `base_style_prompt` 保持 ≤5 行（沿用现有正确经验）。

### P1 · 质量（决定"最好"与否）

#### 4.6 模板/品牌跟随（`references/template-following.md`）
- 四步法：判定用途 → 先侦察（渲染源页、抽尺寸/母版/字体/色/logo/footer）→ 原地编辑复用（禁止新重建、禁止遮罩覆盖）→ 并排验证。
- 借鉴 Anthropic：**模板槽位 ≠ 素材条目**；**改单页优先于改母版**；**记录被改页号**。
- 借鉴 OpenAI：`template-frame-map` 式 ids 编辑计划 + 覆盖率（不编造比例）+ family 指纹校验。
- 落地脚本（P1 可先手动）：`inspect_deck.py` 导出结构，`validate_pptx.py` 查占位符残留/遮罩覆盖。

#### 4.7 原生证据 + 单位护栏（`references/native-evidence.md`）
- 铁律：会被修改的表格、数据图表、图示必须原生；装饰视觉才用位图。
- 图表：单位/正负/精度显式；`31%` 用 `0.31`；删占位 "Chart Title"；堆叠标签 `inEnd/center`；图表字体单独设。
- 表格：每个 total 只算一次并复用；保留模板对齐。
- bullet：提供 `makeNativeBulletParagraphs` 式封装与 EMU/1-100pt 单位说明，禁止手打 bullet 字符/多文本框模拟。

#### 4.8 质检与交付闭环
- 新增 `references/qa/`：
  - **逐页目检清单**（重叠、溢出、贴边、页脚碰撞、低对比、占位符、装饰线错位、<0.3" 间距、<0.5" 边距）。
  - **`render_preview.py`**：优先 artifact-tool/内置渲染，其次 LibreOffice+pdftoppm，输出每页 PNG。
  - **`make_montage.py`**：contact sheet（只用于整册流，不替代逐页目检）。
  - **`validate_pptx.py`**：至少实现 6 类检查（空白页、越界、重叠>5%、文本溢出、表格溢出、字体一致）；输出 `findings`（阻塞）+ `warnings`（启发式）分层。
  - **`delivery.md`**：receipt（slide 数、字体、图表数、校验结果、`claim_boundary`）、原子发布（不覆盖已存在文件）、交付话术（不复述校验术语）。
- 明确 `claim_boundary`：例如"结构校验通过不代表 PowerPoint 能打开，也不代表 Google Slides 保真"。

#### 4.9 内容质量闸（`references/writing-quality.md`）
- 把 OpenAI presentations 的 5 类坏词 + 7 类 AI-isms 翻译为**中文语境版**，并结合现有语言规则：
  - 中文 AI 味负例："赋能/抓手/闭环/颠覆/重塑/生态位/护城河"滥用、"不是 X，而是 Y" 排比、被动句、三段式堆砌、破折号/分号滥用、祈使句标题。
  - 标题：名词短语 vs assertion 的正确使用边界；短标题去句号；禁止"从 X 到 Y"叙事框架。
- 给出生成前的自检清单与一个可选的 `scripts/lint_copy.py`（正则初筛）。

#### 4.10 中文排版专项（`references/design/typography-cjk.md`）
- 字体栈：PingFang SC / Microsoft YaHei / Source Han Sans / Noto Sans SC / 思源字体；标题可选衬线。
- 跨机保真两条路：① 字体子集嵌入（借鉴 html-to-editable-pptx 的"按实际用字子集化"）；② 系统字体回退。
- Path B 中文出图：标题 ≤8 字、正文每行 ≤30 字、避免生僻字、文本与复杂视觉分离（现有经验固化）。
- 度量：给出 CJK/拉丁混合的估算系数（可借 Anthropic 的权重表思路），供 `validate_pptx.py` 用。

#### 4.11 演讲者备注 / 动画
- `references/speaker-notes.md`：每页一段"真正会说的话"，slide 保持视觉化；备注里放引用与来源。
- 动画：优先使用可导出为 PowerPoint 原生动画的声明式约定（`data-anim`，baoyu-design）；Path A 用构建器的动画 API；否则默认不做动画。

### P2 · 进阶

#### 4.12 设计系统 / 自定义角色风格
- 支持"用户上传品牌规范/设计系统 → 抽取 token 作为绑定约束"（参考 baoyu `_ds_prompt.md`）。
- 把现有"Custom Character Style"升级为可复用 preset 生成器（提取视觉 DNA → 落成 `styles/custom-<slug>.md`）。

#### 4.13 资产与性能
- 17 张 PNG → WebP（质量 80）+ 一张总览 contact sheet；目标体积 14MB → ≤3MB。
- 补 Neo-Brutalism 与 5 个编辑风格的样例（可程序化生成，不必 AI 出图）。
- 统一命名（`<id>.webp`）并更新所有引用。

#### 4.14 测试与 CI / 版本
- `tests/test_create_slides.py`、`tests/test_validate_pptx.py`、`tests/fixtures/`（一个含已知缺陷的最小 pptx）。
- GitHub Actions：语法校验 + 脚本冒烟 + `--doctor` + 样例图解码 + 链接检查。
- 引入 `version` 与 CHANGELOG。

#### 4.15 跨 harness 适配
- 新增 `references/harnesses.md`：Claude Code / Codex / DSH / Cursor 各自的"提问、预览、截图、产物链接"工具映射（参考 baoyu-design 的 `references/<harness>.md`）。
- SKILL.md 里的"Ask the user"改为"用宿主提供的提问工具；没有则用聊天气泡"。

#### 4.16 生态联动
- 明确与 `web-research`、数据/图表、`presentations`、`imagegen`、`baoyu-design`、`html-to-editable-pptx` 的关系：默认不依赖，检测到则增强。

---

## 5. 验收标准（Definition of Done）

一个"最好的 PPT skill"应满足：

1. **触发**：仅凭 frontmatter description，能在"做 PPT/幻灯片/演示文稿/Keynote/slides/课件/路演/汇报"等 8 类表述上稳定命中。
2. **可移植**：在没有 `presentations`、没有 `imagegen`、没有 Node 的纯 Python 宿主上，仍能产出一份合法的 .pptx（走兜底）。
3. **可编辑**：凡会被编辑的文字/表格/图表，导出后在 PowerPoint 中都是原生对象（可双击编辑、可选中、可搜索）。
4. **风格**：`styles/index.json` 与 `SKILL.md`、样例图三处计数与命名完全一致；每个风格有可复制的 `base_style_prompt`；选定风格后能渲染 3 张封面预览。
5. **质检**：每份交付跑过 `validate_pptx.py` 且 0 阻塞；逐页 PNG 渲染成功；contact sheet 生成成功。
6. **可审计**：交付附带 receipt（页数、字体、图表/表格数、每类检查结果、`claim_boundary`）。
7. **中文**：CJK 字体正确、无乱码；`typography-cjk.md` 中的规则有对应检查项。
8. **无矛盾**：全文 grep 不存在"一处要求、另一处禁止"的规则；链接全部可达。
9. **体量**：skill 目录 ≤ 5MB；SKILL.md ≤ 200 行；单次典型任务的必读文件 ≤ 4 个。
10. **可维护**：有测试、CI、版本号、`lessons-learned.md`。

**项目 Harness（Pre-P0）另行验收**：`make check` 一条命令跑通全部校验且 CI 绿；`schemas/` 覆盖 SKILL.md、`agents/openai.yaml` 与风格系统；`evals/` 至少 3 个基准可重复；任务模板与 Definition of Done 已固化。

---

## 6. 里程碑与工作量估算

| 阶段 | 内容 | 估算 | 交付物 |
|---|---|---|---|
| **Pre-P0**（Harness，1.5 天） | H1–H7：`AGENTS.md`、schemas、tools 校验器、Makefile+CI、任务模板、eval 基准 | 1.5 人日 | `AGENTS.md` + `schemas/` + `tools/` + `Makefile` + `.github/workflows/ci.yml` + `evals/` |
| **P0**（地基，1–2 天） | 4.1–4.5：SKILL.md 路由器、路径重构（含 B'）、能力探测、修矛盾、风格机读化 | 1.5 人日 | 新 SKILL.md + references/paths/* + styles/ + detect_capabilities.py |
| **P1**（质量，3–5 天） | 4.6–4.11：模板跟随、原生证据、质检闭环、内容闸、CJK、备注/动画 | 4 人日 | references/qa/* + 4 个脚本 + writing-quality.md + typography-cjk.md |
| **P2**（进阶，1–2 周） | 4.12–4.16：设计系统、资产压缩、测试 CI、跨 harness、生态联动 | 6–8 人日 | styles 补全 + tests/ + CI + harnesses.md + lessons-learned.md |

建议顺序：**先做 Pre-P0（Harness，让后续改动能被校验）**，再做 **P0-1/2/3/4**（文档与依赖），接着 **P0-5（质检闸）**，然后 P1。

---

## 7. 风险与取舍

| 风险 | 说明 | 缓解 |
|---|---|---|
| 依赖上游许可 | 上游 huashu-slides 无 LICENSE，fork 内容的再分发存在法律 caveat | 在 README/交付文档保留 provenance 与 caveat；如需开源，补一份说明或取得授权 |
| Path B 出图不可控 | AI 仍可能渲染错中文/多字 | **默认推 B' 混合模式**；Path B 仅在"纯视觉、不要求改字"时用 |
| 质检脚本误报 | 文本度量本质是估算 | 沿用 OpenAI 的分层：结构性/声明式问题阻塞，启发式只警告并标注 `claim_boundary` |
| 跨 harness 工具差异 | 提问/预览/截图 API 各不相同 | `references/harnesses.md` + 能力探测；缺能力时明确降级 |
| HTML→PPTX 保真 | CSS 复杂效果无法 1:1 | 采用"原生几何 + 复杂效果快照垫底 + 文字仍为原生"的路由表 |
| 过度工程 | 一次上太多脚本会拖慢简单任务 | 简单任务走"探测→Path A/B'→build→validate"最短链；脚本按需调用 |
| Harness 本身过重 | 校验器多、入口多，反而拖慢贡献 | 只保留一个入口 `make check`；校验器尽量纯标准库零依赖；每条检查必须给出可操作的错误信息 |

---

## 附录 A：需要立即修正的具体条目

| 文件:位置 | 现状 | 应改为 |
|---|---|---|
| `SKILL.md:29` | Path A = "HTML slides + AI illustrations → html2pptx → editable PPTX" | Path A = "原生可编辑对象（构建器 API）"；HTML 移至 Path C |
| `SKILL.md:520-534` | "Use `$presentations` for HTML-to-editable-PPTX" + HTML 规则（720pt、无渐变、web-safe） | 删除，改为原生构建规则 + 能力探测降级 |
| `SKILL.md:563` | Playwright 截图预览 | 统一走 `render_preview.py`（内置渲染优先） |
| `SKILL.md:385` vs `proven-styles-gallery.md:83` | 一处禁止 NOT 约束，一处要求始终写 NOT | 统一为"不写 NOT 约束" |
| `references/dependencies.md:17,21` | 硬依赖 `$presentations`/`imagegen` | 改为能力矩阵 + 可选增强 + 降级 |
| `references/prompt-templates.md` §2 | base style 1920x1080 | 统一 2048×1152（或标注可配） |
| `proven-styles-gallery.md:1` 与 `SKILL.md:3` | 18 vs 18+5 vs 17 样例 | 以 `styles/index.json` 为唯一事实源 |
| `design-movements.md` 交叉引用编号 | 与 SKILL.md 编号不一致（#7/#13） | 用 style id 引用，不用序号 |

## 附录 B：风格 preset schema 草案

```jsonc
{
  "schema_version": 1,
  "count": 23,
  "styles": [
    {
      "id": "warm-comic-strip",
      "name": "Snoopy温暖漫画",
      "name_en": "Warm Comic Strip",
      "tier": 1,
      "themes": ["品牌/产品介绍", "教育/培训", "个人分享"],
      "formality": "low",
      "path": "B_or_B2",
      "palette": { "background": "#FFF8E8", "text": "#333333", "accent": ["#87CEEB", "#8FBC8F", "#F4A460"] },
      "typography": { "heading": "bold warm", "body": "readable", "ratio": "3:1", "cjk_font": "PingFang SC" },
      "base_style_prompt": "VISUAL REFERENCE: Charles Schulz Peanuts comic strip — warm, philosophical, charming. ...",
      "layout_blocks": ["cover", "single-panel", "multi-panel", "quote"],
      "pitfalls": ["不要在 per-slide 重复 base style", "不要写 NOT 约束", "不要指定颜色比例"],
      "sample": "assets/style-samples/warm-comic-strip.webp",
      "proven": true
    }
  ],
  "theme_recommendations": [
    { "theme": "行业分析/咨询", "first": "pentagram-editorial", "second": "fathom-data", "third": "muller-brockmann-grid" }
  ]
}
```

## 附录 C：主要参考来源

- OpenAI Codex `presentations` skill（本机 `~/.codex/plugins/cache/openai-primary-runtime/presentations/.../skills/presentations`）：finalize 事务、分层 finding、claim boundary、模板保真。
- Anthropic `pptx` skill（本机 `~/.trae/builtin/work/*/skills/pptx`）：`validate_layout.py`、inventory/replace、OOXML pack/unpack、缩略图目检。
- `baoyu-design`（本机 `~/.agents/skills/baoyu-design`）：deck-stage、`data-anim`、editable PPTX、设计系统。
- [Hasasasa/html-to-editable-pptx](https://github.com/Hasasasa/html-to-editable-pptx)：CSS→PPT 路由、字体子集化、side-by-side audit、lessons-learned。
- [yuna78/html-to-pptx](https://github.com/yuna78/html-to-pptx)：原生 DrawingML 重建、中文修复、零出网。
- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-Skill)：双视觉系统、锁定版式、演讲者模式。
- [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)：封面三选一、title-only 可读性测试。
- [alchaincyf/huashu-skills](https://github.com/alchaincyf/huashu-skills)：上游生态与 huashu-design 的"20 设计哲学 + 5 维评审"。
- 项目内真实产物：`.codex-build/ev-trends/build.mjs`、`subaru-ev-trends-validation.json`、`slide-01~10.png`。

---

*本方案基于 2026-09 的项目快照与同机参考 skill 审计。执行时建议先做 P0，再以真实 deck 回归验证。*
