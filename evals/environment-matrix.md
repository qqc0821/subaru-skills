# subaru-slides 环境可执行矩阵

快照时间：2026-09-11T16:59:30Z
基线提交：`788b450abb8fab0778adc5d0cf4eac90bcf89cdb`
工作区：有未提交改动。建议在继续生成评测产物前，由维护者审阅并提交当前改动作为基线；本次任务不代为提交。
复验：2026-09-12T03:12:42Z @ `8a98150534e14359b33f4272d9db6c1cc573344d`，修正渲染器探测（见下）。

## 证据命令

```bash
git rev-parse HEAD
python3 tools/doctor.py --json
python3 skills/subaru-slides/scripts/detect_capabilities.py --json
make check
make test
make eval
```

> GNU Make 不支持 `make doctor --json` 这种参数转发写法，因此 JSON 证据使用上面的等价脚本命令。

原始 JSON 快照保存在 gitignored 的 `evals/results/baseline/20260911T165930Z/`；可提交的 `environment.json` 只保留能力状态与理由，避免把用户主目录写入仓库。

## 覆盖维度

| 维度 | 判定方式 | 当前环境 | 证据 |
|---|---|---|---|
| 触发与路由 | 自动 | 可执行 | frontmatter 触发词静态断言 + A/C/B/fallback 路径决策表单测 |
| 执行与降级 | 自动/半自动 | A、B' BLOCKED；B、C、fallback 可执行 | 能力矩阵 + 固定 brief + 同名 `.run.json` |
| 产物结构 | 自动 | 可执行 | `pptx_inspect`、`validate_pptx`、`html_deck_inspect` 与 `expect.json` |
| 渲染与可读性 | 自动渲染 + 人工逐页 | 本机可执行；干净检出 BLOCKED | soffice/pdftoppm 渲染、浏览器翻页/控制台检查、逐页视觉复核 |

## 路径矩阵

| 路径 | 主要要求 | 状态 | 当前证据 | Claim boundary |
|---|---|---|---|---|
| A 原生可编辑 | artifact-tool 或系统 python-pptx | **BLOCKED** | 两者均未检测到 | 未验证原生可编辑构建 |
| B' / B2 混合 | 图片生成 + 原生构建器 | **BLOCKED** | 图片生成可用；原生构建器缺失 | 未验证 AI 底图与原生文字组合 |
| C HTML deck | deck-stage；导出 PPTX 另需 html2pptx | **RUNNABLE** | deck-stage 可用 | 只能验证 HTML；PPTX 导出仍 BLOCKED |
| B 全 AI 视觉 | 图片生成 | **RUNNABLE** | 宿主图片生成能力可用；固定输入装配案例已执行 | 文本不可编辑；固定案例不声明本轮图片模型质量 |
| fallback 图片 PPTX | uv + 内置 create_slides.py | **RUNNABLE** | 两者可用，依赖由 PEP 723 声明 | 只能生成图片型 PPTX |
| PPTX 视觉 QA | soffice + pdftoppm | **RUNNABLE** | 两者均检测到 | 不包含 Chrome 浏览器渲染 |

## 渲染探测（复验修正）

- 之前 `visual_qa=RUNNABLE` 只在 PATH 恰好包含运行时的 `bin/override` 目录时成立；默认 PATH 下 `make doctor` 与 `detect_capabilities.py` 会漏报 soffice/pdftoppm。
- 现由 `tools/renderer_locate.py` 统一探测，顺序：`SOFFICE_BIN` / `PDFTOPPM_BIN` 环境覆盖 → PATH → 常见绝对路径 → 运行时 glob `$HOME/.cache/codex-runtimes/*/dependencies/bin/override/{soffice,pdftoppm}`。
- `tools/doctor.py`、`tools/render_preview.py`、`skills/subaru-slides/scripts/detect_capabilities.py` 全部复用它；home 目录在运行时解析，不写死用户名。
- 复验：`make doctor` 显示 soffice/pdftoppm OK；`make render PPTX=evals/artifacts/fallback-image-pptx.pptx` 产出 3 PNG。

