# Issue — ISSUE-001 取消订单被再次提交覆盖

## 1. 问题事实

- 编号：ISSUE-001。类型：Implementation defect；依据为已确认 [Spec AC-2](../../specs/order/spec.md) 与 [submit_order 契约](../contracts/order.md)。
- 首次发现：第一阶段付款架构保持评估中作为范围外既有行为查证，证据见[原审查记录](../test-reports/order/mark-paid-review.md)。本轮于 2026-11-15 00:47 +08:00 由独立 sdd-test-loop Agent 在付款整改后的同一工作树候选再次复现，见 [INT-20261115](../test-reports/order/integration-20261115.md)。此前无独立 Issue 记录，现登记唯一编号。
- 版本：HEAD `76e8f410e7adeb3cb702dc1f89bb5129bf381c60` 加第一阶段付款改动；service SHA256 `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`，ui SHA256 `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`。环境为 Python 3.12.3 / SQLite 3.45.1、每场景临时文件数据库，无外部调用。
- 复现：项目根执行 `python -B checks/acceptance.py --scenario AC-2`。公开入口新建 pending→cancel_order→submit_order→关闭重开。
- 预期：提交返回 false，重开仍 cancelled。实际：true，重开 submitted；取消被覆盖。
- 影响：取消状态保护失效，AC-2 不满足，阻止全产品集成 Test Gate PASS。独立取消、正常提交和付款目前分别通过，不将本缺陷归为付款整改新引入；本轮仅登记实测差异，未开展 Bugfix 归因或改动。

## 2. 当前状态与验收接续

负责人：Unassigned。状态：Pending。Fix Task：尚未启动，无修复版本。本阶段仅授权集成验证和文档留证，不允许修改代码/测试/配置或修复本问题。恢复条件为 Main 在另行获准阶段安排缺陷归因、修复及复验。

修复版本验收保持原 AC-2 公开命令及 false/cancelled 判据；必要回归为 AC-1 的 true/submitted 持久化、取消及重复取消、付款公开保持（四种现存状态及缺失/数据库异常传播）、多订单隔离，详见[复跑指南](../../specs/order/quickstart.md)。精确修复边界、任务拆分与其余影响分析由获准执行者给出；不能以内部调用或放宽断言替代原用户入口。本缺陷本地验收不依赖外部 AC-3，但全产品 Gate 仍独立受 AC-3 阻塞影响。

## 3. 处理与复验历史

| 时间／执行者 | 处理和结果 | 修复版本／Task | 证据和状态依据 |
|---|---|---|---|
| 第一阶段／独立架构验收 | 为影响评估查得 AC-2 true/submitted，属付款范围外原有缺陷 | 无修复 | [原审查记录](../test-reports/order/mark-paid-review.md)，未启动缺陷处理 |
| 2026-11-15／sdd-test-loop Agent | 原公开入口及完整指南再次复现失败，登记原问题唯一 Issue | 无修复 | [本轮报告](../test-reports/order/integration-20261115.md)；Pending，不关单 |

## 4. 关联资料

[Spec](../../specs/order/spec.md)、[契约](../contracts/order.md)、[Quickstart](../../specs/order/quickstart.md)、[第一阶段计划](../../specs/order/refactor-plan.md)。无外部平台 Issue 操作。
