# Architecture Review Record — 标记付款架构对齐

## 1. Scope and Context

- 目标：在已确认架构下将付款状态写入统一到现有服务，保留公开调用行为。实际调用者为 Main `/root`；阶段调度为 `/root/payment_refactor`。授权仅当前隔离项目、付款适配实现及直接相关局部测试；文档仅本记录及[实施 Plan](../../../specs/order/payment-alignment-plan.md)。不修改提交、取消、蓝图、规则、外部配置，不部署。
- 依据：[Blueprint](../../blueprint.md) ARC-1～ARC-4、[订单契约](../../contracts/order.md)、[Code Review Rules](../../code-review-rules.md) CR-001、[Spec](../../../specs/order/spec.md)。目标与方案已由 Main 转交确认，无新增架构决定。
- 基线：HEAD `4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df`，初始工作树干净；付款源 SHA-256 `1a6052d6ba2fa2fd34999433ac5068231ab79a173aaeb41a17358872fcd691ae`。
- 环境：隔离本地夹具，Python 3.12.3、SQLite 3.45.1、标准库；每次临时文件数据库、关闭连接后清理。无网络。初审与复核执行者 `/root/payment_refactor/architecture_review`（sdd-architect），不参与实施；行为验收由技能 Agent 执行。
- 规则有效性：CR-001 明确覆盖付款变更触发、实际链路和违规判据，继续有效。初审曾判断无必须先维护规则的缺口；整改复核更正：CR-001 不能覆盖 ARC-2～4 的全部适用要求，CHK-002～004 保留映射待查 UNVERIFIED。现有代码静态符合不替代规则映射。Main 须告知缺口，由用户决定何时维护；未获授权不更新规则。

### 行为基线与验收判据

2026-11-15 整改前由技能 Agent 在公开 `ui.mark_paid(connection, order_id)` 入口实测：现存订单返回 None，关闭重开 SQLite 后 paid；缺失订单抛 `ValueError('order not found')`；`PRAGMA query_only=ON` 后写入抛 `OperationalError('attempt to write a readonly database')`。均与契约相符。现有 `python -B -m unittest discover -s tests -v` 2/2 PASS。测试数据是新建 ORDER-1；调用者负责连接生命周期。无已确认的延迟预算或其他量化指标。

保持验收须在整改版本通过公开调用核对以上结果；并验证 commit 异常不转换为成功、不由适配层关闭连接。数据库异常注入属于局部测试边界，持久化判据使用真实文件 SQLite。

历史业务偏差单列：整改前运行 `python -B checks/acceptance.py --scenario AC-2`，退出 1，实际 accepted=true、重开 persisted_status=submitted；确认预期为 false/cancelled。该偏差不是应保持的需求，源码 `submit_order` 无条件写 submitted 与付款调整无直接依赖，本轮保留并交 Main。AC-1 的全场景验收由后续集成阶段执行，本轮不代判；AC-3 配置缺端点与授权，不发生真实调用。

## 2. Review Checks and Follow-up

| 规则或约束 | 适用性 | 依据及范围 | 检查项 |
|---|---|---|---|
| CR-001 / ARC-1、工程骨架 | 适用 | UI → 服务 → SQLite 的职责、实际依赖与手工模块结构 | CHK-001 |
| ARC-2 / 付款契约 | 待查 UNVERIFIED | 共享持久化及交互语义适用，但 CR-001 缺完成/异常/返回语义映射 | CHK-002 |
| ARC-3 / 测试隔离 | 待查 UNVERIFIED | 共享测试隔离适用，CR-001 未映射正式依赖与测试数据隔离 | CHK-003 |
| ARC-4 / 环境装配 | 待查 UNVERIFIED | 共享环境边界适用，CR-001 未映射网络、配置与环境装配 | CHK-004 |
| 运行保障、并发与后台恢复 | 不适用 | 蓝图无相应机制；不得新增运行策略 | 不计通过数 |
| 产品观测与故障隔离 | 不适用 | 蓝图明确无产品日志；测试 JSON 不算观测实现 | 不计通过数 |
| 生成模板同步 | 不适用 | 无脚手架生成机制；手工工程结构仍按 CHK-001 核对 | 不计通过数 |

