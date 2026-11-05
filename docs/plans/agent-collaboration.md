# Plan：专职 Agent 协作与自动接续

## 1. 目标与依据

- 目标与范围：按本聊天 2026-11-05 已确认的计划，完善 imp、test、review 共用的专职 Agent 协作机制，并实际验证角色调用与闭环；进一步将 Review 检查项作为审查、推进、交接和跟踪的唯一单位。不升级已安装副本或其他项目，不执行 Git 远端交付。
- 上游任务：[工程协作职责 Spec](../../specs/platform-independent-sdd/spec.md) FR-011／AC-011，及本聊天中用户确认的协作、验证与授权边界。
- 当前实现：现行分发规则已覆盖交接与部分修复复核，默认 Main 执行与角色顺序代行的表述尚需调整；原有评测夹具未证明真实角色协作。

## 2. Task 清单

### T001：归并需求和高位职责

- 依据：FR-011／AC-011 与用户确认。
- 改动范围：`specs/platform-independent-sdd/spec.md`、`docs/blueprint.md`。
- 实施内容：documenter 归并协作目标、角色与任务完成边界，按需同步高位描述。
- 依赖：无。
- 完成条件与局部自验：确认来源、既有职责及例外逐项承接；链接、编号和编码检查通过。
- 状态：完成。
- 结果与证据：documenter 已归并确认内容；本轮 10 个受影响 Markdown 文件的 doc_check 为 0 错误、0 警告；待 validator 验收。

### T002：收敛共享治理与执行协作

- 依据：T001。
- 改动范围：`source/project/.agents/sdd/references/sdd-repository-governance.md`、`delegation.md`。
- 实施内容：documenter 分别维护协调与授权边界、角色调用和最小交接的唯一正文。
- 依赖：T001。
- 完成条件与局部自验：三种流程共享机制且不出现竞争正文；例外、独立性与实际授权保持完整；文档检查通过。
- 状态：完成。
- 结果与证据：共享正文已对齐委派和接续；doc_check 无诊断；待 validator 审查覆盖与一致性。

### T003：对齐技能与角色入口

- 依据：T001、T002。
- 改动范围：`source/project/.agents/skills/` 中 imp、test、review 入口，`.codex/agents/` 中必要角色，`docs/installation.md`；GAP-001 消歧涉及 Spec、Blueprint、共享治理与执行协作。
- 实施内容：documenter 保留各流程专属交接并引用共同机制，说明项目升级保留治理正文的边界；按 [Review GAP-001](../test-reports/agent-collaboration/2026-11-05-review.md) 消除复杂任务委派与部署、Git 默认职责冲突。
- 依赖：T002。
- 完成条件与局部自验：职责、自动接续、只审／只验收及部署外部操作授权一致；检查内容及链接。
- 状态：完成。
- 结果与证据：三个技能入口、coder／validator 角色与安装说明已更新；五个角色 TOML 可解析；GAP-001 关联文档已消歧并由原 validator [复核关闭](../test-reports/agent-collaboration/2026-11-05-review.md)，doc_check 无诊断。

### T004：准备评测并实际验证协作

- 依据：T001—T003，FR-011／AC-011。
- 改动范围：`tests/fixtures/skill-behavior/cases.json`、相邻 README 和必要测试夹具；隔离临时评测环境。
- 实施内容：coder 扩充协作案例及可运行的最小 Python 夹具，记录候选规则哈希，不新增调度器；修正只验收案例与六技能安装夹具。validator 以真实调用验证 imp、test、review 的交接与闭环，Main 按结果接续修复。
- 依赖：T003；夹具设计可先准备，行为评测须加载候选规则。
- 完成条件与局部自验：coder 检查 JSON、案例唯一编号及夹具执行；实际角色调用、原执行者复用、Issue／gap 修复复核、部分阻塞继续及证据复用有可复查轨迹；未执行场景保留未验证。
- 状态：完成。
- 结果与证据：原 validator 对 direct、1 个 blind 和 3 个边界场景验收 PASS，实际调用与复验事实见[报告](../test-reports/agent-collaboration/2026-11-05.md)；37 个案例未全部模型执行，能力受限场景未实测。

### T005：验证分发与安装保护

- 依据：T003、现行安装边界。
- 改动范围：必要的 `tests/` 安装测试和隔离构建输出。
- 实施内容：复用分发、角色与安装保护测试，验证候选资源的新安装、升级及重复安装。
- 依赖：T003；可与 T004 独立执行。
- 完成条件与局部自验：相称测试通过；项目配置及既有治理保护保留；不更新任何实际安装副本。
- 状态：完成。
- 结果与证据：初次仓库测试 50 项、构建后安装回归 25 项通过；新构建字节核对 67 项载荷及 46 项共享投影匹配，125 个受保护安装文件不变，来源见[报告](../test-reports/agent-collaboration/2026-11-05.md)。

