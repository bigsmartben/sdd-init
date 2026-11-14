# 项目文档

按任务问题进入本项目实际权威章节；尚未建立正文时，使用下列模板。首次建立入口时以实际章节链接替代相应提示。新增或调整产物时查[工程资产边界](../.agents/sdd/references/sdd-repository-governance.md#工程资产边界)及对应的[文档与产物落点](../.agents/sdd/references/sdd-repository-governance.md#文档与产物落点)。

- **用户要完成什么，界面如何操作？** 查能力需求及其原型。需求交付入口为 [sdd-develop](../.agents/skills/sdd-develop/SKILL.md)，初次编写使用[Spec](../.agents/sdd/assets/spec_template.md)和[Prototype Reference](../.agents/sdd/assets/prototype_reference_template.md)。
- **谁决定，什么条件下才能报告成功？** 查[Blueprint](../.agents/sdd/assets/blueprint_template.md)、[Scenario Sequence](../.agents/sdd/assets/sequence_template.md)、[Interface Contract](../.agents/sdd/assets/contract_template.md)的适用章节；此处链接为模板。
- **比较了哪些技术，为什么选这一项？** 查 Technical Research and Selection Report；按需使用[Technical Research and Selection Report](../.agents/sdd/assets/research_template.md)。实测结果和复现入口查关联 Test Report，初次记录使用[Test Report](../.agents/sdd/assets/test_report_template.md)。
- **怎样复跑本轮用户功能集成验收？** 查 sdd-test-loop 交付的本轮验收文档或链接。已落盘的指南查能力 Spec 和相邻的 `quickstart.md`，其结构见[Quickstart](../.agents/sdd/assets/quickstart_template.md)。实际版本、逐场景结果、证据及人工确认查对应测试报告；初次记录使用[Test Report](../.agents/sdd/assets/test_report_template.md)，Status／Plan 引用报告并记录进度。

- **发现了哪些 Bug，修复后是否已复验关闭？** 沿用 [Issue](../.agents/sdd/assets/issue_template.md) 及编号。评估、归因和派单见 [sdd-bugfix](../.agents/skills/sdd-bugfix/SKILL.md)，修复方案查 [实施与局部自验](../.agents/sdd/references/implementation.md) 的 Plan／Task，关单依据查原 Issue 引用的局部或集成验证证据。

- **项目的 Code Review Rules 在哪里？** 用户决定维护时机，通过 [sdd-documenter](../.agents/sdd/references/delegation.md#文档交接) 按[Code Review Rules](../.agents/sdd/assets/code-review-rules_template.md)生成或更新；首次生成后将此处指向项目规则正文。

- **Code Review Rules 是否落实，检查项偏差是否修复并复核？** 查 Architecture Review Record；初次落盘使用 [Architecture Review Record](../.agents/sdd/assets/review_template.md)，修复方案引用 实施的 Plan／Task。

- **本轮改什么、按什么顺序执行？** 查当前 Plan（Task 清单）；输出结构见 [Plan](../.agents/sdd/assets/plan_template.md)，生成与执行规则见 [实施与局部自验](../.agents/sdd/references/implementation.md)。

- **如何提交、推送或部署？** 使用 [sdd-deliver](../.agents/skills/sdd-deliver/SKILL.md)。启动或重启服务时，从项目运行指南与环境配置定位实际入口。

- **文档写后如何检查？** 使用[文档校验 CLI](../.agents/sdd/references/doc-check.md)检查选定范围的机械问题，语义核对由 sdd-documenter 完成。
