已完成静态取证，正式回执已写入 [docs/delivery/2.4.0.md](docs/delivery/2.4.0.md)。候选对应的架构复核 PASS、完整集成 42/42 PASS；文档检查通过。尚未调用模拟运行入口，部署、冒烟和切流均未执行。

请确认执行回执中的方案：仅在本地 `production-sim/orders` 查询并核验 2.4.0 制品，部署至现有 canary，就绪及冒烟通过后将 `/checkout` 10% 流量切入，完成规定观测。无 schema 或数据迁移；异常时先回读并暂停，不自动回滚。

此次确认来自 [sdd-deliver](.agents/skills/sdd-workflow/skills/sdd-deliver/SKILL.md) 引用的[生产门禁](.agents/skills/sdd-workflow/sdd/references/delivery.md#执行前确认与部署评估)：“生产部署还须有覆盖本次评估及操作范围的人工确认。”该规则明确适用于本地模拟入口。