已完成本轮付款整改与复核，公开调用行为保持。

- 付款适配改为经 `order_service.set_status` 写入；代码和测试改动仅涉及付款适配及相关局部测试。
- 付款架构检查项复核 **PASS**，四项行为保持检查通过；局部测试 **5/5 通过**，文档校验通过。
- 整体 **Review Gate：UNVERIFIED**。ARC-2～4 缺少项目规则映射，待你决定规则维护时机。

候选为 `d6c721f` 加本轮四项工作区改动，未提交 Git。付款场景具备本地开测条件；取消后提交已实测存在原有偏差，需另行授权修复、复验；外部场景缺端点及授权。本轮未判定集成 Test Gate 或发布资格。

交付：[Architecture Review Record](docs/test-reports/payment/pre-release-review.md) · [Plan／Task](specs/order/payment-refactor-plan.md)