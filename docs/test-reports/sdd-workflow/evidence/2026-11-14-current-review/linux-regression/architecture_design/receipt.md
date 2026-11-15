已按 docs/decision.md 完成原位归并：

- [Blueprint](docs/blueprint.md)：新增 ARC-002，明确原子事务、提交后可见及异步派发边界。
- [Scenario Sequence](docs/create-sequence.md)：更新 SCN-001 和时序图，覆盖成功、回滚、503 与事件重试路径。

CON-001 保持不变。五篇相关文档校验及 diff 检查通过，0 错误、0 警告；语义一致性核对通过。

仅修改两篇设计文档，未实施、未提交；验证不包含运行时行为。