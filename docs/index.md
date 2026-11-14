# 项目文档

按任务问题进入本项目实际权威章节；尚未建立正文时，使用下列模板。首次建立入口时以实际章节链接替代相应提示。新增或调整产物时查[工程资产边界](../source/project/.agents/sdd/references/sdd-repository-governance.md#工程资产边界)及对应的[文档与产物落点](../source/project/.agents/sdd/references/sdd-repository-governance.md#文档与产物落点)。

- **用户要完成什么，界面如何操作？** 查[工程协作职责 Spec](../specs/platform-independent-sdd/spec.md)；全产品用例见[蓝图](blueprint.md#3-用户用例)。本仓库以 CLI、指令与资源为主要接口。
- **谁决定，什么条件下才能报告成功？** 查[产品与架构蓝图](blueprint.md)，公开协作入口见[关键协作索引](blueprint.md#8-关键协作索引与未决边界)；新增独立场景或契约时参考[Scenario Sequence](../source/project/.agents/sdd/assets/sequence_template.md)和[Interface Contract](../source/project/.agents/sdd/assets/contract_template.md)。
- **比较了哪些技术，为什么选这一项？** 查 Technical Research and Selection Report；按需使用[Technical Research and Selection Report](../source/project/.agents/sdd/assets/research_template.md)。实测结果和复现入口查关联 Test Report，初次记录使用[Test Report](../source/project/.agents/sdd/assets/test_report_template.md)。
- **怎样复跑本轮用户功能集成验收？** 查 sdd-test-loop 交付的本轮验收文档或链接。已落盘的指南查能力 Spec 和相邻的 `quickstart.md`，其结构见[Quickstart](../source/project/.agents/sdd/assets/quickstart_template.md)。本轮结果见[专职 Agent 协作测试报告](test-reports/agent-collaboration/2026-11-05.md)；实际版本、逐场景结果、证据及人工确认查对应测试报告；初次记录使用[Test Report](../source/project/.agents/sdd/assets/test_report_template.md)，Status／Plan 引用报告并记录进度。

- **怎样把需求推进到交付？** 使用 [sdd-develop](../source/project/.agents/skills/sdd-develop/SKILL.md) 推进需求规格、实施及点对点验收。工单提供验收方案，实施计划和局部证据查关联 Plan／Task。

- **发现了哪些问题，修复后是否已复验关闭？** 查独立 Issue 及关联报告；初次记录使用 [Issue](../source/project/.agents/sdd/assets/issue_template.md)。评估归因和派单见 [sdd-bugfix](../source/project/.agents/skills/sdd-bugfix/SKILL.md)，修复方案查关联的 Plan／Task，关单依据查原 Issue 引用的局部或集成验证证据。

- **Code Review Rules 是否匹配蓝图，检查项偏差是否修复并复核？** 查[目标规则生成、更新及整改验收](test-reports/code-review-rules/2026-11-05.md)、[Review 检查项闭环复核](test-reports/agent-collaboration/2026-11-05-review-items.md)及[专职 Agent 协作 Review](test-reports/agent-collaboration/2026-11-05-review.md)；初次落盘使用 [Architecture Review Record](../source/project/.agents/sdd/assets/review_template.md)，修复方案引用 实施的 Plan／Task。

- **本轮改什么、按什么顺序执行？** 查[设计变更提醒与任务交接 Plan](plans/workflow-continuation.md)；既有工作见[专职 Agent 协作 Plan](plans/agent-collaboration.md)、[安装恢复与旧命令退役 Plan](plans/install-recovery.md)及[对应验证报告](test-reports/install-recovery/2026-11-04.md)。输出结构见 [Plan](../source/project/.agents/sdd/assets/plan_template.md)，生成与执行规则见 [实施与局部自验](../source/project/.agents/sdd/references/implementation.md)。

- **如何提交、推送或部署？** 使用 [sdd-deliver](../source/project/.agents/skills/sdd-deliver/SKILL.md)。启动或重启服务时，从项目运行指南与环境配置定位实际入口。

- **文档写后如何检查？** 使用[文档校验 CLI](../source/project/.agents/sdd/references/doc-check.md)检查选定范围的机械问题，语义核对由 sdd-documenter 完成。
