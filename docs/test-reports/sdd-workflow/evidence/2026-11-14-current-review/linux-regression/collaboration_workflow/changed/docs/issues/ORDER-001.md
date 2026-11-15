# Issue — ORDER-001 取消订单被提交覆盖

## 1. Issue Facts

- **ID、类型**：ORDER-001，Implementation defect。
- **依据**：[Spec AC-2](../../specs/order/spec.md)；[契约](../contracts/order.md)。
- **发现**：2026-11-14，独立 sdd-test-loop；提交 `95cfcb31cf183d04b7ba1359a8dfe80d28608b00`，源哈希见[基线证据](../test-reports/order/evidence/baseline-integration.json)。
- **复现**：`python -B checks/integration.py --case AC-2`；文件 SQLite 新建订单、取消、提交、重开读取。预期 false/cancelled；实际 true/submitted。ISOLATION-1 中同样复现。
- **影响**：已取消业务状态被恢复为提交，阻断 AC-2。
- **验收方案**：原 AC-2 及 ISOLATION-1 恢复；AC-1、付款三种前态、缺失对象、数据库异常与恢复通过；完整集成按[指南](../../specs/order/quickstart.md)复跑。AC-3 独立阻塞，不作为本地缺陷修复证据。

## 2. Current Status

- **Assignee**：sdd-test-loop，独立复验已完成。
- **Fix Task**：[同一 Plan / T001](../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)。
- **Status**：Closed after retest。
- **Blockers and resumption conditions**：本地原判据及必要回归全部通过，无关单阻塞；AC-3 缺真实外部端点及权限，独立保留整轮 Test Gate BLOCKED。

## 3. Handling and Retest History

| Time / Actor | Action and outcome | Fix version / Task / Local verification evidence | Retest report or case and version | Status change and basis |
|---|---|---|---|---|
| 2026-11-14 / sdd-test-loop | 基线发现，交 Main 修复 | 不适用，尚未修复 | [基线结果](../test-reports/order/evidence/baseline-integration.json)，AC-2、ISOLATION-1 | Pending；公开入口实际失败 |
| 2026-11-14 / sdd-bugfix 与 sdd-coder | SQLite trace 显示取消已持久化，随后 submit 无条件 UPDATE/COMMIT；排除取消未落盘、重开读取及串单。修复为 cancelled 早返 false，保持其他既有前态。 | HEAD `95cfcb31` + 未提交修复；[T001](../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)；[修复前后局部证据与完整源哈希](../test-reports/order/evidence/bugfix-local.json) | 7/7 局部检查通过，含原场景无 UPDATE/COMMIT、未提交事务保持、AC-1、付款、缺失对象与数据库恢复；独立集成结果由原测试 Agent 归并 | Pending → Fixed, awaiting retest；局部通过，待独立证据关单 |
| 2026-11-14T15:15:58 UTC / 独立 sdd-test-loop | 原失败入口及必要回归通过；完整 14 项重跑，13 PASS、AC-3 BLOCKED；7/7 单测通过 | HEAD `95cfcb31` 加未提交修复，实际源哈希见[fixed 证据](../test-reports/order/evidence/fixed-integration.json)，运行前后源稳定 | [fixed 报告](../test-reports/order/fixed.md)，AC-2、ISOLATION-1 及全部本地回归 | Fixed, awaiting retest → Closed after retest；原判据与必要回归满足，无必需人工反馈；AC-3 外部阻塞不改变本地 Issue 关单范围 |

## 4. Related References

[集成基线证据](../test-reports/order/evidence/baseline-integration.json)、[原验收入口证据](../test-reports/order/evidence/baseline-acceptance.json)。
