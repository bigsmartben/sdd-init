# 项目文档

按任务问题进入本项目实际权威章节；尚未建立正文时，使用下列模板。首次建立入口时以实际章节链接替代相应提示。新增或调整产物时查[工程资产边界](../.agents/sdd/references/sdd-repository-governance.md#工程资产边界)及对应的[文档与产物落点](../.agents/sdd/references/sdd-repository-governance.md#文档与产物落点)。

- **怎样确定本轮工作和交接边界？** 查[主任务职责](../.agents/sdd/references/sdd-repository-governance.md#职责与交接)、[阶段授权与推进](../.agents/sdd/references/sdd-repository-governance.md#阶段授权与推进)及[技能 Agent 的启动与接续](../.agents/sdd/references/delegation.md#技能-agent-的启动与接续)。
- **用户要完成什么，界面如何操作？** 查能力需求及其原型。需求到实现的入口为 [sdd-develop](../.agents/skills/sdd-develop/SKILL.md)，点对点验收计划与方案查原需求工单。初次编写规格使用[Spec](../.agents/sdd/assets/spec_template.md)和[Prototype Reference](../.agents/sdd/assets/prototype_reference_template.md)。
- **谁决定，什么条件下才能报告成功？** 架构设计与演化使用 [sdd-architecture](../.agents/skills/sdd-architecture/SKILL.md)。现有设计查[Blueprint](../.agents/sdd/assets/blueprint_template.md)、[Scenario Sequence](../.agents/sdd/assets/sequence_template.md)、[Interface Contract](../.agents/sdd/assets/contract_template.md)的适用章节；此处链接为模板。
- **比较了哪些技术，为什么选这一项？** 查 Technical Research and Selection Report；按需使用[Technical Research and Selection Report](../.agents/sdd/assets/research_template.md)。实测结果和复现入口查关联 Test Report，初次记录使用[Test Report](../.agents/sdd/assets/test_report_template.md)。
- **怎样复跑本轮全功能点集成回归？** 查 [sdd-test-loop](../.agents/skills/sdd-test-loop/SKILL.md) 交付的用户验收文档或链接。已落盘的指南查能力 Spec 和相邻的 `quickstart.md`，其结构见[Quickstart](../.agents/sdd/assets/quickstart_template.md)。实际版本、逐场景证据、人工待验、恢复条件和 Test Gate 查对应测试报告；初次记录使用[Test Report](../.agents/sdd/assets/test_report_template.md)，Status／Plan 引用报告并记录进度。

- **发现了哪些 Bug，修复后是否已复验关闭？** 沿用 [Issue](../.agents/sdd/assets/issue_template.md) 及编号。指定缺陷的诊断、修复及定向复验使用 [sdd-bugfix](../.agents/skills/sdd-bugfix/SKILL.md)。修复方案查关联的 Plan／Task，关单依据及恢复条件查原 Issue。

- **项目的 Code Review Rules 在哪里？** 用户决定维护时机，获授权的执行者按[写入规则](../.agents/sdd/references/document-writing.md#code-review-rules)维护。首次建立后将此处指向规则正文。

- **怎样审查架构落地或实施技术重构？** 使用 [sdd-refactor](../.agents/skills/sdd-refactor/SKILL.md)。原检查项、架构复核、行为保持验收和 Review Gate 查 Architecture Review Record，初次落盘使用[模板](../.agents/sdd/assets/review_template.md)。重构方案与局部自验查关联 Plan／Task。

- **本轮改什么、按什么顺序执行？** 查当前 Plan（Task 清单）；输出结构见 [Plan](../.agents/sdd/assets/plan_template.md)，安排执行见[实施交接](../.agents/sdd/references/delegation.md#实施交接)，制定与执行计划见[实施与局部自验](../.agents/sdd/references/implementation.md)。

- **如何操作仓库、流水线、发布、环境、流量、备份恢复或退役？** 使用 [sdd-deliver](../.agents/skills/sdd-deliver/SKILL.md)。从项目运行指南与平台配置定位实际入口，正式发布查[适用依据](../.agents/sdd/references/sdd-repository-governance.md#正式发布依据)，首次建运维记录用 [Delivery Record](../.agents/sdd/assets/delivery_record_template.md)。

- **文档写后如何检查？** 写入者按[共享规则](../.agents/sdd/references/document-writing.md)做语义和机械检查。单独核对正文冲突、冗余或引用时，Main 按[文档交接](../.agents/sdd/references/delegation.md#文档交接)安排只读审查，再按授权和正文归属安排修复。
