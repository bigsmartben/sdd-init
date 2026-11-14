# Plan — WO-ORDER-017

## 1. 目标与依据

按[工单](../../docs/order-export-work.md)及[设计约束](../../docs/export-design.md)执行已确认 A/B；保持[现有需求](spec.md)与[函数契约](../../docs/contracts/order.md)。范围仅为 create_order 入口校验、直接测试与历史来源调查。其他写路径、schema、Blueprint 与既有 submit_order／mark_paid 问题不在修改授权内。

## 2. Task 清单

### T001: 拒绝全空白订单号

- **依据** — WO-ORDER-017／AC-4。
- **改动范围** — `src/order_service.py` 的 create_order；`tests/test_order.py` 直接测试。
- **实施方案** — 仅对校验使用 strip，空白值抛出现有 `ValueError("order_id is required")`；合法订单号按原值创建，不修剪或重写。检查无 SQL 写入、无提交及文件重开后的数据。
- **依赖** — 无。
- **完成判据与局部检查** — 全空白与空字符串拒绝、不写入，合法订单号创建 pending 且原值保存，非字符串沿用原拒绝行为；运行 unittest 定向测试及全部现有直接测试。
- **状态** — Complete。
- **结果与证据** — [实施证据](implementation-evidence.md#t001ac-4)：先红后绿，4 个直接测试通过；调度方已回传 AC-4 与 AC-1 通过，正式结论见[点对点验收](../../docs/order017-acceptance.md)。

### T002: 查证跨重启逐次历史的权威来源

- **依据** — WO-ORDER-017／AC-5 与导出设计约束。
- **改动范围** — 只读检查订单服务、SQLite 存储和付款适配入口；不改其他写路径或 schema。
- **实施方案** — 查找真实事件存储与只读路径，用文件 SQLite 及独立进程检验取消和付款后的持久化内容。只有现状时不实现误导性导出，提供替代路径、影响及恢复条件。
- **依赖** — 无；T001 不依赖本项。两项为 `起点 → T001`、`起点 → T002`，当前由同一执行者串行处理。
- **完成判据与局部检查** — 必须找到可保留准确顺序的权威逐次事件才可完成 AC-5；否则保留 Blocked 并给出可复查反证、约束内替代路径评估及恢复条件。
- **状态** — Blocked。
- **结果与证据** — [来源调查](implementation-evidence.md#t002ac-5)：文件 SQLite 跨进程只保留最终 paid，无事件表／触发器／顺序字段；不存在满足 AC-5 的约束内只读路径。需提供权威事件源，或先确认架构／迁移及全量写路径授权后接续。

## 3. 交付核对

局部自验与来源调查记录于[实施证据](implementation-evidence.md)。正式点对点验收由调度方执行，见[验收记录](../../docs/order017-acceptance.md)；本 Plan 不以局部结果替代验收。T002 若缺少权威事件源，须经 Main 协调独立架构／迁移决定后续派，其他就绪任务继续。
