`sdd-architect` 实际回执：已完成，仅修改两份授权设计文档。

- [Blueprint](docs/blueprint.md)：纳入 ARC-002，明确订单与 outbox 原子提交、回滚、异步发布及事件 ID 重试。
- [Scenario Sequence](docs/create-sequence.md)：更新 SCN-001 及序列图，覆盖响应、异步派发和事务失败路径。

检查：文档检查 **0 errors、0 warnings**；`git diff --check` 通过；现有契约保持不变。仅上述两份文件有未提交修改，未进行实现工作。