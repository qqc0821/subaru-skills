# Eval Harness

固定 brief + 结构断言的回归基准，用于在修改 skill 后确认没有"改 A 坏 B"。

## 结构

```
evals/
├── cases/<id>/brief.md      # 输入 brief
├── cases/<id>/expect.json   # 结构断言
├── artifacts/<id>.pptx      # 生成物（gitignored）
└── results/latest.json      # 最近一次结果（gitignored）
```

## 用法

1. 按 `cases/<id>/brief.md` 生成一个 deck，另存为 `evals/artifacts/<id>.pptx`。
2. 运行 `make eval`（等价于 `python3 tools/run_evals.py`）。
3. 没有产物的 case 会被 SKIP，不会失败；有产物的 case 按 `expect.json` 断言逐项判定。
4. 直接校验某个文件：`python3 tools/run_evals.py --case cn-industry-analysis --pptx path/to/deck.pptx`。
5. 与上次结果对比：`python3 tools/run_evals.py --compare`。

## 断言键

以 `_min` / `_max` 结尾，前缀是 `tools/pptx_inspect.py` 输出的指标名：
`slide_count`、`chart_count`、`table_count`、`image_count`、`text_chars`、`cjk_chars`、`font_families`、`placeholders`、`notes_slide_count`。

## 当前基准

- `cn-industry-analysis` — Path A，中文行业分析，原生图表。
- `full-ai-visual` — Path B，全 AI 视觉页，每页全屏图。
- `hybrid` — Path B'，AI 底图 + 原生可编辑文字。
