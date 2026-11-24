# sdd-init

本仓库分发一套 Codex 工程协作配置：一个负责多轮对话与调度的 Main Agent，以及 architect、analyst、implementer、tester、devops、uat-observer 六个垂直 Agent。

Main 按场景选择路由，再按当前步骤要验收的结果调度角色。历史 `[Coder]` 标签继续由 implementer 承接。集成评估中，缺少预期或阈值的场景保留实测和用户影响，交由 Main 确认。

在消息开头输入 `【蓝图->计划】`，即可获得整体结构和实施计划。若已授权实现，输入 `【blueprint->implent】`，Main 会把蓝图的接口与兼容约束交给 implementer，交付实现与基础单测。需要人工陪测时输入 `【陪测】`，后续直接反馈体验即可。[完整热词与各阶段产物](source/project/.codex/AGENTS.md#显式指令)

| 用户场景 | 谁负责 | 完成条件 |
| --- | --- | --- |
| 咨询或已定位的小改动 | Main 走 Fast Path | 直接回答或完成修改并验证 |
| 未知故障、跨模块修改、环境与构建 | Main 走 Orchestrator Path，按需调用垂直角色 | 定位有依据，修改和运行验证覆盖约定用例 |
| 用户发出 `/live-uat` | Main 保持陪测状态，uat-observer 负责现场观测 | 用户实际操作，异常经修复后复验，结束时清理本轮资源并记录待确认项 |
| 用户发出 `/speckit.*` | Main 读取目标项目已配置的命令契约 | 按该命令及任务标签交付结果 |

`sdd-init` 是分发包与安装命令。安装方式与冲突处理见[安装说明](docs/installation.md)。路由边界和验收条件见[产品 Spec](specs/platform-independent-sdd/spec.md)，各角色的源码见[文档索引](docs/index.md)。
