# Issue — ORDER-001 取消订单被提交覆盖

## 1. 问题事实

- 类型：实现缺陷；发现者：独立集成测试 Agent `/root/order_integration`。
- 依据：[Spec](../../specs/order/spec.md) AC-2、[函数契约](../contracts/order.md) submit_order。
- 首次发现：2026-11-14 UTC，提交 `89df9f629407a6b572c6f65c87fc9768e0f52f5d`，src 无修改，隔离本地 Python 3.12.3 / SQLite 3.45.1。
- 复现：`python -B checks/acceptance.py --scenario AC-2`；真实临时文件数据库，新建 ORDER-1、取消、提交、关闭并重开。
- 预期：提交返回 false，状态保持 cancelled；实际：返回 true，重开后 submitted。
- 影响：取消保护失效，AC-2 不满足；AC-1 正常提交仍须保持。
- 原始证据：[AC 原始输出](../test-reports/order/evidence/initial-acceptance.json)、[初始集成报告](../test-reports/order/initial.md)。

## 2. 当前状态与验收计划

- 状态：Closed after retest（独立集成复验后关闭）；责任方：独立测试 Agent `/root/order_integration`，Main 授权状态写入；修复 Task：[T001](../../specs/order/plan.md#t001-恢复取消保护与-paid-入口契约)。
- 当前终点：原公开故障场景和全部必要本地回归在实际修复快照独立通过；依据 [修复后集成报告](../test-reports/order/fixed.md) 关闭。
- 点对点验收：复跑原 AC-2，记录取消后立即读回 cancelled、提交结果 false、关闭重开仍 cancelled；回归 AC-1、新建持久化、mark_paid、缺失订单异常、数据库异常和多订单隔离，步骤见 [Quickstart](../../specs/order/quickstart.md)。
- 剩余条件：本 Issue 无未完成的关单判据；无必需人工反馈。AC-3 外部授权阻塞独立保留，不影响两项本地缺陷关闭，整轮 Test Gate 仍 BLOCKED；架构 Review 独立判定。

## 3. 处理与复验历史

| 时间 / 执行者 | 操作和结果 | 修复版本 / Task | 测试报告及版本 | 状态变化依据 |
|---|---|---|---|---|
| 2026-11-14 UTC / 集成测试 Agent | 实测确认取消后被提交覆盖 | 尚无 | [初始报告](../test-reports/order/initial.md)，89df9f6 | 新建 Pending，等待跨阶段修复 |
| 2026-11-15 / Bugfix Agent 与 coder | 独立归因后按原判据修复，8项局部自验与17项独立定向复验通过 | [T001](../../specs/order/plan.md)，89df9f6 加工作区；实际源码哈希见报告 | [Bugfix 报告](../test-reports/order/bugfix.md)、[定向原始证据](../test-reports/order/evidence/bugfix-retest.json) | 已修复，待独立集成复验；保留首次失败与本轮证据 |
| 2026-11-14 UTC（后续执行顺序见证据） / 原独立测试 Agent | Main 授权后以冻结原测试资产全量复验，原故障与全部19项本地判据通过；AC-3单列阻塞 | [T001](../../specs/order/plan.md)，HEAD 89df9f6 加修复工作区；service=3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb，ui=4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909 | [修复后报告](../test-reports/order/fixed.md)、[原始逐项证据](../test-reports/order/evidence/fixed-integration.json) | 已修复待复验 → Closed after retest；原场景、必要回归及证据齐备，无人工反馈要求 |

## 4. 关联

原工单：[TASK.txt](../../TASK.txt)。修复与后续复验沿用本编号并保留本次失败事实。

## 5. 本轮归因

2026-11-15，Bugfix Agent 独立复现并验证原因，见 [归因证据](../test-reports/order/evidence/bugfix-diagnosis.json) 和 [修复计划](../../specs/order/plan.md)。submit 读取状态后无条件写 submitted，SQL trace 显示取消后实际 UPDATE/commit，total_changes 增加 1。

归因和修复定向证据见 [Bugfix 报告](../test-reports/order/bugfix.md)；当前关闭依据为后续 [独立全功能复验](../test-reports/order/fixed.md)，原场景及必要本地回归全部通过。初始失败、Bugfix 待复验状态及后续关闭事件均保留。整轮 Test Gate、架构 Review Gate 与 AC-3/CHK-006 分别维护。
