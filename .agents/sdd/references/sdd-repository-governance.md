# 仓库治理规范

本规范是跨流程决策、授权、资产归属和产物权威的上位规范，适用于新增或修改的产物。具体步骤由对应 Skill 或专项规范维护。只读本次任务触发的章节，同一版本已读取的条款直接沿用。

## 人与 Agent 协同及决策权限

项目协作约定指定决策人。产品决定用例、运行环境、非功能指标和集成验收。架构决定系统设计、模块边界及不变量。测试决策负责验收范围和涉及验收含义的数据选择。

意图对齐按[意图对齐](visual-confirmation.md#意图对齐)处理。纯讨论只形成候选或待决结论，按需参考[场景提示](scenarios.md)。需求验收与架构审阅分别按 [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) 与 [sdd-review-loop](../../skills/sdd-review-loop/SKILL.md) 处理。

### 目标仓库的 Code Review Rules

用户决定生成或更新时机。收到明确要求后，由 [sdd-doc](../../skills/sdd-doc/SKILL.md#对话结论落盘)归并已确认的设计依据，并登记正文路径。安装、升级或写入 Blueprint 本身不触发规则维护。项目规则供架构 Review 使用，执行证据归该轮审查记录。

## 职责与交接

Main 与用户对齐意图，根据已确认的目标和预期结果选择对应 Skill。开工时简述目标、产物与完成条件。Main 汇总结果，核对任务覆盖并接续授权内工作。决定执行者时查[委派与独立性](delegation.md#委派与独立性)，需要交接时读[最小交接](delegation.md#最小交接)。

遇到新决策或授权缺口时，Main 只暂停受影响事项及其依赖，记录待决问题、承接者和恢复条件。待确认事项按[意图对齐](visual-confirmation.md#意图对齐)处理后接续。其余可执行事项继续。正式文档由 [sdd-doc](../../skills/sdd-doc/SKILL.md)按[文档写入规则](document-writing.md)归并。各执行流程提交对应结论和证据。Goal 仅在用户或更高优先级指令明确要求时创建。

## 工程资产边界

按系统用途分类。项目已有落点从索引定位，新增资产采用以下默认目录。

| 资产 | 默认目录与范围 |
|---|---|
| 正式实现 | `src/`。业务代码、通用技术模块、契约实现、正式提示词及配套运行配置。具体环境值由环境配置管理。 |
| 测试 | `tests/`。包括可行性验证、Demo、算法对比、候选技术探索、产品原型及测试专用配置。按需使用 `prototypes/`、`experiments/`、`cases/`、`fixtures/`、`datasets/`。 |
| 运维 | `ops/`。部署、排障、备份、恢复工具，按需使用 `deploy/`、`diagnostics/`、`recovery/`。经授权接口操作，记录环境、版本及副作用范围，运行检查与业务验收分别取证。 |

功能完整、接入真实服务、验证通过或方案选中都不改变测试资产的归属。正式方案确定后的产品开发归正式实现。采用测试代码时，任务注明目标行为、契约、需移除的实验装配和验收条件，按[运行隔离与迁入要求](architecture-rules.md#正式实现与测试实现隔离)实施。设计或调整测试工程时读[测试工程规范](architecture-rules.md#测试工程与自动化规范)。探索报告关联场景、算法或路径、版本与结果。

生成物记录来源和重建入口，变更落在生成源。通用研发工具沿用项目目录并登记索引，目录随产物建立。

## 文档与产物落点

需要定位正文时先查 `docs/index.md` 的实际映射。已有正文原位更新，新建时使用默认落点。入口新增、移动或替代时同步索引和直接引用。

| 产物 | 默认落点 |
|---|---|
| Spec、运行与验收指南 | `specs/<能力>/spec.md` 和相邻 `quickstart.md` |
| 原型代码和静态资源 | `tests/prototypes/<能力>/<用例>/index.html` 和相邻 `assets/`。原型引用与确认记录归对应 Spec 或索引指向的权威正文。 |
| 测试报告 | `docs/test-reports/<主题>/<批次>.md`，简单任务可在当前任务记录 |
| Issue | `docs/issues/<问题编号>.md` |
| 架构 Review 记录 | `docs/test-reports/<主题>/<批次>-review.md` |
| Blueprint、时序、接口契约 | `docs/blueprint.md`、`docs/sequences/<场景>.md`、`docs/contracts/<接口或协议>.md` |
| 运维手册、其他文档 | `docs/runbooks/`，其他文档在 `docs/` 按用途归类 |
| 项目 Code Review Rules | `docs/code-review-rules.md` |
| Plan／Task | 当前任务或既有计划载体，同一份正文 |
| Status | 沿用项目进度记录，首次可用当前任务，独立文档默认 `docs/status.md` |
| 初始化运行资产 | 项目根目录 `.sdd-init.lock` 和 `.sdd-init-recovery/`，由初始化器管理 |
| 项目研发规则 | `.agents/governance/`，按需建立 |
| 共享资源、Skills、角色 | `.agents/sdd/`、`.agents/skills/`、`.codex/agents/` |

## 权威实体

| 实体 | 权威内容 |
|---|---|
| Blueprint | 高位产品用例、终端、关键体验及验收维度，已确认架构职责、边界、不变量和 ARC。采用 ADR 的项目用其记录具体取舍。 |
| Spec | 具体需求、业务规则、条件、异常和 AC。引用适用 Blueprint 条款与原型。 |
| 时序、契约 | 设计中的协作顺序、接口语义与异常约定。运行事实归对应报告。 |
| 测试报告、架构 Review 记录 | 分别维护需求行为的批次事实和架构检查项的历次证据。 |
| Issue | 独立问题事实及处理状态。修复方案引用 Plan／Task。 |
| Plan／Task、Status | 分别维护实施方案与任务、进度与恢复点。验证结果引用对应报告和版本。 |

代码记录实现事实。模板规定产物结构，候选与讨论在确认后归并到对应实体。引用在使用处维护，区分设计依据与指定版本的执行证据。

## Skill 场景与对象分工

下表定位七个流程的输入和回执，产物归属由[工程资产边界](#工程资产边界)与[文档与产物落点](#文档与产物落点)统一维护。

| 输入与回执入口 | 产物载体 |
|---|---|
| 已安装的 `sdd-init` Skill | 目标仓库的托管导航、分发资产和安装回执 |
| [sdd-doc](../../skills/sdd-doc/SKILL.md) | 项目权威正文和写后诊断 |
| [sdd-imp](../../skills/sdd-imp/SKILL.md) | 实现或测试资产和 Plan／Task |
| [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) | 测试报告及相关独立 Issue |
| [sdd-review-loop](../../skills/sdd-review-loop/SKILL.md) | 架构 Review 记录 |
| [sdd-deploy](../../skills/sdd-deploy/SKILL.md) | 目标环境的服务状态和运行回执 |
| [sdd-commit](../../skills/sdd-commit/SKILL.md) | Git 仓库、平台对象和交付回执 |

## 测试范围约束

以已确认的验收目标、范围和标准为准。从 Spec／AC、指南和任务约定推导常规数据、边界取值及顺序，记录依据与覆盖，保持已授权范围。仅在范围或标准无法确定、数据涉及新增业务含义、需新增外部授权或有不可逆影响时，按[职责与交接](#职责与交接)暂停受影响项及其依赖。验收环境、证据和用户反馈按 [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) 处理。

## 实施和独立审查

coder 修改实现、测试及自动化脚本并完成定向局部自验。validator 负责集成、跨组件、UI 验证和复验，并核对断言与覆盖。架构 Review 判断架构遵循，Test 验收需求行为。授权范围决定是否进入对应流程，实施完成本身不触发 Review 或 Test Gate。独立性按实际执行者判断，需要独立执行者时按[委派与独立性](delegation.md#委派与独立性)安排。

## 交付

本轮任务包含部署、启动或重启时，进入 [sdd-deploy](../../skills/sdd-deploy/SKILL.md)。本轮任务包含 Git 交付时，进入 [sdd-commit](../../skills/sdd-commit/SKILL.md)。讨论、落盘、实施和验证本身不触发这两个流程。进入流程后，按该 Skill 的环境或终点规则执行，操作范围以已有授权为准。

## 架构变更与遵循检查

按语义影响判定，项目在遵循规范维护具体判据。先判断 L2，再判断 L1 或 L0。

| 级别 | 条件与动作 |
|---|---|
| L2 | 改变职责、状态权威、决策权限、信任边界、依赖方向或关键不变量，按项目门禁确认。 |
| L1 | 已确认边界内的契约扩展，同步生产者、消费者及异常语义。 |
| L0 | 外部契约与架构语义均未改变的调整。 |

提示词、目录及正文迁移按同一语义影响判断。判据无法覆盖的变更按[决策权限](#人与-agent-协同及决策权限)处理。实际遵循检查与取证由 [sdd-review-loop](../../skills/sdd-review-loop/SKILL.md)执行。
