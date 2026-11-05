# 架构 Review 记录：Review 检查项闭环

## 1. 范围与上下文

- 目标及范围：检查新 Review Skill、模板及直接关联要求是否按检查项执行和保留事实；完整适用项待原 validator 继续审查。
- 架构依据：[Blueprint ARC-004、ARC-006](../../blueprint.md#7-架构不变量)及用户确认的检查项闭环与批次复用边界。
- 实现快照：`b46594a1a17704039197d0d1af8b44cbf19ad6fd` 加未提交修改；初审 Review Skill SHA-256 `ee4ae60619d60a8ebaafb19e407f7df2641804de56650ab94a29d8e24baf16ee`，模板 SHA-256 `028715d714f83f81873f74b5afde26b2f01c4b7c72f2995a893ca4f4db72aa7a`。
- 环境与执行者：2026-11-05，本地工作区；独立 sdd-validator 初审，事实由 Main 转交。
- 修复边界：仅本仓库分发资源及必要文档、测试；保留授权、既有业务行为和 imp／test 的实施及验收流程。

## 2. 检查项及闭环

### CHK-NEW-01：检查项循环的执行顺序

- 依据与对象：已确认逐项闭环要求；`source/project/.agents/skills/sdd-review-loop/SKILL.md`。
- 检查方法与预期：阅读执行步骤，检查可修偏差发现后不依赖完成全范围初审或总 Gate 才能接续整改。
- 初审事实：步骤仍可读成全范围检查、全部初审输出后再承接修复、完成后统一复核；仅说明逻辑逐项不足以保证即时接续。初审结论 FAIL；快照见第 1 节。
- 整改交接：以每个检查项的检查、符合 PASS 或偏差接续 imp、原审查者复核和失败返回 Task 为主流程；有依赖或共享 Task 可合批，保留原执行者、实际授权与受影响项阻塞边界。承接者 sdd-documenter。
- imp Task：[本轮 Plan T007](../../plans/agent-collaboration.md)；修复方案只在 Plan。
- 当前状态与结论：已复核关闭／PASS。

| 批次／时间／执行者 | 处理或复核范围与方法 | 快照、实际结果及证据 | 本项结论与状态 |
|---|---|---|---|
| 2026-11-05／sdd-documenter | 调整 Review Skill 为当前项检查、接续和复核循环；Spec 同步 | Review Skill SHA-256 `294f8672184dfcf21036834f428f413817b80178eddab6b2ab31eace65efd234`；8 个受影响 Markdown 的 doc_check 为 0 错误、0 警告 | 已修改待复核／FAIL |
| 2026-11-05／原 sdd-validator | 核对当前检查项即接续、复核及按依赖合批的规则 | 原 validator 判断通过；[字节核对](evidence/review-items/byte-check.json)保留修复后快照 | 已复核关闭／PASS |

### CHK-NEW-02：未检查项的记录方式

- 依据与对象：适用检查项完整覆盖；`source/project/.agents/sdd/assets/review_template.md`。
- 检查方法与预期：范围内尚未执行的检查项能以当前状态及初审事实清楚表达。
- 初审事实：模板要求列未检查项，但当前状态枚举未提供待检查／未检查，初审事实未允许未执行。初审结论 FAIL；快照见第 1 节。
- 整改交接：在同一检查项中增加未检查状态及初审未执行表达，不新增台账。承接者 sdd-documenter。
- imp Task：[本轮 Plan T007](../../plans/agent-collaboration.md)；修复方案只在 Plan。
- 当前状态与结论：已复核关闭／PASS。

| 批次／时间／执行者 | 处理或复核范围与方法 | 快照、实际结果及证据 | 本项结论与状态 |
|---|---|---|---|
| 2026-11-05／sdd-documenter | 模板增加待检查状态及初审未执行表达；Spec 同步 | 模板 SHA-256 `d0dbea7a6a97fa2642c064db31a43ec45ea86ced75522732617b74b34adb4a96`；doc_check 无诊断 | 已修改待复核／FAIL |
| 2026-11-05／原 sdd-validator | 核对模板待检查及初审未执行表达 | 原 validator 判断通过；[字节核对](evidence/review-items/byte-check.json)保留模板快照 | 已复核关闭／PASS |

### CHK-NEW-03：分发导航与 imp 输入术语

- 依据与对象：已确认检查项为唯一交接单位；`source/project/docs/index.md` 与 `source/project/.agents/skills/sdd-imp/SKILL.md`。
- 检查方法与预期：核对新分发导航与 imp 上游类别均使用检查项，不暗示另建 Issue 或 gap 清单。
- 初审事实：分发导航仍称 gap，imp 上游类别仍称 Review issue。初审结论 FAIL；当时两文件 SHA-256 分别为 `a3b9ea3f193743e8a9b813322bf8e4d4761cf9098b4ad606e69eae13b88582f4`、`b7a936fb58200b78097783be8bd420ffdc92f5cbbcc5fb49d5c8210e6330d7d2`。
- 整改交接：仅将两处直接术语改为 Review 检查项；保持已有项目索引升级保护及 imp Plan、实施、自验步骤。承接者 sdd-documenter。
- imp Task：[本轮 Plan T007](../../plans/agent-collaboration.md)；修复方案只在 Plan。
- 当前状态与结论：已复核关闭／PASS。

| 批次／时间／执行者 | 处理或复核范围与方法 | 快照、实际结果及证据 | 本项结论与状态 |
|---|---|---|---|
| 2026-11-05／sdd-documenter | 分发导航及 imp 上游类别使用 Review 检查项 | 导航 SHA-256 `12a4f93996431c8fc11fbfe6c6524a833dd0afdb4077252739d5bbad8e6db968`；imp SHA-256 `9270bad6d8978f0aa2c8dba141ed242ed0ae5170494edd071ab4404ed0551296`；doc_check 无诊断 | 已修改待复核／FAIL |
| 2026-11-05／原 sdd-validator | 核对新分发导航及 imp 上游类别术语、实施和局部自验边界 | 原 validator 判断通过；[模板缺失保护及隔离安装检查](evidence/review-items/targeted-unittest.log)为 2 项通过 | 已复核关闭／PASS |

## 3. Gate 与未完成项

- Review Gate：初审为 FAIL；CHK-NEW-01、CHK-NEW-02、CHK-NEW-03 已分别由原 validator 复核关闭。原 validator 对本轮源规则、模板及直接引用给出 Review PASS；候选源码与[构建载荷快照](evidence/review-items/byte-check.json)一致。
- 未完成项与后续动作：本轮源规则审查无未关闭项；隔离评测的环境与设计条件按[测试报告](2026-11-05.md)保留。
