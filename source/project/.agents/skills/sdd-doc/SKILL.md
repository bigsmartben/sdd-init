---
name: sdd-doc
description: 将已确认对话结论和执行证据归并到对应文档，完成写入一致性检查；纯讨论不触发。
---

# 对话结论落盘

输入：已确认结论或真实执行证据、授权写入范围。新建或需定位正文时查[文档与产物落点](../../sdd/references/sdd-repository-governance.md#文档与产物落点)。

1. 按[权威实体](../../sdd/references/sdd-repository-governance.md#权威实体)确定确认结论或证据应归并的正文。
2. 读取[文档写入规则](../../sdd/references/document-writing.md)的通用步骤和[本轮对象](../../sdd/references/document-writing.md#按对象读取与语义核对)对应行，按语义影响读取适用上游，完成归并、关联同步和写后核对；模板只提供输出结构与填写约束，不扩大职责或授权。
3. 根据事实对象分别写入：测试活动按[测试报告模板](../../sdd/assets/test_report_template.md)，问题生命周期按[Issue 模板](../../sdd/assets/issue_template.md)，架构一致性按 [Review 模板](../../sdd/assets/review_template.md)。按相应模板核对结构与填写要求；修复状态取自 imp 返回，关闭取自验收／复核执行者，Gate 取自对应流程执行者，人工确认取自用户反馈。归并到已定位的权威正文，已有记录沿用，不自动迁移历史。
4. 写后按[文档 CLI](../../sdd/references/doc-check.md)对本次修改及直接受影响的 Markdown 执行机械校验，处理或报告诊断；另行完成语义核对，不用 CLI 通过代替语义判断。
5. 输出实际落点、关键归并、检查范围与结果及待决问题。缺少确认依据时返回讨论，不自行补定。

用户明确要求生成或更新 Code Review Rules 时，读取[目标仓库的 Code Review Rules](../../sdd/references/sdd-repository-governance.md#目标仓库的-code-review-rules)的决策边界，并按默认落点或项目映射定位正文。对照[架构原则](../../sdd/references/architecture-rules.md)、已确认的 Blueprint 和契约，按[项目规则模板](../../sdd/assets/code-review-rules_template.md)将适用原则写成针对本项目入口和职责的可检查约束。同义规则原位归并，保留稳定标识；逐项核对受影响条款，明确撤销的约束从现行规则中移除。缺乏设计依据的归属或冲突列为待决。仅维护规则内容，执行证据归 Review。

需要角色交接时读取[执行协作](../../sdd/references/delegation.md)，按工作批次归并关联证据，简单任务沿用当前任务或既有载体并保留必备结构；正式记录仍按各流程完成要求归并。普通写入不加载实施、验收或交付流程。

例：正文已有“在线请求超时 5 秒，离线任务不受此限”，对话确认在线超时改为 10 秒。原位更新为 10 秒，保留离线例外，同步引用该限制的关联条款，不追加第二份规则。
