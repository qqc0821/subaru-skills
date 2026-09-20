# Style Router

> **自动生成的派生产物，请勿手改。** 唯一事实源是 `index.json`；开发仓库会自动校验两者一致。
>
> 选风格只需要这一张表：先按主题推荐定位，再用 `formality` 与 `path` 过滤，
> 最后**只读选中的那 1 个** `styles/<id>.md` 取 Base Style Prompt 与版式组件。

## 主题 → 推荐

| 主题 | 首选 | 次选 | 第三 |
|---|---|---|---|
| 品牌/产品介绍 | warm-comic-strip | neo-pop-magazine | dunhuang-mural |
| 教育/培训 | neo-brutalism | manga-educational | warm-comic-strip |
| 技术分享 | whiteboard-sketch | neo-brutalism | ligne-claire |
| 数据报告 | pentagram-editorial | fathom-data | ligne-claire |
| 年轻受众 | neo-pop-magazine | pixel-art | risograph |
| 创意/艺术 | dada-collage | risograph | oatmeal-comic |
| 国风/东方 | dunhuang-mural | ukiyo-e | takram-speculative |
| 正式商务 | pentagram-editorial | muller-brockmann-grid | build-luxury-minimal |
| 产品发布/keynote | soviet-constructivism | neo-pop-magazine | pentagram-editorial |
| 内部分享 | neo-brutalism | oatmeal-comic | whiteboard-sketch |
| 行业分析/咨询 | fathom-data | pentagram-editorial | muller-brockmann-grid |
| 培训课件/教材 | takram-speculative | warm-narrative | manga-educational |
| 投资/融资路演 | build-luxury-minimal | pentagram-editorial | soviet-constructivism |

## 风格

样例图：`assets/style-samples/<id>.webp`；完整元数据：`index.json`。

### path: A

| id | 名称 | 主题 | 正式度 | 一句话 |
|---|---|---|---|---|
| neo-brutalism | 新粗野主义 | 企业培训/线下分享/信息密集 | 中 | 粗边框 + 色块 + 大字，远距离可读性极强 |
| pentagram-editorial | 编辑杂志风 | 行业分析/咨询报告/正式商务 | 高 | 字体即语言，网格即思想，让数据自己说话 |
| fathom-data | 数据叙事风 | 数据报告/行业分析/研究汇报 | 高 | 科学严谨 + 设计优雅，图表即叙事 |
| muller-brockmann-grid | 瑞士网格风 | 培训课件/技术架构/流程说明 | 高 | 数学精确的网格让混乱的信息变得有序 |
| build-luxury-minimal | 奢侈极简风 | 投资/融资路演/品牌高管汇报/奢侈品 | 高 | 精致的简单，用留白传达高端感 |

### path: A_or_B2

| id | 名称 | 主题 | 正式度 | 一句话 |
|---|---|---|---|---|
| bauhaus | 包豪斯 | 设计行业/建筑/教育 | 中 | 几何 = 逻辑，形式跟随功能 |
| blueprint | 工程蓝图 | 技术架构/工程方案 | 高 | 精密机器隐喻，适合技术架构 |
| takram-speculative | 日式思辨风 | 培训课件/教材/设计思维/产品愿景 | 中 | 柔和的科技感，用概念原型图传达深度思考 |

### path: B_or_B2

| id | 名称 | 主题 | 正式度 | 一句话 |
|---|---|---|---|---|
| warm-comic-strip | Snoopy温暖漫画 | 品牌/产品介绍/教育/培训/个人IP | 低 | Peanuts 漫画的温暖与哲理感：简单角色说着深刻的话 |
| manga-educational | 学習漫画 | 教程/培训/知识分享 | 低 | 角色带着读者学习，用反应与戏剧性强化重点 |
| ligne-claire | 清线漫画 | 产品说明/流程解释 | 中 | 均匀线条 + 平涂色块 = 零视觉噪音，信息清晰度最高 |
| neo-pop-magazine | 新波普杂志 | 年轻品牌/社交平台/活动 | 低 | 潮流感强，把排版本身当作视觉主体 |
| whiteboard-sketch | xkcd白板手绘 | 技术分享/极客受众/课堂 | 低 | 极简幽默，复杂概念秒懂 |
| soviet-constructivism | 苏联构成主义 | 产品发布/keynote/campaign/品牌宣言 | 中 | 力量感与几何精确性，辨识度极高 |
| dunhuang-mural | 敦煌壁画 | 国风/东方/文化项目/高端场合 | 中 | 东方美学，庄重诗意 |
| ukiyo-e | 浮世绘 | 日本/东方市场/跨境品牌 | 中 | 浪潮隐喻天然表达递进 |
| oatmeal-comic | The Oatmeal信息图漫画 | 科普/社交传播/内部培训 | 低 | 搞笑夸张，信息密度适中 |
| warm-narrative | 温暖叙事 | 用户故事/品牌故事 | 中 | 暖色人物插画，最有"人情味" |
| risograph | 孔版印刷 | 独立品牌/创意行业/音乐 | 低 | 双色叠印独特美学 |
| isometric | 等轴测 | 科技产品/SaaS流程 | 中 | 2.5D 游戏世界感，适合流程与递进 |
| vintage-ad | 复古广告 | 消费品/零售/怀旧 | 低 | 乐观复古，怀旧好感 |
| dada-collage | 达达拼贴 | 创意行业/广告/破冰 | 低 | 反规则，最另类 |
| pixel-art | 像素画RPG | 游戏/年轻群体/gamification | 低 | RPG 任务隐喻，gamification 首选 |

无样例图 / 未验证：neo-brutalism、pentagram-editorial、fathom-data、muller-brockmann-grid、build-luxury-minimal、takram-speculative。
