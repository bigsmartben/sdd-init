<!-- sdd-contract-governance:start -->
## 项目入口

当前仓库启用了共享 SDD 工作流。新工作区缺少本地链接时，运行 sdd-init 接入本机共享资源。

- 从项目已有文档索引定位实际路径，通常为 docs/index.md。
- [仓库治理规范](.agents/skills/sdd-workflow/sdd/references/sdd-repository-governance.md)

Main 面向用户负责入口选择、阶段调度和交付。按[仓库治理规范](.agents/skills/sdd-workflow/sdd/references/sdd-repository-governance.md)判断适用 Skill、局部操作、直接委派和阶段授权。选定阶段后，按[启动与接续](.agents/skills/sdd-workflow/sdd/references/delegation.md#技能-agent-的启动与接续)交给独立技能 Agent；技能 Agent 组织阶段内工作、调度专业角色。派单时写明实际调用者。同层协作由共同上层传递，跨阶段事项和用户决定交 Main。

## 索引

| 工作 | 入口 |
| --- | --- |
| 文档归并与只读一致性审查 | [文档交接](.agents/skills/sdd-workflow/sdd/references/delegation.md#文档交接) |
| 单个需求的规格、实施及点对点验收 | [sdd-develop](.agents/skills/sdd-workflow/skills/sdd-develop/SKILL.md) |
| 仓库级架构设计与演化 | [sdd-architecture](.agents/skills/sdd-workflow/skills/sdd-architecture/SKILL.md) |
| 实施已就绪工单并局部自验 | [sdd-coder](.agents/skills/sdd-workflow/sdd/references/delegation.md#实施交接) |
| 指定缺陷归因、修复与定向复验 | [sdd-bugfix](.agents/skills/sdd-workflow/skills/sdd-bugfix/SKILL.md) |
| 用户功能集成测试与本轮验收文档 | [sdd-test-loop](.agents/skills/sdd-workflow/skills/sdd-test-loop/SKILL.md) |
| 架构审查、架构对齐与技术重构 | [sdd-refactor](.agents/skills/sdd-workflow/skills/sdd-refactor/SKILL.md) |
| 明确请求审查提示词、比较候选版或获授权修订复验 | [sdd-review-prompt](.agents/skills/sdd-workflow/skills/sdd-review-prompt/SKILL.md) |
| 仓库交付、构建发布、运行排障、流量、备份恢复与退役 | [sdd-deliver](.agents/skills/sdd-workflow/skills/sdd-deliver/SKILL.md) |

按本轮任务选择入口并读取适用章节。[场景提示](.agents/skills/sdd-workflow/sdd/references/scenarios.md)用于讨论和定位正文，[执行协作](.agents/skills/sdd-workflow/sdd/references/delegation.md)用于委派或交接。实体模板按产物选用。
<!-- sdd-contract-governance:end -->
