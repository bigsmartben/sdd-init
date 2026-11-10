<!-- agent-communication:start -->
## 首要沟通原则：对齐意图

变更前，先与用户确认要解决的问题和预期结果。用户确认后直接执行。已有确认继续有效，不重复授权与确认。具体按[呈现与确认](.agents/sdd/references/visual-confirmation.md#呈现与确认)处理。
<!-- agent-communication:end -->

# sdd-init 维护约定

先读 [README](README.md) 的仓库定位与导航；已确认需求统一维护为 Spec，按任务契约确定写入范围和完成条件。

## 维护边界

- 已确认的具体需求以对应 Spec 文件为唯一正文；README 只保留定位与导航，计划和状态引用需求并记录各自的方案或事实，不复制需求正文。Plan 与 Task 合并为同一份可执行清单；HTML、Blueprint 和交付记录的职责及引用关系按 Spec 中已确认约定执行。
- 维护通用流程与资源时，沿用目标项目的已确认决定；业务需求、组件库选型和产品架构由目标项目确定。本仓库自身的维护任务以规则、文档和工具为检查对象。
- `source/initializer/` 维护初始化器自身；`source/project/` 维护项目分发正文，共享模板、治理与观测资源只在 `source/project/.agents/sdd/` 下维护。生成的 `.build/` 和 ZIP 不是编辑入口；`baselines/` 仅供追溯。来源与历史差异见 [导入清单](baselines/import-manifest.json) 和 [来源盘点](docs/inventory.md)。
- 历史导入源码中的旧规则是待迁移实现，不覆盖已确认目标；导入目录、Skill 数量及现存角色引用不构成最终设计。未决方案以关联 Spec 中后续确认的结论为准，不把临时链接当作固定基线。
- 不直接改用户级已安装 Skill、其他项目副本、产品代码或历史需求；安装、升级与迁移须在实际任务范围内单独处理。
- 机械工具用于检查结构、编号、引用和证据时效，需求、架构或实现的语义判断由 Agent 完成。
- 允许信息架构、结构布局、交互和业务状态符合性检查；排除纯视觉样式与像素还原检查。原型模拟、局部自验、正式系统验收分别取证。
- 纯文档变更核对内容、链接和编码；打包或工具变更运行相称测试。
- 已有 Git 授权在范围内沿用；远端交付、push、merge 按任务实际授权执行，不从建仓推定后续所有远端动作均已授权。


<!-- sdd-contract-governance:start -->
## 项目入口

- [项目文档与实际路径映射](docs/index.md)
- [仓库治理规范](.agents/sdd/references/sdd-repository-governance.md)

## 索引

| 工作 | 入口 |
| --- | --- |
| 固化确认内容与原型文档 | [sdd-doc](.agents/skills/sdd-doc/SKILL.md) |
| 实施、修复、重构与局部自验 | [sdd-imp](.agents/skills/sdd-imp/SKILL.md) |
| 需求行为验收与整改后复验 | [sdd-test-loop](.agents/skills/sdd-test-loop/SKILL.md) |
| 蓝图与实现一致性检查及整改后复核 | [sdd-review-loop](.agents/skills/sdd-review-loop/SKILL.md) |
| 部署、启动或重启服务 | [sdd-deploy](.agents/skills/sdd-deploy/SKILL.md) |
| Git 与 GitHub／GitLab 分支、Issue、PR／MR 及合并 | [sdd-commit](.agents/skills/sdd-commit/SKILL.md) |

从本轮任务对应的 Skill 进入，按其触发条件读取相关章节。[场景提示](.agents/sdd/references/scenarios.md)用于讨论和定位正文，[执行协作](.agents/sdd/references/delegation.md)用于委派或交接。实体模板按产物选用。
<!-- sdd-contract-governance:end -->
