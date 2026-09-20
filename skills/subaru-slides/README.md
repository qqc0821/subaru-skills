# subaru-slides

中文优先的演示文稿 skill：把主题、资料或已有文档，做成结构清晰、可编辑性边界明确的 PPTX 或 HTML deck。

## 调用

把本目录放入宿主的 skill 目录，或安装：

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-slides
~~~

~~~text
用 $subaru-slides 把这份市场分析做成 10 页管理层汇报 PPT。
~~~

装好后可以显式调用 `$subaru-slides`；涉及 PPT、幻灯片、演示文稿、Keynote、路演、汇报或课件时，宿主 Agent 也可能自动选中它。

默认 Guided 协作：Agent 会在大纲、风格方向、关键页预览三处请求确认。也可以指定 Full Auto 或 Collaborative，选择输出形态（可编辑 PPTX / 视觉型 PPTX / 单文件 HTML deck），并补齐受众、时长、语气和品牌模板。

## 执行路径与编辑性

先探测宿主能力，再按 **A 原生可编辑 → B' 混合 → C HTML deck → B 全 AI 视觉 → fallback** 选路；可编辑内容默认使用原生对象。

| 路径 | 产物 | 编辑性边界 |
|---|---|---|
| A | 原生可编辑 PPTX | 文字、表格、图表保持可编辑 |
| B' | AI 底图 + 原生文字/图表 | 底图不可编辑，文字与图表可编辑 |
| C | 单文件 HTML deck | HTML 静态可编辑；无转换器时不承诺 PPTX |
| B | 全 AI 视觉 PPTX | 整页为图片，文字通常不可编辑 |
| fallback | 图片型 PPTX | 仅图片装配，不恢复原生编辑性 |

## 能力与降级

`scripts/detect_capabilities.py` 探测原生构建器、图片生成、HTML runtime 与渲染器。它们都只是可选增强：缺失时沿下一条路径降级并明确告知，不会静默换路，也不会把图片型 PPTX 说成可编辑。

只有 uv 时的最低兜底：

~~~bash
uv run scripts/create_slides.py a.webp b.webp --layout fullscreen --output out.pptx
~~~

支持 fullscreen、title_above、title_below、title_left、center、grid 六种布局；它只做图片装配。

## 风格

`styles/index.json` 是风格数据的唯一事实源（id、中文/英文名称、主题推荐、正式程度、适用路径、样例映射、proven 状态）；`styles/router.md` 是由它生成的选型摘要（Agent 选风格时只读这一张表），每个风格另有 `styles/<id>.md` preset，样例图在 `assets/style-samples/`。

## 更多

- 运行时规则、流程与检查点：[SKILL.md](SKILL.md)
- 工作流与路径细节：[references/workflow.md](references/workflow.md)
- 设计与 QA：[references/qa/checklist.md](references/qa/checklist.md)
- 再分发：本 skill 含第三方来源的文档与样例图，再分发前请确认各自的授权边界。
