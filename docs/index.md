# 项目文档

按任务问题进入本项目实际权威章节；尚未建立正文时，使用下列模板。首次建立入口时以实际章节链接替代相应提示。工程资产与默认落点见[仓库治理](../source/project/.agents/sdd/references/sdd-repository-governance.md)。

- **用户要完成什么，界面如何操作？** 查[工程协作职责 Spec](../specs/platform-independent-sdd/spec.md)；全产品用例见[蓝图](blueprint.md#3-用户用例)。本仓库以 CLI、指令与资源为主要接口。
- **谁决定，什么条件下才能报告成功？** 查[产品与架构蓝图](blueprint.md)，公开协作入口见[关键协作索引](blueprint.md#8-关键协作索引与未决边界)；新增独立场景或契约时参考[场景时序模板](../source/project/.agents/sdd/assets/sequence_template.md)和[接口契约模板](../source/project/.agents/sdd/assets/contract_template.md)。
- **候选方案在什么条件下可行？** 查方案可行性测试报告及复现入口；初次记录使用[测试报告模板](../source/project/.agents/sdd/assets/test_report_template.md)。
- **验证哪些情形，这一版实际做到了吗？** 查能力 Spec 和相邻的 `quickstart.md`；初次编写使用[运行与验收指南模板](../source/project/.agents/sdd/assets/quickstart_template.md)。本轮结果见[专职 Agent 协作测试报告](test-reports/agent-collaboration/2026-11-05.md)；实际版本、逐场景结果、证据及人工确认查对应测试报告；初次记录使用[测试报告模板](../source/project/.agents/sdd/assets/test_report_template.md)，Status／Plan 引用报告并记录进度。

- **测试发现了哪些问题，修复后是否已复验关闭？** 查独立 Issue 记录及关联的发现／复验报告；初次记录使用 [Issue 模板](../source/project/.agents/sdd/assets/issue_template.md)；以 Issue 入口和编号交接，修复方案查关联的 imp Plan／Task。

- **Code Review Rules 是否匹配蓝图，检查项偏差是否修复并复核？** 查[目标规则生成、更新及整改验收](test-reports/code-review-rules/2026-11-05.md)、[Review 检查项闭环复核](test-reports/agent-collaboration/2026-11-05-review-items.md)及[专职 Agent 协作 Review](test-reports/agent-collaboration/2026-11-05-review.md)；初次落盘使用 [Review 模板](../source/project/.agents/sdd/assets/review_template.md)，修复方案引用 imp 的 Plan／Task。

- **本轮改什么、按什么顺序执行？** 查[设计变更提醒与任务交接 Plan](plans/workflow-continuation.md)；既有工作见[专职 Agent 协作 Plan](plans/agent-collaboration.md)、[安装恢复与旧命令退役 Plan](plans/install-recovery.md)及[对应验证报告](test-reports/install-recovery/2026-11-04.md)。输出结构见 [Plan 模板](../source/project/.agents/sdd/assets/plan_template.md)，生成与执行规则见 [sdd-imp](../source/project/.agents/skills/sdd-imp/SKILL.md)。

- **如何部署、启动或重启服务？** 使用 [sdd-deploy](../source/project/.agents/skills/sdd-deploy/SKILL.md)，从本项目运行指南与目标环境配置定位实际入口。

- **文档写后如何检查？** 使用[文档校验 CLI](../source/project/.agents/sdd/references/doc-check.md)检查选定范围的机械问题，语义核对由 sdd-doc 完成。
