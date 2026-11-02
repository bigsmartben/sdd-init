<!-- sdd-contract-governance:start -->
## 规则

- 按明确自然语言意图选择工作，无需精确 Skill 口令。普通 Chat 讨论不擅自写入；固化不顺带改产品代码；实施不自动部署验收；验收不自动修代码。
- 先定位相关 Issue、适用 Blueprint、Draft PR 与实现事实，沿用已有结论及授权，不要求每项工作走完整链路或反复确认。
- Issue 保存需求，Blueprint 保存已确认架构，Draft PR 保存实施 Plan 与实际结果；互相引用，不新建独立 Spec 或 plan.md。
- 保留项目术语、业务事实与模型选择，不从模板补造架构或需求。允许结构、交互及业务状态检查，排除纯视觉样式与像素还原检查。
- 原型确认、局部自验、部署准备与用户人工验收分别记录，不互相代替。

## 索引

| 工作 | 入口 |
| --- | --- |
| 固化确认内容与原型文档 | [sdd-doc](.agents/skills/sdd-doc/SKILL.md) |
| 实施、修复、重构与局部自验 | [sdd-imp](.agents/skills/sdd-imp/SKILL.md) |
| 指定版本部署与人工验收准备 | [sdd-accept](.agents/skills/sdd-accept/SKILL.md) |
| 授权的 Git 交付 | [sdd-commit](.agents/skills/sdd-commit/SKILL.md) |

[协作约定](.agents/sdd/references/governance.md)、[场景提示](.agents/sdd/references/scenarios.md)与[执行协作](.agents/sdd/references/delegation.md)按需读取。七个独立角色安装在 .codex/agents/，场景与模型建议见执行协作；不固定模型或推理强度，不要求全员启动。实体模板在 .agents/sdd/assets/，按任务裁剪；项目索引仅指向实际 Issue、Blueprint 和 PR，不虚构占位文件。
<!-- sdd-contract-governance:end -->
