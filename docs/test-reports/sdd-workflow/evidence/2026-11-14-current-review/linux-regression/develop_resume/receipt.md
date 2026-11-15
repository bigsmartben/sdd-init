WO-ORDER-004 已完成实现和验收。

- 空或全空白订单号被拒绝，数据库无写入。
- 合法编号保留原值，正常保存为 `pending`。
- Main 最终 AC-4 验收、正常提交回归及 4 项单测均通过；文档检查通过。

证据已归并至[原工单](docs/order-work-order.md#验收记录)和[Plan](docs/order-plan.md)。改动未提交，仅操作当前隔离项目。

复跑：`python -B checks/acceptance.py --scenario AC-4`