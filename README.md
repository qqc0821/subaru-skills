# subaru-skills

中文优先的 [Agent Skills](https://agentskills.io/) 仓库，当前提供演示文稿制作能力。

[English](README.en.md) · [变更记录](CHANGELOG.md) · [来源与许可](PROVENANCE.md)

## 包含的 skill

| Skill | 能力 | 文档 |
|---|---|---|
| `subaru-slides` | 从主题、资料或已有文档到可编辑 PPTX / HTML deck：内容结构化、风格选择、构建与交付质检 | [使用说明](skills/subaru-slides/README.md) · [SKILL.md](skills/subaru-slides/SKILL.md) |

使用 [skills CLI](https://github.com/vercel-labs/skills) 安装：

~~~bash
npx skills add qqc0821/subaru-skills                          # 装到当前项目
npx skills add qqc0821/subaru-skills --global                 # 装到用户级 skill 目录
npx skills add qqc0821/subaru-skills --skill subaru-slides    # 只装 subaru-slides
~~~

装好后直接交给宿主 Agent，例如：`用 $subaru-slides 把这份市场分析做成 10 页管理层汇报 PPT。`

不用 CLI 时，把 `skills/<name>/` 复制到宿主的 skill 目录即可。

## 仓库结构

- `skills/<name>/` —— 可独立安装的 skill 包，装哪个就只用哪个；
- `schemas/`、`tools/`、`tests/`、`evals/`、`docs/` —— 开发与回归 Harness，不随 skill 安装，详见 [AGENTS.md](AGENTS.md)。

## 开发与质量门

~~~bash
make check      # 链接 / 一致性 / 资产 / 风格系统 / 可安装性（唯一必过门）
make test       # 工具 smoke test 与单元测试
make doctor     # 当前机器能力自检

make validate PPTX=deck.pptx
make render   PPTX=deck.pptx OUT=preview/
make pixel-qa DIR=preview/            # 渲染图像素缺陷：换行孤字、超大字号、色带切割
make montage  DIR=preview/ OUT=montage.webp
~~~

## 许可

仓库原创内容采用 [MIT License](LICENSE)。`skills/subaru-slides` 派生自 `huashu-slides`（上游审计基线无根 LICENSE），再分发前请阅读 [PROVENANCE.md](PROVENANCE.md)。
