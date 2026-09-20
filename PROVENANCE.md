# Provenance & Licensing

本文件记录 `subaru-skills` 中第三方来源内容的出处与再分发条件。

## `skills/subaru-slides`

- **上游**：`huashu-slides`。
- **审计基线 commit**：`791450a2594a3506144917517ff5533c344a62b0`。
- **上游许可状态**：该 commit 处上游**没有根 LICENSE 文件**（无明确授权声明）。
- **本仓库处置**：内容已在本仓库内大幅重构（组织为 skill 包 + Harness：`schemas/`、`tools/`、
  `evals/` 等为本仓库原创）。**再分发前必须确认上游授权。**

## 许可边界

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
