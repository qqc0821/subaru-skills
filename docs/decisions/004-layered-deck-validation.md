# ADR-004：结构、像素与人工检查分层验收

状态：已采纳。记录日期：2026-10-06（整理现有设计；检测有效性仍有验证缺口）。

## 背景

PPTX XML 可以验证对象和几何属性，但无法完整表达字体实际呈现、文字折行和画面语义。渲染 PNG 也不能可靠还原对象层级或设计意图。

## 决策

分别使用结构校验、渲染图检测与逐页人工检查；交付声明覆盖范围。
检测类别、阈值和操作要求由 [像素 QA reference](../../skills/subaru-slides/references/qa/pixel-artifacts.md) 与 [检测脚本](../../skills/subaru-slides/scripts/detect_pixel_artifacts.py) 维护。

## 依据与取舍

分层检查覆盖不同缺陷，增加渲染和复核成本。结构通过不能替代视觉验证，像素候选不能直接等同于缺陷。
仅凭最终图像难以区分连线正常终止与被遮挡，因此对象关系由生成侧布局规则与人工检查验证；不以缺乏可区分信号的检测扩大自动化承诺。

## 影响

涉及 [结构校验器](../../tools/validate_pptx.py)、渲染流程、像素检测和交付说明。
HTML 导出的视觉保真与文字可编辑边界继续由 [Path C](../../skills/subaru-slides/references/paths/path-c-html.md) 维护；跨机字体由 [字体规范](../../skills/subaru-slides/references/typography-cjk.md) 维护。

## 验证

[Harness 测试](../../tests/test_harness.py) 的 `TestDeckTools` 覆盖部分字体元数据、字号与 HTML 结构规则。
现有代码和文档不能证明像素检测的误报率、跨渲染器保真或所有 CSS 转换效果；专项证据要求见 [验证缺口](../verification-gaps.md)。
