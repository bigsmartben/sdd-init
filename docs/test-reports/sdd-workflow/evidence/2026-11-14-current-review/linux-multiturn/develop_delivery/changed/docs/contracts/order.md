# 订单函数契约

输入数据库连接由调用者创建并最终关闭；订单编号规则见 [Spec](../../specs/order/spec.md) AC-4、AC-5。调用方传入原始编号，由服务校验；除新建外，操作对象必须已经存在。状态写入归属遵循[蓝图](../blueprint.md) ARC-1、ARC-2。

| 接口 | 结果与状态 |
|---|---|
| create_order(connection, order_id) | 空字符串、全空白字符串及非字符串抛出 ValueError("order_id is required")，不新增或改变订单；合法编号保留原值，创建 pending 并 commit。 |
| cancel_order(connection, order_id) | 持久化为 cancelled。 |
| submit_order(connection, order_id) | pending 时持久化为 submitted 并返回 true；cancelled 时不写入并返回 false。 |
| set_status(connection, order_id, status) | 现有服务写入入口，持久化给定合法状态；mark_paid 使用 paid。 |
| mark_paid(connection, order_id) | UI 适配函数，保持调用后 paid 的可观察结果，状态写入职责归服务。 |

不存在的订单抛出 ValueError；数据库异常向上传播，不转为成功。函数不进行网络操作、日志采集、重试或部署。
