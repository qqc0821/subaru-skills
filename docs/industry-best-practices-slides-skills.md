# 行业 slides skill 最佳实践研究

## 结论

一个真正成熟的 slides skill，不是“能生成好看的页面”，而是一个把以下四件事连成闭环的沟通系统：

1. **理解任务**：知道受众、目的、时长、交付平台与素材可信度。
2. **组织信息**：每页只有一个主要断言，并用合适的视觉证据支持它。
3. **生成可维护产物**：文字、表格、图表、版式和备注保留为可编辑、可复用的结构。
4. **验证真实结果**：同时检查渲染像素、文件结构、可访问性、数据语义和来源边界。

“好看”只是其中一个结果变量。若文字不可读、图表不可改、来源说不清、屏幕阅读器读不通，或者导出后布局漂移，那么视觉上漂亮的页面仍然不是一个好的 presentation artifact。

这不是一条来自单一厂商的“官方标准”，而是四类证据的交集：认知与传播研究、可访问性标准、PowerPoint/Google Slides 的平台契约，以及最近针对 AI/Agent 编辑演示文稿的评测研究。下面把这四类证据分开说明。

## 一、什么才算“最佳”

建议把 slides skill 的质量定义成一个多目标问题：

| 维度 | 关键问题 | 失败例子 |
|---|---|---|
| 理解力 | 观众能否快速知道这一页要表达什么？ | 标题只是“市场分析”，观众要读完 8 个 bullet 才知道结论 |
| 证据力 | 页面上的视觉是否真的支持标题？ | 用装饰照片替代数据、因果关系或机制图 |
| 可读性 | 大屏、远距离、低视力和 CJK 字体环境下是否可读？ | 字体被压缩、浅色字叠在图片上、中文变成方框 |
| 可编辑性 | 用户能否修改数字、文字、表格和布局？ | 整页截图放进 PPTX，或图表只有一张图片 |
| 可复用性 | 下一页、下一版、下一套品牌是否能低成本复用？ | 每页手工摆放，改一处全册漂移 |
| 可验证性 | 能否证明生成结果符合要求？ | export 命令成功就宣称“已完成” |
| 可信度 | 事实、数字、引用和推断的边界是否清楚？ | 模型补写了用户没有提供的数字，却没有标注来源 |

因此，最佳实践不是一张“设计技巧清单”，而是让上述维度彼此不冲突的工程约束。

## 二、被研究和平台证据支持的最佳实践

### 1. 先定义受众、目的和素材边界，再生成

成熟系统都会在生成前确认场景：汇报、教学、路演、答辩、销售、社交传播，还是可打印的 handout；还要确认受众、时长、语言、品牌/模板和输入材料的完整度。

为什么这很重要：同一事实在“演讲页”和“参考手册”中的最佳密度完全不同。若不先定义目的，模型很容易把所有事实塞进一页，或者把讲稿误当成屏幕文案。素材边界也决定了系统应当“整理已有事实”，还是先进入研究流程。

