# 工程决策索引

本目录解释影响后续维护的设计取舍。当前约束由开发入口、工程规范与 skill references 维护，缺陷行为由实现和回归断言表达。
常规修复无需新增决策记录；重要设计变化才建立或更新记录。

## 记录方式

文件使用稳定的递增编号与英文主题：`NNN-topic.md`。记录背景、决策、依据与取舍、影响和验证入口，保持简短，不复制完整操作规范。
状态使用“已采纳 / 已替代 / 待验证”。已采纳表示设计已采用，不代表效果已充分验证。
决策替换时，旧记录标为已替代并链接新记录；未知效果归入 [验证缺口](../verification-gaps.md)。

## 决策

| 记录 | 状态 | 主题 |
|---|---|---|
| [ADR-001](001-optional-capabilities.md) | 已采纳 | 可选能力与降级 |
| [ADR-002](002-derived-style-router.md) | 已采纳 | 风格数据与派生摘要 |
| [ADR-003](003-context-budget.md) | 已采纳 | 安装体积与上下文成本 |
| [ADR-004](004-layered-deck-validation.md) | 已采纳 | 分层质检与检测边界 |

## 历史条目迁移核对

下表仅记录本次整理结果，不继续作为追加日志维护。历史编号供 Git 内容比对；具体要求以链接的目标为准。
未找到专项回归断言的内容保留为验证缺口，不以实现存在替代覆盖证明。

| 历史编号 | 处理结果与依据 |
|---|---|
| L-01 | 提示词效果归入 [V-01](../verification-gaps.md#v-01-提示词约束与视觉多样性)，操作指南保持现状 |
| L-02 | 提示词约束由 [工程规范](../engineering.md#2-风格系统约定) 与 [一致性规则](../../tools/consistency-rules.json) 维护；规则覆盖范围见 V-01 |
| L-03 | 分辨率分别由 [配图指南](../../skills/subaru-slides/references/illustrations.md) 和 [Path C](../../skills/subaru-slides/references/paths/path-c-html.md) 维护；一致性规则只扫描匹配的声明，非通用分辨率验证 |
| L-04 | 合并到 ADR-002；注册表与摘要各自职责明确 |
| L-05 | 图表路径识别保留于 [inspector](../../tools/pptx_inspect.py)，专项回归缺口列入 V-03 |
| L-06 | Baseline 更新保留于 [公共实现](../../tools/_common.py)，维护要求见 [Harness](../harness.md#3-baseline-机制)，专项回归缺口列入 V-04 |
| L-07 | 合并到 ADR-001；执行约束由依赖策略维护 |
| L-08 | 生成物约束由 [开发入口](../../AGENTS.md#6-git-与提交范围)、[忽略配置](../../.gitignore) 和 [资产校验](../../tools/check_assets.py) 维护；资产校验范围为 skill 包，不是全库垃圾扫描 |
| L-09 | 操作规范保留于 Path C；设计边界见 ADR-004，保真缺口列入 V-05 |
| L-10 | 操作规范保留于 [字体规范](../../skills/subaru-slides/references/typography-cjk.md)，跨机验证列入 V-05 |
| L-11 | 合并到 ADR-003，区分安装成本与实际读取成本 |
| L-12 | 命名规则保留于风格校验器；`TestStyleSystem` 已有样例命名与映射断言，见 ADR-002 |
| L-13 | `TestSemanticQualityGuards` 已有损坏标记与样例路径负向 fixture；相关实现保留，不重复维护缺陷叙述 |
| L-14 | 目标场景验收方案保留于 [专项方案](../slides-focus-proposal.md)，验证状态列入 V-02 |
| L-15 | 合并到 ADR-002，历史成本测量不作为当前结果使用 |
| L-16 | 合并到 ADR-003，当前预算由实现维护 |
| L-17 | 合并到 ADR-004，像素检测验证缺口列入 V-06；操作规则保持在 skill 内 |
| L-18 | 协作判断与任务规模由 [开发入口](../../AGENTS.md) 和 [DoD](../definition-of-done.md) 维护，无需独立决策重复正文 |
