# Issue — ORDER-001 取消订单被提交覆盖

## 1. 问题事实

- **类型与依据**：实现行为缺陷；[Spec AC-2](../../specs/order/spec.md)及 [submit_order 契约](../contracts/order.md)要求取消后提交返回 false，状态保持 cancelled。
- **首次发现**：2026-11-15（Asia/Shanghai），独立测试技能 Agent `/root/order_integration`；版本 `5cf8f4dfb11879bf0f82e0808cb71dfc0c2b6932`，isolated-local-fixture。
- **复现**：在隔离项目根目录运行 `python -B checks/acceptance.py --scenario AC-2`。入口建立真实文件 SQLite，新建订单、取消、提交并重开数据库。
- **预期 / 实际**：预期 false / cancelled；实际 true / submitted。见 [原始全量输出](../test-reports/order/2026-11-15-evidence/acceptance.json)与 [报告 AC-2](../test-reports/order/2026-11-15.md#6-逐项结果)。
- **影响**：取消保护失效，阻止本批集成通过。不推断其他状态迁移或真实外部服务结果。

## 2. 当前状态

- **责任人**：未分配。
- **修复任务**：无；本轮明确禁止修改实现/测试及启动修复。
- **状态**：Pending（已登记，未启动处理）。
- **恢复条件**：Main 获得修复授权并提供实际修复版本后，沿用 AC-2 复验；同时回归 AC-1、paid 及适用异常路径。AC-3 的外部阻塞须独立解决，修复本项不代表 Test Gate 通过。

## 3. 处理及复验历史

| 时间 / 执行者 | 行为与结果 | 修复版本 / Task | 证据与版本 | 状态依据 |
|---|---|---|---|---|
| 2026-11-15 / order_integration | 真实集成取证并登记，未诊断或修复 | 无 | [本批报告](../test-reports/order/2026-11-15.md)，5cf8f4d | 新建 Pending；判据明确而实测不符 |

## 4. 关联引用

复跑步骤及预期见 [用户验收指南](../../specs/order/quickstart.md)。本记录不包含实施方案、修复授权或关单证据。
