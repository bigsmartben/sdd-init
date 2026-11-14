已完成付款路径整改：`mark_paid` 改用现有 `set_status`，保持公开调用行为。架构复核 PASS；付款局部测试 5/5、独立公开调用验收 3/3 通过。

整体 **Review Gate＝UNVERIFIED**：ARC-2～4 缺项目规则映射，需决定维护时机后按原检查项续审。

候选为 `b5c9315` 加当前未提交改动。付款本地可测，需 Python 3.11+、SQLite、可写临时目录及含现存订单的连接。集成限制：

- AC-2 取消后提交仍覆盖状态，已实测失败；需另行修复、复验。
- AC-3 缺端点及授权，保持阻塞。
- 本轮未执行完整集成测试或发布。

交付：[审查记录](docs/test-reports/payment/pre-release-review.md)、[Plan／Task](docs/payment-refactor-plan.md)。改动限于授权文件。