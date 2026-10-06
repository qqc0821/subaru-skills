# ADR-009：独立包版本与发布渠道

状态：已采纳。

## 背景与决策

skill 可单独复制与安装，根 VERSION 无法识别包版本。各包使用 `SKILL.md` 的 `metadata.version` 作为独立 SemVer 来源，由 schema 与 `validate_skills` 验证；README 引导读取该字段，避免复制当前版本号。

仓库版本记录发布批次；Git tag 固定整仓快照，各包版本可不同。默认安装跟随 main，稳定安装固定实际发布 tag，并以显式换 tag 重新安装升级。未发布开发内容使用预发布版本，精确修订依赖 commit 或 CLI 内容记录，包版本本身不承担自动更新检测。

## 依据、影响与验证

2026-10-06 通过 GitHub Releases API 与 `git ls-remote --tags origin` 核实远端均为空，默认分支 main。历史 0.1.0 是仓库记录，不能提供虚构的稳定安装命令。当前仅提供 Release 查询入口和固定 tag 模板；实际发布须另获授权。

不新增联网自更新脚本或运行时依赖；CLI 安装由其更新命令管理，手动复制由用户完整替换。验证入口为 `make check`、`make test` 与 `tests/test_skill_versions.py`。外部安装端到端边界见 [验证缺口](../verification-gaps.md#v-08-skill-安装与更新渠道)。