### T006：原 validator 复核与证据归并

- 依据：T001—T005。
- 改动范围：本计划、适用测试及 Review 记录、直接受影响导航。
- 实施内容：原 validator 验收、审查和复核整改；documenter 据真实执行事实归并记录；Main 协调剩余问题直至完成或具体阻塞。
- 依赖：T004、T005。
- 完成条件与局部自验：所需角色与自动闭环有真实轨迹，未完成项列明承接者、具体问题及恢复条件；历史失败、执行范围与版本保留。
- 状态：完成。
- 结果与证据：原 validator 复核关闭 [GAP-001](../test-reports/agent-collaboration/2026-11-05-review.md)，并给出协作机制阶段验收 PASS；范围和夹具本身保留的 FAIL／BLOCKED 见[报告](../test-reports/agent-collaboration/2026-11-05.md)。

### T007：以检查项收敛 Review 规则与模板

- 依据：用户 2026-11-05 确认的 Review 收敛方向；[工程协作职责 Spec](../../specs/platform-independent-sdd/spec.md)。
- 改动范围：Review Skill、`review_template.md`、直接受影响的 Spec、治理与写入规则引用、imp／Plan 模板术语及必要文档。
- 实施内容：documenter 归并已确认设计，使同一检查项承载依据、初审、imp Task、复核证据与当前状态；消除检查项与独立 gap 清单的重复跟踪，不新增审批或问题生命周期。按[初审检查项 CHK-NEW-01／02／03](../test-reports/agent-collaboration/2026-11-05-review-items.md)调整逐项即时接续顺序、未检查占位及直接入口术语；保留历史记录原义和编号，不自动迁移旧记录。
- 依赖：T006。
- 完成条件与局部自验：逐项检查、整改、复核、失败续修、证据补查及受影响项阻塞可表达；支持多 Task 对一项或一 Task 对多项，仍按完整批次复用执行者；imp 的 Plan、实施、自验流程保持不变。文档语义和链接检查通过。
- 状态：完成。
- 结果与证据：Review Skill、模板及直接受影响条款已按检查项收敛；初审的 CHK-NEW-01／02／03 已由原 validator [逐项复核关闭](../test-reports/agent-collaboration/2026-11-05-review-items.md)，8 个受影响 Markdown 的 doc_check 无诊断。

### T008：验证检查项闭环与分发

- 依据：T007、用户确认的 Review 收敛方向。
- 改动范围：必要的 Review 行为评测和测试夹具、验证记录及隔离构建输出。
- 实施内容：coder 调整现行案例及 README 的检查项术语，新增复用订单 seed 的 Review 闭环案例，在 `docs/review-scope.md` 明确同一 Task 对应状态权威与依赖两项并分别复核；取消缺陷不在该案例修复范围。原 validator 复核检查项规则、失败续修、批次复用及历史保护，并验证受影响分发内容。
- 依赖：T007。
- 完成条件与局部自验：coder 执行准备器 4 项局部检查；真实执行及相称检查证据与候选快照一致；适用检查项分别有结论、Task 引用和复核事实，未执行项标明限制；不改现有安装或旧评测运行目录。
- 状态：完成。
- 结果与证据：原 validator 的模板缺失保护及隔离重复安装测试 2 项通过，新构建载荷 67／67、共享投影 46／46 字节匹配，见[原始输出](../test-reports/agent-collaboration/evidence/review-items/targeted-unittest.log)和[核对结果](../test-reports/agent-collaboration/evidence/review-items/byte-check.json)。r2 由原 blind 团队执行，两检查项共享 Task 并分别复核，原 validator 对已声明机制场景验收 PASS；夹具 Gate 和未实测分支见[测试报告](../test-reports/agent-collaboration/2026-11-05.md)。

## 3. 交付核对

- 目标覆盖与完成情况：T001—T008 已完成；本仓库源规则 Review 与已声明机制场景验收均由原 validator 给出 PASS。
- 阻塞与后续动作：源工作无未关闭项；隔离夹具的外部授权／连接和观测契约适用性分别保留具体恢复条件，见[测试报告](../test-reports/agent-collaboration/2026-11-05.md)。
- 未覆盖与待验收范围：38 个静态案例并非全部执行模型评测；复核失败返回 Task、单项多 Task、能力或工具不可用的分支未在本轮实测。不代表已安装项目规则生效。
