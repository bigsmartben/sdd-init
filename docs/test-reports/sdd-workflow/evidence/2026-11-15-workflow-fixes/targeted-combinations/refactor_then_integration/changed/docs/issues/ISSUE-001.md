# Issue — ISSUE-001 取消后提交覆盖取消状态

## 1. 问题事实

- ID：ISSUE-001；类型：实现缺陷；依据：[Spec AC-2](../../specs/order/spec.md)、[submit_order 契约](../contracts/order.md)。
- 发现：ORDER-INTEGRATION-001 独立集成，2026-11-14 16:28 UTC（Asia/Shanghai 为 2026-11-15），由 `/root` Main 调度的独立 sdd-test-loop 技能 Agent 复现。Main 提供的历史结果一致；本轮另行真实执行，不推定历史版本。
- 实际版本：HEAD `4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df` + 未提交付款适配与局部测试改动，完整哈希及环境见[本轮报告](../test-reports/order/payment-integration.md)。
- 复现：隔离项目根目录执行 `python -B checks/acceptance.py --scenario AC-2`；在临时文件库新建 ORDER-1→取消→提交→关闭重开读取。
- 预期：提交返回 false，持久化仍为 cancelled。实际：返回 true，重开后 submitted。公开入口、参数、数据与原 AC-2 一致。
- 影响：取消保护失效，取消状态被后续提交覆盖；直接阻止本轮全产品 Test Gate 通过。未据此推定其他状态提交规则或扩大业务范围。

## 2. 当前状态

- Assignee：Unassigned，交 `/root` Main 调度。
- Fix Task：未建立；当前无产品修复授权，不新增 Plan/Task。
- Status：**Pending**。
- 接续条件：授权独立缺陷处理并返回实际修复候选；原预期保持不变，不能以当前 true/submitted 重定义需求。
- 验收计划与方案：复跑同一公开 AC-2；通过条件 false/cancelled 且重开持久化。必要回归包括 AC-1 pending 提交 true/submitted、取消及重复取消、公开付款四合法前态、缺单与文件库写异常、跨订单隔离；复用[指南](../../specs/order/quickstart.md)和报告用例。修复执行者决定实现方案；本轮不推定已归因，不修改服务代码。
- 关单依据：当前没有修复版本或修后证据，不能关闭；Issue 修复复验结论与整轮 Test Gate 分别判断。AC-3 仍须真实外部授权及回执。

## 3. 处理与复验历史

| 时间 / 执行者 | 动作与结果 | 修复版本 / Task | 证据 | 状态依据 |
|---|---|---|---|---|
| 2026-11-14 16:28 UTC / 独立集成 Agent | 原公开 AC-2 在付款整改候选复现 true/submitted，记录不修复 | 无 | [ORDER-INTEGRATION-001 AC-2](../test-reports/order/payment-integration.md#6-逐项结果与证据) | 新建 Pending；未满足原验收条件 |

## 4. 关联

[Spec](../../specs/order/spec.md) · [契约](../contracts/order.md) · [复跑指南](../../specs/order/quickstart.md) · [集成报告](../test-reports/order/payment-integration.md)。未创建或修改外部平台议题。
