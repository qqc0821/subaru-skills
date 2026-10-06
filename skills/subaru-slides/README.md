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

## 渲染图质检

`scripts/detect_pixel_artifacts.py`（零依赖、只读、不联网）对逐页渲染的 PNG 检查三类只在像素里可见的缺陷：数字组换行产生的孤字、被自动缩放撑大的孤字、横穿色块边界的细带。判据、阈值与生成侧预防见 [references/qa/pixel-artifacts.md](references/qa/pixel-artifacts.md)。

## 风格

`styles/index.json` 是风格数据的唯一事实源（id、中文/英文名称、主题推荐、正式程度、适用路径、样例映射、proven 状态）；`styles/router.md` 是由它生成的选型摘要（Agent 选风格时只读这一张表），每个风格另有 `styles/<id>.md` preset，样例图在 `assets/style-samples/`。

## 更多

- 运行时规则、流程与检查点：[SKILL.md](SKILL.md)
- 工作流与路径细节：[references/workflow.md](references/workflow.md)
- 设计与 QA：[references/qa/checklist.md](references/qa/checklist.md)
- 再分发：本 skill 含第三方来源的文档与样例图，再分发前请确认各自的授权边界。

## 版本、更新与稳定发布

包版本查看安装目录中 `SKILL.md` 的 `metadata.version`；它是该 skill 的版本来源。带 `-dev.N` 的版本是开发预发布版，同一开发版在正式发布前仍可能有内容变化；精确追踪需结合 CLI 安装来源记录或 Git commit。

不指定分支的安装命令获取仓库默认分支 `main` 的最新内容，可能包含尚未发布的修改；“默认分支最新版”不等于“最新稳定版”。

通过 [skills CLI](https://github.com/vercel-labs/skills#skills-update) 安装后，在原项目目录运行项目级更新，或使用 `-g` 更新全局安装：

~~~bash
npx skills update subaru-slides -p
npx skills update subaru-slides -g
~~~

更新依赖 CLI 保存的安装来源与内容记录，不按 `metadata.version` 自动选择最新稳定 Release。旧 CLI 不支持命令、或来源记录缺失时，使用原来的 `npx skills add` 命令重新安装，并选择相同宿主和项目级 / 全局范围（全局加 `--global`）。更新前备份自定义修改；更新后按宿主要求重新加载 skill 或开启新会话。

手动下载 ZIP / 复制目录的用户：重新下载所选分支或发布版本，备份旧目录，再用对应的 `skills/<name>/` 完整替换宿主中的 skill 目录，避免遗留新版已删除的文件。只对下载仓库执行 `git pull` 不会同步已复制的副本；手动复制也不保证能由 CLI 更新接管。

稳定版入口：[GitHub Releases](https://github.com/qqc0821/subaru-skills/releases)。截至 2026-10-06，远端尚无 Release 或 tag，当前没有可安装的稳定版；历史 `0.1.0` 记录不代表已有稳定发布。

发布稳定版后，从 Release 页面选定实际存在且包含所需 skill 的 tag，再通过固定 tag 安装：

~~~bash
# 模板：把 <release-tag> 换成 Release 页面中实际存在的 tag
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>" --skill subaru-slides
~~~

固定 tag 的安装用于保留该版本，不会自动切换到后续稳定 tag。升级稳定版时先阅读目标 Release 的变更说明，再将安装 URL 的 tag 换成新 tag 重新安装；想切回默认分支则使用不带 tag 的原安装命令。
