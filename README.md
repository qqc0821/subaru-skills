# subaru-skills

中文优先的 [Agent Skills](https://agentskills.io/) 仓库：把主题、资料或已有文档，转成结构清晰、视觉可控的演示文稿。

[English](README.en.md) · [变更记录](CHANGELOG.md) · [来源与许可边界](PROVENANCE.md)

当前仓库包含一个可安装 skill：**subaru-slides**。它负责从内容结构化、视觉风格选择，到 PPTX / HTML deck 构建和交付前质检的完整流程。仓库根目录同时维护开发 Harness，不会随 skill 包一起安装。

## 快速开始

### 安装

使用 [skills CLI](https://github.com/vercel-labs/skills) 安装整个仓库：

~~~bash
# 安装到当前项目
npx skills add qqc0821/subaru-skills

# 安装到用户级 skill 目录
npx skills add qqc0821/subaru-skills --global

# 只安装 subaru-slides
npx skills add qqc0821/subaru-skills --skill subaru-slides

# 查看可安装项
npx skills add qqc0821/subaru-skills --list
~~~

安装后可以显式调用 $subaru-slides；涉及 PPT、幻灯片、演示文稿、Keynote、路演、汇报或课件时，宿主 Agent 也可以自动选中它。

不使用 CLI 时，也可以手动复制 skills/subaru-slides/ 到宿主 Agent 的 skill 目录：

~~~bash
git clone https://github.com/qqc0821/subaru-skills.git
cp -R subaru-skills/skills/subaru-slides <你的宿主 skill 目录>/
~~~

只需安装 skills/subaru-slides/；tools/、schemas/、evals/、tests/ 和 docs/ 是本仓库开发与回归验证使用的 Harness。

### 使用

~~~text
用 $subaru-slides 把这份市场分析做成 10 页管理层汇报 PPT。
~~~

默认使用 Guided 协作模式：Agent 会在大纲、风格方向和关键页预览处请求确认。也可以指定：

- 合作模式：Full Auto、Guided 或 Collaborative；
- 输出形态：可编辑 PPTX、视觉型 PPTX 或单文件 HTML deck；
- 受众、时长、目标、语气、品牌规范和已有模板。

## 它如何工作

subaru-slides 的入口是薄路由器，详细方法按需加载自 references/：

1. **能力探测**：先运行 scripts/detect_capabilities.py，确认宿主能做什么。
2. **选择路径**：按能力和输出目标选择最佳执行路径。
3. **确认设置**：确认合作模式和输出形态，必要时补齐受众、时长与语气。
4. **结构化内容**：逐页生成断言式标题、要点和视觉类型，在 Checkpoint 1 确认大纲。
5. **选择风格**：根据主题、正式程度和路径提供三个差异化方向，在 Checkpoint 2 确认风格。
6. **构建与预览**：生成原生对象或视觉底图，展示关键页，在 Checkpoint 3 复核。
7. **质检与交付**：尽可能逐页渲染、检查结构与可读性，并附文件路径、receipt 和 claim boundary。

核心原则是：可编辑内容默认使用原生对象；能力缺失必须明确说明并降级；未做的视觉或应用兼容性检查不能被宣称为已完成。

## 执行路径与编辑性边界

选择顺序为：A 原生可编辑 → B' 混合 → C HTML deck → B 全 AI 视觉 → fallback。

| 路径 | 产物 | 主要能力 | 编辑性边界 |
|---|---|---|---|
| A | 原生可编辑 PPTX | 原生构建器 | 文字、表格、图表保持可编辑 |
| B' | AI 无文字底图 + 原生文字/图表 | 图片生成 + 原生构建器 | 视觉底图不可编辑，文字、表格、图表可编辑 |
| C | 单文件 HTML deck | deck runtime；导出 PPTX 另需转换器 | HTML 内容保持静态可编辑；无转换器时不承诺 PPTX |
| B | 全 AI 视觉 PPTX | 图片生成 | 每页是完整图片，文字通常不可编辑 |
| fallback | 图片型 PPTX | scripts/create_slides.py | 仅做图片装配，不恢复原生编辑性 |

无原生构建器时，不能把图片型 PPTX 宣称为 Path A；无渲染器时，只做结构检查，并在交付中说明未完成视觉 QA。AI 图片中的中文也可能出现错字，因此会优先使用短标题，必要时把文字移到原生对象层。

## 能力与可选依赖

运行 skill 默认不依赖外部 Agent skill。宿主能力会被探测为可选增强，缺少时沿下一条路径降级：

| 能力 | 启用内容 | 缺失时 |
|---|---|---|
| 原生构建器 | Path A / B' | 改用 HTML、全视觉或图片 fallback；不承诺可编辑 PPTX |
| 图片生成 | Path B / B' 的视觉底图 | 使用原生图形与排版，或改走没有 AI 配图的路径 |
| HTML runtime / HTML→PPTX 转换器 | Path C 与可选 PPTX 导出 | 交付 HTML；没有转换器时明确说明不能导出 PPTX |
| LibreOffice + Poppler | PPTX 逐页渲染和视觉 QA | 只做结构校验，并声明未做视觉检查 |
| uv | 运行内置 fallback helper，并解析其 PEP 723 依赖 | fallback 在该环境中不可执行 |

内置 create_slides.py 声明的依赖是 python-pptx>=1.0.0 与 Pillow>=10.0.0，只在使用 fallback 时按需解析。HTML deck 运行或导出还可能需要 Chrome / Chromium 和相应 runtime；这些不是 subaru-slides 的硬依赖。

### 环境探测

从仓库根目录运行：

~~~bash
python3 skills/subaru-slides/scripts/detect_capabilities.py
# 机器可读输出
python3 skills/subaru-slides/scripts/detect_capabilities.py --json
~~~

若 skill 已安装到其他位置，把命令中的路径替换为实际安装路径。探测结果只描述当前机器，不是安装成功的前置条件。

### 最低 fallback 示例

仓库内的 WebP 样例可以直接装配成图片型 PPTX：

~~~bash
uv run skills/subaru-slides/scripts/create_slides.py \
  skills/subaru-slides/assets/style-samples/warm-comic-strip.webp \
  skills/subaru-slides/assets/style-samples/bauhaus.webp \
  skills/subaru-slides/assets/style-samples/blueprint.webp \
  --layout fullscreen \
  --output output.pptx
~~~

支持的布局是 fullscreen、title_above、title_below、title_left、center 和 grid。fallback 只验证图片装配，不代表文字可编辑、数据图表原生或 AI 图片生成质量。

## 风格系统

风格数据的唯一事实源是 [skills/subaru-slides/styles/index.json](skills/subaru-slides/styles/index.json)：

- 其中维护风格 id、中文/英文名称、主题推荐、正式程度、适用路径、样例映射和 proven 状态；
- 每个 preset 位于 skills/subaru-slides/styles/<id>.md，包含调色板、字体、Base Style Prompt、版式组件与注意事项；
- 样例图片使用 assets/style-samples/<style-id>.webp，是否存在以 registry 为准；
- 新增或修改风格时，必须同步更新 registry 与 preset，不要在其他文档复制一份会漂移的数量、色板或推荐表。

当前风格覆盖漫画与插画、教育与知识分享、技术蓝图、东方文化、数据叙事、编辑杂志、复古广告、像素画和其他原生构建方向。正式商务、行业分析等主题优先从 Path A 风格中选择；创意、培训和品牌主题可按能力探测结果选择视觉风格。

## 设计与交付约定

- 一页一个核心观点；标题优先写成可验证的断言句。
- 控制信息密度，通常不超过四个要点，避免连续堆叠文字页。
- 表格、数据图表和需要后续修改的文字必须是原生对象；装饰视觉才使用位图。
- 中文优先，采用宿主可用的 CJK 字体回退栈；跨机器交付时说明字体差异或嵌入策略。
- AI 配图描述情绪和世界观，不用过度微操坐标、颜色比例或角色姿势；Path B' 的底图不放文字。
- 交付前尽可能逐页渲染并检查溢出、对比度、裁剪、占位符、字体和数据单位。
- receipt 应包含文件路径、大小或哈希、页数、字体、原生图表/表格数量、已做检查和 claim boundary。

详细规则见 [skills/subaru-slides/SKILL.md](skills/subaru-slides/SKILL.md) 及其 references/；风格选择见 [styles/index.json](skills/subaru-slides/styles/index.json)。

## 仓库结构

~~~text
subaru-skills/
├── README.md / README.en.md        # 使用者入口，中文 / English
├── skills/subaru-slides/           # skill 包本体
│   ├── SKILL.md                    # 薄入口：路由、铁律、检查点
│   ├── references/                 # 工作流、路径、设计、QA 等长文
│   ├── styles/                     # 风格 registry 与 preset
│   ├── scripts/                    # 能力探测与图片 PPTX fallback
│   └── assets/                     # WebP 风格样例
├── tools/                          # Harness 校验器
├── schemas/                        # 机读契约（frontmatter / preset / index）
├── evals/                          # 回归基准：固定 brief + 结构断言
├── tests/                          # Harness 单元测试
├── docs/                           # DoD、模板与经验沉淀
├── Makefile                        # 统一入口
├── AGENTS.md                       # 工程规范的单一事实源
└── PROVENANCE.md                   # 上游出处与许可边界
~~~

安装者只需要 skills/subaru-slides/；其他目录用于维护、质量门和回归验证。

## 开发与质量门

修改仓库前先阅读 [AGENTS.md](AGENTS.md)。按规范，任务开始时运行 make new-task，它会生成被 .gitignore 忽略的 task_plan.md、findings.md 和 progress.md；这些过程文件不应提交。

常用命令：

~~~bash
make check       # frontmatter / 链接 / 一致性 / 资产 / 风格系统 / 可安装性
make test        # 工具 smoke test 与 Harness 单元测试
make doctor      # 当前机器能力探测
make eval        # 本机固定案例与覆盖率闸门
make eval-ci     # 重建 CI 固定 fixture 后运行独立闸门
make new-task    # 生成任务过程三件套
make help        # 查看全部命令
~~~

针对具体 deck：

~~~bash
make validate PPTX=deck.pptx
make render PPTX=deck.pptx OUT=preview/
make montage DIR=preview/ OUT=montage.webp
make lint-copy SRC=outline.md
make new-style ID=my-style NAME="我的风格"
~~~

make check 是本地和 CI 共用的质量门；make eval 的 PASS / FAIL / SKIP / BLOCKED 由评测策略和当前环境共同决定，未执行不等于通过。CI 只声明确定性 fixture 的结构回归，不声明外部图片模型、HTML runtime 或 Office 渲染器的质量。

## 许可与来源

仓库原创内容采用 [MIT License](LICENSE)。skills/subaru-slides 派生自 huashu-slides；上游审计基线没有根 LICENSE，因此再分发前请先阅读 [PROVENANCE.md](PROVENANCE.md)，确认第三方文档、脚本和样例图的授权边界。
