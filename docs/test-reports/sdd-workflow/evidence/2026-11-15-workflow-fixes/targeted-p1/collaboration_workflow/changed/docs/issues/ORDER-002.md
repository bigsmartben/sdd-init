# Issue — ORDER-002 公开付款对缺失订单静默成功

## 1. Issue Facts

- **编号与类型**：ORDER-002，已复现实现缺陷。
- **依据**：[订单契约](../contracts/order.md) 不存在订单抛 ValueError，公开接口 mark_paid。
- **发现版本**：HEAD `fc366da8aff900abc000129676514d994ca5c671`，产品源码无改动；隔离本地 Python 3.12.3 / SQLite 3.45.1。
- **复现**：`python -B tests/order_regression.py --case O-14`；新文件 SQLite 建 ORDER-1，调用 `ui.mark_paid(connection, "MISSING")`。
- **预期**：抛 ValueError，既有行 pending 且不创建 MISSING。
- **实际**：无异常（exception=null），未创建行，原有行 pending；调用者无法得知订单缺失。
- **证据与影响**：[首轮补充原始输出](../test-reports/order/evidence/initial-regression.json) O-14；公开付款缺失对象的错误语义与契约不符。

## 2. Current Status

- **已验证归因与边界**：`ui.mark_paid` 直接 UPDATE/commit，缺失行更新零条仍正常返回；未经过服务的 `read_status`，与首轮 O-14 一致。恢复通过既有 `order_service.set_status(..., "paid")` 检查存在性并写入；保持现存订单 paid 持久化、签名、数据库异常传播及无网络行为，沿用 ARC-1，不改变架构约束。

- **Assignee**：Bugfix 技能 Agent `/root/order_bugfix`；实施角色 `/root/order_bugfix/implement`。
- **Fix Task**：[同一修复 Plan](../plans/order-bugfix.md)。
- **Status**：Closed after retest。
- **恢复条件**：本缺陷无剩余关单缺口；[定向复验](../test-reports/order/bugfix.md) 已证明原场景及必要回归恢复。原测试 Agent 已完成[独立全产品集成复验](../test-reports/order/retest.md)，22 个本地场景通过；整轮 Gate 因 AC-3 外部证据缺口为 BLOCKED，与本缺陷关闭分别判定。
- **验收计划与方案**：实施者先定向自验 O-14；原测试 Agent 在修复后实际快照重跑 [Quickstart](../../specs/order/quickstart.md) 全量，尤其 O-07/08/09 现存订单付款持久化、O-10～14 缺失对象无副作用、O-15～20 数据库异常传播，以及 AC-1/2。O-14 必须抛 ValueError、行保持；架构内部状态写入归属由 Main 单独 Review，不以架构结论代替本业务验收。

## 3. Handling and Retest History

| Time / Actor | Action and outcome | Fix version / Task / Local verification evidence | Retest report or case and version | Status change and basis |
|---|---|---|---|---|
| 首轮 UTC 见证据 / order_test | O-14 实测 missing 付款不抛异常 | 未修复 | [initial-regression](../test-reports/order/evidence/initial-regression.json)，HEAD fc366da | Pending，公开契约不符 |
| 修复批次 UTC 见证据 / order_bugfix | 归因、修复及原场景定向复验通过，必要回归通过 | [Plan T001](../plans/order-bugfix.md)，[实际修复指纹](../test-reports/order/evidence/bugfix-local-version.json) | [定向报告](../test-reports/order/bugfix.md)，[原始证据](../test-reports/order/evidence/bugfix-retest.json) | Pending → In progress → Closed after retest；原故障恢复、必要回归与副作用检查齐备 |
| 独立集成复验 UTC 见证据 / order_test，经 Main 回传 | 原故障恢复，23 场景 22 PASS / 0 FAIL / 1 BLOCKED（仅 AC-3），另 2 单测 PASS | 与修复快照指纹一致，执行前后产品与验证资产不变，见[版本证据](../test-reports/order/evidence/retest-version-after.json) | [独立全量复验报告](../test-reports/order/retest.md)，同一实际修复快照 | 保持 Closed after retest；独立复验补充原场景及完整本地回归关闭依据；AC-3 环境阻塞不影响本缺陷判据 |

## 4. Related References

[首轮报告](../test-reports/order/initial.md)、[取消提交缺陷](ORDER-001.md)。
