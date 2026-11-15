付款路径整改已完成：`mark_paid` 改为调用现有服务 `set_status`，公开调用行为保持。代码和测试改动限于付款适配及局部测试。

- CR-001 架构复核、付款行为保持验收均 **PASS**；局部测试 5/5 通过。
- 整体 **Review Gate 为 UNVERIFIED，尚未通过**：CHK-002～006 缺少有效项目规则映射，需决定规则维护时机后复核。
- 已查证既有缺陷：取消后提交仍返回 `true`、写入 `submitted`。本轮未修复，需另行授权处理。

集成准备条件：补齐规则映射并复核、处理上述缺陷、固定最终候选后完成全功能集成回归及 Test Gate。本轮未执行全产品集成、提交或发布。

证据与计划：[Architecture Review Record](docs/test-reports/payment/2026-11-14-review.md)、[Plan／Task](docs/payment-refactor-plan.md)。