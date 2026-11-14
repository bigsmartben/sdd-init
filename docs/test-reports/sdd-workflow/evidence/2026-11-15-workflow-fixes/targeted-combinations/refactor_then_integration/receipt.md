两个阶段均已完成，改动保留在当前隔离项目，未提交 Git。

- **付款整改完成**：`mark_paid` 改为调用现有服务写入；原违规项复核 PASS，公开行为保持检查及局部测试 5/5 通过。
- **完整 Review Gate：UNVERIFIED**：部分适用条款缺少项目规则映射，待授权维护后复核；不影响本地集成开测。
- **集成 Test Gate：FAIL**：13 项中 11 PASS、1 FAIL、1 BLOCKED。AC-2 取消后提交仍返回 `true / submitted`，已登记缺陷；AC-3 缺外部端点及授权，保留待验。

交付文件：[架构审查记录](docs/test-reports/order/payment-alignment-review.md)、[Plan](specs/order/payment-alignment-plan.md)、[集成报告](docs/test-reports/order/payment-integration.md)、[复跑指南](specs/order/quickstart.md)、[ISSUE-001](docs/issues/ISSUE-001.md)。

后续通过条件：获授权修复 AC-2 并复验，补齐 AC-3 真实外部证据，以及完成规则映射复核。文档检查与 `git diff --check` 均通过。