# ARCH-001 — UI 绕过订单状态服务入口

## 事实与依据

类型为已确认架构偏差，依据 [Blueprint](../blueprint.md) ARC-1、[CR-001](../code-review-rules.md) 和 [订单契约](../contracts/order.md)。初审由 `/root/review/architect_check` 于本轮隔离项目取证，基线快照见 [环境证据](../test-reports/order-cancel/baseline-environment.json)，最终候选 ui SHA256 仍为 `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b`，详细检查沿 [CHK-001](../reviews/order-candidate-review.md#chk-001-状态写入权威)。

`src/ui.py:4-6` 的 `mark_paid` 直接 UPDATE 和 commit，未调用已有服务 `set_status`。现存订单 paid 可以持久化，但状态写入职责不符合；不存在订单异常为旁路影响：独立集成 CT-10 已证实正常返回而非 ValueError，见 [集成原始输出](../test-reports/order-integration/contracts.stdout.txt)。其业务缺陷状态和修复归 [BUG-002](BUG-002.md)，ARCH-001 仅维护职责边界偏差。影响为 UI 旁路服务裁决和异常语义，不会自动阻止本地 AC-1、AC-2 及 paid 集成运行。

## 当前状态与恢复条件

状态：Awaiting confirmation，未整改、未关闭；后续整改责任方未分配。当前授权只读取证和本地记录，不含此偏差实施、项目规则更新、Git 或平台操作。无实施 Task。本轮取消缺陷原单 [BUG-001](BUG-001.md) 与本单分开维护。

恢复需要 Main 取得用户对此偏差的整改授权；目标为 UI 经已有服务状态写入口完成，保持现存订单 paid 和文件持久化，保留公开接口。复核全部写入位置、UI→服务调用链，以临时文件 SQLite 检查第二连接 paid 和数据库异常传播。缺失订单业务行为沿 [BUG-002](BUG-002.md) 验收，不在本单重复维护业务缺陷状态。实施者届时维护同一工单关联 Plan，独立复核后再判断关闭。

## 处理历史

| 执行者 | 动作与证据 | 状态 |
| --- | --- | --- |
| /root/review/architect_check | 初审 ui.py 写入路径，关联 CHK-001 和基线源码快照 | 确认偏差 |
| /root/review | 本地登记并核对修复候选 ui 哈希未变，原偏差仍存在；仅取证，不修改产品或规则 | Awaiting confirmation |
