<!-- sdd-contract-governance:start -->
## 项目入口

当前仓库启用了共享 SDD 工作流。新工作区缺少本地链接时，运行 sdd-init 接入本机共享资源。

- 从项目已有文档索引定位实际路径，通常为 docs/index.md。
- [仓库治理规范](.agents/skills/sdd-workflow/sdd/references/sdd-repository-governance.md)

## 索引

| 工作 | 入口 |
| --- | --- |
| 固化确认内容与原型文档 | [sdd-doc](.agents/skills/sdd-workflow/skills/sdd-doc/SKILL.md) |
| 实施、修复、重构与局部自验 | [sdd-imp](.agents/skills/sdd-workflow/skills/sdd-imp/SKILL.md) |
| 需求行为验收与整改后复验 | [sdd-test-loop](.agents/skills/sdd-workflow/skills/sdd-test-loop/SKILL.md) |
| 蓝图与实现一致性检查及整改后复核 | [sdd-review-code](.agents/skills/sdd-workflow/skills/sdd-review-code/SKILL.md) |
| 提示词冗余、歧义及行为一致性审查 | [sdd-review-prompt](.agents/skills/sdd-workflow/skills/sdd-review-prompt/SKILL.md) |
| 部署、启动或重启服务 | [sdd-deploy](.agents/skills/sdd-workflow/skills/sdd-deploy/SKILL.md) |
| Git 与 GitHub／GitLab 分支、Issue、PR／MR 及合并 | [sdd-commit](.agents/skills/sdd-workflow/skills/sdd-commit/SKILL.md) |

从本轮任务对应的 Skill 进入，按其触发条件读取相关章节。[场景提示](.agents/skills/sdd-workflow/sdd/references/scenarios.md)用于讨论和定位正文，[执行协作](.agents/skills/sdd-workflow/sdd/references/delegation.md)用于委派或交接。实体模板按产物选用。
<!-- sdd-contract-governance:end -->
