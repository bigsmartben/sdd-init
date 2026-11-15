# 项目文档

按任务问题进入本项目实际权威章节；尚未建立正文时，使用下列模板。首次建立入口时以实际章节链接替代相应提示。新增或调整产物时查[工程资产边界](../source/project/.agents/sdd/references/sdd-repository-governance.md#工程资产边界)及对应的[文档与产物落点](../source/project/.agents/sdd/references/sdd-repository-governance.md#文档与产物落点)。

- **怎样确定本轮工作和交接边界？** 查[主任务职责](../source/project/.agents/sdd/references/sdd-repository-governance.md#职责与交接)、[阶段授权与推进](../source/project/.agents/sdd/references/sdd-repository-governance.md#阶段授权与推进)及[技能 Agent 的启动与接续](../source/project/.agents/sdd/references/delegation.md#技能-agent-的启动与接续)。
- **sdd-init 承诺交付什么，如何验收？** 查[工程协作职责 Spec](../specs/platform-independent-sdd/spec.md)与[产品用例](blueprint.md#3-用户用例)。使用方式按本索引进入对应 Skill、角色或共享规则。
- **sdd-workflow 的设计目标和 review 依据是什么？** 查[白皮书](sdd-workflow-whitepaper.md)中的已确认设计；执行规则、RW 子项、对象矩阵与设计／Spec 追溯见[审查判据](../.agents/skills/sdd-workflow-review/references/review-criteria.md)，统计方法见[质量成本口径](../.agents/skills/sdd-workflow-review/references/evidence-and-cost.md)。[白皮书模板](../.agents/skills/sdd-workflow-review/assets/whitepaper-template.md)组织设计，[Review 报告模板](../.agents/skills/sdd-workflow-review/assets/review-report-template.md)承载各批次结论、证据与成本；历史记录见[报告目录](test-reports/sdd-workflow/)，本轮分工维护验证见[验证记录](test-reports/sdd-workflow/2026-11-14-artifact-division-validation.md)。
- **工作流采用怎样的职责组织与依赖约束？** 查[实现策略](sdd-workflow-whitepaper.md#实现策略)，包括三层架构、职责单一、同层禁止依赖、上下位禁止倒置及主任务直接使用下位能力的边界。

- **如何接入、升级、重连或恢复 SDD 工作流？** 查[安装指南](installation.md)、[sdd-init](../source/initializer/SKILL.md)及[验证证据](workflow-evidence.md#2026-11-14-初始化升级与恢复)。
- **谁决定，什么条件下才能报告成功？** 查[产品与架构蓝图](blueprint.md)。架构设计与演化入口为 [sdd-architecture](../source/project/.agents/skills/sdd-architecture/SKILL.md)。公开协作入口见[关键协作索引](blueprint.md#8-关键协作索引与未决边界)；新增独立场景或契约时参考[Scenario Sequence](../source/project/.agents/sdd/assets/sequence_template.md)和[Interface Contract](../source/project/.agents/sdd/assets/contract_template.md)。
- **比较了哪些技术，为什么选这一项？** 查 Technical Research and Selection Report；按需使用[Technical Research and Selection Report](../source/project/.agents/sdd/assets/research_template.md)。实测结果和复现入口查关联 Test Report，初次记录使用[Test Report](../source/project/.agents/sdd/assets/test_report_template.md)。
- **怎样复跑本轮用户功能集成回归？** 查 [sdd-test-loop](../source/project/.agents/skills/sdd-test-loop/SKILL.md) 交付的本轮用户验收文档或链接。已落盘的指南查能力 Spec 和相邻的 `quickstart.md`，其结构见[Quickstart](../source/project/.agents/sdd/assets/quickstart_template.md)。历史执行记录见[专职 Agent 协作测试报告](test-reports/agent-collaboration/2026-11-05.md)；实际版本、逐场景证据、人工待验、恢复条件和 Test Gate 查对应测试报告；初次记录使用[Test Report](../source/project/.agents/sdd/assets/test_report_template.md)，Status／Plan 引用报告并记录进度。

- **怎样把需求推进到可集成交付？** 使用 [sdd-develop](../source/project/.agents/skills/sdd-develop/SKILL.md)。点对点验收计划与方案查原工单，实施计划和局部证据查关联 Plan／Task。

- **发现了哪些问题，修复后是否已复验关闭？** 查独立 Issue 及关联报告；初次记录使用 [Issue](../source/project/.agents/sdd/assets/issue_template.md)。指定缺陷的诊断、修复及定向复验使用 [sdd-bugfix](../source/project/.agents/skills/sdd-bugfix/SKILL.md)。修复方案查关联的 Plan／Task，关单依据及恢复条件查原 Issue。

- **怎样审查架构落地或实施技术重构？** 使用 [sdd-refactor](../source/project/.agents/skills/sdd-refactor/SKILL.md)，先定位蓝图并初始化或核对项目规范与独立 [Review 矩阵](../source/project/.agents/sdd/assets/review-matrix_template.md)。按确认范围生成本轮任务；原检查项、重构工单、两类复核及 Review Gate 查 [Architecture Review Record](../source/project/.agents/sdd/assets/review_template.md)，实施方案和局部自验查关联 Plan／Task。本轮维护见[实施清单](plans/refactor-review-matrix.md)。历史证据见[目标规则生成、更新及整改验收](test-reports/code-review-rules/2026-11-05.md)、[Review 检查项闭环复核](test-reports/agent-collaboration/2026-11-05-review-items.md)及[专职 Agent 协作 Review](test-reports/agent-collaboration/2026-11-05-review.md)。

- **怎样专项审查提示词或比较改版后的行为？** 将明确的工单交给用户级通用角色 [review-prompt](../source/initializer/assets/user-agents/review-prompt.toml)。角色随[用户级安装](installation.md#首次安装)提供，可在未接入 SDD 的仓库使用。
- **怎样全面审查并回归本仓工作流？** 用户显式调用 [sdd-workflow-review](../.agents/skills/sdd-workflow-review/SKILL.md)，按固定版本的设计与判据，交付版本化覆盖、回归证据、获授权后的修复复验及质量成本报告。

- **本轮改什么、按什么顺序执行？** 查[4+1 角色独立性整改 Plan](plans/role-independence.md)。既有工作见[DevOps 职责与迁移 Plan](plans/devops.md)、[设计变更提醒与任务交接 Plan](plans/workflow-continuation.md)、[专职 Agent 协作 Plan](plans/agent-collaboration.md)和[安装恢复与旧命令退役 Plan](plans/install-recovery.md)。实施任务使用 [Plan 模板](../source/project/.agents/sdd/assets/plan_template.md)。

- **如何处理仓库交付、构建发布、运行排障、流量、备份恢复或退役？** 使用 [sdd-deliver](../source/project/.agents/skills/sdd-deliver/SKILL.md)。发布证据查[正式发布依据](../source/project/.agents/sdd/references/sdd-repository-governance.md#正式发布依据)，本仓实际验证查[实施证据](workflow-evidence.md)。

- **文档写后如何检查？** 写入者按[共享规则](../source/project/.agents/sdd/references/document-writing.md)做语义和机械检查。角色配置及调度见[执行协作](../source/project/.agents/sdd/references/delegation.md)。
