# 发布与发现维护

[返回首页](../README.md) · [站点源码](../site/README.md) · [发布许可记录](../PROVENANCE.md)

## 当前可审阅结果

- README 首屏提供实际案例、单 skill 安装与第一次调用。
- 两份原创 PPTX 和一份创意探索产物附输入、预览与验证边界。
- 静态文档站有中英文对应页面、canonical、语言链接、分享元信息和 sitemap。
- 生成站点不打包 skill 或第三方来源资产；没有添加分析追踪、外部字体或联网构建依赖。
- 尚未修改远端 About / Topics、提交推送、部署 Pages、创建 Release 或向其他社区发消息。

## GitHub Pages 上线顺序

1. 审阅本轮 diff 与 [Definition of Done](definition-of-done.md)，通过 `make check` / `make test`。
2. 按用户明确授权提交并推送；在默认分支合入 Pages 工作流和站点源码。
3. 仓库 Settings → Pages → Build and deployment，将 Source 设为 GitHub Actions。
4. Actions → Publish documentation → Run workflow，选择默认分支。
5. 确认 build / deploy 成功，再打开实际 page_url，检查首页、中英文切换、安装指南和三个案例下载。
6. 核对部署地址与 `site/config.json` 相同；不同则改配置后重建。上线后再在 README 和 About 添加实际网站链接，不预先把规划地址当成已上线结果。
7. 如维护者控制该站点，按搜索引擎要求验证站点并提交 sitemap。收录与 AI 引用都不保证。

工作流采用 [GitHub 官方自定义 Pages 部署方式](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)，本地检查不能替代远端部署执行。

## About 与 Topics 的建议值

这是待应用的元数据，未修改远端。

Description：`Chinese-first agent skills for editable presentations and brainstorming, with inspectable examples.`

Topics：`agent-skills`、`presentation`、`pptx`、`powerpoint`、`brainstorming`、`chinese`。宿主标签只在该宿主安装、加载与一次完整产出经过验证后添加。GitHub Topics 支持按主题发现仓库，不承诺排名：[官方文档](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)。

## 稳定发布准备

当前不改包版本或创建 tag。2026-10-07 远端只读 tag 核查为空。

- slides：先确认上游文档与风格样例的再分发授权。不得把根 MIT 解释成第三方授权；替换或移除前需审查 preset / index / router / 样例映射，避免破坏独立安装。
- brainstorm：原创许可边界清楚，但目标宿主的临时目录安装、重新加载与更新验证仍待完成；行为效果评测仍没有配对真实证据。可以声明“开发预发布”，不能宣称效果评测通过。
- 发布说明应列出各 skill 版本、变更、实际验证与未完成项。创建不可变 tag 后才提供真实固定 tag 安装命令；详见 [版本渠道决策](decisions/009-skill-version-channels.md)。

## 案例传播材料

先使用一篇完整案例介绍获取真实反馈，附输入、产物与安装入口：

- 中文管理层汇报：怎样用原生图表与表格呈现一个两周试点？
- 无生图技术分享：怎样把 RAG 资料入库与在线回答分开讲清楚？
- 创意探索：怎样从八个不同机制走向一个可执行的小实验？

这三项是可用选题，不是已发布文章。向相关社区、教程作者或资源目录提交时遵循其收录要求；未经用户明确授权不发送消息。

## 衡量

先记录时间与基线，再观察真实安装失败、第一次产出完成、重复使用与贡献。GitHub 访问统计需要维护者权限；Star 不等于实际使用。skills.sh FAQ 说明其通过 skills CLI 安装遥测收录并统计安装，项目当前收录状态未验证：[Skills FAQ](https://www.skills.sh/docs/faq)。不通过重复自安装制造增长。

固定搜索问题，例如“中文可编辑 PPT skill”“AI 头脑风暴 点子重复”“agent skill editable pptx”，记录平台、查询、日期、会话条件、是否出现项目以及介绍是否准确。一次推荐不代表稳定排名。

Google 的 AI 搜索文档要求沿用基础 SEO，重要信息有可抓取文字和清晰内部链接，没有必需的 AI 文本文件；这不是其他搜索产品的统一保证：[Google 官方说明](https://developers.google.com/search/docs/appearance/ai-features)。本轮不新增 llms.txt 或 SEO 效果承诺。
