# ADR-002：风格注册表派生选型摘要

状态：已采纳。记录日期：2026-10-06（整理现有设计）。

## 背景

校验器需要完整风格元数据，运行时选型只需要主题、正式程度和执行路径等摘要。各文档独立维护数量、名称和样例映射容易漂移。

## 决策

以注册表维护完整数据，由生成器派生选型摘要，运行时读取摘要与选中的一个 preset。
具体数据归属、命名和更新要求见 [风格系统规范](../engineering.md#2-风格系统约定) 与 [skill 入口](../../skills/subaru-slides/SKILL.md)。

## 依据与取舍

相比直接读取全部注册表，摘要减少不参与选型的上下文；相比手写摘要，生成和一致性检查避免引入第二份人工维护的数据。
代价是修改注册表后必须重新生成摘要；摘要只支持选型，不能替代完整契约校验。

## 影响

涉及 [生成器](../../tools/gen_style_router.py)、[风格系统校验](../../tools/check_style_system.py)、注册表、preset 与样例。
展示名称与机器标识分离，样例路径契约由校验器维护。

## 验证

[Harness 测试](../../tests/test_harness.py) 的 `TestStyleRouter` 检查摘要同步、风格覆盖和单 preset 读取约定；`TestStyleSystem` 检查样例命名与 preset 映射；`TestSemanticQualityGuards` 包含非规范样例路径的负向 fixture。
风格登记与样例存在不证明成品质量，相关缺口见 [验证缺口](../verification-gaps.md#v-02-目标场景的内容与视觉质量)。
