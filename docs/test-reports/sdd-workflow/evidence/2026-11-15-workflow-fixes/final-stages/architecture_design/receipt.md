已完成设计文档归并：

- [Blueprint](docs/blueprint.md)：保留 ARC-001，新增 ARC-002，明确事务原子性、提交可见性及异步派发职责。
- [Scenario Sequence](docs/create-sequence.md)：原位更新 SCN-001，覆盖成功、回滚、503，以及提交后 201 与异步派发的并行关系。

CON-001 保持不变。5 份相关 Markdown 校验通过，0 错误、0 警告；语义一致性核对通过，未验证 Mermaid 渲染。

未实施、未执行 Git 写操作或接触外部平台。后续实施需独立工单。