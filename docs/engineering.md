# Skill 包工程规范

修改包结构、脚本、元数据或风格时按需阅读。协作流程与验证要求见 [开发入口](../AGENTS.md)。

## 1. Skill 包规范

### 1.1 目录结构

```
skills/<name>/
├── SKILL.md               # 薄入口（Agent 视角）：路由 + 铁律 + 流程 + 检查点（≤200 行）
├── README.md / .en.md     # 使用者视角：能力、调用方式、编辑性边界（中文优先 + 英文镜像）
├── agents/openai.yaml     # UI 元数据（见 1.5）
├── references/            # 按需加载的长文（设计原则、路径细节、QA 清单…）
├── scripts/               # 可执行辅助脚本（见 1.4）
├── assets/                # 样例图等静态资产（见 1.6）
└── styles/                # （可选）机读风格系统（见第 2 节）
```

文档分层：skill 的 `README` 只写"是什么 / 怎么用"，`SKILL.md` 是运行时规则的**唯一事实源**。
路径表、能力降级表、风格计数等只允许维护一处，其余文档引用它。skill 的 `README` 会随包发布，
因此不得引用仓库专有路径（`tools/`、`schemas/`、`AGENTS.md`、`make` 目标）。

### 1.2 `SKILL.md` frontmatter

```yaml
---
name: <skill-name>        # 必须与目录名完全一致，小写连字符
description: <一句话>      # 必须写清"当用户……时使用"，包含中英文触发词与同义词
---
```

### 1.3 行数与体积预算

- `SKILL.md` ≤ 200 行。
- 单个 reference 文件 ≤ 600 行；超出需拆分。
- 一个 skill 包总量 ≤ 5MB。

### 1.4 `scripts/`

- 优先 Python 3.10+，使用 **PEP 723 内联依赖**，用 `uv run` 可直接执行。
- 每个脚本必须有 `--help`、清晰的错误信息与明确的退出码。
- 依赖环境的脚本提供 `--doctor` 自检（缺什么、怎么装）。
- 不写死路径；默认不联网（除非用户明确要求）。

### 1.5 `agents/openai.yaml`

```yaml
interface:
  display_name: "<显示名>"
  short_description: "<一句话，说明能力>"
  brand_color: "#RRGGBB"
  default_prompt: "Use $<name> to <目标>. <关键约束>."
policy:
  allow_implicit_invocation: true
```

### 1.6 `assets/`

- 样例图使用 **WebP**；文档中声明的体积/尺寸必须与实际一致。
- 命名使用稳定的风格 id（英文小写连字符），不要用中文或空格。

---

## 2. 风格系统约定

- 若 skill 提供多风格，`styles/index.json` 是**风格数量、命名、主题推荐、样例映射的唯一事实源**。
- `SKILL.md`、gallery 文档、样例目录**不得各自维护**一份可能漂移的计数；只引用 index。
- 每个风格一个 `styles/<id>.md` preset（字段定义见 [style.preset.schema.json](../schemas/style.preset.schema.json)）。
- 风格 base prompt 保持**简短**（≤5 行），描述情绪与世界观；不微操构图、不写 NOT 约束。

## 3. 机读契约

- [Skill frontmatter](../schemas/skill.frontmatter.schema.json)
- [OpenAI agent 元数据](../schemas/openai-agent.schema.json)
- [风格注册表](../schemas/styles.index.schema.json)
- [风格 preset](../schemas/style.preset.schema.json)
- [设计基础](../schemas/design.foundation.schema.json)

修改契约时同步检查校验器与相关测试。
