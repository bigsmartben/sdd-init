# WO-ORDER-004 Plan

依据 [原工单](order-work-order.md)、[订单 Spec](../specs/order/spec.md) AC-4、[订单接口](contracts/order.md) 的 `create_order` 条款和[验收指南](../specs/order/quickstart.md)。本轮仅增加新建入口的空白编号校验，保持函数签名、合法编号原值及其他状态操作。

T001 调查时，入口 `src/order_service.py:create_order` 已拒绝空字符串和非字符串，但全空白字符串会写入并提交。T002 已在 SQL 执行前检查字符串的 `strip()` 结果，只作有效性判断，不修改合法编号。局部测试使用临时 SQLite 文件，覆盖拒绝异常、同连接及重开数据库后的无写入、合法编号保存 pending，并运行现有单测。

## 任务清单

| Task | 完成条件 | 直接依赖 | 状态 |
| --- | --- | --- | --- |
| T001 | 定位新建公开入口及局部测试 | 无 | 已调查，见 `src/order_service.py`、`tests/test_order.py` |
| T002 | 新建入口拒绝全空白并保留正常创建，运行定向测试 | T001 | 完成 |

### T001: 定位公开入口与局部测试

- 范围：`src/order_service.py`、`tests/test_order.py`，只读定位。
- 实施与结果：沿用已调查结果；公开入口为 `create_order(connection, order_id)`，测试通过标准库 unittest 运行，无需安装依赖。
- 完成条件：定位 AC-4 的写入点与局部测试入口；已满足，无直接依赖。

### T002: 实施 AC-4 并局部自验

- 依据：原工单 AC-4 与订单接口的新建条款。
- 改动范围：`src/order_service.py`、`tests/test_order.py` 及本 Plan。
- 实施：先补空字符串、空格、制表符、换行组合及合法编号的测试，确认空白缺口，再在原校验中使用 `strip()`，不调整 SQL、提交或其他状态逻辑。
- 直接依赖：T001 已定位入口与测试，已满足。执行顺序为 T001 → T002；同一实现文件串行修改。
- 完成条件与局部验证：拒绝输入抛出 `ValueError`，数据库不新增订单且已有订单保持；合法编号（含边缘空白）原样持久化为 pending；运行 `python -B -m unittest discover -s tests -p test_order.py -k create_order -v` 及 `python -B -m unittest discover -s tests -v` 均通过。
- 状态：完成。
- 实际改动：`create_order` 在执行 SQL 前使用 `not order_id.strip()` 拒绝空或全空白字符串，保留原有非字符串拒绝行为。单测新增拒绝场景的异常与无写入检查，以及正常编号和带边缘空白的合法编号原样保存 pending 的检查；均核对当前连接与重开连接。
- 版本：基于 HEAD `7943f41f342ca7e11011db7b65f644e2bbb96f23` 的未提交工作树，未执行 Git 写操作。2026-11-14 本地临时 SQLite 文件执行。
- 实测文件 SHA-256：`src/order_service.py` 为 `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`；`tests/test_order.py` 为 `95b7a63950ddbfdf110285722888164962137a9fb27569cb5bffa81102a6c693`。
- 缺口复现：实现修改前，`python -B -m unittest discover -s tests -p test_order.py -k create_order -v` 退出 1，2 项测试中的全空格、制表符、制表符与换行组合共 3 个子场景报 `ValueError not raised`；合法编号测试通过。
- 修复后证据：同一定向命令退出 0，2 项通过；`python -B -m unittest discover -s tests -v` 退出 0，4 项通过，包含既有正常提交与 paid 持久化检查。局部覆盖 AC-4 的拒绝、不写入、合法编号 pending，以及正常提交和 paid 行为回归。

## 交付核对

- 目标覆盖：T001、T002 已完成；实现和单测限于本工单的新建行为，函数签名及其他状态逻辑未改动，无实施阻塞。
- 独立验收：据调度方回传，Main 已从公开入口复跑 AC-4，结果 PASS；技能 Agent 补验 AC-4、AC-1 均 PASS，AC-1 提交返回 true，重开数据库为 submitted。实际执行及版本证据见[原工单验收记录](order-work-order.md#验收记录)，运行入口见[验收指南](../specs/order/quickstart.md)。
- 未验边界：AC-2 取消后提交及真实外部服务 AC-3 未由本批次验证，既有完整单测不覆盖这两项，不扩大本工单范围。
- 文档核对：保留原 Plan 与 T001/T002 编号，链接权威 AC-4 和契约，区分调查事实、失败复现、局部通过及独立验收。机械检查命令 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-plan.md docs/order-work-order.md specs/order/spec.md docs/contracts/order.md specs/order/quickstart.md`；首次 0 错误、1 项标题层级警告，补齐任务清单标题后复查为 0 错误、0 警告；本次验收证据归并后复查同为 0 错误、0 警告。
