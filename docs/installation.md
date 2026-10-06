# 安装、更新与版本

[返回首页](../README.md)

## 安装一个 skill

选一个包安装，再按宿主要求重新加载。使用 slides 前检查 [PROVENANCE](../PROVENANCE.md) 中的许可边界。

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-brainstorm
npx skills add qqc0821/subaru-skills --skill subaru-slides
~~~

包版本查看安装目录中 `SKILL.md` 的 `metadata.version`；它是该 skill 的版本来源。带 `-dev.N` 的版本是开发预发布版，同一开发版在正式发布前仍可能有内容变化；精确追踪需结合 CLI 安装来源记录或 Git commit。

不指定分支的安装命令获取仓库默认分支 `main` 的最新内容，可能包含尚未发布的修改；“默认分支最新版”不等于“最新稳定版”。

通过 [skills CLI](https://github.com/vercel-labs/skills#skills-update) 安装后，在原项目目录运行项目级更新，或使用 `-g` 更新全局安装：

~~~bash
npx skills update subaru-slides subaru-brainstorm -p
npx skills update subaru-slides subaru-brainstorm -g
~~~

更新依赖 CLI 保存的安装来源与内容记录，不按 `metadata.version` 自动选择最新稳定 Release。旧 CLI 不支持命令、或来源记录缺失时，使用原来的 `npx skills add` 命令重新安装，并选择相同宿主和项目级 / 全局范围（全局加 `--global`）。更新前备份自定义修改；更新后按宿主要求重新加载 skill 或开启新会话。

手动下载 ZIP / 复制目录的用户：重新下载所选分支或发布版本，备份旧目录，再用对应的 `skills/<name>/` 完整替换宿主中的 skill 目录，避免遗留新版已删除的文件。只对下载仓库执行 `git pull` 不会同步已复制的副本；手动复制也不保证能由 CLI 更新接管。

稳定版入口：[GitHub Releases](https://github.com/qqc0821/subaru-skills/releases)。2026-10-07 只读核查远端 tag 列表为空，当前没有可固定安装的稳定 tag；本次未创建 Release。后续以 Release 页面实际记录为准；历史 `0.1.0` 记录不代表已有稳定发布。

发布稳定版后，从 Release 页面选定实际存在且包含所需 skill 的 tag，再通过固定 tag 安装：

~~~bash
# 模板：把 <release-tag> 换成 Release 页面中实际存在的 tag
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>"
~~~

固定 tag 的安装用于保留该版本，不会自动切换到后续稳定 tag。升级稳定版时先阅读目标 Release 的变更说明，再将安装 URL 的 tag 换成新 tag 重新安装；想切回默认分支则使用不带 tag 的原安装命令。
