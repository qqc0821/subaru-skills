# ADR-001：外部能力可选，按探测结果选择执行路径

状态：已采纳。记录日期：2026-10-06（整理现有设计，非本次新增运行时行为）。

## 背景

Skill 会安装在不同宿主中。原生构建、图片生成、HTML 转换与渲染能力各自可能缺失，将具体外部 skill 设为必需会限制独立安装。

## 决策

通过能力探测选择可用路径，外部工具作为增强；能力不足时按已有降级策略交付，并声明结果边界。
执行顺序与能力矩阵只在 [依赖策略](../../skills/subaru-slides/references/dependencies.md) 维护。

## 依据与取舍

探测与降级增加路径分支，但可避免将单个宿主环境假定为用户环境。
兜底产物不能自动继承原生可编辑交付的承诺。

## 影响

涉及 [能力探测](../../skills/subaru-slides/scripts/detect_capabilities.py)、入口路由和独立安装边界。

## 验证

[Harness 测试](../../tests/test_harness.py) 的 `TestPathRouting` 检查能力选择顺序，`TestInstalledPackageIsStandalone` 从隔离副本执行探测，`TestInstallabilityBoundary` 检查包内仓库专有引用。
这些断言不证明所有外部构建器均能端到端执行；实际产物仍需对应路径的验收。
