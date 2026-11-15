# Issue — ORDER-002 mark_paid 缺失订单未抛异常

## 1. Issue Facts

- **ID、类型**：ORDER-002，Implementation defect。
- **依据**：[函数契约](../contracts/order.md)规定不存在订单抛出 ValueError；[Spec](../../specs/order/spec.md)保持现存订单 paid 与持久化结果。
- **发现**：2026-11-14，独立 sdd-test-loop；提交 `95cfcb31cf183d04b7ba1359a8dfe80d28608b00`；源哈希见[证据](../test-reports/order/evidence/baseline-integration.json)。
- **复现**：`python -B checks/integration.py --case MISSING-1`；空文件数据库调用 `ui.mark_paid(connection, 'MISSING')`；预期 ValueError，实际无异常。其他四个读取／变更入口正确抛出 ValueError。
- **影响**：公开付款适配入口将不存在的订单当作已处理，违背错误语义。
- **验收方案**：MISSING-1 原入口正确抛异常；PAID-1/2/3 保持现存订单持久化为 paid；DB-1 保持数据库异常传播；AC-1、AC-2、组合及恢复回归。按[指南](../../specs/order/quickstart.md)独立复跑。

## 2. Current Status

- **Assignee**：sdd-test-loop，独立复验已完成。
- **Fix Task**：[同一 Plan / T001](../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)。
- **Status**：Closed after retest。
- **Blockers and resumption conditions**：本地原判据及必要回归全部通过，无关单阻塞；AC-3 缺真实外部端点及权限，独立保留整轮 Test Gate BLOCKED。

## 3. Handling and Retest History

| Time / Actor | Action and outcome | Fix version / Task / Local verification evidence | Retest report or case and version | Status change and basis |
|---|---|---|---|---|
| 2026-11-14 / sdd-test-loop | 基线发现，交 Main 修复 | 尚未修复 | [基线结果](../test-reports/order/evidence/baseline-integration.json)，MISSING-1 | Pending；公开付款入口未抛契约异常 |
| 2026-11-14 / sdd-bugfix 与 sdd-coder | SQLite trace 显示 UI 对缺失行直接 UPDATE/COMMIT 且不检查存在性；修复委派既有 set_status，恢复 ValueError 与单一服务写入口。关联 [CHK-001 / CHK-005](../test-reports/order/local-review.md)，CR-001 / ARC-1。 | HEAD `95cfcb31` + 未提交修复；[T001](../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)；[修复前后局部证据与完整源哈希](../test-reports/order/evidence/bugfix-local.json) | 7/7 局部检查通过，含缺失对象五入口、三种现存前态 paid 持久化、数据库异常传播及恢复；独立集成结果由原测试 Agent 归并 | Pending → Fixed, awaiting retest；局部通过，待独立证据关单 |
| 2026-11-14T15:15:58 UTC / 独立 sdd-test-loop | 原失败入口及必要回归通过；完整 14 项重跑，13 PASS、AC-3 BLOCKED；7/7 单测通过 | HEAD `95cfcb31` 加未提交修复，实际源哈希见[fixed 证据](../test-reports/order/evidence/fixed-integration.json)，运行前后源稳定 | [fixed 报告](../test-reports/order/fixed.md)，MISSING-1、PAID-1/2/3、DB-1 及全部本地回归 | Fixed, awaiting retest → Closed after retest；原判据与必要回归满足，无必需人工反馈；AC-3 外部阻塞不改变本地 Issue 关单范围 |

## 4. Related References

[契约](../contracts/order.md)、[集成证据](../test-reports/order/evidence/baseline-integration.json)。架构写入职责的判断由独立架构 Review 承接。
