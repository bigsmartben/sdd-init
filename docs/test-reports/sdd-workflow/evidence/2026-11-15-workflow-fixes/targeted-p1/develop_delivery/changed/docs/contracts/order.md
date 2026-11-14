# 订单函数契约

输入数据库连接由调用者创建并最终关闭；新建订单编号须为包含非空白字符的字符串，其他操作的对象必须已经存在。编号校验范围与合法值保留规则以 [Spec](../../specs/order/spec.md) AC-4、AC-5 为准。

| 接口 | 结果与状态 |
|---|---|
| create_order(connection, order_id) | 合法编号原样创建 pending 并 commit；空字符串、全空白字符串或非字符串抛出 ValueError(`order_id is required`)，不执行订单写入。 |
| cancel_order(connection, order_id) | 持久化为 cancelled。 |
| submit_order(connection, order_id) | pending 时持久化为 submitted 并返回 true；cancelled 时不写入并返回 false。 |
| set_status(connection, order_id, status) | 现有服务写入入口，持久化给定合法状态；mark_paid 使用 paid。 |
| mark_paid(connection, order_id) | UI 适配函数，保持调用后 paid 的可观察结果，状态写入职责归服务。 |

不存在的订单抛出 ValueError；数据库异常向上传播，不转为成功。函数不进行网络操作、日志采集、重试或部署。
