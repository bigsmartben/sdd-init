# Plan：设计变更提醒与任务交接

## 1. 目标与依据

- 目标与范围：准备在分发规则中落实设计变更提醒和最小任务交接；升级沿用现有流程，升级风险、运行状态及后续处理由用户负责。该边界限于升级及本次交接场景，不改变明确的部署任务职责。
- 上游任务：用户于 2026-11-06 确认的简化方案；需求及验收条件见[工程协作职责 Spec](../../specs/platform-independent-sdd/spec.md) FR-006／AC-006、FR-011／AC-011。
- 当前实现：分发源中的[文档写入规则](../../source/project/.agents/sdd/references/document-writing.md)及[执行协作](../../source/project/.agents/sdd/references/delegation.md)已承接本次补充。已有安装流程及其他项目不在实施范围。

## 2. Task 清单

### T001：补充简短规则

- 依据：[Spec](../../specs/platform-independent-sdd/spec.md) FR-006／AC-006、FR-011／AC-011。
- 改动范围：`source/project/.agents/sdd/references/document-writing.md`、`source/project/.agents/sdd/references/delegation.md`。
- 实施内容：在现有正文中分别补充设计变更提醒与任务交接约定，沿用已有职责及载体。
- 依赖：本计划及引用的已确认需求。
- 完成条件与局部自验：对照关联 FR／AC 语义核对，仅在指定分发正文增补必要说明；检查本次修改及直接受影响 Markdown 的链接、编码和差异格式。无需新增安装器代码、Skill、角色、台账或机械字符串测试。
- 状态：完成。
- 结果与证据：两处正文已分别补充提醒和交接约定；对照关联 FR／AC 及 FR-022 语义核对，保留既有部署职责。`python -B source/project/.agents/sdd/scripts/doc_check.py --root . source/project/.agents/sdd/references/document-writing.md source/project/.agents/sdd/references/delegation.md docs/plans/workflow-continuation.md specs/platform-independent-sdd/spec.md docs/index.md` 检查 5 个 Markdown，0 错误、0 警告；`git diff --check` 通过；两处分发正文及本计划均为 UTF-8 无 BOM。机械检查不证明真实模型行为。

## 3. 交付核对

- 目标覆盖与完成情况：T001 完成；本计划及 Spec 已归并，分发正文已更新。
- 阻塞与后续动作：无。
- 未覆盖与待验收范围：本计划不证明分发规则已生效；用户级安装、其他项目升级和真实模型行为均未验证。
