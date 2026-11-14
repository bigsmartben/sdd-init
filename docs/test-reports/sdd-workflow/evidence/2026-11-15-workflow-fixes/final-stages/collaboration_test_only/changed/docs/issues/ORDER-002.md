# Issue — ORDER-002 mark_paid 对不存在订单未抛异常

## 1. 问题事实

- **类型与依据**：实现行为缺陷；[订单函数契约](../contracts/order.md)规定“不存在的订单抛出 ValueError”，涵盖公开 mark_paid 入口。
- **首次发现**：2026-11-15（Asia/Shanghai），独立测试技能 Agent `/root/order_integration`；版本 `5cf8f4dfb11879bf0f82e0808cb71dfc0c2b6932`，isolated-local-fixture。
- **复现**：执行 [指南 TC-6 补充命令](../../specs/order/quickstart.md#3-场景与复跑步骤)，在空文件 SQLite 上调用 `ui.mark_paid(connection, 'missing')`。
- **预期 / 实际**：预期 ValueError；实际正常返回（错误类别为 null），数据库仍为 0 行。对同一缺失订单调用 read_status、cancel_order、submit_order、set_status 均为 ValueError。见 [补充原始输出](../test-reports/order/2026-11-15-evidence/supplemental.json)。
- **影响**：调用者无法经异常辨识缺失订单；本批适用异常契约未满足。现存订单 paid 持久化已独立通过，不据此推断数据被错误新增。

## 2. 当前状态

- **责任人**：未分配。
- **修复任务**：无；本轮不修改实现/测试、不启动修复。
- **状态**：Pending（仅登记）。
- **恢复条件**：另行授权处理并提供修复版本后复跑原 TC-6；必要回归 TC-4 paid 持久化、TC-7 数据库异常传播及其他缺失订单入口。不得因单项修复关闭其他缺陷或整轮 Gate。

## 3. 处理及复验历史

| 时间 / 执行者 | 行为与结果 | 修复版本 / Task | 证据与版本 | 状态依据 |
|---|---|---|---|---|
| 2026-11-15 / order_integration | 执行公开入口、真实 SQLite 观察并登记 | 无 | [本批 TC-6](../test-reports/order/2026-11-15.md#6-逐项结果)，5cf8f4d | 新建 Pending；契约明确而实际未抛异常 |

## 4. 关联引用

[用户验收指南](../../specs/order/quickstart.md)；[集成报告](../test-reports/order/2026-11-15.md)。本轮没有架构合规结论、根因诊断或修复结果。