## 基线结论

- `make check`：PASS。
- `make test`：PASS（8 tests）。
- `make eval`：`0 validated / 3 skipped` 且退出码为 0，确认为零覆盖假绿灯。
- 当前案例中：`cn-industry-analysis`（A）和 `hybrid`（B2）应报告 BLOCKED；`full-ai-visual`（B）可执行但尚无产物，应报告 SKIP，并由覆盖率闸门阻断。

## 当前闭环结论

- 本机目标：至少 3 PASS、0 FAIL、0 SKIP；A/B' 允许 BLOCKED，但必须有非空理由。
- 已执行：fallback、固定输入 B、HTML C；A 与 B' 不以“未测”冒充通过。
- C 已在真实浏览器中验证 `#1 -> #2 -> #3`，控制台 0 warning / 0 error；首次复核发现浅底白字问题，修复后计算样式为 `rgb(21, 32, 43)` 并再次逐页检查。
- fallback 与固定输入 B 均已通过 PPTX 结构校验和本机渲染；AI 图片模型的实时生成质量不在固定输入案例的声明范围内。
- 暂不新增通用 Path A 构建器：`python-pptx` 依赖可由 uv 临时解析，但仓库尚无 Path A 内容 schema、布局器与原生对象生成契约；仅安装包不能把图片装配 helper 变成可维护的原生构建路径。A/B' 保持 BLOCKED，后续应作为独立能力建设任务。

## 干净检出矩阵

`make eval-clean` 在干净检出上重建固定输入 B/fallback 两个 gitignored 产物，闸门要求至少 2 PASS、0 FAIL、0 SKIP。A、B'、C 和视觉 QA 按 `environment-clean.json` 明确 BLOCKED；它因此只声明确定性装配与结构回归，不声明外部运行时、实时图片生成或渲染质量。仓库不附带 CI workflow，该闸门由本地、Agent 或自建 CI 显式调用。

## 已确认问题与最小复现

| 分级 | 问题 | 最小复现 | 关键证据片段 | 处理 |
|---|---|---|---|---|
| P0 | 零产物/零案例仍返回成功 | 删除/移开 `evals/artifacts/*` 后运行 `make eval`；或对空 `--evals-dir` 运行评测器 | `0 validated / 3 skipped`, exit 0；空 case 目录也曾 exit 0 | 改为策略化覆盖率闸门；无 case、0 PASS 或 runnable SKIP 均为非 0 |
| P0 | fallback 无法装配 WebP | 执行 `fallback-image-pptx/brief.md` 中命令 | `ValueError: unsupported image format ... got 'WEBP'` | 插入 PPTX 前在内存中转为 PNG |
| P1 | fullscreen 图片对象越界 | `make validate PPTX=evals/artifacts/fallback-image-pptx.pptx` | 3 个 out-of-bounds error，每页 1 个 | 改为画布内对象 + OOXML crop；复验 0 error/0 warning |
| P1 | 路由实现与 A→B' 顺序冲突 | `python3 -m unittest tests.test_harness.TestPathRouting -v` | native + image 曾返回 B2 | 原生能力优先返回 A，合成决策表单测锁定 |
| P1 | Path C 浅底白字 | `python3 -m http.server 4312 --directory evals/artifacts` 后打开 `html-deck.html#1` | 修复前标题继承白色；截图不可清晰辨读 | 显式声明 ink 色；inspector 新增规则，浏览器复验 0 console issue |
| P1 | 渲染器探测漏报 | `make doctor` / `python3 tools/render_preview.py --check` | `soffice: not found`；override 目录内二进制实际可执行 | 新增 `tools/renderer_locate.py` 运行时探测并接入三处；`make render` 复验 3 PNG |
