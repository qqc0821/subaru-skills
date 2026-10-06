# Provenance & Licensing

本文件记录 `subaru-skills` 中第三方来源内容的出处与再分发条件。

## `skills/subaru-slides`

- **上游**：`huashu-slides`。
- **审计基线 commit**：`791450a2594a3506144917517ff5533c344a62b0`。
- **上游许可状态**：该 commit 处上游**没有根 LICENSE 文件**（无明确授权声明）。
- **本仓库处置**：内容已在本仓库内大幅重构（组织为 skill 包 + Harness：`schemas/`、`tools/`、
  `evals/` 等为本仓库原创）。**再分发前必须确认上游授权。**

## 许可边界

`skills/subaru-brainstorm` 及其新增会话协议、评测案例和检查器为本仓库原创，适用根 MIT LICENSE；未复制第三方文档、脚本或图片。

- 仓库根 `LICENSE`（MIT，LesBit）**仅覆盖本仓库原创内容**。
- 它**不自动覆盖**上述第三方复制内容，也不覆盖 `skills/subaru-slides/assets/style-samples/`
  中作为风格样例收录的示意图（其版权归各自来源所有，仅作风格对照用途）。
- `LICENSE` 中保留的第三方署名与来源说明，不因本仓库的 MIT 声明而改变。

## 贡献者须知

新增任何来自外部的文档、脚本、图片或风格 preset 时，必须在本文件补充：

1. 来源（上游仓库 / 作者 / URL）；
2. 取用的 commit 或版本；
3. 该来源的许可类型；
4. 是否允许再分发。

## 商业研究设计参考（2026-10-06）

`skills/subaru-slides/references/business-references.md` 记录 10 份公开报告的来源、版本和抽样页码。
新增文字为本项目原创设计分析；未将第三方 PDF、页面截图、图表、logo 或字体纳入安装包。
原报告权利归发布者，公开可阅读不代表可再分发。

## 公开案例与文档站（2026-10-07）

`examples/management-report/`、`examples/rag-sharing/`、`examples/knowledge-library/` 与 `site/` 为本次新编写的原创内容，适用根 MIT LICENSE。管理层案例的业务数据为虚构；RAG 案例为原创教学总结，技术参考 URL 与读取日期记录在 `examples/rag-sharing/source.json`，未复制第三方图表、截图或文档正文。PPTX 与 WebP 预览使用原生对象渲染，未分发字体文件。

上述原创案例的发布不会改变 `skills/subaru-slides` 上游复制内容与原有风格样例的授权状态；该缺口仍需分别取得许可、替换或经审查移除。本站构建只复制新案例，不上传 skill 包。
