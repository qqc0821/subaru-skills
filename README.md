# subaru-skills

中文优先的 [Agent Skills](https://agentskills.io/) 仓库，提供演示文稿制作与头脑风暴能力。

[English](README.en.md) · [变更记录](CHANGELOG.md) · [来源与许可](PROVENANCE.md)

## 包含的 skill

| Skill | 能力 | 文档 |
|---|---|---|
| `subaru-slides` | 从主题、资料或已有文档到可编辑 PPTX / HTML deck：内容结构化、风格选择、构建与交付质检 | [使用说明](skills/subaru-slides/README.md) · [SKILL.md](skills/subaru-slides/SKILL.md) |
| `subaru-brainstorm` | 探索问题与创意、切换思考方式、保留分支，通过摘要续谈并整理成方案或实验 | [使用说明](skills/subaru-brainstorm/README.md) · [SKILL.md](skills/subaru-brainstorm/SKILL.md) |

使用 [skills CLI](https://github.com/vercel-labs/skills) 安装：

~~~bash
npx skills add qqc0821/subaru-skills                          # 装到当前项目
npx skills add qqc0821/subaru-skills --global                 # 装到用户级 skill 目录
npx skills add qqc0821/subaru-skills --skill subaru-slides    # 只装 subaru-slides
npx skills add qqc0821/subaru-skills --skill subaru-brainstorm # 只装 subaru-brainstorm
~~~

装好后直接交给宿主 Agent，例如：`用 $subaru-slides 把这份市场分析做成 10 页管理层汇报 PPT。`

不用 CLI 时，把 `skills/<name>/` 复制到宿主的 skill 目录即可。

## 版本、更新与稳定发布

包版本查看安装目录中 `SKILL.md` 的 `metadata.version`；它是该 skill 的版本来源。带 `-dev.N` 的版本是开发预发布版，同一开发版在正式发布前仍可能有内容变化；精确追踪需结合 CLI 安装来源记录或 Git commit。

不指定分支的安装命令获取仓库默认分支 `main` 的最新内容，可能包含尚未发布的修改；“默认分支最新版”不等于“最新稳定版”。

通过 [skills CLI](https://github.com/vercel-labs/skills#skills-update) 安装后，在原项目目录运行项目级更新，或使用 `-g` 更新全局安装：

~~~bash
npx skills update subaru-slides subaru-brainstorm -p
npx skills update subaru-slides subaru-brainstorm -g
~~~

更新依赖 CLI 保存的安装来源与内容记录，不按 `metadata.version` 自动选择最新稳定 Release。旧 CLI 不支持命令、或来源记录缺失时，使用原来的 `npx skills add` 命令重新安装，并选择相同宿主和项目级 / 全局范围（全局加 `--global`）。更新前备份自定义修改；更新后按宿主要求重新加载 skill 或开启新会话。

手动下载 ZIP / 复制目录的用户：重新下载所选分支或发布版本，备份旧目录，再用对应的 `skills/<name>/` 完整替换宿主中的 skill 目录，避免遗留新版已删除的文件。只对下载仓库执行 `git pull` 不会同步已复制的副本；手动复制也不保证能由 CLI 更新接管。

稳定版入口：[GitHub Releases](https://github.com/qqc0821/subaru-skills/releases)。截至 2026-10-06，远端尚无 Release 或 tag，当前没有可安装的稳定版；历史 `0.1.0` 记录不代表已有稳定发布。

发布稳定版后，从 Release 页面选定实际存在且包含所需 skill 的 tag，再通过固定 tag 安装：

~~~bash
# 模板：把 <release-tag> 换成 Release 页面中实际存在的 tag
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>"
~~~

固定 tag 的安装用于保留该版本，不会自动切换到后续稳定 tag。升级稳定版时先阅读目标 Release 的变更说明，再将安装 URL 的 tag 换成新 tag 重新安装；想切回默认分支则使用不带 tag 的原安装命令。

## 仓库结构

- `skills/<name>/` —— 可独立安装的 skill 包，装哪个就只用哪个；
- `schemas/`、`tools/`、`tests/`、`evals/`、`docs/` —— 开发与回归 Harness，不随 skill 安装，详见 [AGENTS.md](AGENTS.md)。

## 开发与质量门

~~~bash
make check      # 链接 / 一致性 / 资产 / 风格系统 / 可安装性（唯一必过门）
make test       # 工具 smoke test 与单元测试
make doctor     # 当前机器能力自检
make eval-brainstorm # 对话证据与语义审阅闸门；缺少真实运行记录不会通过

make validate PPTX=deck.pptx
make render   PPTX=deck.pptx OUT=preview/
make pixel-qa DIR=preview/            # 渲染图像素缺陷：换行孤字、超大字号、色带切割
make montage  DIR=preview/ OUT=montage.webp
~~~

## 许可

仓库原创内容采用 [MIT License](LICENSE)。`skills/subaru-slides` 派生自 `huashu-slides`（上游审计基线无根 LICENSE），再分发前请阅读 [PROVENANCE.md](PROVENANCE.md)。
