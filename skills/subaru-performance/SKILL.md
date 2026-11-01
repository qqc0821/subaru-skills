---
name: subaru-performance
description: 当用户要分析网页加载、LCP、主线程阻塞或把 Chrome Performance trace 做成简洁可交互报告时使用；支持 browser performance profiling、脚本文件归因和加载时间线。无需用于普通网页浏览或未涉及实测数据的通用前端优化。
metadata:
  version: "0.1.0-dev.0"
---

# 主线程性能透视

把实际录制转成「首屏判断 → Canvas 时间线 → 优先检查项 → 执行证据」报告。默认中文，删除导入导出等无关界面。不要沿用示例站点结论，也不要承诺自动识别所有阻塞根因。

## 输入与能力

- 用户给出 trace 文件：直接离线分析，Python 3.10+ 标准库即可。
- 用户给出 URL 并授权实测：探测 ego-browser；可用时读取其技能或运行 `ego-browser skill`，按当前文档创建一个任务空间并打开指定 URL。缺少该工具时使用已授权且支持 CDP tracing 的浏览器工具，或请用户提供录制文件，不自动安装或切换用户浏览器配置。
- 按需：开始新采集前，读取 [采集与计量边界](references/capture.md)。已有文件不需要重新访问站点。

## 采集

在已有任务空间的目标页面执行（所有路径用运行时实际路径）：

```bash
python3 <skill>/scripts/capture.py --space <id> --page p1 --seconds 25 --out <work>/capture
```

采集会重新加载当前页面，不导航到其他地址。先确认当前 URL 是用户指定的站点。Tracing start、reload、wait、end、读取 events 必须在同一 ego 调用内；跨调用的 CDP 会话不一定延续。不要同时运行第二份 tracing。

采集不清除缓存、不修改限速、不点击网页；保持页面前台。记录实际环境。工具报错或用户接管时停止并检查状态，不盲目重试。原始录制存入工作目录，不提交到 skill 包。

## 生成

```bash
python3 <skill>/scripts/analyze.py <work>/capture/trace.json --perf <work>/capture/perf.json --out <output>/index.html
```

已有 Chrome 未压缩 JSON 可省略 `--perf`。默认解析第一条可识别顶层导航；多导航用 `--navigation` 选择索引，核对输出 URL。仅使用同一次采集的 perf 快照。缺少 LCP 或请求关联时保留空缺，不猜测四段耗时。脚本拒绝无法识别导航或主线程任务的格式。

输出为离线单文件 HTML；可通过本地 HTTP 服务预览。已有页面修改时保留用户内容和版本，不覆盖无关文件。只创建本地文件；发布网站、提交仓库或发送录制不是本 skill 的默认动作。

## 归因原则

- 资源请求与脚本执行分开；下载慢不等于阻塞主线程。
- 任务超过 50 ms 标为长任务；超额占用只计每个任务超过 50 ms 的部分，不称为 Lighthouse TBT。
- 用事件区间切分消除嵌套重复。布局/样式仅关联到包围它的脚本调用；这不是自耗时或完整因果证明。
- 没有来源的工作保留为未归因，不强行分配到附近的文件。
- LCP 之后的任务不能解释已发生的 LCP 延迟；没有 LCP 时不判断先后。
- 当前报告聚焦顶层主线程，省略低于 1 ms 的外层任务；不声称覆盖 iframe、Worker 或所有浏览器工作。

## 验证与交付

核对归因总量不超过任务总时长、长任务计数、LCP 原始时间和报告 URL。默认聚焦 LCP 前；优先项按当前区间长任务与占用排序，不能沿用全程排名。预览并操作时间线缩放、横向拖动、任务选择、脚本联动、范围重置与 LCP 后活动；检查缺失 LCP 与空结果状态。只交付实际成功生成并检查过的报告，简述证据边界。截图或单次数据不足时，不把推测写成确定原因。
