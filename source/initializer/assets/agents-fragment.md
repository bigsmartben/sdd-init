<!-- sdd-contract-governance:start -->
## 项目入口

本项目使用共享 SDD 工作流。缺少本地链接时，运行 sdd-init 接入。项目资料从已有文档索引定位，通常为 docs/index.md。

Main 面向用户负责入口选择、阶段调度和交付。按[仓库治理规范](.agents/sdd-workflow/sdd/references/sdd-repository-governance.md)判断适用 Skill、局部操作、直接委派和阶段授权。选定阶段后，按[启动与接续](.agents/sdd-workflow/sdd/references/delegation.md#技能-agent-的启动与接续)交给独立技能 Agent；技能 Agent 组织阶段内工作、调度专业角色。派单时写明实际调用者。同层协作由共同上层传递，跨阶段事项和用户决定交 Main。

## Skill 入口

| 交付目标 | Skill |
| --- | --- |
| 单个需求的规格、实施与点对点验收 | [sdd-develop](.agents/skills/sdd-develop/SKILL.md) |
| 仓库级架构设计与演化 | [sdd-architecture](.agents/skills/sdd-architecture/SKILL.md) |
| 指定缺陷的归因、修复与定向复验 | [sdd-bugfix](.agents/skills/sdd-bugfix/SKILL.md) |
| 全功能点集成回归、用户验收文档与 Test Gate | [sdd-test-loop](.agents/skills/sdd-test-loop/SKILL.md) |
| 架构审查、架构对齐与技术重构 | [sdd-refactor](.agents/skills/sdd-refactor/SKILL.md) |
| 仓库交付、构建发布与运行维护 | [sdd-deliver](.agents/skills/sdd-deliver/SKILL.md) |

## 专业角色入口

专业角色按工单执行本职任务，向实际调度方回报；角色分工与调度约束见[执行协作](.agents/sdd-workflow/sdd/references/delegation.md)。其中，sdd-coder 承接已就绪的实施工单，要求见[实施交接](.agents/sdd-workflow/sdd/references/delegation.md#实施交接)。

## 文档与证据

固化已确认内容及实测证据时，遵循[共享文档写入规则](.agents/sdd-workflow/sdd/references/document-writing.md)，按产物选用模板。
<!-- sdd-contract-governance:end -->
