---
name: subaru-slides
description: 端到端制作 PPT / 幻灯片 / 演示文稿 / Keynote：内容结构化、风格选择、原生可编辑或 AI 视觉构建、PPTX 装配与质检。当用户提到"做PPT""做幻灯片""演示文稿""keynote""slides""路演""汇报""课件"时使用。
---

# subaru-slides · Presentation Router

> 薄入口：本文件只做路由与铁律。流程细节在 `references/`；风格数据在 `styles/index.json`。

## When to use / not use
- **用**：从主题或文档做演示文稿；需要可编辑 PPTX；需要 AI 视觉风格；需要 HTML deck。
- **不用**：单独做图表、纯文档排版（用对应的图表/文档 skill）。

## The 6 rules
1. **可编辑是默认**：会被修改的文字/表格/图表必须原生；只有装饰视觉可以是位图。
2. **风格是数据**：计数、命名、推荐、样例只在 `styles/index.json`；其他文件不得重复维护。
3. **能力探测优先**：先跑 `scripts/detect_capabilities.py`；缺能力必须明说并降级，禁止静默换路。
4. **中文优先**：slide 文案中文优先（保留必要英文术语）；代码、路径、JSON key 用英文。
5. **交付前过检**：逐页渲染 + 目检；并说明哪些检查**没有**做（claim boundary）。
6. **按所在地的规范交付**：作为独立安装包使用时，遵守该宿主 Agent 的规范与交付约定。
<!-- repo-only -->
   > 在开发仓库内改动本 skill 时：遵循 `AGENTS.md`，并跑 `make check` 过闸。
<!-- /repo-only -->

## Step 0 · Capability probe
```bash
python3 scripts/detect_capabilities.py     # 或 --json
```
推荐顺序：`A 原生可编辑 → B' 混合 → C HTML deck → B 全 AI 视觉 → fallback`。
缺能力时明确告知用户，再走下一档。

## Step 1 · Pick a path
| Path | Product | Requires | Details |
|---|---|---|---|
| A | 原生可编辑 PPTX | 原生构建器 | `references/paths/path-a-native.md` |
| B' | AI 底图 + 原生可编辑文字（推荐默认） | 图片生成 + 原生构建器 | `references/paths/path-b2-hybrid.md` |
| C | 单文件 HTML deck | deck-stage / HTML→PPTX 转换器 | `references/paths/path-c-html.md` |
| B | 全 AI 视觉 PPTX | 图片生成 | `references/paths/path-b-visual.md` |
| fallback | 图片 PPTX（最低兜底） | python-pptx + Pillow | `references/paths/path-b-visual.md` |

## Step 2 · Confirm settings
问用户两件事（未说明则默认）：**合作模式**（Full Auto / Guided / Collaborative，默认 Guided）
与**输出形态**（可编辑 PPTX / 视觉 PPTX / HTML deck）。详见 `references/workflow.md`。

## Step 3 · Structure the content
标题=断言句；每页 1 个观点、≤4 条要点；5/5/5。
读 `references/content-structure.md`，产出逐页大纲。
**Checkpoint 1**：展示大纲表，请用户确认或调整。

## Step 4 · Choose a style
读 `styles/index.json`，按 `theme_recommendations` → `formality` → `path` 匹配，
选 **3 个方向不同**的候选；每个给出：一句话 + 调色板 + 样例图。
**Checkpoint 2**：请用户选一个。若宿主能渲染，直接给 3 张封面预览而不是文字描述。
细节：`references/design-movements.md`、`references/design-principles.md`。

## Step 5 · Build
按选定路径执行：
- AI 配图/出图：读 `references/illustrations.md`，并使用该风格 preset（`styles/<id>.md`）的 **Base Style Prompt**。
- 原生对象与单位护栏：`references/paths/path-a-native.md`。
**Checkpoint 3**：展示 2-3 张关键页（Collaborative 模式逐页），请用户确认。

## Step 6 · Assemble & preview
逐页渲染 PNG 并目检：`references/qa/render-and-validate.md`。
contact sheet 只用于整册节奏，**不替代**逐页检查。
<!-- repo-only -->
在开发仓库内可用：`make validate PPTX=...`、`make render PPTX=...`、`make montage DIR=...`。
<!-- /repo-only -->

## Step 7 · QA & delivery
`references/qa/checklist.md` → `references/qa/delivery.md`（附 receipt 与 claim boundary）。
**Checkpoint 4**：给出文件路径，问是否还需调整。

## Language rules
- slide 文案中文优先，仅保留必要英文术语。
- section label（INSIGHT / TAKEAWAY / PART 03）可作设计元素。
- 标题短小写实；不要强行制造悬念、张力或"金句"。

## Quick reference
- 5/5/5：≤5 词/行，≤5 要点/页，文字密集页不超过连续 5 页。
- 标题:正文 ≈ 3:1；配色 60-30-10；每页至少一个视觉元素。
- 一个观点，一分钟一页。
- 中文出图：标题 ≤8 字，正文每行 ≤30 字，避免生僻字。

## Reference index
| 文件 | 内容 |
|---|---|
| `references/workflow.md` | 端到端 7 步与检查点 |
| `references/content-structure.md` | 内容结构化与大纲模板 |
| `references/illustrations.md` | AI 出图方法论与 custom style |
| `references/dependencies.md` | 能力矩阵与降级策略 |
| `references/paths/*.md` | 四条执行路径 + fallback |
| `references/qa/*.md` | 目检、渲染、交付 |
| `references/template-following.md` | 模板/品牌跟随 |
| `references/native-evidence.md` | 原生表格/图表/bullet 与单位护栏 |
| `references/writing-quality.md` | 中文反 AI 文风负例库 |
| `references/typography-cjk.md` | 中文字体/度量/跨机保真 |
| `references/speaker-notes.md` | 演讲备注与动画 |
| `references/design-system.md` | 设计系统与自定义风格 |
| `references/harnesses.md` | 跨 harness 工具映射 |
| `references/integrations.md` | 可选增强集成 |
| `references/design-principles.md` | 十规则、色板、字体、版式 |
| `references/design-movements.md` | 设计运动 → 风格对照 |
| `references/proven-styles-gallery.md` | 风格选择策略（数据以 `styles/index.json` 为准） |
| `references/proven-styles-snoopy.md` | Snoopy 风格实战经验 |
| `references/prompt-templates.md` | 内容与出图 prompt 模板 |
| `styles/index.json` + `styles/<id>.md` | 风格注册表与 23 个 preset |
| `scripts/detect_capabilities.py` | 能力探测与路径推荐 |
| `scripts/create_slides.py` | 图片→PPTX 兜底 |

## Output
- `.pptx`（PowerPoint / Keynote / Google Slides 兼容；尽量使用普适字体）
- 或单文件 `.html` deck
- AI 配图 PNG 作为独立资产
