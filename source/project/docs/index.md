# 项目文档

按任务问题进入本项目实际权威章节；尚未建立正文时，使用下列模板。首次建立入口时以实际章节链接替代相应提示。工程资产与默认落点见[仓库治理](../.agents/sdd/references/sdd-repository-governance.md)。

- **用户要完成什么，界面如何操作？** 查能力需求及其原型；初次编写使用[需求规格](../.agents/sdd/assets/spec_template.md)和[原型引用](../.agents/sdd/assets/prototype_reference_template.md)。
- **谁决定，什么条件下才能报告成功？** 查[蓝图](../.agents/sdd/assets/blueprint_template.md)、[场景时序](../.agents/sdd/assets/sequence_template.md)、[接口契约](../.agents/sdd/assets/contract_template.md)的适用章节；此处链接为模板。
- **候选方案在什么条件下可行？** 查方案可行性测试报告及复现入口；初次记录使用[测试报告模板](../.agents/sdd/assets/test_report_template.md)。
- **验证哪些情形，这一版实际做到了吗？** 查能力 Spec 和相邻的 `quickstart.md`；初次编写使用[运行与验收指南模板](../.agents/sdd/assets/quickstart_template.md)。实际版本、逐场景结果、证据及人工确认查对应测试报告；初次记录使用[测试报告模板](../.agents/sdd/assets/test_report_template.md)，Status／Plan 引用报告并记录进度。

- **测试发现了哪些问题，修复后是否已复验关闭？** 查独立 Issue 记录及关联的发现／复验报告；初次记录使用 [Issue 模板](../.agents/sdd/assets/issue_template.md)；以 Issue 入口和编号交接，修复方案查关联的 imp Plan／Task。

- **项目的 Code Review Rules 在哪里？** 用户决定维护时机，通过 [sdd-doc](../.agents/skills/sdd-doc/SKILL.md) 按[规则模板](../.agents/sdd/assets/code-review-rules_template.md)生成或更新；首次生成后将此处指向项目规则正文。

- **Code Review Rules 是否落实，检查项偏差是否修复并复核？** 查架构 Review 记录；初次落盘使用 [Review 模板](../.agents/sdd/assets/review_template.md)，修复方案引用 imp 的 Plan／Task。

- **本轮改什么、按什么顺序执行？** 查当前 Plan（Task 清单）；输出结构见 [Plan 模板](../.agents/sdd/assets/plan_template.md)，生成与执行规则见 [sdd-imp](../.agents/skills/sdd-imp/SKILL.md)。

- **如何部署、启动或重启服务？** 使用 [sdd-deploy](../.agents/skills/sdd-deploy/SKILL.md)，从本项目运行指南与目标环境配置定位实际入口。

- **文档写后如何检查？** 使用[文档校验 CLI](../.agents/sdd/references/doc-check.md)检查选定范围的机械问题，语义核对由 sdd-doc 完成。
