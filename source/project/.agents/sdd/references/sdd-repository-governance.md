# 仓库治理规范

本规范是跨流程决策、授权、资产归属和产物权威的上位规范，适用于新增或修改的产物。具体步骤由对应 Skill 或专项规范维护。只读本次任务触发的章节，同一版本已读取的条款直接沿用。

## 人与 Agent 协同及决策权限

项目协作约定指定决策人。产品决定用例、运行环境、非功能指标和集成验收。架构决定系统设计、模块边界及不变量。测试决策负责验收范围和涉及验收含义的数据选择。

按[意图对齐](visual-confirmation.md#意图对齐)处理用户决定。需求到实现依本阶段的 A／B 确认范围执行。纯讨论只形成候选或待决结论，按需参考[场景提示](scenarios.md)。用户功能集成测试与架构审阅分别按 [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) 与 [sdd-review-code](../../skills/sdd-review-code/SKILL.md) 处理。

### 目标仓库的 Code Review Rules

用户决定生成或更新时机。收到明确要求后，由 [sdd-documenter](delegation.md#文档交接)归并已确认的设计依据，并登记正文路径。安装、升级或写入 Blueprint 本身不触发规则维护。项目规则供架构 Review 使用，执行证据归该轮审查记录。

## 职责与交接

Main 与用户对齐意图，根据已确认的目标和预期结果选择对应 Skill。开工时简述目标、产物与完成条件。Main 汇总结果，核对任务覆盖并接续授权内工作。决定执行者时查[委派与独立性](delegation.md#委派与独立性)，需要交接时读[最小交接](delegation.md#最小交接)。

遇到新决策或授权缺口时，Main 只暂停受影响事项及其依赖，记录待决问题、承接者和恢复条件。待确认事项按[意图对齐](visual-confirmation.md#意图对齐)处理后接续。其余可执行事项继续。正式文档由[获授权的写入者](delegation.md#文档交接)按[文档写入规则](document-writing.md)归并。各执行流程提交对应结论和证据。Goal 仅在用户或更高优先级指令明确要求时创建。

上游在派单前定义交付目标、范围、通过判据及可执行的[验收计划与方案](#验收计划与方案)，可引用原载体。用户功能和用户可感知的非功能指标从用户操作或公开调用入口定义，Bug 沿用原 Issue。架构变更引用已确认决定，Review 按 [sdd-review-code](../../skills/sdd-review-code/SKILL.md) 从开发者视角在原检查项定义整改验收方案，由原审查者复核。工单同时涉及用户侧和架构判据时，分别引用对应的判据、执行者及证据。sdd-coder 根据局部自验证据判定 Task 完成，本轮仅要求实施和局部自验时可据此结束。约定的用户验收按上游方案实际取证，集成测试按本轮明确范围进入。Main 核对本轮剩余验收项。

用户明确发起指定缺陷处理时，Main 选择 [sdd-bugfix](../../skills/sdd-bugfix/SKILL.md)。该阶段沿原 Issue 完成归因、修复和定向复验，按实际修复版本的证据和授权更新状态。只诊断或只复验按指定终点交付。集成测试中的缺陷发现交回 Main。获授权的集成批次可按原 Issue 判据和必要复验证据更新状态，整轮 Test Gate 独立判定。

### 阶段授权与推进

Main 根据用户明确授权和实际就绪条件组织跨阶段工作。同一请求明确授权多个阶段时按指定顺序推进，各阶段沿用适用的确认节点。Skill 各自独立受理，在授权内执行、取证、修正和复验。跨阶段事项随证据、影响及恢复条件交回 Main，由用户显式发起未授权的阶段。

## 验收计划与方案

单个需求、缺陷或 Review 检查项采用点对点验收。原工单记录以下内容或提供可访问引用。

- **验收计划**明确验哪些项、由谁执行、何时执行或满足什么条件后执行，覆盖本工单及直接受影响的行为。
- **验收方案**明确各项的前置条件、操作或检查步骤、观察点和通过判据。用户侧从实际操作或公开调用入口出发，Review 从开发者视角检查适用架构约束。

需求依据 Spec／AC 定义，缺陷归入原 Issue，整改归入原检查项。混合工单分别关联用户侧与架构判据、执行者及证据。直接复用已确认和可执行的内容，从已有依据推导常规步骤、数据与取证方式。根据已确认的主流程、主要体验及交付范围推导需求的具体通过判据。涉及用户决定的变更或必要信息缺失时，在回执中说明差异、影响及接续条件，只暂停受影响项及其依赖。计划和方案应足以确定实施范围和局部自验，并能在条件具备后照方案取证。实际版本、运行入口和结果按取得的事实补记。

点对点验收按工单范围取证，可按判据运行真实组件。集成测试从 Blueprint、Spec／AC 和适用契约推导全功能点覆盖清单，交付可复跑的用户验收文档。可复用工单中的操作或检查步骤。

## 工程资产边界

按系统用途分类。项目已有落点从索引定位，新增资产采用以下默认目录。

| 资产 | 默认目录与范围 |
|---|---|
| 正式实现 | `src/`。业务代码、通用技术模块、契约实现、正式提示词及配套运行配置。具体环境值由环境配置管理。 |
| 测试 | `tests/`。包括可行性验证、Demo、算法对比、候选技术探索、产品原型及测试专用配置。按需使用 `prototypes/`、`experiments/`、`cases/`、`fixtures/`、`datasets/`。 |
| 运维 | `ops/`。部署、排障、备份、恢复工具，按需使用 `deploy/`、`diagnostics/`、`recovery/`。经授权接口操作，记录环境、版本及副作用范围，运行检查与业务验收分别取证。 |

功能完整、接入真实服务、验证通过或方案选中都不改变测试资产的归属。正式方案确定后的产品开发归正式实现。采用测试代码时，任务注明目标行为、契约、需移除的实验装配和验收条件，按[运行隔离与迁入要求](architecture-rules.md#正式实现与测试实现隔离)实施。设计或调整测试工程时读[测试工程规范](architecture-rules.md#测试工程与自动化规范)。探索报告关联场景、算法或路径、版本与结果。

生成物记录来源和重建入口，变更落在生成源。通用研发工具沿用项目目录并登记索引，目录随产物建立。

<a id="document-and-artifact-locations"></a>

## 文档与产物落点

需要定位正文时先查 `docs/index.md` 的实际映射。已有正文原位更新，新建时使用默认落点。入口新增、移动或替代时同步索引和直接引用。

| 产物 | 默认落点 |
|---|---|
| Spec / Quickstart | `specs/<能力>/spec.md` 和相邻 `quickstart.md` |
| 原型代码和静态资源 | `tests/prototypes/<能力>/<用例>/index.html` 和相邻 `assets/`。原型引用与确认记录归对应 Spec 或索引指向的权威正文。 |
| Test Report | `docs/test-reports/<主题>/<批次>.md`，简单任务可在当前任务记录 |
| Issue | `docs/issues/<问题编号>.md` |
| Architecture Review Record | `docs/test-reports/<主题>/<批次>-review.md` |
| Prompt Review Record | 当前任务记录，需独立落盘时用 `docs/test-reports/<主题>/<批次>-prompt-review.md` |
| Blueprint / Scenario Sequence / Interface Contract | `docs/blueprint.md`、`docs/sequences/<场景>.md`、`docs/contracts/<接口或协议>.md` |
| Technical Research and Selection Report | `docs/research/<主题>.md`，按需建立 |
| 运维手册、其他文档 | `docs/runbooks/`，其他文档在 `docs/` 按用途归类 |
| Code Review Rules | `docs/code-review-rules.md` |
| Plan／Task | 当前任务或既有计划载体，同一份正文 |
| Status | 沿用项目进度记录，首次可用当前任务，独立文档默认 `docs/status.md` |
| 初始化运行资产 | 项目根目录 `.sdd-init.lock` 和 `.sdd-init-recovery/`，由初始化器管理 |
| 项目研发规则 | `.agents/governance/`，按需建立 |
| 共享资源、Skills、角色 | `.agents/skills/sdd-workflow/sdd/`、`.agents/skills/sdd-workflow/skills/`、`.codex/config.toml` 中的角色引用 |

<a id="authoritative-documents"></a>

## 权威实体

| 实体 | 权威内容 |
|---|---|
| Blueprint | 高位产品用例、终端、关键体验及验收维度，已确认架构职责、边界、不变量和 ARC。采用 ADR 的项目用其记录具体取舍。 |
| Technical Research and Selection Report | 调研问题、候选方案比较、证据引用、选型建议和确认记录。已确认的架构决定归 Blueprint 或项目已有 ADR，实际验证结果归对应 Test Report。 |
| Spec | 具体需求、业务规则、条件、异常和 AC。引用适用 Blueprint 条款与原型。 |
| Scenario Sequence / Interface Contract | 设计中的协作顺序、接口语义与异常约定。运行事实归对应 Test Report。 |
| Quickstart | 可复跑的操作、条件与预期。由上游工单提供；集成测试按 sdd-test-loop 复用并补齐本轮运行信息。正式落盘由 sdd-documenter 按需归并。 |
| Test Report / Architecture Review Record | 分别维护实际验证的批次事实和架构检查项的历次证据。 |
| Prompt Review Record | 维护本轮提示词规则映射、场景依赖、审查发现和验证证据。已确认职责及预期行为引用各自权威正文。 |
| Issue | 独立问题事实、Bug 工单及处理状态。修复方案引用 Plan／Task。 |
| Plan／Task、Status | 分别维护实施方案与任务、进度与恢复点。验证结果引用对应报告和版本。 |

代码记录实现事实。模板规定产物结构，确认后的决定归并到对应实体。引用在使用处维护，区分设计依据与指定版本的执行证据。

## Skill 场景与对象分工

下表定位各流程的输入和回执，产物归属由[工程资产边界](#工程资产边界)与[文档与产物落点](#文档与产物落点)统一维护。

| 输入与回执入口 | 产物载体 |
|---|---|
| 已安装的 `sdd-init` Skill | 目标仓库的托管导航、分发资产和安装回执 |
| [sdd-documenter](delegation.md#文档交接) | 项目权威正文和写后诊断 |
| [sdd-develop](../../skills/sdd-develop/SKILL.md) | Spec／AC、工单验收计划与方案、Plan／Task、点对点验收证据和集成准备条件 |
| [实施交接](delegation.md#实施交接) | 接收含验收依据的上游工单，按 Plan／Task 实施，交付版本及代码单测等局部证据 |
| [缺陷修复](../../skills/sdd-bugfix/SKILL.md)，输入异常报告或原 Issue 及已确认行为依据 | 原 Issue、归因及历次复验证据、Plan／Task、修复版本、关闭依据或恢复条件 |
| [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) | 用户功能集成测试的验收文档及 Test Report |
| [sdd-review-code](../../skills/sdd-review-code/SKILL.md) | Architecture Review Record |
| [提示词审查](../../skills/sdd-review-prompt/SKILL.md)，输入待审指令版本和实际加载依据 | [Prompt Review Record](../assets/prompt_review_template.md)，记录规则、发现和适用的复验结果 |
| [sdd-deliver](../../skills/sdd-deliver/SKILL.md) | Git 与平台交付回执、目标环境的服务状态和运行回执 |

<a id="testing-scope-constraints"></a>

## 测试范围约束

以已确认的验收目标、范围和标准为准。从 Spec／AC、指南和任务约定推导常规数据、边界取值及顺序，记录依据与覆盖，保持已授权范围。仅在范围或标准无法确定、数据涉及新增业务含义、需新增外部授权或有不可逆影响时，按[职责与交接](#职责与交接)暂停受影响项及其依赖。集成测试的环境、验收文档、证据和用户反馈按 [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) 处理。

## 实施和独立审查

coder 按[实施与局部自验](implementation.md)修改实现、测试及自动化脚本并完成定向局部自验。validator 按任务负责用户功能集成测试、归因检查与架构 Review，核对断言和覆盖。集成测试按已明确范围执行，Test Gate 仅表达该范围在所声明版本和环境下的结果。架构遵循与整改复核按 sdd-review-code 执行。独立性按实际执行者判断，需要独立执行者时按[委派与独立性](delegation.md#委派与独立性)安排。

## 交付

本轮任务包含 Git 交付、部署、启动或重启时，进入 [sdd-deliver](../../skills/sdd-deliver/SKILL.md)。讨论、落盘、实施和验证本身不触发交付。操作范围以已有授权为准，后续路径按该 Skill 的规则处理。

## 架构变更与遵循检查

按语义影响判定，项目在遵循规范维护具体判据。先判断 L2，再判断 L1 或 L0。

| 级别 | 条件与动作 |
|---|---|
| L2 | 改变职责、状态权威、决策权限、信任边界、依赖方向或关键不变量，按项目门禁确认。 |
| L1 | 已确认边界内的契约扩展，同步生产者、消费者及异常语义。 |
| L0 | 外部契约与架构语义均未改变的调整。 |

提示词、目录及正文迁移按同一语义影响判断。判据无法覆盖的变更按[决策权限](#人与-agent-协同及决策权限)处理。实际遵循检查与取证由 [sdd-review-code](../../skills/sdd-review-code/SKILL.md)执行。
