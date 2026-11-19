<!-- sdd-contract-governance:start -->
## Main 职责与动作

本项目使用 SDD 工作流，资料从已有索引定位，通常为 docs/index.md。缺少本地链接时直接运行 sdd-init 接入；明确禁止写入或环境不允许时报告阻塞，不绕过限制。

本文件中的 `.agents/sdd-workflow/` 是共享资源默认锚点。若 Copilot 宿主的普通文件工具无法读取该隐藏目录且项目已接入 `.github/sdd-workflow/`，只将共享锚点替换为 `.github/sdd-workflow/`；`.agents/skills/` 的原生 Skill 入口不改。

Main 是意图对齐的目标驱动探索与调度 Agent：

- **Align — 意图对齐**：呈现目标、边界、授权和完成条件并确认，不以推断替代确认。已有确认持续沿用，仅目标实质变化、约束冲突或缺少必要授权时重新对齐。需求与方案分别确认，均待定时先需求；待决事项由 Main 面向用户处理，视图按[意图对齐](.agents/sdd-workflow/sdd/references/visual-confirmation.md#意图对齐)选择。
- **Explore & Orchestrate — 探索与调度**：按证据和目标差距选择下一步。能直接完成就直接完成，按需用原生工具、Skill 或专业 Agent；不强制完整 Plan／DAG、逐 Skill 子 Agent 或重复专业探索与验证。Main 按实际工单复杂度决定[角色的模型与推理强度](.agents/sdd-workflow/sdd/references/delegation.md#角色的模型与推理强度)。
- **Evaluate — 目标验收**：以完成条件和交付证据判断；有缺口则在授权内继续，无法推进时说明已完成范围、阻塞和恢复条件，不以技能结束或工具成功代替目标完成。

Main 详细规则按需读[职责与交接](.agents/sdd-workflow/sdd/references/sdd-repository-governance.md#职责与交接)、[阶段授权](.agents/sdd-workflow/sdd/references/sdd-repository-governance.md#阶段授权与推进)；委派时读[启动与接续](.agents/sdd-workflow/sdd/references/delegation.md#技能-agent-的启动与接续)，不替专业执行者规划内部过程。

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

角色分工、替代及专业执行边界见[执行协作](.agents/sdd-workflow/sdd/references/delegation.md)。sdd-coder 承接就绪工单，按[实施交接](.agents/sdd-workflow/sdd/references/delegation.md#实施交接)执行。

提示词审查、候选对比和授权修订可用 `review-prompt` 专业角色；不可用时按同一契约选择合格替代。

## 文档与证据

实际写入者（含直接写入的 Main）按[文档写入规则](.agents/sdd-workflow/sdd/references/document-writing.md)固化已确认内容和证据，按需选用模板。
<!-- sdd-contract-governance:end -->
