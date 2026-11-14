<!-- sdd-contract-governance:start -->
## 项目入口

当前仓库启用了共享 SDD 工作流。新工作区缺少本地链接时，运行 sdd-init 接入本机共享资源。

- 从项目已有文档索引定位实际路径，通常为 docs/index.md。
- [仓库治理规范](.agents/skills/sdd-workflow/sdd/references/sdd-repository-governance.md)

## 索引

| 工作 | 入口 |
| --- | --- |
| 固化确认内容与原型文档 | [sdd-documenter](.agents/skills/sdd-workflow/sdd/references/delegation.md#文档交接) |
| 单个需求的规格、实施及点对点验收 | [sdd-develop](.agents/skills/sdd-workflow/skills/sdd-develop/SKILL.md) |
| 实施已就绪工单并局部自验 | [sdd-coder](.agents/skills/sdd-workflow/sdd/references/delegation.md#实施交接) |
| Bug 评估、归因与派单 | [sdd-bugfix](.agents/skills/sdd-workflow/skills/sdd-bugfix/SKILL.md) |
| 用户功能集成测试与本轮验收文档 | [sdd-test-loop](.agents/skills/sdd-workflow/skills/sdd-test-loop/SKILL.md) |
| 蓝图与实现一致性检查及整改后复核 | [sdd-review-code](.agents/skills/sdd-workflow/skills/sdd-review-code/SKILL.md) |
| 明确请求审查提示词、比较候选版或获授权修订复验 | [sdd-review-prompt](.agents/skills/sdd-workflow/skills/sdd-review-prompt/SKILL.md) |
| Git、GitHub／GitLab 交付，部署、启动或重启服务 | [sdd-deliver](.agents/skills/sdd-workflow/skills/sdd-deliver/SKILL.md) |

按本轮任务选择入口并读取适用章节。[场景提示](.agents/skills/sdd-workflow/sdd/references/scenarios.md)用于讨论和定位正文，[执行协作](.agents/skills/sdd-workflow/sdd/references/delegation.md)用于委派或交接。实体模板按产物选用。
<!-- sdd-contract-governance:end -->
