# 订单函数契约

输入数据库连接由调用者创建并最终关闭；订单编号为含有非空白字符的字符串，对已有订单的操作要求对象已经存在。

| 接口 | 结果与状态 |
|---|---|
| create_order(connection, order_id) | 合法编号按原样创建 pending 并 commit，成功返回 None。空字符串、全空白字符串或非字符串均抛出 `ValueError("order_id is required")`，不得新增或更改订单；合法编号的首尾空白不去除。 |
| cancel_order(connection, order_id) | 持久化为 cancelled。 |
| submit_order(connection, order_id) | pending 时持久化为 submitted 并返回 true；cancelled 时不写入并返回 false。 |
| set_status(connection, order_id, status) | 现有服务写入入口，持久化给定合法状态；mark_paid 使用 paid。 |
| mark_paid(connection, order_id) | UI 适配函数，保持调用后 paid 的可观察结果，状态写入职责归服务。 |

不存在的订单抛出 ValueError；数据库异常向上传播，不转为成功。函数不进行网络操作、日志采集、重试或部署。

订单号校验依据 [Spec 的 AC-4、AC-5、AC-6](../../specs/order/spec.md)。其实现状态和实施授权见 [Plan](../../specs/order/plan.md)，契约不代表实现已通过验收。
