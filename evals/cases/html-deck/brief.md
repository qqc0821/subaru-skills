# Eval: deck-stage HTML 演示

**id:** `html-deck`
**执行路径:** `C`

## Brief

制作三页 1920×1080 的静态 HTML 演示，用于说明 `subaru-slides` 的测试闭环。必须使用 `deck-stage.js`，每页是带唯一 `data-label` 的直接 `<section>`，正文保持静态可编辑，并包含 wrapper fill rule。

仓库中的 `fixture.html` 是固定回归源；本地执行时复制到 `evals/artifacts/html-deck.html`，并从运行时探测到的位置复制 `deck-stage.js`。不把运行时文件或生成物提交到仓库。

## 自动判定

- 一个 1920×1080 `deck-stage`。
- 三页以上、每页有唯一 label。
- 引用 `deck-stage.js`。
- wrapper fill rule 存在。
- 字体下限不少于 24px，无占位文字。

## Claim boundary

- 自动检查 HTML 结构、基础排版契约和运行元数据。
- 浏览器检查运行加载、键盘翻页、控制台错误和截图。
- 当前不验证 HTML→PPTX 导出，因为未检测到 html2pptx。
