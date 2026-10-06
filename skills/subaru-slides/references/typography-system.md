# 字体配置、解析记录与验证

换字体、中英搭配、品牌字体或跨平台交付时读本文件与 `../typography/profiles.json`。
配置提供候选；用户已认可的设计基线优先。选择字体配置不会改配色、构图或插图。

## 职责与角色

- `../styles/foundation.json`：观看 profile 与字号唯一来源。`inherits` 合并未覆盖角色；
  旧 profile 未声明 inherits 时仍继承 default。`role_aliases` 复用已有尺寸，不再另写字号表。
- `../typography/profiles.json`：字体候选、脚本分工、角色的真实字款名称；不包含本机路径或字号。
- `../scripts/detect_fonts.py`：按当前环境生成解析记录；字体元数据和字形覆盖不等于渲染通过。
- 默认便携单家族；已认可 v5 场景可用 v5-reference；product-clean 是 MiSans 候选，需样张验证。
  字体 profile 与视觉风格不是同一目录：不要给每种品牌字体新增一个视觉 preset。
- 标题按页面任务设置，正文保持阅读字款。`display-title` 适合少量展示大字；
  `metric-value` / `metric-unit` 分开控制数字与解释，布局时仍作为一组。
- 配置的 role_styles 是试排起点，用户要求或模板可提供自定义配置。修改字款映射后重新解析与试排。

## 两档探测

原有命令继续可用，无外部 Python 依赖：

```bash
python3 scripts/detect_fonts.py --locale zh-CN --json
```

它只检查 fontconfig family，`--target-platform` 只改变候选顺序，查询仍在本机。
缺 fontconfig 返回 unverified，不表示字体不存在。

需要真实字款/字形时：

```bash
python3 scripts/detect_fonts.py --profile v5-reference \
  --text-file deck-text.txt --font-dir task-fonts \
  --output typography-receipt.json --policy-output font-policy.json
```

- `--font-file` / `--font-dir` 可重复；脚本只读，自动搜索系统常用字体目录（包括 macOS 下载字体资产），不安装、不下载。
  platform_fallback 从 foundation 读取目标平台候选；仍只验证本机或所提供的文件。
  隔离实验用 `--no-system-fonts`；其结果只代表提供的文件，不代表整个系统。
- 元数据增强用可选 fontTools；缺少时返回 unverified。先探测当前 Python；
  已有字体信息 API 也可补充验证。安装新依赖需遵守宿主授权，不静默安装。
- 按字体中的 family 别名与 style 名精确匹配，不把 Noto Sans 和 Noto Sans CJK 当同一家族。
  使用 Regular/Bold 等实际字款名称；数字权重值原样记录，不强行换算成惯常数值。
- 当前自动解析只选择非斜体、正常宽度的静态字款。可变、斜体、窄体不是缺陷，
  但不由当前探测器冒充正常静态字款。需要这些表达时由支持它们的后端单独验证。
- 缺字款或实际文案缺字时尝试声明的下一家族，记录 missing-family / missing-static-face / missing-glyphs。
  portable-single 的 Bold 可在所有家族都无对应字款后回退真实 Semibold；其他配置不隐式替换字款。
  style_fallbacks 是明确声明的替代，记录请求与实际 style；回退后重新试排。
  不得用伪粗体或隐藏字体替换声称保持原设计。
- 未提供文案时 coverage 为 unverified。覆盖率按脚本分开检测，包含中文标点与扩展区汉字。
  cmap 检查是字符映射证据，不证明复杂 shaping、OpenType 功能或轮廓绘制正确。
- 解析记录包含 actual family/style/PostScript name、版本、权重、文件、集合索引和 axes。
  文件位置只保存在任务产物，不写入安装包。字体 fsType 是技术标记，不替代授权协议。

## 构建与回退

将解析结果明确传给原生构建器，逐角色设置 Latin / East Asian 字体和语言；同步主题字体时
保持用户的中英分工。具名字款可能在不同后端有不同 family 表达，先用原生样张验证。

普通/粗体两档构建器仅在真实 Regular/Bold 字款可加载时使用对应开关；
Medium/Semibold 需要具名字款或支持真实权重的后端。某字体只有一个可用字款时不能宣称完成多字重配置。

每次改组合先固定文案、坐标、pt、颜色，比字体/字款；确认后再改变层级、行距和中英尺寸补偿。
中英字号补偿按具体组合和角色记录，不设永久全局系数。光学尺寸、等宽数字等能力须在后端验证。

## 最终 PPTX 检查

字体策略 JSON 包含 `roles`，每个角色明确 `ea` 与 `latin` 允许家族；`*` 是未标注角色的兜底。
v5-reference 的 Latin 策略明确允许 CJK 家族承担句中 Latin，独立品牌/数字可用 Latin 家族。
策略必须与实际字款解析和已认可样张一致，不能把意外字体加入允许列表来消除 warning。

在有对应校验工具的宿主，用解析记录的 font_policy 检查最终 PPTX 的每个文本段；
合法中英配对不因家族数报警，未声明家族或错误脚本分配应定位到页/对象/段。
未解析的主题继承应报告 unverified。该检查只核对声明，不检测渲染器的隐式字体替换。
没有该工具时手工检查声明并回导入逐页渲染，保留未验证项。

最终文件重新导入、渲染、目检；记录后端和字体加载路径。解析记录默认不声称 builder、
final_pptx_render、recipient_environment 或 embedding 已验证，由实际执行证据分别补充。
PowerPoint / Keynote / Google Slides 分别记录；本机两种引擎通过也不是跨机器证明。

## 来源与授权

字体按任务取得并保留来源/许可。默认不携带字体包；免费商用不等于可修改、分发或嵌入。
MiSans 与其他品牌字体优先使用官方静态字款，未经许可不实例化、改造或另设下载渠道。
嵌入与可编辑嵌入单独核对；未嵌入的 PPTX 需说明收件环境可能回退。
