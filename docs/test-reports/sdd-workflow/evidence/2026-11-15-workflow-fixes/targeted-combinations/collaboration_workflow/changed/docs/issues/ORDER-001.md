# Issue — ORDER-001 取消订单被提交覆盖

## 1. 问题事实

- 类型：实现缺陷。依据 [Spec AC-2](../../specs/order/spec.md) 和 [订单契约](../contracts/order.md)。
- 首次发现：2026-11-14T16:21:34Z，独立测试 Agent `/root/integration`；提交 a8f4cf7154b9e81d9b4ab62b8cd0cecddb36eec5，产品源文件无未提交改动，本地 Python + 文件 SQLite。
- 复现：`python -B checks/order_regression.py --scenario AC-2`。新建 ORDER-1、取消、提交，关闭并重开文件数据库。预期 false/cancelled；实际 true/submitted。
- 影响：取消保护失效，直接阻止 AC-2 验收。[原始证据](../test-reports/order/initial-results.json)、[初测报告](../test-reports/order/initial.md)。

## 2. 当前状态

- 负责人：Bugfix `/root/bugfix`，实际调用者 Main `/root`。
- Fix Task：[order-fixes T001](../plans/order-fixes.md)。
- 状态：Closed。
- 关闭依据：[修复版本定向报告](../test-reports/order/bugfix-verification.md)、[逐项证据](../test-reports/order/bugfix-results.json)、[实际快照](../test-reports/order/bugfix-snapshot.json)；原场景及必要回归通过。原测试 Agent 已完成 [独立全量复验](../test-reports/order/retest.md)，其 [实际快照](../test-reports/order/retest-snapshot.json) 与修复候选源哈希完全一致；11 个本地场景通过。整轮 Test Gate 为 BLOCKED，仅因 AC-3 缺真实外部端点与授权，不影响这两个本地缺陷关闭。
- 验收方案：沿用 [指南](../../specs/order/quickstart.md) AC-2 的公开 submit 入口、返回 false、重开后 cancelled；同时回归 AC-1、新建、取消、paid、异常传播、不存在对象。已验证归因与实施见 [T001](../plans/order-fixes.md)。

- 本轮验收计划与方案：由 Bugfix 在实际修复快照按 [T001](../plans/order-fixes.md) 的前置、公开入口、观测及通过判据执行原场景和受影响回归；Main 续派原测试 Agent 做独立集成复验。归因、写入/commit 边界及版本取证见同一 Plan。

## 3. 处理与复验历史

| 时间 / 执行者 | 动作与结果 | 修复版本 / Task / 局部证据 | 复验报告与版本 | 状态依据 |
| --- | --- | --- | --- | --- |
| 2026-11-14T16:21:34Z / integration | 初次实测 AC-2 失败，已报 Main | 无修复 | [初测](../test-reports/order/initial.md)，a8f4cf7 | 新建 Pending |
| 2026-11-14T16:24:37Z / bugfix | 验证直接因果并恢复既定行为，原场景及必要回归通过 | [T001](../plans/order-fixes.md)、[归因证据](../test-reports/order/bugfix-diagnosis.json)、[修复快照](../test-reports/order/bugfix-snapshot.json) | [定向报告](../test-reports/order/bugfix-verification.md)，a8f4cf7 + src/tests 未提交修复 | 获授权按齐备定向证据关闭；整体 Gate 独立判定 |
| 2026-11-14T16:25:12.976119+00:00 / integration | 原 AC-2 恢复 false/cancelled；total_changes=0，trace 仅 SELECT；AC-1 及完整本地回归通过 | [修复实际快照](../test-reports/order/retest-snapshot.json)，HEAD a8f4cf7 + 未提交修复；执行前后源哈希稳定 | [完整复验](../test-reports/order/retest.md)、[逐项结果](../test-reports/order/retest-results.json) | 保持 Closed；原场景与必要回归证据齐备，AC-3 独立阻塞 |

## 4. 相关引用

[Spec](../../specs/order/spec.md)、[指南](../../specs/order/quickstart.md)、[初测](../test-reports/order/initial.md)。无外部平台操作。
