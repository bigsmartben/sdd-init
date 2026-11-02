---
name: sdd-review-loop
description: 任务需要检查架构落地时使用；对照 Blueprint 与适用 ARC 审查实现，在授权范围整改并复核，记录各能力 Review Gate 与跨能力证据。
---

# sdd-review-loop — 架构范式落地契约

## 场景、职责与作用对象

场景：确认当前实现是否遵守已确认架构，包括重构后的边界和跨能力关系检查。
职责：核验所有适用 ARC，识别架构偏差，在授权范围整改并复核，记录 Review Gate。
作用对象：Blueprint/ARC 是判断依据；源码、依赖、所有权、数据流和时序是检查对象；各能力 Status 是证据写入对象。代码/测试修改仅限已获授权的整改范围。
完成依据：选定能力及相关跨 Spec 关系在同一最新快照上满足架构 Gate，或明确记录阻塞。不是重新设计架构，也不替代需求 Test Gate；执行是否独立取决于实际分工，不能把 Main 自查称为独立审查。

遵循[实体治理](../../sdd/references/governance.md)，涉及测试、验收及证据核对时按其中的[测试范围约束](../../sdd/references/governance.md#测试范围约束)执行。

**启动规则**：Agent 根据任务目标、风险与已有授权自主选择本 Skill 开展架构符合性审查，可在实施后接续，无需用户点名；流程选择不扩大检查或修改范围。需修改代码时核对既有整改授权，缺少相关授权才澄清；已提交迭代的整改应建立新迭代。独立性取决于实际执行者。

**输入**：权威 Blueprint、一个或多个目标能力的 Spec、当前源码/模块依赖/全局数据流/时序以及各自 Status。**产出**：各 Spec 的 ARC 和 Review Gate 证据；不生成新权威实体、不创建 commit。

### 多 Spec 选择与批量契约
- 支持显式指定 `specs/payment/spec.md specs/order/spec.md ...`；未指定时请请求明确范围或以本轮已批准写入边界对应的能力集为范围，**不可悄悄扩大修改权限**。
- **逐份**识别适用 ARC、核验每个 Spec 所受影响的架构不变量，并检查**跨 Spec 的数据所有权、接口依赖、数据流/时序、业务与运维可观测分离**等交互一致性；不能只做每份独立 PASS 的逻辑与。
- **按能力分别**由当前执行者更新原有 `status.md` 的 ARC 与 Review Gate；不存在第四类“批次规格”或新的状态实体。每份证据都应指明本轮覆盖的跨能力交互（如果有）。对无法验证的跨 Spec 关系应报告 BLOCKED/UNVERIFIED，不得对相关 Gate 标记 PASS。
- 批量结果只有在所有选定 Spec 的 Review Gate 及相关跨 Spec 关系在**同一最新仓库内容快照**下有效时才算 PASS；任何修复均需重新检查被影响的 Gate。
- 批量机械检查示例：`python .agents/sdd/scripts/govern.py --root <repo> check --name payment --name order --strict`。记录与 `attest` 命令仍**每份 Spec 单独执行**；不能把单份 Status 的 PASS 当成整个批次 PASS。


## Review Gate（不规定具体审查步骤顺序）
- 对本次影响模块逐一判断哪些全局 ARC 适用，**不能只审 Spec 已列的 ARC 就忽略其他相关蓝图条款**。发现缺失引用应提出 Spec 引用修订，等用户批准；不能自改契约后伪装通过。
- 审查概念所有权、职责边界、禁止依赖、数据流/时序语义、业务与运维可观测分离等**项目已采纳**的规则。对于可执行约束优先运行依赖检查、契约/时序/架构测试；语义审查需要具体代码与调用链证据。
- FAIL 可在批准写入范围内自行修复；越界、变更重大架构决策、无法判断真实架构时停止，由当前执行者写阻塞 Status。
- 仅当各适用 ARC 为同一最新内容快照上的真实 PASS，且遗漏适用约束的风险已审查，方可将 Review Gate 标记 PASS。无适用 ARC 时也要提供审查证据，不能默认为通过。

以下状态 CLI 由当前执行者根据审查者真实证据执行。

## 共用 CLI（仅登记证据，非自动判定语义）
- `python .agents/sdd/scripts/govern.py --root <repo> record --name <capability> --arc ARC-001 --result PASS --evidence '具体检查命令及结果'`
- `python .agents/sdd/scripts/govern.py --root <repo> attest --name <capability> --gate review --result PASS --evidence '架构审查覆盖、证据位置与结论'`

向用户报告 Review Gate 的结论和快照。需要实施、测试或 Git 交付时，由 Agent 按任务契约与已有授权选择对应 Skill 接续；本流程不直接 Commit；任何后续修改都可能使证据过期。


## 执行方式

默认 Main 核验并记录证据。需要独立审查时按 [执行约定](../../sdd/references/delegation.md) 安排独立审查；修复后由原独立审查者复核。不得将 Main 自查声明为独立审查。协作与执行能力边界见执行约定。

## 运维与可观测强制基线

必读[强制基线](../../sdd/references/observability-baseline.md)，核对本轮范围的 SDD-OBS-01/02/03 与项目 ARC、需求及规范的映射。该基线对所有 SDD 项目生效；不能因项目漏引用或只列为候选而跳过，冲突与缺项明确记录，不通过修改契约伪装通过。流程选择遵循任务契约，保持本 Skill 的写入与验证边界。

Review 必须按基线的“映射、审查与闭环”逐项保留适用性、代码/调用链或运行证据及最新快照。先检查文字日志常态记录、持久化及 SSOT，关闭或切换 Debug 不停记或清空文字；媒体等高开销采集默认关闭，仅在用户明确 Debug 授权范围内开启。再检查职责隔离、业务非阻塞与无业务副作用（含观测慢写、故障、缓冲饱和及重试）、文字事实及 Debug 授权范围内原始媒体覆盖、跨语言格式、持久化及失败处理；仅静态检查不能证明真实落地。适用项 FAIL/UNVERIFIED/BLOCKED 均不得标记 Review Gate PASS。缺项目 ARC 时报告映射缺口并等待授权文档归并，不免审；整改后复核受影响项，跨能力证据需一致。
