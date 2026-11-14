# 当前任务：新建订单号空白校验

## 确认与范围

2026-11-15，用户确认 A：“已确认空或全空白订单号按空字符串处理：拒绝且不创建订单。合法订单号照常创建，其他订单行为保持。请先仅固化规格与方案，等待我确认后再交付实施。”该确认沿用此前呈现的场景：空格、制表符、换行、Unicode 空白均拒绝；合法编号的首尾空白原样保留。

2026-11-15，用户确认 B：“按刚才的范围、用户流程和已确认的就绪条件开始实施，并完成本轮隔离验收。”本次授权覆盖 T001 实施、局部自验和隔离点对点验收，不包含 Git 提交、其他订单缺陷修复或外部服务操作。

状态：T001 实施、局部自验及 sdd-develop 隔离点对点验收完成；AC-4、AC-5 通过，AC-1 必要回归通过。实际结果见本记录及证据引用。

需求正文为 [Spec](../specs/order/spec.md) AC-4、AC-5；本记录是原任务及同一份 Plan 的接续入口。适用[订单契约](contracts/order.md)与[蓝图](blueprint.md) ARC-1 至 ARC-4：保持服务层写入职责、文件 SQLite 持久化、正式实现与验证资产隔离、本地无网络调用。

保持函数签名、其他订单操作及合法编号原值；本任务不修复取消后提交等其他订单问题，不涉及外部服务或部署。既有 AC-1 至 AC-3 保持原义；AC-2、AC-3 本轮未执行，不宣称通过。

## 验收计划与方案

在 B 确认并完成实现后，由实施执行者局部自验，sdd-develop 从公开 `create_order` 调用入口逐项验收。环境沿用[本地验收指南](../specs/order/quickstart.md)的 Python 3.11+、标准库 SQLite；每个输入用新的临时文件数据库，预建一条 `BASELINE` 订单并记录全部行，结束后关闭连接并删除临时目录。

| 判据 | 输入与操作 | 观察点及通过条件 |
| --- | --- | --- |
| AC-4 空值 | 分别以 `""`、`" "`、`"   "`、`"\t"`、`"\n"`、`" \t\n "` 新建 | 每次抛出 ValueError，信息恰为 `order_id is required`；失败前后全部订单行一致，关闭重开数据库后亦一致。 |
| AC-4 Unicode 空白 | 分别以 `"\u00a0"`、`"\u3000"`、`" \t\u3000\n"` 新建 | 与上一行相同；不新增订单、不修改既有订单。 |
| AC-5 合法编号 | 分别以 `"ORDER-1"`、`" ORDER-1 "`、`"0"` 新建 | 新增一条 pending 订单；查询所得编号与输入完全一致；重开数据库后编号与状态仍一致，BASELINE 保持原样。 |
| AC-5 既有类型校验 | 分别以 `None`、`0`、`False` 新建 | 保持现有 ValueError 及相同错误信息；重开数据库后全部订单行与调用前一致。 |
| 直接受影响行为 | 执行既有 AC-1 入口及正常提交、mark_paid 持久化局部测试 | 依原判据核验；结果分别记录，不以新建校验通过替代其他行为结论。发现独立存量失败则带证据回报，不扩大修复。 |

局部检查采用 `python -B -m unittest discover -s tests -v`；AC-1 采用 `python -B checks/acceptance.py --scenario AC-1`。新增边界测试已落于 `tests/test_order.py`，分别覆盖空白、非字符串和合法编号；验收调用正式服务并核对文件数据库持久化。实际版本、命令及结果见下文。AC-2、AC-3 的修复、集成回归和外部验证不在本任务执行范围。

## 实施准备 Plan

### T001: 在新建入口拒绝全空白编号

