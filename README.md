# subaru-skills

用 AI 制作中文演示文稿、探索产品创意的 [Agent Skills](https://agentskills.io/)。从自己的资料或问题出发，得到可检查、可继续修改的产物。

[English](README.en.md) · [三个完整案例](examples/README.md) · [安装与更新](docs/installation.md) · [来源与许可](PROVENANCE.md)

![原创管理层汇报的实际 PPTX 封面：先验证能否找到答案，再扩大知识库投入](examples/management-report/preview.webp)

上图来自本仓库原创的 6 页演示案例，包含原生图表、表格与流程图；业务数据为虚构演示数据。[下载 PPTX](examples/management-report/deck.pptx) · [查看输入与验证边界](examples/management-report/README.md)。

## 先完成一次小任务

先试无需第三方运行依赖的头脑风暴 skill：

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-brainstorm
~~~

> 用 $subaru-brainstorm 探索团队知识库还能有哪些用途。先给 8 个不同机制的方向，暂时不要排名。

安装后按宿主要求重新加载 skill 或开启新会话。宿主不支持 `$skill-name` 语法时，可用自然语言要求使用该 skill。没有 CLI 时，把 `skills/<name>/` 放到宿主支持的 skill 目录。

`subaru-slides` 的第三方再分发授权尚待确认，先阅读 [PROVENANCE.md](PROVENANCE.md)。确认适用许可后，可单独安装：

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-slides
~~~

> 用 $subaru-slides 把这份资料做成 6 页中文管理层汇报。Full Auto，优先可编辑 PPTX，保留来源与备注；缺工具时说明替代方案。

## 选择适合的 skill

| 你的问题 | Skill | 入口 |
|---|---|---|
| 把主题、资料或文档变成中文汇报、课件或技术分享 | `subaru-slides` | [使用说明](skills/subaru-slides/README.md) · [实际案例](examples/rag-sharing/README.md) |
| 打开思路、突破重复点子、发展方案或保存讨论 | `subaru-brainstorm` | [使用说明](skills/subaru-brainstorm/README.md) · [完整产物](examples/knowledge-library/result.md) |

文字、表格、图表与流程图需要编辑时，优先使用原生对象。没有原生构建能力时会说明降级；图片型 PPTX 不恢复原生文字。生图为可选增强。具体运行规则以各包 `SKILL.md` 为准。

## 看输入，也看结果

| 案例 | 实际产物 | 证据边界 |
|---|---|---|
| [管理层汇报：知识库两周试点](examples/management-report/README.md) | 6 页 PPTX、图表、表格、流程图、备注 | 原创虚构场景；没有客户或业务效果证据 |
| [技术分享：RAG 与有来源的回答](examples/rag-sharing/README.md) | 6 页 PPTX、两条流程、评估检查表、备注 | 原创教学材料；未运行 RAG 服务或性能基准 |
| [创意探索：知识库还能做什么](examples/knowledge-library/README.md) | 8 个机制、展开分支、实验卡、续谈摘要 | 单次助手产物；没有多轮用户访谈或真实实验 |

两份 PPTX 在本次 Codex 会话中按本地 skill 指引直接编写，使用 python-pptx 构建并经 LibreOffice 逐页渲染。字体未嵌入；PowerPoint、Keynote、Google Slides 与跨机字体未验证。案例不证明所有宿主能自动加载或执行 skill；CLI 安装更新仍待端到端验证。

## 版本与许可

当前包为开发预发布内容，版本读取各自 `SKILL.md` 的 `metadata.version`。默认安装跟随 `main`，不等于稳定版；稳定安装只使用 [Releases](https://github.com/qqc0821/subaru-skills/releases) 中实际存在的 tag。[完整更新与版本说明](docs/installation.md)。

根 [MIT LICENSE](LICENSE) 只覆盖原创内容。`subaru-brainstorm` 与本轮新案例为原创；slides 的第三方文档与样例图许可边界见 [PROVENANCE.md](PROVENANCE.md)。

## 文档站与贡献

[静态文档站源码](site/README.md)包含中英文问题指南、案例下载和发布状态；目前已准备本地构建与手动 GitHub Pages 部署流程，不能据此认为网站已经上线。

反馈请提供宿主、安装命令、输入与具体失败结果：[提交 Issue](https://github.com/qqc0821/subaru-skills/issues)。贡献与工程验证见 [AGENTS.md](AGENTS.md)，发布与发现渠道维护见 [运营入口](docs/discovery.md)。

~~~bash
make check       # 仓库质量门，包括文档站链接与元信息
make test        # 工具与构建器测试
make doctor      # 本机能力探测
make site        # 零第三方依赖构建到 output/site/
~~~

变更历史见 [CHANGELOG.md](CHANGELOG.md)。
