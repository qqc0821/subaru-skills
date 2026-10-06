# Public documentation site

中英文问题指南、安装步骤、三个原创案例、许可与发布状态。源码为 `content.json`、`style.css` 与 `app.js`；构建器使用 Python 3.10+ 标准库，不联网、不引入前端依赖。版本从各 skill 的 `SKILL.md` 读取。

## 本地查看

在仓库根目录执行：

~~~bash
make site
python3 -m http.server 8000 --directory output/site
~~~

浏览器打开 `http://localhost:8000/`。构建输出在已忽略的 `output/site/`，不提交。案例成品与预览是有意维护的公开资产，位于 [examples](../examples/README.md)，每个文件小于 1MB；原始渲染留在忽略目录。

## 部署

[Pages 工作流](../.github/workflows/pages.yml)只允许手动触发，上传生成的网站，不上传仓库或 skill 包。GitHub Pages 配置为 GitHub Actions 后，在默认分支运行工作流。操作顺序与上线后的检查见 [发布与发现维护](../docs/discovery.md)。准备了工作流不等于部署成功。

`config.json` 中的站点地址是预定 GitHub Pages 地址。域名改变时更新配置，或使用 `python3 tools/build_site.py --base-url https://example.com/` 重建 canonical、语言链接、分享元信息与 sitemap。仓库子路径下的 robots.txt 不能控制宿主根目录的抓取策略，因此不生成误导性的 robots.txt。

## 验证

`make check-site` 临时构建并检查站内链接、锚点、语言、标题、描述、canonical、sitemap、图片替代文本、下载 hash 和大小预算。`make test` 包含构建器的负向回归。外部链接可达性、搜索收录、AI 引用和远端 Actions 执行不由本地检查证明。
