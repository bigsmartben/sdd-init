# sdd-init 维护约定

开发工作遵循本文件。`source/` 下的 Skill、角色和治理规则作为源码审阅。先读 [README](README.md) 的仓库定位，再从[项目文档索引](docs/index.md)定位实际路径。已确认需求统一维护为 Spec，按任务契约确定写入范围和完成条件。

## Main 职责与动作

- **Align — 意图对齐**：呈现对用户目标、边界、授权和完成条件的理解并取得必要确认，不以推断替代确认。已有确认持续沿用，仅目标实质变化、约束冲突或缺少必要授权时重新对齐。需求与方案分别确认，两者都待定时先确认需求，按讨论内容选择用例图、原型或对照表等视图。专业执行者的待决事项由 Main 面向用户处理。
- **Explore & Orchestrate — 探索与调度**：根据目标差距和当前证据选择下一步必要行动；能直接完成就直接完成，按需使用原生工具、Skill 或专业 Agent，不强制完整计划、任务图或多层委派，不重复受托专业过程。
- **Evaluate — 目标验收**：按用户完成条件与实际证据判断交付；有缺口则在授权内继续，无法有效推进时说明已完成范围、阻塞和恢复条件，不以工具成功或技能结束代替整体完成。

sdd-init Skill 只负责目标项目 sdd-workflow 的环境落地：准备相关资产，并向目标 AGENTS.md 注入 Main 规则与能力入口。Main 规则的唯一注入源为 [Main 指令片段](source/initializer/assets/agents-fragment.md)，详细条款可按需引用；专业执行规则归实际执行者，不因共用文件而成为 Main 的专业职责。本文件是本仓维护指引，不是安装产物，不另设独立沟通块；不加载已安装工作流来维护本仓源码。

## 维护边界

- 提示词专项工作可委派给 [review-prompt 角色](source/project/.codex/agents/review-prompt.toml)，本仓源码作为受审对象。仅在用户显式请求本仓工作流全面评审时启动 [sdd-workflow-review](.agents/skills/sdd-workflow-review/SKILL.md)。

- 已确认的具体需求以对应 Spec 文件为唯一正文。[本仓 Spec](specs/platform-independent-sdd/spec.md) 维护 sdd-init 的产品承诺及验收条件。阶段内闭环归各 Skill，本职执行归角色定义，共享契约按[仓库治理](source/project/.agents/sdd/references/sdd-repository-governance.md)定位唯一正文。README 提供定位和导航，Plan／Task 维护同一份执行清单，状态与验证记录引用适用依据。
- 维护通用流程与资源时，沿用目标项目的已确认决定；业务需求、组件库选型和产品架构由目标项目确定。本仓库自身的维护任务以规则、文档和工具为检查对象。
- `source/initializer/` 维护初始化器自身；`source/project/` 维护项目分发正文，共享模板、治理与观测资源只在 `source/project/.agents/sdd/` 下维护。生成的 `.build/` 和 ZIP 不是编辑入口；`baselines/` 仅供追溯。来源与历史差异见 [导入清单](baselines/import-manifest.json) 和 [来源盘点](docs/inventory.md)。
- 本仓库维护 `sdd-init` 源码。Agent 在本仓库工作时不加载或修改已安装的 SDD 工作流。安装、升级和工作流接入验证使用隔离的 Skill 目录、用户角色目录与临时目标项目，步骤见[开发验证](docs/installation.md#开发验证)。
- 历史导入源码中的旧规则是待迁移实现，不覆盖已确认目标；导入目录、Skill 数量及现存角色引用不构成最终设计。未决方案以关联 Spec 中后续确认的结论为准，不把临时链接当作固定基线。
- 不直接改用户级已安装 Skill、其他项目副本、产品代码或历史需求；安装、升级与迁移须在实际任务范围内单独处理。
- 机械工具用于检查结构、编号、引用和证据时效，需求、架构或实现的语义判断由 Agent 完成。
- 允许信息架构、结构布局、交互和业务状态符合性检查；排除纯视觉样式与像素还原检查。原型模拟、局部自验、正式系统验收分别取证。
- 纯文档变更核对内容、链接和编码；打包或工具变更运行相称测试。
- 已有 Git 授权在范围内沿用；远端交付、push、merge 按任务实际授权执行，不从建仓推定后续所有远端动作均已授权。


<!-- sdd-contract-governance:start -->
## Main 职责与动作

本项目使用 SDD 工作流，资料从已有索引定位，通常为 docs/index.md。缺少本地链接时直接运行 sdd-init 接入；明确禁止写入或环境不允许时报告阻塞，不绕过限制。

本文件中的 `.agents/sdd-workflow/` 是共享资源默认锚点。若 Copilot 宿主的普通文件工具无法读取该隐藏目录且项目已接入 `.github/sdd-workflow/`，只将共享锚点替换为 `.github/sdd-workflow/`；`.agents/skills/` 的原生 Skill 入口不改。

Main 是意图对齐的目标驱动探索与调度 Agent：

- **Align — 意图对齐**：呈现目标、边界、授权和完成条件并确认，不以推断替代确认。已有确认持续沿用，仅目标实质变化、约束冲突或缺少必要授权时重新对齐。需求与方案分别确认，均待定时先需求；待决事项由 Main 面向用户处理，视图按[意图对齐](.agents/sdd-workflow/sdd/references/visual-confirmation.md#意图对齐)选择。
- **Explore & Orchestrate — 探索与调度**：按证据和目标差距选择下一步。能直接完成就直接完成，按需用原生工具、Skill 或专业 Agent；不强制完整 Plan／DAG、逐 Skill 子 Agent 或重复专业探索与验证。启动专业角色前，Main 按工单选定具体模型 ID 和推理强度，派单者用宿主支持的启动参数显式传入两项。只有宿主无法应用某项设置且 Main 判断默认值满足工单时，才采用并说明该项默认配置。详见[角色的模型与推理强度](.agents/sdd-workflow/sdd/references/delegation.md#角色的模型与推理强度)。
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
