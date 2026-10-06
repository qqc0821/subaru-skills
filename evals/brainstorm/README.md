# Brainstorm 对话评测

这里评测实际对话行为，独立于现有 PPTX/HTML 产物评测。
输入是 [cases](cases/) 中的固定用户消息，语义判断遵循 [rubric](rubric.md)。
检查器不调用模型、不联网、不生成评测证据；无新增第三方依赖。

## 运行

1. 使用同一宿主和模型，逐条发送案例中的 `turns`，完整记录助手回复。
2. baseline 只使用普通头脑风暴提示词；skill 使用相同基础提示词并加载当前 skill。
3. 固定可控制的参数和工具能力，采用相近输出预算，每例每组运行三次，不挑选最好的一次。
4. 审阅完整对话，按案例 criteria 记录判断、理由和助手原文证据。
5. 将每次真实运行保存为 `evals/results/brainstorm/runs/<case>.<arm>.<repeat>.json`。
6. 执行 `make eval-brainstorm`，报告在 `evals/results/brainstorm/latest.json`。

每个组开始一个新会话，多轮 case 内保持上下文；不同 case 之间不共享会话。
保存实际基础提示词、工具提供方式与执行条件。不得用手写示范回复替代真实模型输出。
代码单元测试中的 synthetic fixture 只验证检查器，不参与对话质量评测。

获取当前运行规则指纹：

```sh
python3 tools/check_brainstorm_evals.py --fingerprint
```

记录契约示意（尖括号内容必须替换；下面不是已运行证据）：

```json
{
  "case": "execution-boundary",
  "arm": "skill",
  "repeat": 1,
  "status": "executed",
  "model": "<actual model/version>",
  "prompt_version": "<common prompt version and skill version>",
  "common_prompt": "<exact common prompt used by both arms>",
  "generator": "<host or runner that actually generated the replies>",
  "parameters": {"max_output_tokens": 2048},
  "host_capabilities": [],
  "execution_path": "<same host conversation path for both arms>",
  "recorded_at": "<actual timestamp>",
  "skill_digest": "<fingerprint>",
  "transcript": [
    {"role": "user", "content": "<exact fixed user turn>"},
    {"role": "assistant", "content": "<unaltered actual reply>"}
  ],
  "review": {
    "reviewer": "<reviewer identifier>",
    "kind": "human",
    "criteria": {
      "scope": {
        "passed": true,
        "reason": "<semantic reasoning based on this reply>",
        "evidence": [{"turn": 1, "quote": "<literal assistant excerpt>"}]
      }
    }
  }
}
```

`arm` 是 baseline 或 skill，repeat 从 1 开始；证据 turn 是 transcript 中从 0 开始的消息索引。
每项 criterion 都需 boolean、理由和真实引用；不存在的行为可引用整段相关回复并解释缺失。
review kind 可为 human / model / self；自评必须明示，不能当作独立验证。
模型不能设置的参数注明实际默认或 unavailable，不捏造 temperature/seed。
`parameters`、`model`、`common_prompt`、`host_capabilities`、`execution_path` 在同一配对中必须一致。
指纹绑定 SKILL.md 与 references；运行规则改变后旧结果不能通过当前质量门。

无法执行时保存 `case`、`arm`、`repeat`、`status: "BLOCKED"` 和具体 `reason`。
缺记录为 SKIP；缺审阅或记录损坏为错误。两者及 BLOCKED 都不能形成通过。
baseline 的行为失败允许作为比较证据；skill 的行为失败会阻断质量门。
默认要求 cases 目录中的全部案例两组各三次，完整覆盖；`--repeats 1` 仅供小规模试跑，不能声明默认闸门通过。

建议类案例同时覆盖仍有纠结、明确只要结论和收到建议后重新探索，防止修复过早收敛却变成强制提问。
案例使用泛化情境，不将个人会话原文或身份细节提交到仓库。

检查器能核对证据是否引用真实记录，但不能判断审阅是否准确，也不能证明记录未被人为伪造。
覆盖率通过不等于创造力提升或统计显著优势。当前证据状态见 [验证缺口](../../docs/verification-gaps.md#v-07-brainstorm-行为与对照效果)。
