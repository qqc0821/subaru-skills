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
metadata:
  version: "0.1.0-dev.0"   # 每包必需，SemVer 字符串
---
```

版本的唯一来源是各包 `SKILL.md` 的 `metadata.version`，不在 README 重复维护当前版本号。各 skill 独立递增：修复升 patch、兼容能力新增升 minor、不兼容变更升 major；未发布内容使用预发布标记。开发版本发布前可继续修改，精确修订由 Git commit / CLI 内容记录识别。`validate_skills` 与 schema 检查存在性和 SemVer 格式。

仓库 `VERSION` 与根 CHANGELOG 记录仓库发布批次，不替代包版本。准备发布时在 CHANGELOG 记录各受影响 skill 与版本，更新包版本并通过质量门；经用户授权创建不可变 tag 和 GitHub Release 后，才将它称作稳定发布。一个仓库 tag 固定整仓快照，可以包含版本不同的 skill。默认分支安装跟随 `main`；稳定安装固定实际 tag，后续稳定升级通过指定新 tag 重新安装，不提供浮动 `latest` tag。

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
- 风格 base prompt 保持**简短**（≤5 行），描述整册视觉语言，不写逐页坐标或无关 NOT 约束。
  逐页资产简报可指定为内容准确性、留白、裁切与透明背景所需的主体、关系和构图条件；不把逐页要求复制进 preset。

## 3. 机读契约

- [Skill frontmatter](../schemas/skill.frontmatter.schema.json)
- [OpenAI agent 元数据](../schemas/openai-agent.schema.json)
- [风格注册表](../schemas/styles.index.schema.json)
- [风格 preset](../schemas/style.preset.schema.json)
- [设计基础](../schemas/design.foundation.schema.json)
- [字体配置](../schemas/typography.profiles.schema.json)：脚本字款与回退；字号仍由 foundation 维护

修改契约时同步检查校验器与相关测试。

## 4. 对话 skill 与上下文预算

`subaru-brainstorm` 基础运行仅需宿主对话能力；文件、搜索、图示等按任务探测并降级。
当前不引入运行时脚本或第三方依赖，能力及会话协议在其 `SKILL.md` 与 references 维护。

每个 skill 的典型读取路径和预算声明在 `tools/context-budgets.json`，由
`check_context_budget.py` 在统一质量门中检查。新增 skill 必须声明预算；
按需参考文件须在入口标明读取条件。slides 还保留其 preset、派生 router 的专项护栏。
计量是字符估算，不代表宿主实际 tokenizer 用量；不把包总量当作每次必读成本。

对话的行为效果使用真实 transcript 与语义审阅验证；包结构通过不代表创意效果通过。
评测工具仅用 Python 标准库，依赖及记录契约见 [对话评测](../evals/brainstorm/README.md)。