公开的 slide-skill 实现已经把“场景路由、受众、时间预算、输入质量”放在生成之前；另一个实现会把 topic-only 请求先转入研究，再生成大纲，而不是凭空补事实。[ICGMA slide-skill](https://github.com/icgma/slide-skill/blob/master/SKILL.md) [LGWAnAI ppt-skill](https://github.com/lgwanai/ppt-skill/blob/main/SKILL.md)

**最佳实现形态**：把输入分成四种状态，并在 outline 中保留它们：

- `provided`：用户明确提供的事实；
- `researched`：有可追溯来源的外部事实；
- `inference`：基于事实的分析判断；
- `unknown`：尚未验证，不能当作事实写进标题或图表。

这条规则不是为了让模型变得保守，而是为了防止“内容很流畅、事实却没有来源”。

### 2. 每页一个主要断言，正文提供证据

Penn State 的 Assertion–Evidence 方法把 body slide 组织成两层：标题是一句完整的关键消息，正文用图、表、照片、机制图或必要的短文来支撑该消息；次要细节和演讲脚本放在 notes 中。[Penn State Assertion–Evidence Guide](https://writing.engr.psu.edu/assertion_evidence_EA.html)

它之所以优于默认的“主题词 + bullet 列表”，不是因为句子标题永远更漂亮，而是因为它强迫作者先回答：**这一页到底要让观众相信什么？** 一旦标题是断言，正文就必须具有证据关系；如果出现第二个独立观点，最自然的动作是拆页，而不是缩小字体。

这也得到相关传播研究的支持：研究比较了常见 PowerPoint 结构与 Assertion–Evidence 结构，认为后者更符合多媒体学习原则；后续研究报告了理解和心理努力方面的差异，但效果会随受众、材料和任务变化，因此它应作为默认组织方式，而不是所有页面的硬模板。[Garner et al., “Common Use of PowerPoint versus the Assertion–Evidence Structure”](https://www.researchgate.net/publication/263502714_Common_Use_of_PowerPoint_versus_the_Assertion-Evidence_Structure) [Garner et al., “How the Design of Presentation Slides Affects Audience Comprehension”](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)

**适用边界**：目录、术语表、完整流程、法规条文、数据字典和 handout 页面可能需要更高密度。最佳 skill 应允许例外，但要求显式标注“这是参考页/资料页”，不要把例外误当成默认。

### 3. 让文字和视觉互相解释，而不是互相竞争

Richard Mayer 的多媒体学习研究提出，设计应同时考虑视觉/言语通道、有限容量和主动加工，并总结了 multimedia、contiguity、coherence、modality 等原则：文字和图片可以协同，但无关的文字、图片和声音会增加负荷；对应的文字和图形应当靠近，避免观众来回寻找。[Mayer, PubMed](https://pubmed.ncbi.nlm.nih.gov/19014238/) [Mayer, 1999](https://doi.org/10.1075/dd.1.1.02may)

由此可以推导出几个比“少放字”更准确的规则：

- 视觉必须服务于当前断言；装饰图不是自动有价值。
- 图表标签、注释和重点应靠近它们解释的对象。
- 不要在屏幕上逐字复制讲稿；备注和页面承担不同任务。
- 避免让多个互不相关的视觉抢夺同一个注意力中心。

所以“每页至少一个视觉元素”还不够；更好的检查是：**删掉这个视觉后，观众是否失去理解当前断言所需的信息？** 如果答案是否定的，它可能只是装饰。

### 4. 图表按问题选择，并保留数据语义

图表不是页面装饰，而是量化关系的编码。Cleveland 和 McGill 的图形知觉研究比较了位置、长度、角度、面积、颜色等基本感知任务；这为“用更容易比较的编码表达主要差异”提供了经验基础。[Cleveland & McGill, 1984](https://doi.org/10.1080/01621459.1984.10478080)

工程上应至少保留这些语义：类别、系列、单位、时间范围、正负号、精度、排序、数据来源和计算口径。PowerPoint 的官方文档明确支持在演示文稿中直接编辑图表数据，修改会反映到图表中；这说明 native chart 不只是“看起来像图表”，而是平台所承诺的可维护对象。[Microsoft: Change the data in an existing chart](https://support.microsoft.com/en-us/powerpoint/change-the-data-in-an-existing-chart)

**推荐的生成契约**：每个数据视觉同时保存 `chart_type`、`question`、`source`、`unit`、`transform`、`precision`、`highlight`。例如，若标题是“收入增长主要来自新客户”，图表配置应能回答：增长率的分母是什么？新客户与存量客户的分类口径是什么？高亮为何落在该系列？

### 5. “可编辑”必须是对象级的，不是文件扩展名级的

把 PNG 放进 `.pptx` 并不等于交付了可编辑 PPTX。真正可编辑的证据是：文字仍是文字，表格仍是表格，图表仍能打开数据编辑器，布局仍可调整，备注仍可读取，必要时 master/layout 仍能复用。

Google Slides 的官方模型把 presentation 拆成 slides、page elements、masters、layouts 和 notes；页面可以从 layout/master 继承属性。[Google Slides page elements](https://developers.google.com/workspace/slides/api/concepts/page-elements) [Google Slides speaker notes](https://developers.google.com/workspace/slides/api/guides/notes)

PowerPoint 也把 slide master 与关联 layouts 作为控制颜色、字体、标题、占位符和重复元素的复用机制。[Microsoft: Customize a slide master](https://support.microsoft.com/en-us/PowerPoint/training/customize-a-slide-master)

**为什么这很重要**：对象级结构降低了下一次修改的边际成本，也降低了“生成一次、用户不得不重做”的浪费。它还使 QA 可以检查数据、字体、阅读顺序和元素关系，而不是只能对一张图片做模糊的相似度判断。

### 6. 用结构化中间表示，把内容、设计和渲染解耦

成熟的公开实现普遍把流程拆成“素材/研究 → 大纲 → 设计规格 → 页面源码或 SVG → PPTX/HTML → 验证”，而不是一次 prompt 直接导出最终文件。这个中间表示可以是 Markdown、YAML、JSON、SVG、HTML 或自定义 deck state，但必须能表达：

- 页面角色：cover、section、content、data、closing；
- 标题断言、正文证据、视觉类型和讲稿备注；
- 版式/主题/字体/颜色 token；
- 可编辑对象与装饰资产的边界；
- 每个事实或数字的来源；
- alt text、阅读顺序和导出约束。

为什么它是最佳实践：当内容、样式或渲染器出错时，可以局部重跑。也可以在“生成 PPTX”之前检查大纲，在“生成图像”之前检查 prompt，在“导出”之后检查结构和像素。没有中间表示，所有错误都会混在一个不可解释的最终文件里。

### 7. 模板和品牌要提取成可验证的设计系统

模板跟随不是“看起来像”，而是恢复并复用 master/layout、字体、尺寸、页边距、占位符、logo、页脚、图像裁切规则和重复元素。PowerPoint 官方说明 slide master 用来统一颜色、字体、标题、logo 和其他样式；Google Slides 的模型则明确展示了 master → layout → slide 的继承关系。[Microsoft slide master](https://support.microsoft.com/en-us/PowerPoint/training/customize-a-slide-master) [Google Slides inheritance](https://developers.google.com/workspace/slides/api/concepts/page-elements)

因此，最好的模板工作流是：先渲染并审计来源，再提取设计 DNA，建立可复用 spec，生成时引用 spec，最后做并排比较。只看一张缩略图或只比较颜色覆盖率，无法证明模板被保留。

### 8. 可访问性是结构要求，不是最后加分项

W3C WCAG 2.2 要求非文本内容提供等价文本替代；对普通文本规定至少 4.5:1 的对比度，对大文本规定至少 3:1；同时建议在技术允许时使用真正的文本，而不是把文字烘焙进图片。[WCAG 2.2](https://www.w3.org/TR/WCAG22/) [Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

Microsoft 的 PowerPoint 指南把这些要求落到了演示文稿对象上：每页有唯一标题、对象有 alt text、阅读顺序合乎逻辑、不能只靠颜色传递信息、表格要有列标题、文字与背景有足够对比度，并建议使用 Accessibility Checker。[Microsoft PowerPoint accessibility](https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities)

对 slides skill 来说，最重要的不是“把所有页面做成网页标准”，而是把以下内容纳入生成契约和 QA：

- 每页的语义标题，即使视觉上隐藏也要能被辅助技术找到；
- 图片、图表、流程图和复杂表格的 alt text 或等价描述；
- 视觉阅读顺序与屏幕阅读顺序；
- 颜色之外的编码（标签、形状、纹理、位置）；
- 对比度、字体 fallback、CJK glyph 和投影环境下的最低可读性；
- 视频/音频有字幕或文字替代。

### 9. QA 必须覆盖“结构 + 像素 + 语义 + 交互”

仅结构检查会漏掉白字、裁切、溢出、字体替换和图像遮挡；仅截图相似度又会漏掉“看起来像图表但不可编辑”“数字单位错误”“阅读顺序错误”。成熟的 QA 应至少分四层：

| 层 | 检查什么 | 典型手段 |
|---|---|---|
| 结构 | 页数、对象类型、边界、占位符、字体、备注、图表/表格 | PPTX/XML inspector、结构 validator |
| 像素 | 溢出、重叠、对比、裁切、页面节奏、跨页一致性 | 每页渲染 PNG、逐页目检、contact sheet |
| 语义 | 标题是否为断言、图表是否支持标题、单位/来源/精度是否正确 | 规则检查 + 人工/模型评审 |
| 可用性 | 对象能否修改、模板能否继续复用、notes/alt text/reading order 是否存在 | 真实 PowerPoint/Google Slides 或等价 API 验证 |

最近的 PPTArena 基准专门评估真实 PowerPoint 的原位编辑，覆盖文字、图表、表格、动画和 master-level style；PPT-Eval 进一步强调任务复杂、答案不唯一、二元成功/失败不足，因此采用带部分得分的任务 rubric。[PPTArena](https://arxiv.org/abs/2512.03042) [PPT-Eval](https://arxiv.org/abs/2606.31154)

这给 slides skill 一个很具体的启示：回归测试不能只断言“有 6 页、至少 1 张图”。还要测“把第 3 页的数字改掉后，图表是否仍然工作”“换成长标题后是否溢出”“改变 master 后同类页面是否一致”“来源和备注是否仍然保留”。

### 10. 交付时明确 claim boundary

好的系统不会把“导出成功”写成“在 PowerPoint、Keynote、Google Slides 都验证通过”。不同宿主的字体、动画、链接、图表和布局能力不同。交付 receipt 应写清：

- 哪个文件、多少页、哪些字体；
- native chart/table/notes 的数量；
- 做过哪些结构、渲染、可访问性和真实宿主检查；
- 哪些能力缺失或未验证；
- 来源和事实边界是什么。

这不是免责话术，而是让用户知道下一步风险在哪里，也使自动化系统不会把“未执行”误算成“通过”。

## 三、哪些规则不能被误称为科学定律

`5/5/5`、标题正文约 `3:1`、`60-30-10` 配色、每页一分钟、每页至少一个视觉元素，都可以作为默认启发式，但目前不能把它们当作对所有场景都成立的研究结论。

它们的实际价值是“快速暴露风险”：提醒模型不要把整段报告塞进一页、不要让正文小到投影看不见、不要让页面没有视觉锚点。它们的限制也很明显：教学 handout、财务附录、法规对照、技术架构、无障碍高对比版本和模板填充页都可能需要不同密度。

更好的做法是：保留这些规则，但把它们命名为 `heuristic`，允许按场景覆盖，并在 eval 中记录覆盖原因。真正需要硬闸的是：不溢出、不越界、标题/证据关系成立、图表数据语义正确、关键对象可编辑、可访问性要求满足、来源边界明确。

## 四、对 `subaru-slides` 的审计

### 已经接近行业成熟度的部分

- **薄入口 + 参考文档路由**：`SKILL.md` 只做触发、路径选择和检查点，细节下沉到 `references/`，符合可维护的 skill 包结构。
- **可编辑优先**：`references/native-evidence.md` 明确要求可修改的文字、表格、图表使用 native 对象，只有装饰视觉使用位图。
- **能力探测与显式降级**：`detect_capabilities.py`、A → B' → C → B → fallback 的顺序，以及环境矩阵中的 BLOCKED/claim boundary，避免静默假装端到端可用。
- **内容先于设计**：先大纲、后风格、再构建，且有用户 checkpoint；标题断言、视觉证据、notes 分工已经写进流程。
- **模板跟随**：要求 render/recon、保留 master/layout/theme/fonts/spacing、并排验证，强于很多只做“颜色近似”的实现。
- **CJK 与跨机器保真**：字体 fallback、East Asian font metadata、glyph 宽度和渲染复核已经被显式考虑。
- **质量门**：结构 validator、逐页渲染、contact sheet、eval coverage gate、安装边界测试和环境矩阵，已经形成比较完整的工程骨架。
- **单一事实源**：`styles/index.json` 负责风格计数、命名、推荐和样例映射，降低文档漂移。

### 最值得优先补上的部分

#### P0：把“事实边界”和“可访问性”加入 build contract

新增一个轻量的 outline/source schema，至少包含：

```text
slide_id
title_assertion
evidence_items[]
source_refs[]
content_status: provided | researched | inference | unknown
audience
duration
visual_type
speaker_notes
alt_text
reading_order
```

在生成前阻止 `unknown` 事实直接进入数字、图表或断言标题；在 QA 中要求每页有唯一语义标题，并检查 alt text、reading order、对比度、颜色冗余编码。

原因：这是当前实现中最明显的“内容可信度”和“可访问性”缺口，且不依赖新增外部 skill；可以先用标准库 XML/HTML 检查做降级实现。

#### P1：把“可编辑”从计数升级成内容加权指标

当前 `pptx_inspect` 已经统计 text/chart/table/image，但“有 text shape”不等于“关键内容可编辑”。建议增加：

- `editable_content_ratio`：标题、正文、数据表、图表等关键内容中 native 对象的占比；
- `critical_visual_editability`：页面主视觉是否为 native chart/table/diagram，或明确标注为装饰位图；
- `notes_coverage`、`alt_text_coverage`、`unique_title_coverage`；
- `source_traceability_coverage`：数字/外部事实是否能映射到 source ref；
- `cross_slide_consistency`：同类 layout 的字体、页边距、标题位置、颜色 token 是否漂移。

原因：最新 benchmark 的评测对象已经从“截图像不像”转向“能否可靠编辑真实 deck”；本地 eval 应随之升级。

#### P1：增加“编辑任务”型回归用例

除了当前的固定输入生成案例，增加小型可重复任务：

1. 修改一张 native chart 的一个数值，检查图表和标题是否仍一致。
2. 把标题替换为更长的中文句子，检查是否溢出或错误缩小字体。
3. 替换一个主题 token，检查所有同类页面是否一致变化。
4. 移除图片，检查 alt text/notes/reading order 是否仍合法。
5. 从参考模板复制一页后，检查 master/layout/footers 是否保留。

原因：这些任务直接测试用户交付后的真实维护成本，而不是一次性导出的表面质量。

#### P2：加入参考 deck 的“设计 spec 提取”能力

如果未来要增强模板跟随，可以将来源 PPTX 提取为：页面角色、layout signature、字体、颜色、页边距、占位符、图像裁切和重复组件，并对同类页面去重。生成时选择 spec，渲染后并排比较。

原因：这会把当前已经很好的 template-following 文字规则变成可执行的中间表示；但它依赖更多 PPTX 解析能力，不应在没有能力探测时变成硬依赖。

#### P2：把“deck vs handout”做成显式输出选项

现在流程已有 speaker notes，但可以在 Step 2 直接区分：

- `presentation`：远距可读、视觉优先、脚本在 notes；
- `handout`：允许更高密度、完整来源和定义；
- `hybrid`：双产物，视觉 deck + 详细文档。

原因：一个文件同时承担“现场讲解”和“会后查阅”两种任务，通常会让两者都变差。公开 skill 也把视觉 slides 与详细文档视为两个 artifact。

## 五、推荐的成熟度模型

| 等级 | 能力 | 典型验收 |
|---|---|---|
| L0 导出器 | 能产出 PPTX/HTML/图片 | 文件能打开，页数正确 |
| L1 设计助手 | 有风格、版式、密度和内容建议 | 大纲先行，逐页可读，视觉风格一致 |
| L2 生产 skill | 有能力探测、native 对象、模板跟随和渲染 QA | 可编辑、可渲染、失败路径透明 |
| L3 可验证生产系统 | 有 source boundary、无障碍、结构/像素/语义 eval 和 receipt | 关键事实可追溯，编辑任务回归通过 |
| L4 协作式 presentation agent | 能理解真实 deck、执行跨页修改、保留组件关系并根据评审迭代 | 参考模板、内容、样式、交互编辑任务都有 rubric 与部分得分 |

`subaru-slides` 目前已经稳健地处在 **L2**，并在能力探测、模板跟随、CJK 和 claim boundary 上接近 L3；最值得做的是补齐 L3 的 source/accessibility/edit-task 三件套，而不是继续堆风格 preset 数量。

## 六、最终判断

如果只保留五条原则，我会选择：

1. **先问清受众、目的、时长和素材可信度。**
2. **一页一个断言，正文只保留能支撑它的证据。**
3. **关键内容使用 native、可复用、可追溯的结构。**
4. **把可访问性和 CJK/跨机器保真当作生成契约。**
5. **渲染、结构、语义和编辑任务都验证，并明确未验证的部分。**

这五条之所以是最佳实践，是因为它们同时降低了四种成本：观众理解成本、用户后续编辑成本、系统调试成本和错误事实传播成本。色板、插画和“高级感”只能优化其中一小部分；不能替代这条闭环。

## 七、Skill 体积审计：不算大，但热路径仍可瘦身

### 7.1 结论

`subaru-slides` 的 Git 跟踪内容约 **1,217,561 bytes（1.16 MiB）**，只使用了仓库 5 MiB 上限的约 **23%**。因此，从安装、上传和版本管理角度看，它**不属于过大的 skill**。

更重要的是区分“磁盘体积”和“上下文体积”。[Agent Skills 开放规范](https://agentskills.io/specification)采用渐进式披露：发现阶段只读取 frontmatter，激活后读取 `SKILL.md`，其他 references、scripts 和 assets 按需读取。当前 `SKILL.md` 为 **113 行 / 6.3 KiB**，既低于开放规范建议的 500 行，也低于本仓库更严格的 200 行上限。真正的风险不是整个包有 1.16 MiB，而是一次任务中是否重复读取了内容相似的热路径文件。

| 区域 | Git 跟踪文件 | 大小 | 占比 | 判断 |
|---|---:|---:|---:|---|
| `assets/` | 17 | 1,087,492 bytes | 89.3% | 磁盘主因，但不是常规上下文主因 |
| `references/` | 24 | 71,117 bytes | 5.8% | 总量合理，存在重复与低内聚文件 |
| `styles/` | 24 | 35,937 bytes | 3.0% | 数量合理，完整 index 属于热路径 |
| `scripts/` | 2 | 16,348 bytes | 1.3% | 很小 |
| `SKILL.md` | 1 | 6,330 bytes | 0.5% | 健康，但还可进一步“只做路由” |
| `agents/` | 1 | 337 bytes | <0.1% | 可忽略 |

17 张样例图都是 WebP，最大单张不足 109 KiB；15 张为 960×535，2 张为 1200×669。它们远低于单文件 1 MiB 上限，也适合作为风格预览。为减少包体而删除样例图，会损失可视化选型能力，却几乎不降低普通任务的文本上下文成本。

### 7.2 优化优先级

#### P0：消除热路径重复

`SKILL.md` 已经描述 Step 0–7，`references/workflow.md` 又重复同一流程。如果两者在同一任务中被加载，模型会付出两次上下文成本，还可能在未来出现版本漂移。应二选一：

- 保留当前 70–100 行左右的入口流程，把 `workflow.md` 改成只包含模式差异、checkpoint 模板和异常分支；或
- 让 `SKILL.md` 只保留规则、路径表和引用条件，把完整流程唯一地放在 `workflow.md`。

推荐第一种，因为用户触发 skill 后最常用的流程无需再读取第二个文件，同时复杂分支仍可按需披露。

#### P0：拆分 `prompt-templates.md`

该文件为 **395 行 / 17.7 KiB**，虽然未超过 600 行硬上限，但同时包含当前模板、图片生成、具体产品集成、外部资源和历史实验，内聚度偏低；其“精确指定构图/颜色”建议还与 `illustrations.md` 的“短 prompt、避免微操构图”存在张力。

建议拆为：

1. `prompt-templates.md`：只保留稳定、平台无关、当前生效的模板；
2. `integrations.md`：吸收 NotebookLM 等产品特定内容；
3. `references/archive/` 或 lessons learned：迁移历史实验和不再作为运行时契约的材料。

这里的收益不仅是少读约十几 KiB，更重要的是降低冲突指令导致的执行不确定性。

#### P1：让风格索引“可查询”，而不是默认整份读取

`styles/index.json` 为 **11.1 KiB**，作为风格数量、命名和推荐的唯一事实源是正确设计，不应复制出第二份手工维护的数据。可以增加一个无状态查询脚本，从同一 index 输出候选 style id、formality、path 和 sample；选中后再读取单个 preset。这样既保持单一事实源，又避免每次把完整注册表放入上下文。

#### P1：规范发布包，而不是压缩一切

工作树中存在被 Git 忽略的 `scripts/__pycache__/*.pyc`。它不计入上述 1.16 MiB，但直接把目录打成 ZIP 时可能被误收。发布时应从 `git ls-files` 或明确 allowlist 建立 staging 目录，而不是压缩当前工作树。这个控制比继续压缩几十 KiB 的文档更可靠。

#### P2：统一样例尺寸和文件名

可将两张 1200×669 样例统一到 960×535，但预计只是小幅磁盘收益。更高价值的动作是把文件名统一为稳定的 style id，例如 `constructivism.webp`，并由 `styles/index.json` 映射展示名称。这样可以减少重命名和跨平台路径问题。

## 八、标准合规审计：核心结构通过，仓库规范为“部分通过”

### 8.1 三层标准不能混为一谈

| 标准层 | 审计结果 | 依据 |
|---|---|---|
| Agent Skills 开放规范 | **通过** | 目录含 `SKILL.md`；frontmatter 的 `name` 与目录一致，符合小写连字符规则；`description` 同时说明能力与触发条件；使用标准的 `scripts/`、`references/`、`assets/` 结构 |
| OpenAI/Codex 宿主扩展 | **通过（以本仓库 schema 为准）** | `agents/openai.yaml` 含 display name、description、brand color、default prompt 和 implicit invocation policy；OpenAI 公开 API 支持目录/ZIP skill bundle 与版本管理，但目前公开页面没有给出一套比本仓库 schema 更完整的 Codex `SKILL.md` 文件规范 |
| 本仓库 `AGENTS.md` 硬性规范 | **部分通过** | 行数、总体积、WebP、薄入口、相对路径、能力探测和降级设计通过；资源命名、文档语义质量和脚本 doctor 约定存在偏差 |

开放规范侧的判定还可由 GitHub 对 Agent Skills 的说明交叉验证：skill 是包含指令、脚本和资源的可移植目录，按需加载以减少上下文开销。[GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)

### 8.2 已符合的关键项

- `SKILL.md` 113 行，低于仓库 200 行上限；最大 reference 395 行，低于 600 行上限；总包 1.16 MiB，低于 5 MiB。
- frontmatter 名称 `subaru-slides` 与目录一致，description 同时包含 PPT、幻灯片、slides、路演、课件等触发词。
- `styles/index.json` 被定义为风格数量、命名、推荐和样例映射的唯一事实源，符合本仓库的防漂移约定。
- 执行路径明确使用“能力探测 → 路由 → 降级”，且提供最低图片 PPTX fallback，没有把外部 skill 写成全局强依赖。
- 所有样例位图均为 WebP，单文件和总包体积均过闸。
- `agents/openai.yaml` 通过仓库机读 schema；`make check` 当前通过。

### 8.3 未完全符合或需要澄清的项

#### 1. 资源文件名违反仓库约定（已修复）

审计时，11 个样例文件名含中文，例如 `slide04-01-苏联构成主义-constructivism.webp`。这不违反 Agent Skills 开放规范，但违反本仓库“使用稳定英文小写 style id，不用中文或空格”的硬规则。现已将全部 17 张样例统一为 `<style-id>.webp`，并同步更新 `styles/index.json` 与各 preset；文件内容未改变。

#### 2. 五处文档存在 `@@` 损坏标记（已修复）

审计时，`workflow.md`、`native-evidence.md` 和 `path-a-native.md` 中曾有 `path@@.`、`31@@`、`indent@@` 等五处明显损坏。它们不是排版瑕疵：出现在路径选择、百分比数据和单位护栏中，会改变运行时含义。现已改为明确的 `path`、`0.31` 与 `indent` 表述，并通过 `make check`；质量门仍应补充文档损坏/异常字符扫描，以防止复发。

#### 3. Path A 的 fallback 描述与实现边界不够一致（已修复）

审计时，`path-a-native.md` 把 plain `python-pptx` 称为 “bundled fallback”，但仓库内置的 `create_slides.py` 实际是“图片 → PPTX”的最低兜底，不是能构建 native 表格、图表和文本系统的完整 Path A builder。现已明确区分：Path A 需要能创建原生对象的 builder；内置 helper 只能用于图片型 PPTX fallback，且必须披露内容不可编辑。

#### 4. `--doctor` 约定只有包级实现，缺少脚本级一致性

`detect_capabilities.py` 实质上承担了 package doctor 的职责，并支持 `--json`；`create_slides.py` 有 `--help`，但没有字面上的 `--doctor`。若严格执行“依赖环境的脚本提供 `--doctor`”，应给 `create_slides.py` 增加代理检查，或在依赖文档中明确 package-level doctor 是统一入口。

#### 5. 当前校验器存在盲点

`make check` 能验证 frontmatter、行数、链接、WebP、体积和 style registry 一致性。现已额外拒绝：

- 运行时 Markdown（代码块外）中的 `@@` 损坏标记；
- index、preset 或样例目录中不符合 `<style-id>.webp` 的 style sample 路径；

它目前仍不会阻止：

- 被忽略目录在“直接 ZIP 工作树”时进入发布包；
- prompt 规则间的语义冲突；
- Path 文档声称的能力与实际脚本能力不一致。

因此，“`make check` 通过”应解释为**机器可检查的结构标准通过**，不能等同于完整的语义合规。

### 8.4 建议的整改顺序

| 优先级 | 动作 | 原因 | 建议验收 |
|---|---|---|---|
| P0 | 修复 5 处 `@@`，澄清 Path A 与图片 fallback | 直接影响运行时含义和能力声明 | **已完成**：全库无异常标记；能力矩阵与脚本边界一致 |
| P0 | 将 11 个中文样例名改为 style id | 明确违反仓库硬规则 | **已完成**：17 个样例统一为 style id；index、preset、文件名一致；旧链接为零 |
| P0 | 为 validator 增加异常标记和 asset 命名检查 | 防止同类问题回归 | **已完成**：新规则与失败 fixture 已加入；正常 skill 通过质量门 |
| P1 | 去重 `SKILL.md` / `workflow.md`，拆分 prompt 模板 | 降低热路径上下文和冲突概率 | 行为不变；reference 路由更精确 |
| P1 | 明确 package-level `--doctor` 契约或为脚本补齐 | 消除规范解释空间 | `--help` 与 `--doctor` 都有测试 |
| P2 | 由 index 查询脚本输出精简候选 | 保持 SSOT，同时减少热路径读取 | 查询结果与 index schema 一致 |

综合评级：**开放 Agent Skills 结构合规；本仓库工程规范部分合规；生产成熟度仍为 L2，完成上述 P0 后才适合称为“严格按本仓库标准完成”。**

## Sources

1. [Penn State, Engineering Ambassadors: Learning the Assertion-Evidence Approach](https://writing.engr.psu.edu/assertion_evidence_EA.html)
2. [Richard E. Mayer, Applying the science of learning: evidence-based principles for the design of multimedia instruction](https://pubmed.ncbi.nlm.nih.gov/19014238/)
3. [W3C, Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)
4. [W3C, Understanding Success Criterion 1.4.3: Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
5. [Microsoft, Make your PowerPoint presentations accessible to people with disabilities](https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities)
6. [Microsoft, Customize a slide master](https://support.microsoft.com/en-us/PowerPoint/training/customize-a-slide-master)
7. [Microsoft, Change the data in an existing chart](https://support.microsoft.com/en-us/powerpoint/change-the-data-in-an-existing-chart)
8. [Google for Developers, Pages, Page Elements, and Properties](https://developers.google.com/workspace/slides/api/concepts/page-elements)
9. [Google for Developers, Work with speaker notes](https://developers.google.com/workspace/slides/api/guides/notes)
10. [Cleveland & McGill, Graphical Perception: Theory, Experimentation, and Application](https://doi.org/10.1080/01621459.1984.10478080)
11. [Ofengenden et al., PPTArena: A Benchmark for Agentic PowerPoint Editing](https://arxiv.org/abs/2512.03042)
12. [Gandhi et al., PPT-Eval: A Benchmark for Computer-Use Agents on PowerPoint Tasks](https://arxiv.org/abs/2606.31154)
13. [ICGMA, slide-skill](https://github.com/icgma/slide-skill/blob/master/SKILL.md)
14. [LGWAnAI, ppt-skill](https://github.com/lgwanai/ppt-skill/blob/main/SKILL.md)
15. [hunkim, slide-skill](https://github.com/hunkim/slide-skill)
16. [Agent Skills, Specification](https://agentskills.io/specification)
17. [GitHub Docs, About Agent Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
18. [OpenAI API Reference, Skills](https://developers.openai.com/api/reference/go/resources/skills)
19. [OpenAI, Latest model guidance](https://developers.openai.com/api/docs/guides/latest-model)
