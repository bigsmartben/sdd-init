# Issue — ORDER-001 取消订单仍可提交

## 1. Issue Facts

- **编号与类型**：ORDER-001，已复现实现缺陷。
- **依据**：[Spec](../../specs/order/spec.md) AC-2、[契约](../contracts/order.md) submit_order。
- **发现**：订单集成测试 Agent，当前 HEAD `fc366da8aff900abc000129676514d994ca5c671`，产品源码无修改，隔离本地 Python 3.12.3 / SQLite 3.45.1。
- **复现**：`python -B checks/acceptance.py --scenario AC-2`；真实文件 SQLite 新建 ORDER-1 → cancel_order → submit_order → 关闭重开。
- **预期**：返回 false，重开后仍 cancelled；**实际**：返回 true，重开后 submitted。
- **证据与影响**：[首次 CLI 原始输出](../test-reports/order/evidence/initial-acceptance.json)；取消保护失效，AC-2 不满足。

## 2. Current Status

- **已验证归因与边界**：`submit_order` 先读取状态但不分支，无条件 `set_status(..., "submitted")`；对 cancelled 的预测为覆盖且返回 true，与首轮 AC-2 一致。恢复取消时 false 且不写入；保持 pending 成功、其他既有行为和异常传播。只修改订单服务，不增加状态或接口。

- **Assignee**：Bugfix 技能 Agent `/root/order_bugfix`；实施角色 `/root/order_bugfix/implement`。
- **Fix Task**：[同一修复 Plan](../plans/order-bugfix.md)。
- **Status**：Closed after retest。
- **恢复条件**：本缺陷无剩余关单缺口；[定向复验](../test-reports/order/bugfix.md) 已证明原场景及必要回归恢复。原测试 Agent 已完成[独立全产品集成复验](../test-reports/order/retest.md)，22 个本地场景通过；整轮 Gate 因 AC-3 外部证据缺口为 BLOCKED，与本缺陷关闭分别判定。
- **验收计划与方案**：修复执行者先按原 CLI AC-2 定向自验；随后原集成测试 Agent 在修复后实际快照重跑 [验收指南](../../specs/order/quickstart.md) 全部场景。原 AC-2 必须 false/cancelled；AC-1 仍 true/submitted，付款、缺失对象及数据库异常契约保持。AC-3 缺少外部授权时单列阻塞，不以本地结果替代。

## 3. Handling and Retest History

| Time / Actor | Action and outcome | Fix version / Task / Local verification evidence | Retest report or case and version | Status change and basis |
|---|---|---|---|---|
| 首次批次 / order_test | CLI 实测复现取消后提交覆盖状态 | 尚未修复 | [initial-acceptance](../test-reports/order/evidence/initial-acceptance.json)，HEAD fc366da | Pending，原始缺陷成立 |
| 修复批次 UTC 见证据 / order_bugfix | 归因、修复及原场景定向复验通过，必要回归通过 | [Plan T001](../plans/order-bugfix.md)，[实际修复指纹](../test-reports/order/evidence/bugfix-local-version.json) | [定向报告](../test-reports/order/bugfix.md)，[原始证据](../test-reports/order/evidence/bugfix-retest.json) | Pending → In progress → Closed after retest；原故障恢复、必要回归与副作用检查齐备 |
| 独立集成复验 UTC 见证据 / order_test，经 Main 回传 | 原故障恢复，23 场景 22 PASS / 0 FAIL / 1 BLOCKED（仅 AC-3），另 2 单测 PASS | 与修复快照指纹一致，执行前后产品与验证资产不变，见[版本证据](../test-reports/order/evidence/retest-version-after.json) | [独立全量复验报告](../test-reports/order/retest.md)，同一实际修复快照 | 保持 Closed after retest；独立复验补充原场景及完整本地回归关闭依据；AC-3 环境阻塞不影响本缺陷判据 |

## 4. Related References

[首次集成报告](../test-reports/order/initial.md)、[验收指南](../../specs/order/quickstart.md)。
