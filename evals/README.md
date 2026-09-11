# Eval Harness

固定 brief + 结构断言的回归基准，用于在修改 skill 后确认没有"改 A 坏 B"。

## 结构

```
evals/
├── cases/<id>/brief.md      # 输入 brief
├── cases/<id>/expect.json   # 结构断言
├── artifacts/<id>.pptx      # 生成物（gitignored）
├── results/latest.json      # 最近一次结果（gitignored）
└── results/runs/*.json      # 时间戳化运行 ledger（gitignored）
```

## 用法

1. 按 `cases/<id>/brief.md` 生成一个 deck，另存为 `evals/artifacts/<id>.pptx`。
2. 运行 `make eval`（等价于 `python3 tools/run_evals.py`）。
3. 没有产物的 case 根据 `environment.json` 分为 SKIP 或 BLOCKED；状态本身不直接决定退出码，最终由 `policy.json` 的覆盖率闸门决定。
4. 直接校验某个文件：`python3 tools/run_evals.py --case cn-industry-analysis --pptx path/to/deck.pptx`。
5. 与上次结果对比：`python3 tools/run_evals.py --compare`。
6. 干净检出的 CI 运行 `make eval-ci`：先在隔离的 gitignored 目录重建两个仓库固定输入案例，再使用 `policy-ci.json` 与 `environment-ci.json` 判定，避免本机残留产物扩大 CI 声明范围。

## 状态与覆盖率闸门

- `PASS`：案例已执行且全部断言通过。
- `FAIL`：案例已执行但至少一项断言失败。
- `SKIP`：路径可执行，但当前没有评测产物。
- `BLOCKED`：环境不具备路径能力，且必须记录非空原因。

`policy.json` 当前要求至少 3 个 PASS、0 个 FAIL、0 个 SKIP；BLOCKED 可以存在，但必须有明确原因。每个已执行案例还必须在同名 `.run.json` 中记录 `model`、`prompt_version`、`parameters` 与 `execution_path`。这样环境阻塞不会被误算为产品失败，未执行或缺少运行上下文的案例也不会形成绿灯。

当前环境证据与 claim boundary 见 `environment-matrix.md`；供工具读取的对应状态在 `environment.json`。

CI 通过 `astral-sh/setup-uv` 提供 `uv`，仅用于解析 `create_slides.py` 已声明的 PEP 723 依赖并重建 gitignored 产物。CI 不安装 deck-stage、html2pptx、图片生成服务或 Office 渲染器，因此只要求固定输入的 B/fallback 两例 PASS，其余路径必须按 `environment-ci.json` 明确报告 BLOCKED；这不是对相应能力的通过声明。

## 断言键

断言支持 `_min`、`_max`、`_eq` 与 `_in`。可用指标包括：
`slide_count`、`chart_count`、`table_count`、`image_count`、`picture_shape_count`、`text_shape_count`、`graphic_frame_count`、`native_editable_object_count`、`text_chars`、`cjk_chars`、`font_families`、`placeholders`、`notes_slide_count`、`validation_error_count`、`validation_warning_count`、HTML stage/label/script/wrapper/显式文字颜色指标与 `execution_path`。

每个评测产物可带同名运行元数据，例如 `fallback-image-pptx.run.json`。每次运行除覆盖 `results/latest.json` 外，还会写入不可变的 `results/runs/<timestamp>.json` ledger，便于比较多轮结果与模型/提示词/参数。

## 当前基准

- `cn-industry-analysis` — Path A，中文行业分析，原生图表。
- `full-ai-visual` — Path B，全 AI 视觉页，每页全屏图。
- `hybrid` — Path B'，AI 底图 + 原生可编辑文字。
- `fallback-image-pptx` — 内置 helper 的三页图片型 PPTX，验证最低兜底链路。
- `html-deck` — Path C 的三页 deck-stage HTML，验证结构与浏览器运行。
