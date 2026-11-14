# Issue — ORDER-001 取消后提交覆盖取消状态

## 1. 问题事实

- 类型：产品实现缺陷；发现者 `/root/integration_test`；批次时间见[原始证据](../test-reports/order/evidence/ci-reruns.json)。
- 版本：`67e0283f880b4995f5df4d58f2c2b6a3ca8b2003`，产品无工作区改动；环境 isolated-local-fixture。
- 判据：[Spec AC-2](../../specs/order/spec.md)；受影响场景：AC-2。
- 复现：新建 ORDER-1 → cancel_order → submit_order → 关闭重开。项目根运行 `python -B checks/integration_runner.py` 或指南中的单项命令。
- 预期与实际：提交应返回 false，状态保持 cancelled；实际返回 true，重开 submitted。
- 影响：违反已确认订单状态或输入保护判据，阻止本轮 Test Gate 通过；未开展额外根因或架构审查。

## 2. 当前状态

- 经办：未指派，待 Main 按授权安排。
- 状态：Pending（已留证，产品实现冻结）。
- 修复 Task：无，本轮不授权产品修复。
- 恢复条件：获得产品修复授权并交回明确修复版本后，由原测试 Agent 复验同一场景及完整回归；外部路径仍需单独满足环境条件。
- 验收计划：按[指南](../../specs/order/quickstart.md)执行上述同编号场景，异常类型、返回值、中间态和关闭重开状态全部符合原判据，再运行完整入口检查回归。

## 3. 处理与复验历史

| 时间 / 执行者 | 处理与版本 | 结果与证据 |
|---|---|---|
| 本轮证据时间 / integration_test | 当前基线独立执行两次；未修产品 | 两次均复现，见[报告](../test-reports/order/2026-11-15-integration.md)及[逐项记录](../test-reports/order/evidence/ci-reruns.json) |

## 4. 关联

[规格](../../specs/order/spec.md)、[契约](../contracts/order.md)、[状态](../status.md)。未创建外部平台议题。
