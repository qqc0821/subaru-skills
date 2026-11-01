# subaru-performance

把真实的网页性能录制变成简洁、可点击的主线程报告：查看文件执行、长任务、资源请求时间与 LCP。

> 用 $subaru-performance 采集这个网址，展示哪些脚本占用主线程，以及它们与 LCP 的关系。

也可以提供 Chrome 导出的未压缩录制 JSON，完全离线生成报告。文件排名是记录到的执行关联，不是对网站慢的全部根因证明。报告不含 iframe 和 Worker 执行。

使用 Python 3.10+，在线采集可选 ego-browser；缺少浏览器工具时可分析已有文件。生成的 HTML 无外部依赖。
