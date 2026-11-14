# WO-ORDER-004 Plan

依据 [原工单](order-work-order.md) 与 AC-4。

| Task | 完成条件 | 直接依赖 | 状态 |
| --- | --- | --- | --- |
| T001 | 定位新建公开入口及局部测试 | 无 | 已调查，见 `src/order_service.py`、`tests/test_order.py` |
| T002 | 新建入口拒绝全空白并保留正常创建，运行定向测试 | T001 | 已完成；实施、局部自验及 Main 正式验收均通过 |

T002 依据 [AC-4](../specs/order/spec.md) 及[订单接口](contracts/order.md)，修改范围为 `src/order_service.py`、`tests/test_order.py`。在写入前保留类型检查并以 `order_id.strip()` 判空；判定不改变合法编号原值，保持函数签名及其他状态操作。

局部自验覆盖空串、全空格、制表符及换行组合拒绝；拒绝前后的当前连接及重开连接订单集合应一致；普通合法编号及两端含空白但包含非空白字符的编号应原样保存 pending。先新增定向测试验证缺口，再实施及复跑：

```sh
python -m unittest tests.test_order.OrderTests.test_create_rejects_blank_order_ids_without_writing tests.test_order.OrderTests.test_create_preserves_valid_order_ids_and_pending_status -v
```

执行顺序为 T001 → T002，无可并行的实施 Task。Main 已按[原工单验收方案及正式结果](order-work-order.md)从公开入口使用独立临时数据库完成验收：AC-4 及 AC-1 均通过，并重跑 4 项单测通过；实现源文件摘要与下列回执一致。

实施与局部证据由独立 `sdd-coder` 回传并核对：新增测试在实现前执行 2 项，其中 3 个全空白子场景因未抛出 ValueError 失败；实现后在 Python 3.12.3 执行 `python -m unittest discover -s tests -p test_order.py -v`，4 项全部通过，包含拒绝且无写入、合法编号原样 pending、原有正常提交及 paid 持久化测试。`git diff --check` 通过。实际改动与上述两文件范围一致，其他状态操作未改。

本轮实现版本为基线 `515346f27a84fb0d8158303d7da385a8a53d0598` 加工作树改动。SHA-256：`src/order_service.py` 为 `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`；`tests/test_order.py` 为 `cedc5c46e819257330b0959fc81d6da6311a31cbfbce60402326f962e3c88901`。无实施阻塞；正式 AC-4 结果归 Main 的[原工单记录](order-work-order.md)，复跑入口见[本地验收指南](../specs/order/quickstart.md)。
