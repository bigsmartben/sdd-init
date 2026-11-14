# RP-01 只读提示词专项工单

调用方：本轮 sdd-workflow-review；用户显式要求实际调用夹具注册的 review-prompt。调用方式：collaboration.spawn_agent，agent_type=review-prompt；注册路径 `.codex/config.toml` → `.codex/agents/review-prompt.toml`，请读取确认。

受审提交：07a29d1dbb465f73b786bd99a97f8d5dbb64f402；工作区初始干净。对象：guidance/main.md、guidance/prompt.md；精确 SHA-256 见同目录 snapshot-before.json。无候选版本，无修订授权。

权威预期仅用夹具 docs/sdd-workflow-whitepaper.md、specs/platform-independent-sdd/spec.md（FR-001、AC-001）、docs/review-criteria.md。合成矩阵：主任务 RW-06.1；待办助手 RW-06.1、RW-07.1。检查工单传递产物位置和实际回读要求；成功回读后报告完成；回读不可用时保留待验原因及再次回读条件。其余子项须遵循合成裁剪，不把通用真实工作流条款当成本夹具的产品承诺。

场景：成功回读、回读不可用。沿 checks/load_guidance.py 和 config/service.toml 检查实际可见的入口／装配证据。可以运行 python checks/load_guidance.py，但它只读取文本，不执行模型。本轮没有待办助手行为轨迹、实际产物或实跑环境；禁止将本次 review-prompt 专项调用当作待办助手的行为回归。区分静态偏差、行为证据不足及不适用。

授权终点：只读取证，向实际调用方回执；不得修改受审源码、Spec、白皮书、判据、Skill 或配置。所有必要文件仅可写 docs/test-reports/sdd-workflow/20261115-01/；你只负责该目录 review-prompt-receipt.md，可写其专项原始证据。你并非独占代码库，不要撤销他人的改动。无需另行委派，不开展全面评审，不代调用方作整版结论。

请在回执中保留：对象版本、判据、源码行位置、权威依据、发现及影响、静态与实际行为结论、未验范围及恢复条件；并记录调用身份和实际执行情况。完成后向调用方返回回执路径与关键发现。runtime usage 不可得则写未测，不估算为实测。
