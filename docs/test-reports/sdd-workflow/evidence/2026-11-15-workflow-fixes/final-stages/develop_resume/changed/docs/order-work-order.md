# WO-ORDER-004

已完成需求落盘前及交付实施前确认。适用依据为 [订单 Spec](../specs/order/spec.md) 和 [订单接口](contracts/order.md)。

AC-4 在本地测试数据库从公开新建入口依次提交空字符串、全空格、制表符及换行组合。应报告拒绝，查不到对应订单。合法编号应创建并保存 pending 订单。门槛为空或全空白，保持有效编号、函数签名与其他状态操作。

验收由 Main 在实现版本就绪后从公开入口执行，使用独立临时数据库，记录调用结果、持久化状态、实际版本及复跑入口。

## 实施及验收结果

状态：已完成实施及点对点验收。需求与实施确认沿用本轮用户明确重申的既有确认，范围仍为 AC-4；实施及局部证据见[原 Plan](order-plan.md)。

Main 于 2026-11-15 在当前隔离项目执行正式验收。实际版本为基线 `515346f27a84fb0d8158303d7da385a8a53d0598` 加本轮未提交改动；`src/order_service.py` SHA-256 为 `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`。实际组件为 Python 3.12.3、SQLite 3.45.1 与公开 `create_order` 入口，每个场景使用独立临时 SQLite 文件，检查后关闭连接并自动清理；没有模拟数据库结果。环境取证入口为 `python -B checks/runtime_details.py`。

修复前，Main 运行 `python -B checks/acceptance.py --scenario AC-4`，退出码 1：空串已拒绝；全空格、制表符及混合空白未拒绝并持久化为 pending；两项合法编号通过。修复后使用同一入口复验：

| 判据 / 输入 | 实际结果 | 结论 |
| --- | --- | --- |
| AC-4：空串、三个空格、制表符、制表符/换行/空格/回车组合，共 4 例 | 每例均抛出 ValueError；当前连接与重开连接均返回空订单集合 | 4 例通过 |
| AC-4：`ORDER-4`、两端含空白的合法编号，共 2 例 | 重开连接后读到原样编号及 pending | 2 例通过 |
| 直接受影响的正常新建后提交，AC-1 | 返回 true，重开连接读到 submitted | 通过 |

正式复跑入口见[本地验收指南](../specs/order/quickstart.md)：`python -B checks/acceptance.py --scenario AC-4` 和 `python -B checks/acceptance.py --scenario AC-1`，本轮均退出 0。Main 另运行 `python -B -m unittest discover -s tests -v`，4 项全部通过，覆盖拒绝后保留已有订单、合法创建、正常提交及 paid 持久化。产品代码只修改新建入口的空白判定，函数签名和其他状态操作保持。

本工单 6 个 AC-4 用例及 1 个直接回归用例全部通过，无未完成判据，无需人工体验判断。本结果限于 WO-ORDER-004 的本地点对点验收；AC-2、AC-3 不属本轮，未执行。本轮未访问外部平台、网络服务或真实部署，未创建 Git 提交。后续可在此工作树使用上述命令复验和集成。
