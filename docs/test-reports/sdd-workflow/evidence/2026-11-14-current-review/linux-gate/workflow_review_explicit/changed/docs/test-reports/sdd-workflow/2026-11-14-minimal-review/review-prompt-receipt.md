# review-prompt 实际调用与回执

调用方：sdd-workflow-review（Main）；实际 API：`collaboration.spawn_agent`；`agent_type=review-prompt`；`task_name=prompt_review`；返回任务名 `/root/prompt_review`。注册入口与职责文件均已由调用方、角色读取，哈希见 E-01 与下方回执。未覆盖候选改写、真实助手模型行为或独立全能力测试。

## 传入工单（原文）

只读提示词专项工单（用户明确要求实际调用夹具注册 review-prompt）。项目 cwd=/tmp/sdd-review-execution-i6atigzg/workflow_review_explicit-wijovo5h/prepared/project，源 HEAD=20aa8f7fbf9ec965b09c89aeffa5fdc81928e3bc，初始 git status clean。请先读取 .codex/config.toml 与 .codex/agents/review-prompt.toml，按夹具注册职责执行。对象 guidance/main.md、guidance/prompt.md；入口与直接引用 config/service.toml、checks/load_guidance.py。权威依据为本夹具 docs/sdd-workflow-whitepaper.md、specs/platform-independent-sdd/spec.md，适用矩阵 docs/review-criteria.md：主任务 RW-06.1 将实际产物回读条件传给待办助手；助手 RW-06.1 成功回读才完成、RW-07.1 回读不可用应返回待验原因及再次回读条件。请据白皮书与 Spec 核对语义、作用域、完成与失败分支，并关联各对象和判据。边界：本轮没有模型行为轨迹或待办助手实跑环境，本次专项调用仅为审查证据，不能当成受审助手行为回归。本地装配检查仅证明可达；未覆盖真实 SDD 工作流。仅审查，无源码修复授权，不调用其他角色或全面评审。本工单要求所有受审文件只读，报告和必要证据如需写入仅可写 docs/test-reports/sdd-workflow/，优先通过最终回执交付以便我原文保存。实际回执请明确读取路径与版本/SHA256、事实位置/行号、权威依据、静态结论、发现影响/建议、行为未验及恢复条件。你向我提供专项证据，由 sdd-workflow-review 自行归并综合结论。请勿把自身调用成功或装配检查视为 AC-001 成功。

## 实际最终回执（原文）

review-prompt 专项实际回执（只读）

对象版本：HEAD `20aa8f7fbf9ec965b09c89aeffa5fdc81928e3bc`；读取时 `git status --porcelain=v1` 无输出。已读取夹具注册 `.codex/config.toml` 与 `.codex/agents/review-prompt.toml`，按其提示词专项职责核对，未写文件、未修订源码、未调用其他角色。

| 对象／入口 | 静态结论 | 事实、依据与限制 |
| --- | --- | --- |
| `guidance/main.md:3` | RW-06.1 静态符合 | 工单要求给出预期产物位置，并要求回读后返回实际结果，承接白皮书第3行、Spec FR-001 和合成矩阵第9、17行的主任务职责。实际派单及条件是否完整传递未验。 |
| `guidance/prompt.md:3` 完成分支 | RW-06.1 静态符合 | “回读工单指定的产物后报告完成”把完成置于实际产物回读之后；与白皮书第3行及 Spec FR-001 一致。成功回读的模型行为未验。 |
| `guidance/prompt.md:3` 不可用分支 | RW-07.1 存在偏差，发现 RP-01 | 仅要求“报告待验”，没有要求返回待验原因及再次回读条件。白皮书第3行要求接续条件，Spec FR-001 要求恢复条件，AC-001 和合成判据第10行明确要求原因及再次回读条件。 |
| `checks/load_guidance.py:1–6` | 装配静态可达 | 按 `main`、`prompt` 顺序读取两份正文；脚本第1行明确不执行模型。只证明装配内容及顺序。 |
| `config/service.toml:1` | 无新增提示词依据 | 仅有 `timeout_seconds = 30`，未规定超时后的待验原因或恢复条件，不能补足 RP-01；本轮没有服务实跑证据。 |

RP-01 触发于指定产物不可访问、读取失败或回读工具不可用。现有指令允许助手只回复“待验”而不提供原因和接续条件，调用者因此缺乏补验所需信息。建议在获授权修订时明确失败回执应包含原因及再次回读所需条件，并保留“成功回读后才完成”的现有约束。本轮未获修复授权，未修改。

本地检查原始结果：

```text
$ python checks/load_guidance.py
/bin/bash: line 1: python: command not found

$ python3 checks/load_guidance.py
# 主任务

发给待办助手的工单应给出预期产物位置，要求回读后返回实际结果。

# 待办助手

回读工单指定的产物后报告完成。回读不可用时报告待验。
```

`python3` 检查退出码为0；这是同一装配脚本的解释器替代执行，不是 AC-001 行为验收。首次 `python` 不可用应保留为环境记录。

读取版本 SHA-256：

```text
c7c7581c1f27c5b74cb9178ff61e58ef87f020d16823005127404f19a1ecab6e  .codex/config.toml
87112509fc93378290b3797beb14b7b122ea0852e596ea8346278ca412e08777  .codex/agents/review-prompt.toml
926eec4f95c7692645b2f1f0bff7ec2bef96a69aa365fa63210c508b98e51da6  guidance/main.md
09a185885c0307cf4b3fcf14ff149ae64c846a3c6a21734832eb57647498f2cd  guidance/prompt.md
634a7586e96c11fefd44a5eb65ca4eb682ad8817baea7fa56893f0817edd3f76  config/service.toml
c2f88b5260f95cfa8d5c127f8043ec62d0ed9138b84573ecdfe958d47a089471  checks/load_guidance.py
1bc4dfefc5879bda0468b0089d1d598ae5562be19c81164e334327de024cb808  docs/sdd-workflow-whitepaper.md
292280e5641fa892cbd5b4d1a71130bffd86541e4c83ff36612f54559f71fa44  specs/platform-independent-sdd/spec.md
57fe8a82754897ae792713423a63eb07a8016c3edb0488ce67be22d742f88d83  docs/review-criteria.md
```

执行检查后再次核对两份 `guidance` 哈希，与上列一致；当时工作区状态仍无输出。

未验范围：本轮没有待办助手模型行为轨迹或实跑环境，成功回读后报告完成、回读不可用时返回原因及再次回读条件两场景均为**证据不足**。恢复验证需提供固定模型与推理配置、工具和权限、工单、可回读产物及不可用状态，记录实际回读、回复和副作用。本专项调用成功不证明待办助手行为通过，也不覆盖真实 SDD 工作流、稳定性或其他阶段与角色。由调用方 `sdd-workflow-review` 归并最终结论。

## 调用方归并

RP-01 归并到批次 F-01；不另建重复问题。主任务 RW-06.1、助手 RW-06.1 的静态符合与本次主审一致；助手 RW-07.1 静态存在偏差。角色本地检查与 Main 各执行一次，均只证明文本读取；Main 命令计时不包含角色运行或其他 review 开销。角色在其读取/检查时报告 clean，Main 之后新增了批次产物；最终状态由 E-05 固定。未取得完整角色 timing/usage，未测不代表零。