- 依据：上述 AC-4、AC-5 验收方案及订单契约；实施前 `src/order_service.py` 的 `create_order` 仅拒绝非字符串和空字符串，校验后直接 INSERT、commit，未转换合法编号。
- 改动范围：实际仅调整 `src/order_service.py` 的新建校验，以及 `tests/test_order.py` 的对应边界与持久化验证；其他状态操作和配置保持。
- 实施方案：保留字符串类型检查与现有错误，在任何 SQL 写入前，用 `not order_id.strip()` 判断空或全空白；仅将该结果用于校验，INSERT 继续使用原始编号。边界测试对每个输入新建文件数据库和 BASELINE，比较调用前后及关闭重开后的全部订单行。Python 字符串空白判定覆盖上述 Unicode 数据。
- 依赖：用户明确确认 B；已于 2026-11-15 取得，见本记录确认与范围。
- 完成条件与局部自验：实现和边界测试覆盖本记录全部输入类别、相同错误语义、无新增及既有数据保持、合法原值持久化；执行上述局部检查和 AC-1，记录实际结果与范围外失败。
- 状态：Complete；实施、局部自验及独立点对点验收完成。
- 结果与证据：源提交 `5213fb89f831ab4bf3bee39a7161909e49dbae4f` 上的未提交工作树；实现／测试 SHA-256 见[实际版本](test-reports/order-id/local-version.json)。先补测试复现 8 个全空白子场景失败；实现后 `python -B -m unittest discover -s tests -v` 退出 0，5 个方法通过（新增 15 组编号输入与既有正常提交、mark_paid）；`python -B checks/acceptance.py --scenario AC-1` 退出 0，返回 true 且重开后 submitted。命令均将 TMPDIR 指向允许的 scratch。完整命令、失败／复验证据与覆盖见[局部自验报告](test-reports/order-id/local.md)。本批未出现其他失败；独立验收见下文，AC-2／AC-3 未运行且不据此声明通过。

## 隔离点对点验收结果

2026-11-15，由 /root/develop 在实施回执后独立执行。版本为上述源提交的未提交工作树，Python 3.12.3、SQLite 3.45.1；服务 SHA-256 为 `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`，与实施回执一致。

执行入口为项目根目录的 `python -B -` 标准输入脚本，TMPDIR 指向 `/tmp/sdd-review-execution-7z3ofaey/develop_delivery-ry89i00a/scratch`。脚本直接调用正式 `create_order`，逐一使用上表全部 15 个输入；每例建立独立文件数据库和 BASELINE，捕获错误并精确比较信息，比较当前全部行，再关闭重开数据库比较全部行，最后关闭并删除临时目录。脚本退出 0，[逐输入原始结果](test-reports/order-id/acceptance.json)记录环境、产品哈希和各例结果；可用现有 unittest 入口复跑同等输入及数据库断言，无新增长期测试脚手架。

| 判据 | 实测结果 | 证据 |
| --- | --- | --- |
| AC-4 | 9/9 PASS；空串、ASCII 与 Unicode 全空白均按相同异常拒绝，当前及重开后无新增、既有行不变。 | [独立验收 JSON](test-reports/order-id/acceptance.json) |
| AC-5 | 6/6 PASS；3 组合格字符串原样新增 pending 并持久化，3 组非字符串维持原拒绝结果与数据。 | [独立验收 JSON](test-reports/order-id/acceptance.json) |
| AC-1 必要回归 | PASS；复用相同产品哈希的真实文件 SQLite 局部证据，提交返回 true，关闭重开后 submitted。 | [AC-1 原始结果](test-reports/order-id/local-ac1.json)、[版本](test-reports/order-id/local-version.json) |
| 其他直接回归 | 正常提交与 mark_paid 持久化均 PASS；复用同版本的现有测试结果。 | [局部自验](test-reports/order-id/local.md) |

本轮独立验收 15 例全通过，必要回归证据适用于当前产品版本；无验收失败或新增范围外失败。AC-2 未运行，已知取消后提交的存量问题未修；AC-3 未运行，外部端点及授权缺口未处理。本轮结果仅证明上述范围，不形成集成 Test Gate 或架构 Review Gate。

## 接续条件

本轮已确认范围完成，可由 Main 交付未提交工作树及上述证据；没有剩余实施或验收待办。集成 Test Gate、Git 提交和发布不在本次授权范围；若后续开展，由 Main 按用户新授权接续。
