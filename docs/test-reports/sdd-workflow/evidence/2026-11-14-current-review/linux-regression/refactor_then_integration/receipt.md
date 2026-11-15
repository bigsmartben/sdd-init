两个阶段已完成，改动未提交。

- 付款适配已改走现有服务入口，公开行为保持；6 项局部测试通过，CR-001 独立复核通过。
- **Review Gate：UNVERIFIED**，其余适用条款的项目规则映射仍待补齐。见[审查记录](docs/test-reports/order/payment-review.md)与[Plan／Task](docs/test-reports/order/payment-plan.md)。
- **Test Gate：FAIL**：15 个集成场景中，13 通过、1 失败、1 阻塞。取消后提交覆盖取消已登记为 [BUG-001](docs/issues/BUG-001.md)，未超范围修复；AC-3 缺端点和授权，保留待验。

[复跑指南](specs/order/quickstart.md)和[集成报告](docs/test-reports/order/integration.md)已交付。发布前仍需修复并复验 AC-2、补验真实外部回执，以及补齐规则映射复核。