### CHK-001: 付款职责与工程结构

- 初审：sdd-architect 只读核验基线 `src/ui.py`，仅调用 `read_status` 后自行 UPDATE、commit，违反 CR-001/ARC-1，FAIL。服务 `set_status` 已具备同等读取、写入、提交职责，无需新增模块。
- 整改工单：仅 `src/ui.py` 通过现有 `order_service.set_status` 写 paid，UI 不直接执行状态 SQL、不承担 commit。保持签名、None 返回、paid 结果、异常传播和调用者连接生命周期；禁止修复取消后提交。
- 验收计划：实施者接单后制定同一 Plan、完成实现及局部自验；原架构审查者在实际整改版本独立复核；技能 Agent 在局部证据就绪后执行业务保持验收。
- 架构复核方案：沿 `ui.mark_paid → order_service.set_status → read_status/UPDATE/commit` 追踪真实依赖，检查 UI 不写状态、不提交、不关闭连接，未新增分层或测试依赖；源码及实际服务委派证据共同满足 CR-001 即通过。
- 行为验收方案：按上节基线从公开入口执行现存订单、缺失订单及只读数据库检查；执行局部 commit 失败断言，核对实际候选版本。全部保持方可关闭。
- 实施 Task：[T001](../../../specs/order/payment-alignment-plan.md#t001-付款适配职责对齐与局部自验)。状态：Closed after recheck，PASS。初审 FAIL 保留，T001 已完成，整改复核及行为保持均通过。

### CHK-002: 付款持久化与异常契约

- 初审：静态 PASS，现有读取→UPDATE→commit、异常上抛与契约一致；动态基线见第 1 节。
- 工单：随 CHK-001 保持，不修改服务；同一 T001。
- 验收方案：原审查者核对相同连接进入现有服务、同步 commit 后返回、无异常吞掉或重试；技能 Agent 执行第 1 节全部付款保持判据。初审静态通过不能代替整改版本验收。
- 当前状态：映射待查 UNVERIFIED；实现静态核对及付款行为保持通过。缺口路径是付款服务 SELECT、UPDATE、commit 和失败返回；缺少持久化完成、失败传播及正常返回语义规则。恢复条件：用户决定维护时机并授权后，补入可执行项目规则，再沿本编号复核。

### CHK-003: 正式实现与测试依赖隔离

- 初审：静态 PASS，src 无 tests/checks、测试身份或夹具配置依赖；测试调用正式模块。
- 工单：随 CHK-001 保持；仅直接相关测试在 tests，禁在 src 加测试分支或运行开关；同一 T001。
- 复核方案：原审查者检查所有 src 导入及实际付款装配，检查测试调用真实正式模块、数据独立、清理可执行；符合 ARC-3 则通过。
- 当前状态：映射待查 UNVERIFIED；实现静态核对未见偏差。缺口为 src 全依赖及 tests 装配中的运行隔离与数据隔离规则；恢复条件：用户决定维护时机并授权后，映射已确认 ARC-3，沿本编号复核。

### CHK-004: 本地环境及外部边界

- 初审：静态 PASS，付款链无网络，storage 仅连接及建表，文件 SQLite 为已确认选择。
- 工单：随 CHK-001 保持，不改配置与 storage；同一 T001。
- 复核方案：原审查者追踪实际装配及 diff，技能 Agent 核对运行环境，确认同步本地 SQLite、无外部依赖或网络副作用即通过。
- 当前状态：映射待查 UNVERIFIED；实现静态核对未见偏差。缺口为 ui/service/storage 与 runtime 配置上的网络、外部配置及环境装配规则；恢复条件：用户决定维护时机并授权后，映射已确认 ARC-4 及文件 SQLite 选择，沿本编号复核。

### 整改版本复核与行为验收证据

候选为 HEAD `4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df` 加本轮未提交改动；未创建新提交。代码和测试仅 `src/ui.py`、`tests/test_order.py`，文档仅本记录与 Plan。

| 文件 | SHA-256 |
|---|---|
| src/ui.py | 1b43c863d5f9dd8100d3c5a9f0dade6cde3e020502d780bf933cb489a122c63c |
| tests/test_order.py | 24f31eae7e6ae3f5c15430f9afa1b8d4e045f8c093f9f25f95f3718df7ecc87e |
| src/order_service.py（未改） | 96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de |

| 批次 / 执行者 | 原编号、方法及实际结果 | 结论 |
|---|---|---|
| 2026-11-15 实施者 | T001 完成；unittest 5/5 PASS，局部详情见 Plan | 实施完成 |
| 2026-11-15 原 sdd-architect | CHK-001：核对候选哈希、diff 与真实调用链 UI → set_status → read_status → UPDATE → commit；UI 无 SQL/commit/异常处理/关闭连接，无新增模块，手工工程结构与导入方向符合 | 架构复核 PASS |
| 同批原 sdd-architect | CHK-002：服务未改，隐式 None、异常上抛；CHK-003：读全部 src，无测试依赖，mock 仅 tests、临时数据库清理；CHK-004：本地同步 SQLite，storage/runtime 未改、无网络 | 实现静态核对无偏差，规则映射 UNVERIFIED |
| 2026-11-15 技能 Agent | 独立运行 `python -B -m unittest discover -s tests -v`，5/5 PASS，包含真实文件持久化、缺失订单、只读数据库和 commit 失败/调用者 rollback | 付款保持 PASS |
| 同批技能 Agent | 另从公开 ui.mark_paid 入口在新临时文件 SQLite 执行：返回 None、调用后连接仍可读 paid、关闭重开 paid；缺失订单 ValueError('order not found')；query_only 写失败 OperationalError('attempt to write a readonly database') 向上传播，原 paid 保留 | CHK-001/002 行为验收 PASS；CHK-001 关闭 |

审查者未重复执行动态测试；上表独立行为验收由未参与实现的技能 Agent 实测。初审和整改后服务哈希一致，历史 AC-2 事实仍有效，不需为付款复核反复执行全场景验收。

## 3. Gate and Remaining Work

- Review Gate：UNVERIFIED（全范围），CHK-002～004 的项目规则映射缺口尚待用户决定维护时机。CR-001 / CHK-001 局部整改架构复核 PASS 且关闭，不扩大为全范围 PASS。本轮代码偏差已解决，映射缺口保留并交 Main。
- 行为保持：付款公开行为及局部异常验收 PASS；历史 AC-2 FAIL 单列，不能称已满足需求。
- 集成准备：实际候选为上列 HEAD 加未提交两代码/测试文件及两文档，付款路径可测；映射缺口不导致依赖、入口或数据不可用，不阻止本地集成开测。本地 Python 3.11+、标准库、可写临时目录、项目根执行为真实开测条件。运行入口及数据复位见[现有验收指南](../../../specs/order/quickstart.md)。AC-2 可以开测但存在已知失败；无需阻止其他本地场景。AC-3 缺授权端点与调用权限，恢复须由有权人员提供，不能以本地结果替代。集成 Test Gate 由 Main 后续独立 test-loop 阶段判断，正式发布未授权。

- 写后检查：两文档读回，对照初审、复核、实施与实测回执核对编号、引用、归属及范围；无新增架构决定。机械检查命令 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/payment-alignment-review.md specs/order/payment-alignment-plan.md`，退出 0，2 文件、0 errors、0 warnings（仅机械检查）；`git diff --check` 退出 0。文档检查不代表完整 Review Gate 通过。
