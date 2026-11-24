# sdd-init

本仓库分发 sdd-init Skill，为 Codex Desktop 和 GitHub Copilot App 的目标仓库接入 Agent 协作环境。根目录 `AGENTS.md` 提供主会话入口，Main 按需读取治理规则，并通过宿主原生入口派发六个垂直角色。

用户确认意图时选择直接交付或调度交付。主会话按选定路径执行和处理阻塞，无法继续时报告原因与恢复条件。调度交付按工单产物分配角色。历史 `[Coder]` 标签继续由 implementer 承接。

显式请求可选择一个阶段，或串联多个阶段。各入口、角色和交付物见 [Main 路由](source/project/.codex/agentsmd_template.md#路由)。

| 用户场景 | 谁负责 | 完成条件 |
| --- | --- | --- |
| 选择直接交付 | 主会话执行 | 直接回答或完成修改并验证 |
| 选择调度交付 | 主会话派单并验收，主责角色执行并自验 | 工单产物及证据满足约定条件 |
| 人工陪测 | Main 保持陪测状态，uat-observer 负责现场观测 | 用户实际操作，异常经修复后复验，结束时清理本轮资源并记录待确认项 |
| 调用项目已有的 Spec Kit 命令 | Main 读取目标项目已配置的命令契约 | 按该命令及任务标签交付结果 |

通过 `uvx --from . sdd-init install` 从本仓源码初始化用户级 Skill，再在目标仓库的新会话中调用 `sdd-init`。接入工单包括规则升级、原生角色配置、可复跑检查及宿主验收。[安装说明](docs/installation.md) · [产品 Spec](specs/platform-independent-sdd/spec.md) · [文档索引](docs/index.md)
