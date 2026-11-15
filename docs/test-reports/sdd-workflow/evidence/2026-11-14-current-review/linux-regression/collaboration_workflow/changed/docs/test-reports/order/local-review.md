# Architecture Review Record — 订单本地缺陷修复相关审查

## 1. 范围与依据

- 目标：检查隔离订单实现及修复后的模块职责、状态权威、文件持久化、同步接口、测试依赖及实际装配。只审查并维护本记录；源码修复由 Bugfix 执行者承接。
- 授权：[TASK.txt](../../../TASK.txt)；本地 Python、标准库文件 SQLite；不访问外部服务、不配置凭据、不部署、不更新蓝图或规则。
- 依据：[项目索引](../../index.md)、[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[Blueprint](../../blueprint.md) ARC-1～4、[项目规则](../../code-review-rules.md) CR-001～004、[共享架构规范](../../../.agents/skills/sdd-workflow/sdd/references/architecture-rules.md)。
- 基线：Git HEAD `95cfcb31cf183d04b7ba1359a8dfe80d28608b00`，初读时工作区无改动。2026-11-14 独立审查 Agent `order_review`；Python 3.12.3、SQLite 3.45.1，运行事实由 `python -B checks/runtime_details.py` 实测。此命令不产生验收结论。
- 修复快照：同一 HEAD 加未提交修复；`src/order_service.py` SHA-256 = `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，`src/ui.py` = `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`；其余 src 不变。审查者逐文件读取、`git diff -- src`、`rg` 全写入及依赖扫描、`sha256sum src/*.py` 与[修复环境](evidence/fixed-runtime.json)和[独立复验](evidence/fixed-integration.json)哈希一致。
- 基线文件 SHA-256：`src/order_service.py` = `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`；`src/ui.py` = `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b`；`src/storage.py` = `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9`；`src/__init__.py` = `10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded`。
- 保持判据：AC-1 返回 true 且重开仍 submitted；AC-2 取消后提交返回 false 且仍 cancelled；mark_paid 对现存订单保持 paid 并持久化；不存在订单抛 ValueError，数据库错误向上传播；函数签名不变。原先覆盖取消状态及未报不存在订单是缺陷事实，不是保持目标。
- 实测基线与修复集成验收由独立测试执行者记录，本记录只记录架构判断及其证据，不替代 Test Gate。

## 2. 规则筛选、映射与逐项记录

| 规则或共享指导 | 适用性 | 依据及取证范围 | 检查项 |
| --- | --- | --- | --- |
| CR-001；模块边界与依赖 | Applicable | ARC-1 明确 UI → service → SQL；遍查全部 src、正式调用及状态写入 | CHK-001 |
| 工程骨架规范 | Applicable | 实际 src 三模块、checks、tests 与 ARC-1/3 职责一致性；无 package 构建或代码生成模板，不新增模块要求 | CHK-001、CHK-003 |
| CR-002；状态权威与持久化 | Applicable | ARC-2 的文件 SQLite、service 写入、commit、重开与错误传播 | CHK-002 |
| 接口与交互语义 | Applicable | CR-002 已显式引用整个订单契约，CR-001 覆盖服务状态入口；取消及不存在订单语义在该引用范围内，不要求逐字复制所有 AC | CHK-005 |
| CR-003；正式实现与测试实现隔离 | Applicable | ARC-3，沿 src imports、checks/acceptance.py、tests/test_order.py 核查依赖方向 | CHK-003 |
| 测试设计与执行 | Applicable（本轮测试资产） | CR-003 映射正式依赖隔离；Quickstart 直接提供临时文件、清理、退出码及原始 JSON 的执行约定，实际结果归 Test Report，不自动升级为额外架构规则 | CHK-006 |
| CR-004；环境边界与运行装配 | Applicable | ARC-4；runtime.json、storage.connect、实际检查入口，不允许本地调用联网 | CHK-004 |
| 业务与运行保障分工 | Not applicable（专项机制） | 蓝图明确无后台恢复；src 无重试、限流、熔断、保活或业务补偿机制，取消是订单业务状态，纳入 CHK-005；不引入运行模块 | Not applicable |
| 观测数据与日志契约 | Not applicable | 蓝图及契约明确无产品日志采集与传输；验收 JSON 为验证资产输出，不能当作已实现产品观测 | Not applicable |
| 观测影响与故障隔离 | Not applicable | 无产品观测路径、导出器或缓冲；因此不运行日志故障或预算实验 | Not applicable |
| 并发、超时、迟到、后台恢复 | Not applicable（专项机制） | 蓝图明确仅同步函数交互，无并发任务和后台恢复；SQLite 错误仍须传播，纳入 CHK-002 | Not applicable |
| 远端环境及真实外部接口验证 | Not applicable（本地架构审查范围） | Spec AC-3 要求真实服务，当前端点 null、authorized=false；其阻塞归 Test Report，不能借本地 CR-004 通过宣称 AC-3 通过 | Not applicable |

规则有效性：逐项核对后，CR-001～004 已覆盖本轮相关架构决定。初读曾将“未逐字复述契约断言／Quickstart 操作”视为 CHK-005/006 映射缺口；进一步沿 CR-002 的契约引用及 CR-003 的隔离范围复核后，此项疑点已消除，没有确认的实质架构映射缺口。业务断言及测试执行细节分别沿契约和 Quickstart 验证，不据此自动要求新增规则。未修改规则。

### CHK-001：订单状态写入权威与工程边界

- 依据、对象：CR-001、ARC-1；[ui.py](../../../src/ui.py)、[order_service.py](../../../src/order_service.py)、[storage.py](../../../src/storage.py)。
- 初审事实：FAIL。基线 `ui.mark_paid` 第 5～6 行直接执行订单 UPDATE 和 commit，绕过唯一业务入口。storage 仅 connect/建表，service 的 create/set_status 是其他状态写入位置；实际三模块工程结构存在，但 UI 的职责语义越界。
- 整改工单：沿本编号交 Bugfix 原 Issue/Task；若缺失订单异常缺陷获实测证实，由 mark_paid 委派现有 `order_service.set_status(connection, order_id, 'paid')` 可在同一缺陷补丁恢复 ARC-1。范围仅 UI 适配调用，保持公开签名、现存订单 paid 持久化、异常传播，不引入新分层。未授权的独立技术重构不实施。
- 验收计划及复核步骤：修复快照就绪后原独立审查者检查 UI 调用、全部 SQL 写入及 imports；通过条件是 UI 无状态 SQL/commit、实际调用既有服务入口，storage 无业务裁决。
- 行为保持：独立测试执行者从 `ui.mark_paid` 公开入口检查现存订单 paid／第二连接可见、不存在订单 ValueError、数据库异常传播，并关联修复版本。
- Implementation Tasks：[ORDER-002](../../issues/ORDER-002.md)、[Bugfix Plan T001](../../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)。
- 修复复核：ui.py:3 导入正式服务、:7 调用 set_status，UI 不再执行 SQL/commit。service 保持状态写入权威，storage 仍只连接／建表。复验 PAID-1/2/3、MISSING-1、DB-1 在同一源哈希均 PASS，paid 持久化及错误传播保持。
- 当前：Closed after recheck，PASS。审查者未修改源码。

| 批次／审查者 | 方法 | 快照及事实 | 结论 |
| --- | --- | --- | --- |
| baseline／order_review | 全量读取 src 与行号核对 | 基线 ui.py:5～6 直接写状态，其他目录职责与蓝图相符 | FAIL，等待缺陷修复后复核 |
| fixed／order_review | 按原路径复查服务委派、全写入与业务保持证据 | 修复哈希见上；[独立复验](evidence/fixed-integration.json) PAID-1/2/3、MISSING-1、DB-1 PASS | PASS，复核关闭 |

### CHK-002：文件持久化、完成及数据库失败语义

- 依据、对象：CR-002、ARC-2、契约；service 写入 → commit，storage 文件连接，测试重开路径。
- 初审事实：静态路径符合。create_order、set_status 在写入后 commit；cancel/submit 调用 set_status；未捕获并转换数据库异常为成功。mark_paid 基线虽提交，但职责越界单列 CHK-001。持久化动态证据等待独立测试基线及修复复验，不以读码代替文件读回。
- 验收计划：修复后复查所有写入和错误传播；复用目标版本独立测试的第二连接／关闭重开及数据库写入失败证据；commit 失败传播沿同步无捕获调用链静态检查，证据不足时才补故障实验。通过条件为写成功才返回成功、提交错误向上传播。
- 整改工单：本项尚无独立结构整改要求；AC-2 业务缺陷交 CHK-005 和 Bugfix。
- 行为保持：使用 AC-1、AC-2、mark_paid 及异常判据；无新增性能阈值。
- Implementation Tasks：[Bugfix Plan T001](../../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)。
- 修复复核：所有写入均由 create_order/set_status 在 SQL 后 commit；submit_order 仅在 set_status 完成后返回 true，无捕获异常或提前成功。复用[独立复验](evidence/fixed-integration.json) NEW-1、AC-1/2、CANCEL-1、PAID-1/2/3、STATUS-1 的第二连接／重开持久化证据及 DB-1、RECOVERY-1 的 SQLite 写错误传播／恢复证据。commit 异常向上传播由无异常转换的同步调用链取证，没有声称动态注入过 commit 专用故障。
- 当前：Closed after recheck，PASS；初审未完成的动态证据已在目标快照补足。

### CHK-003：正式依赖、验证资产及装配方向

- 依据、对象：CR-003、ARC-3；src 全部 imports、checks/acceptance.py、checks/runtime_details.py、tests/test_order.py。
- 初审事实：PASS。src 仅 storage 导入标准库 sqlite3；没有测试身份、测试运行器、夹具配置或动态加载。checks 和 tests 导入 src 正式模块，测试身份不进入数据库或业务路由。src/__init__.py 无运行装配副作用。
- 验收计划：修复后检查改动 imports 及实际服务调用，禁止通过测试身份分支修复；不要求新增框架或生产配置。
- 整改工单／行为保持：无需整改，动态功能结果归集成报告。
- 修复复核：UI 新依赖只指向正式 order_service；src 其余依赖未变；新增 tests 和 checks/integration.py 只调用正式模块，SQL 诊断／PRAGMA 故障注入留在验证资产中。无测试身份分支和产品测试开关。
- 当前：Conforming，PASS（修复快照）。

### CHK-004：本地环境与外部边界

- 依据、对象：CR-004、ARC-4；runtime.json、src、checks。
- 初审事实：PASS。runtime 指向每场景临时 SQLite 文件、端点 null、外部未授权、network=false；正式模块仅本地 SQLite。acceptance 的 AC-3 仅读配置返回 BLOCKED，无网络客户端和外部调用。
- 验收计划：修复后复查源码和配置差异，无网络依赖／外部配置变更。通过条件为本地操作仍不触网，不制造真实外部回执。
- 整改工单：无。AC-3 的恢复条件为有权人员提供已授权真实测试端点及权限，并在另行授权范围运行真实验证。
- 修复复核：正式运行装配及 runtime 未变，源码无网络导入和调用；[修复环境](evidence/fixed-runtime.json)仍 external_endpoint=null、authorized=false。
- 当前：Conforming，PASS（修复快照）；不据此关闭 AC-3。

### CHK-005：契约状态与错误语义

- 依据、对象：CR-002 已引用完整契约；结合 CR-001、契约 submit_order、mark_paid 及异常段、Spec AC-2 检查实际状态路径。规则引用契约无需复制每个业务断言。
- 初审事实：基线 submit_order 第 29～31 行忽略 read_status 返回值，任意现存状态写 submitted 并返回 true；ui 第 5～6 行不检查存在性，UPDATE 零行仍正常返回。独立[基线实测](evidence/baseline-integration.json)的 AC-2、MISSING-1、ISOLATION-1 证实失败，已分别进入 [ORDER-001](../../issues/ORDER-001.md)、[ORDER-002](../../issues/ORDER-002.md)。这些是现行缺陷，不是新需求。
- 验收计划：修复后独立核对 cancelled 分支在写入前返回 false、其余已确认路径与签名保留；mark_paid 经 read_status 检查的服务写入口抛 ValueError；复用目标快照的定向及集成实测。
- 整改交接：保持 AC-1、cancelled 持久化及 paid 结果；仅修复已确认本地缺陷，链接原 Issue/Task，不扩展未声明状态转移规则。
- 映射复核：初读映射疑点经 CR-002 设计依据的完整契约引用消除，不要求用户修改规则。
- 修复复核：submit_order 在 cancelled 状态先返回 false，不执行状态写入或 commit；UI 经 set_status 的 read_status 检查不存在对象。签名无变化，不扩展未确认状态转移策略。[独立复验](evidence/fixed-integration.json) AC-1/2、MISSING-1、ISOLATION-1 全 PASS；[原验收入口](evidence/fixed-acceptance.json)AC-1/2 同样 PASS。[Bugfix Plan T001](../../plans/order-bugfix/plan.md#t001-恢复取消提交与缺失付款契约)关联原 Issue；行为保持的其他付款及错误结果见 CHK-001/002。
- 当前：Closed after recheck，PASS。

### CHK-006：验证资产的执行边界

- 依据、对象：Quickstart、共享测试设计与执行；checks/acceptance.py 及 tests/test_order.py。
- 初审事实：静态观察为每场景 TemporaryDirectory、文件 SQLite、固定 ORDER-1，连接在 finally 关闭、上下文清理；AC-1/2 对照行为断言、原始逐项 JSON、退出码 0/1/3，AC-3 不模拟外部成功；单元 unittest 的 setUp 使用 cleanup。不存在本地 CI 配置、并行执行或重试机制，不添加相关策略。实际失败清理与复跑事实由 Test Report 证明。
- 映射复核：CR-003 检查正式依赖隔离，Quickstart 已直接明确执行约定；这些并非未落地的架构决定，不要求把验收指南全文转为新增规则。
- 验收计划：独立测试执行者提供目标快照、实际环境、原始结果、复跑及清理证据；审查者核对未为通过测试引入产品分支。
- 不适用：CI、生成模板、超时及重试专项机制因无项目机制不适用；不引入新策略。
- 修复复核：独立[复验证据](evidence/fixed-integration.json)记录实际 Python/SQLite、源哈希、固定测试哈希及 source_stable_during_run=true，初次与复验均保留原始输出；测试执行者另维护集成报告。未引入重试以掩盖首次失败。
- 当前：PASS（修复快照的验证资产边界与执行约定）；不在本项宣称产品集成 Test Gate 通过。

## 3. Gate 与后续条件

- 基线 Review Gate：FAIL，CR-001／CHK-001 存在明确职责越界；CHK-002 等待目标动态证据，CHK-005 为已证实契约缺陷；CHK-005/006 的初读规则映射疑点经完整引用复核已消除。CR-003/004 的基线检查通过；不适用项不计通过数。
- 剩余架构工作：无。原问题在同一 Bugfix T001 修复，相关行为与原检查项复核完成；未实施独立技术重构。
- 修复版本 Review Gate：PASS。上述实际工作树哈希的 CR-001～004 及相关 CHK-001～006 全部通过；不适用专项不计通过。不存在尚未解决的本轮架构偏差或实质规则映射缺口；未扩充业务判据或维护架构规则。
- 集成就绪与 Test Gate：目标快照的本地行为保持证据为 13 PASS、0 FAIL，AC-3 独立 BLOCKED。按[验收指南](../../../specs/order/quickstart.md)在相同本地环境复跑；集成 Test Gate 由独立 Test Report 判断，真实服务 AC-3 的外部阻塞不以本地 Review PASS 或单测通过替代。
- 写后检查：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/local-review.md`，退出 0，1 文件、0 错误、0 警告；已核对依据、范围与语义，机械结果不代替架构结论。无远程链接校验及全仓扫描。
