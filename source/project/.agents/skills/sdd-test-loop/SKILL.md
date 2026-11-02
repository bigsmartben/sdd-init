---
name: sdd-test-loop
description: 任务需要需求验收时使用；对照 Spec 的 AC、边界和质量目标验证真实行为，在授权范围修复重测，记录各能力 Test Gate 与跨能力验收证据。
---

# sdd-test-loop — 需求验收契约

## 场景、职责与作用对象

场景：对功能、重构或迁移开展明确范围的需求验收。
职责：验证 FR/NFR 对应的 AC、边界与质量目标，补充必要测试，在授权范围修复重测，记录 Test Gate。
作用对象：Spec 是验收依据；真实实现、可观察行为和测试是验证对象；各能力 Status 是证据写入对象。测试及实现修改仅限已获授权范围。
完成依据：全部目标 AC 及相关跨 Spec 组合行为在同一最新快照上通过，或如实记录失败/阻塞。不能以构建通过替代行为验收，不能改低 Spec 要求；不替代架构 Review Gate 或自动提交代码。

验收范围、用例补充及 AC 覆盖遵循[测试范围约束](../../sdd/references/governance.md#测试范围约束)；既有契约冲突按该约束处理，未解决时不得标记相关 Test Gate 或批次 PASS。

**启动规则**：Agent 根据任务目标、风险与已有授权自主选择本 Skill 开展需求验收，可在实施后接续，无需用户点名；流程选择不扩大检查或修改范围。需修改代码时核对既有整改授权，缺少相关授权才澄清；已提交迭代的整改应建立新迭代。独立性取决于实际执行者。

完整业务流程、系统整体效果及全量业务回归属于本 Skill 或任务契约内的专项验收，禁止由 `sdd-imp` 执行。仅按任务契约确定的验收范围开展，不因承接 imp 的待验收项而自动扩大到整个系统；imp 完成及其局部自验证据不代表本 Test Gate 已通过。

**输入**：一个或多个目标能力的当前有效 Spec、现有测试和实现、各自 Status。**产出**：逐份 AC 的真实证据、跨 Spec 集成验收与各自 Test Gate；不生成 tasks/plan 文档、不提交代码。

### 多 Spec 选择与批量契约
- 支持显式指定 `specs/payment/spec.md specs/order/spec.md ...`，逐份核对全部当前有效 AC、边界场景及质量目标，按测试范围约束执行允许的验证并登记契约冲突。
- 除逐份验收外，必须检查**跨 Spec 的组合行为**（跨模块调用、协议兼容、共享数据、事务/时序、异常恢复）；不能以“每个 Spec 单独测试通过”推导“组合行为通过”。发现缺少跨能力验收条件时只报告缺口，需用户批准后才能改 Spec。
- 各能力由当前执行者维护自己的 `status.md`，逐份写 AC 与 Test Gate 证据；关联的集成测试、跨能力证据在各受影响 Status 中引用同一实际测试报告/命令和快照。不生成批次 Status/Tasks。
- 批次 PASS = **所有指定 Spec 的 Test Gate PASS + 跨 Spec 交互验证 PASS + 同一最新仓库内容快照**。任何实现修改使证据失效，必须重新验收相关 Spec。
- 批量机械检查：`python .agents/sdd/scripts/govern.py --root <repo> check --name payment --name order --strict`；`record/attest` 仍逐个能力登记。


## Test Gate
- 测试范围约束允许验证的每条当前有效 FR/NFR、独立场景与边界情形必须有相应可验证的 AC；不能用“代码改了/编译通过了”证明行为目标已实现。
- 对 Given/When/Then 的前提、触发、可观察结果进行真实验证；按项目特性选择单元/契约/集成/端到端/性能/故障测试。不能因某种验证工具不可用就虚构 PASS。
- 未达成时可在批准边界内自主修复再测；缺失测试可以补充，不能为了通过测试擅自降低验收要求。
- 全部目标 AC 在**同一当前代码内容快照**具有复查证据、场景覆盖无遗漏且无未解决的测试范围契约冲突，才可标记 Test Gate PASS；不得通过排除冲突项缩减分母获得 PASS。
- 需要改变蓝图、Spec、范围或超过三轮修复无进展时停止，由当前执行者在 Status 记录失败证据和阻塞原因。

以下状态 CLI 由当前执行者根据审查者真实证据执行。

## 共用 CLI（登记证据，不替代真实测试）
- `python .agents/sdd/scripts/govern.py --root <repo> record --name <capability> --ac AC-001 --result PASS --evidence '实际测试命令及结果'`
- `python .agents/sdd/scripts/govern.py --root <repo> attest --name <capability> --gate test --result PASS --evidence '全量验收覆盖与测试结果'`

向用户报告 Test Gate 结论和快照。需要实施、架构审查或 Git 交付时，由 Agent 按任务契约与已有授权选择对应 Skill 接续；本流程**不 Commit**。其他修改可能使 Test Gate 过期，必须重验。


## 执行方式

默认 Main 核验并记录证据。需要独立审查时按 [执行约定](../../sdd/references/delegation.md) 安排独立审查；修复后由原独立审查者复核。不得将 Main 自查声明为独立审查。协作与执行能力边界见执行约定。

## 运维与可观测强制基线

必读[强制基线](../../sdd/references/observability-baseline.md)，核对本轮范围的 SDD-OBS-01/02/03 与项目 ARC、需求及规范的映射。该基线对所有 SDD 项目生效；不能因项目漏引用或只列为候选而跳过，冲突与缺项明确记录，不通过修改契约伪装通过。流程选择遵循任务契约，保持本 Skill 的写入与验证边界。
