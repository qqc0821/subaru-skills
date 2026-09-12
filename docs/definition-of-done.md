# Definition of Done

本文件把 `AGENTS.md` 的硬性规则整理成可勾选清单。
每个任务结束、每个 PR 提交前逐项确认。

## A. 通用（每个改动）
- [ ] `make check` 通过（无新增阻塞项）
- [ ] 变更范围单一，未夹带无关格式化
- [ ] 文档与实现一致（无"文档说 A、实现做 B"）
- [ ] 无 secrets、无 >1MB 二进制、无 `.DS_Store` 与临时产物
- [ ] 路径/重命名已同步修复所有相对链接（`check_links` 通过）
- [ ] 过程三件套（`task_plan.md` / `findings.md` / `progress.md`）**未入库**；可复用结论已写入 `docs/lessons-learned.md`

## B. skill 变更
- [ ] `SKILL.md` ≤ 200 行；长文在 `references/`
- [ ] frontmatter 的 name 与目录名一致；description 写清触发场景
- [ ] `agents/openai.yaml` 字段完整
- [ ] 无外部 skill 硬依赖；能力均有探测与降级路径
- [ ] 风格相关的计数/命名/推荐只引用 `styles/index.json`，不重复维护
- [ ] 新增依赖/资产已在文档说明必要性

## C. 交付质量（deck 产出，P1 起）
- [ ] 会被编辑的文字/表格/图表为原生对象
- [ ] 逐页渲染通过；`validate_pptx` 0 阻塞
- [ ] 无占位符残留；中文无乱码
- [ ] 交付附带 receipt 与 claim_boundary

## D. Harness 变更
- [ ] 新增检查有明确 check id 与退出码
- [ ] 需要接受的历史问题已通过 `make baseline` 记录，而非静默忽略
- [ ] CI 与本地使用同一入口（`make check`）
