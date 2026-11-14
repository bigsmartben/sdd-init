# 订单编号 T001 局部自验

## 1. 目标与依据

2026-11-15，由 /root/develop/coder 执行实施者局部自验，回执接收方 /root/develop。依据为[原任务及验收方案](../../status.md)、[Spec](../../../specs/order/spec.md) AC-4、AC-5，以及 AC-1 直接受影响回归。

## 2. 范围与计划

覆盖 9 组空或全空白、3 组非字符串、3 组合法编号及既有正常提交、mark_paid 持久化；按原方案核对异常原文、既有行保持、合法原值与重开数据库后的持久化。B 已授权实施及隔离验收，本报告只记录局部自验；独立点对点验收由 sdd-develop 另行执行。AC-2、AC-3 不在本批范围。

## 3. 环境与版本

Python 3.12.3、SQLite 3.45.1，标准库真实文件 SQLite，无替代服务、网络调用或部署。源提交 `5213fb89f831ab4bf3bee39a7161909e49dbae4f`，本项目未提交工作树；修改 `src/order_service.py` 一行校验并补充 `tests/test_order.py`。绝对工作树路径及最终文件 SHA-256 见[版本记录](local-version.json)。AC-1 执行后仅加强测试错误信息的精确相等断言，产品文件未再改变。

## 4. 数据与准备

新增每个输入均用新的临时文件数据库，预建 pending 的 BASELINE；测试拒绝后比较全部行，关闭并重开再比较。合法值验证恰新增一行 pending，编号原值保留。全部临时目录位于授权 scratch，由 TemporaryDirectory 退出时清理，连接在 finally 或清理钩子关闭。无准备缺口。

## 5. 执行与覆盖统计

以下命令均从项目根执行，并设置 `TMPDIR=/tmp/sdd-review-execution-7z3ofaey/develop_delivery-ry89i00a/scratch`，`-B` 禁用 pycache。

- 补测试后的修复前批次：`python -B -m unittest discover -s tests -v`，退出 1，8 个全空白子场景因未抛 ValueError 失败，其他场景通过；[原始输出](local-before.txt)。
- 修复后最终批次：同一命令退出 0，5 个测试方法通过；[原始输出](local-after.txt)。按输入与既有行为计 17 例，Pass 17、Fail 0、Not run 0、Blocked 0。
- AC-1：`python -B checks/acceptance.py --scenario AC-1`，退出 0，1 例 Pass；[原始输出](local-ac1.json)。

最终批次合计 18 例全通过；5 个 unittest 方法与其中 15 个参数子场景不重复计数。AC-4、AC-5 全部计划输入均完成局部验证，独立验收尚待调度方执行。

## 6. 逐项结果

| Case / 依据 | 数据及方法 | 预期与实际 | 结论 | 证据 |
| --- | --- | --- | --- | --- |
| L01 / AC-4 | `test_blank_ids_are_rejected_without_writes`；空串、单空格、多空格、制表、换行、混合 ASCII、NBSP、全角空格、Unicode 混合，共 9 例 | ValueError 原文精确相等；当前及重开后全部行保持，均符合 | Pass | [测试及输出](local-after.txt) |
| L02 / AC-5 | `test_non_string_ids_keep_existing_rejection`；None、0、False，共 3 例 | 相同异常与信息、数据保持，均符合 | Pass | [输出](local-after.txt) |
| L03 / AC-5 | `test_valid_ids_are_preserved_and_persisted`；ORDER-1、首尾带空格编号、字符串 0，共 3 例 | 原值新增 pending，当前及重开后全部行精确匹配，BASELINE 保持，均符合 | Pass | [输出](local-after.txt) |
| L04 / 直接回归 | `test_normal_submit`，1 例 | true、submitted，符合 | Pass | [输出](local-after.txt) |
| L05 / 直接回归 | `test_mark_paid_is_persisted`，1 例 | 新连接读取 paid，符合 | Pass | [输出](local-after.txt) |
| L06 / AC-1 | 文件数据库新建、提交、关闭重开，1 例 | true、submitted，符合 | Pass | [JSON](local-ac1.json) |

## 7. 问题与影响

修复前的 8 个失败对应本次明确的全空白校验缺口，修复后通过，失败证据保留。未观察到其他失败。取消后提交问题属于既有范围外行为，本批未执行 AC-2，未修复或宣称通过；AC-3 未执行，不推定外部结果。无新增 Issue。

## 8. 结论与局限

T001 实施与局部自验完成；合法编号继续原值入库，类型与错误语义保持。待 sdd-develop 按原方案独立执行 AC-4、AC-5 点对点验收。无 UI，人工视觉确认不适用。本报告不是集成 Test Gate，也不代表 AC-2、AC-3 或外部环境验证通过。

文档写后核对：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/status.md docs/test-reports/order-id/local.md` 退出 0，2 文件、0 错误、0 警告；[输出](local-doc-check.txt)。已对照 Spec、契约及实际命令检查本报告与 T001 的语义及链接，`git diff --check` 通过。Status 其他章节由调度方同步执行进展。机械检查不替代独立验收。
