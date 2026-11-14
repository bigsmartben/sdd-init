# Architecture Review Record — 订单本地初审与修复复核

## 1. Scope and Context

- 目标：检查全部正式状态读写、持久化、异常、依赖及运行装配；调用者和回执接收方为 Main `/root`。审查者为独立专业角色 `/root/order_architecture_check`，未实施产品修复。
- 依据：[Blueprint](../../blueprint.md) ARC-1～4、[接口契约](../../contracts/order.md)、[CR-001～004](../../code-review-rules.md)、[Spec](../../../specs/order/spec.md)、[验收指南](../../../specs/order/quickstart.md)，以及共享 [架构规范](../../../.agents/skills/sdd-workflow/sdd/references/architecture-rules.md) 与 [观测专项规范](../../../.agents/skills/sdd-workflow/sdd/references/observability-baseline.md)。
- 初审版本：`89df9f629407a6b572c6f65c87fc9768e0f52f5d`；初审开始无未提交修改。执行日期 2026-11-15；Python、SQLite 版本、实际源码内容及 SHA-256 均见 [初审原始证据](review-initial.json)。隔离本地文件 SQLite，每轮独立临时目录、关闭连接并清理，未访问网络。
- 修复复核快照：基础 HEAD 未改变，叠加 [T001](../../../specs/order/plan.md) 的未提交修复。`src/order_service.py` SHA-256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，`src/ui.py` 为 `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`；storage、__init__ 与初审相同。冻结集成资产 SHA-256 为 `496fa99f09e2c5d0796678ac580ffa49553e155f266a68673b68e58e93e1bc99`。2026-11-15 同一独立审查者复核，执行前后哈希一致，完整记录见 [复核证据](review-fixed.json)。
- 授权边界：只审查并写本记录及原始证据，不改设计、规则、产品代码、外部配置或部署。修复须由 Main 分派；只沿已确认接口和架构恢复行为。
- 规则有效性：CR-001～004 与 ARC-1～4 对应且仍有效。取消提交的拒绝语义有明确契约，但项目规则违反条件未明确覆盖，作为 CHK-006 保留映射待查；不自动补规则，不把规范建议当门禁。
- 行为基线：确认判据为 AC-1 持久化 submitted、AC-2 取消不可被提交覆盖、现存订单 mark_paid 持久化 paid、对象不存在抛 ValueError、数据库异常上抛。初始实测与确认行为不同的项目见 CHK-001、CHK-005，不能把缺陷作为应保持行为。AC-3 需真实外部服务授权，超出本审查执行边界，测试结果由集成测试报告负责。

## 2. Review Checks and Follow-up

| Rule ID | Applicability | Rationale and source | Check |
|---|---|---|---|
| CR-001 / ARC-1 | Applicable | 全部状态入口及 UI 调用；初审存在直接写入 | CHK-001 |
| CR-002 / ARC-2 | Applicable | SQLite 文件持久化、成功时点与异常 | CHK-002 |
| CR-003 / ARC-3 | Applicable | src 与 checks/tests 的导入及装配 | CHK-003 |
| CR-004 / ARC-4 | Applicable | 本地配置、网络及真实服务边界 | CHK-004 |
| 通用：模块边界与依赖 | Applicable | storage 连接建表，业务服务状态写入，UI 服务适配 | CHK-001、CHK-003 |
| 通用：状态权威与持久化 | Applicable | SQLite 唯一状态来源，无缓存/副本 | CHK-001、CHK-002 |
| 通用：业务与运行保障分工 | Not applicable | Blueprint 明确无后台机制，源码无重试、保活、重启、熔断或业务补偿 | Not applicable |
| 通用：接口与交互语义 | Applicable | 同步完成、取消、缺失订单及异常有明确契约 | CHK-001、CHK-002、CHK-005 |
| 通用：观测数据与日志契约 | Not applicable | Blueprint 无产品观测系统；checks 的 JSON 是验证证据，不是产品日志 | Not applicable |
| 通用：观测影响与故障隔离 | Not applicable | 无产品采集、导出、队列、缓冲或观测故障策略 | Not applicable |
| 通用：环境边界与运行装配 | Applicable | 文件 SQLite、隔离本地运行，无网络授权 | CHK-004 |
| 通用：测试隔离与可控验证 | Applicable | 测试仅调用正式模块，临时数据及诊断与版本明确 | CHK-003、CHK-007 |
| 专项：观测职责与隔离 | Not applicable | 无辅助遥测、观测运行控制或产品审计管线；订单表按业务实体检查 | Not applicable |
| 专项：数据保存与日志契约 | Not applicable | 无产品日志保存政策或日志生产消费链；业务 SQLite 归 CHK-002 | Not applicable |
| 专项：采集、持久化与故障处理 | Not applicable | 无观测采集、传输、轮转、缓冲饱和及导出路径 | Not applicable |
| 工程结构生成、媒体、后台机制 | Not applicable | Blueprint 排除，源码亦未存在这些路径 | Not applicable |
| 取消提交拒绝语义的项目规则映射 | Pending check | CR-002 引用契约但违反条件仅描述持久化/异常，未明确状态转移判据 | CHK-006 |

### CHK-001: 状态写入权威及 paid 适配

- 依据与路径：CR-001、ARC-1、mark_paid 契约。初始 `src/ui.py:mark_paid` 直接 UPDATE/commit；`order_service.create_order` INSERT、`set_status` UPDATE；cancel/submit 调用 set_status；storage 仅连接和建表。无其他状态写入位置。
- 初审：**FAIL**。UI 绕过唯一业务入口，同时 missing_mark_paid 返回无异常，而 missing read/set_status/cancel/submit 均抛 ValueError。现存订单 paid 可被第二连接读取，见初审证据。
- 整改工单目标：沿现有服务入口消除 UI 状态 SQL，保持公开函数签名、paid 持久化并恢复不存在订单 ValueError；不建立新职责或接口。具体实施由 Main 调度的 Bugfix 执行者决定。
- 验收计划与复核方法：Main 提供修复快照及 Task 后由本审查者检查全部写入位置、UI → set_status → SQL/commit；独立运行现存及不存在订单、写入/commit 故障。通过判据为 UI 无状态 SQL、服务唯一写入口、paid 第二连接可读且不存在订单抛 ValueError。
- 行为保持验收：集成测试执行者在修复快照回归 AC-1/AC-2、paid 与异常契约；本项独立直接调用作为相关行为补证。初审时 Not run；修复版结果见本项后续结果。
- Implementation Tasks：[T001](../../../specs/order/plan.md)；产品修复由独立实施者完成。
- 初审状态：Unfixed / FAIL。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | 全量复查状态 SQL 仅保留 service.create_order INSERT 与 service.set_status UPDATE；storage 仅建表。ui.mark_paid → order_service.set_status → read_status → UPDATE/commit，公开签名不变。独立 paid_second_connection/paid_reopen 均 paid；missing_mark_paid 为 ValueError，writes/commits 均 0。相关 execute/commit/closed 异常上抛。架构与适用行为保持均 PASS，Closed after recheck。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | PASS |

### CHK-002: 持久化完成与异常传播

- 依据与路径：CR-002、ARC-2。create/set_status 均 execute 后 commit；cancel 经过 set_status；submit 成功返回位于 set_status 后；初始 UI 自行 commit 的越界另归 CHK-001。
- 初审：**PASS**（限持久化及异常传播）。create、正常 submit、cancel、paid、set_status 的结果由独立 SQLite 连接读取。五个写入口分别注入 execute 和 commit 的 OperationalError，十例全部向上传播；不存在成功返回。证据为初审 JSON 对应各 case。
- 计划与判据：修复后检查全部写入与异常捕获路径，并重复第二连接读取和故障注入。调用失败不得变为成功；成功操作须 commit 后可回读。注入仅在审查调用方包装真实 SQLite 连接，无测试钩子进入 src。无自动 rollback 契约，不额外要求回滚机制。
- 整改：本项无独立整改；受 CHK-001/005 变更影响后复核。Implementation Tasks：[T001](../../../specs/order/plan.md)。
- 初审状态：Conforming / PASS（初始版本）；当时修复复核 Not run。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | 复查五个写入口及异常路径，正常操作通过 commit 后由第二连接读取；paid 关闭重开仍存在。10 项 execute/commit 故障上抛 OperationalError，独立连接仍读 pending，失败 create 无新行；测试方 rollback 仅用于清理，不宣称产品自动回滚。6 项关闭连接异常均 ProgrammingError。PASS / Conforming。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | PASS |

### CHK-003: 正式依赖隔离

- 依据与路径：CR-003、ARC-3。逐个阅读 src 全部模块及 checks/tests：storage 仅 import sqlite3；初始 service/ui 无 imports；src/__init__ 只有说明。checks 与 tests 导入 src，无反向导入、动态加载、测试身份判断或夹具配置开关。
- 初审：**PASS**。源码快照见初审 JSON；正式状态决策不依赖验收编号。
- 计划与判据：修复后复查全部 imports、动态加载及配置分支；只允许验证资产依赖正式模块，src 不加载 tests/checks/runtime 夹具身份。运行入口无测试替代行为。
- 整改：Not applicable；Implementation Tasks 不适用；修复时同一检查项复核。
- 初审状态：Conforming / PASS（初始版本）。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | 新增正式依赖只有 ui 对 order_service 的相对导入。逐个检查全部 src、扩展 tests 和新增 checks/order_integration.py，正式模块仍不加载验证资产、runtime 夹具配置或测试身份；依赖方向符合 ARC-3。测试故障包装仅在 tests 或审查脚本中。PASS / Conforming。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | PASS |

### CHK-004: 环境与外部调用边界

- 依据与路径：CR-004、ARC-4；runtime.json 和全部正式调用链。配置为 isolated-local-fixture、临时文件 SQLite，外部端点 null、权限 false、network false。src 无网络导入或调用。
- 初审：**PASS**。checks/acceptance.py 的 AC-3 仅返回 BLOCKED 与配置事实，没有模拟成功回执；独立审查亦无网络调用。
- 计划与判据：修复后核对正式入口与配置未引入外部调用或虚假外部证据。真实 AC-3 非本项通过的推论，恢复需有权人员提供端点、调用权限及相应执行授权。
- 整改：Not applicable；Implementation Tasks 不适用。
- 初审状态：Conforming / PASS（初始版本）。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | runtime 配置与初审相同；正式源码只有 sqlite3 技术依赖及内部服务调用，无网络调用。新增集成脚本 AC-3 始终 BLOCKED，不伪造真实服务回执。外部授权与端点仍缺失，但本地边界检查 PASS / Conforming。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | PASS |

### CHK-005: 取消后的同步提交语义

- 依据与路径：Blueprint 取消提交条款、接口契约 submit_order、Spec AC-2；通用接口语义。初始 submit_order 读取状态却不判断，随后 set_status submitted。
- 初审：**FAIL**。独立调用 create → cancel → submit 得 true，第二连接读 submitted。取消状态被覆盖；与持久化能力本身不是同一问题。
- 整改工单目标：恢复 cancelled 不写入且返回 false；保持 pending 正常提交 true/submitted、paid 公开入口和异常契约。Main 安排既有行为缺陷修复，实施方案不归本记录。
- 计划与判据：修复快照上检查状态决策及所有写入路径；运行取消后提交并检查返回 false、数据库仍 cancelled 且没有状态写入；正常提交 commit 后 true、重开后 submitted；缺失对象 ValueError。集成测试执行者负责 AC-1/AC-2 的正式复验。
- Implementation Tasks：[T001](../../../specs/order/plan.md)；架构与相关行为复验见本项后续结果。
- 初审状态：Unfixed / FAIL。项目规则映射缺口另归 CHK-006，不削弱明确契约失败事实。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | submit_order 仅在已读取状态 cancelled 时返回 False，发生在 set_status 前。独立 cancelled_submit_no_write 为 false/cancelled，writes=0、commits=0，原始 trace 只有 SELECT；非 cancelled 的 pending/paid/submitted 提交均 true/submitted。missing_submit 为 ValueError 且零写入。正常路径及故障语义保持。架构/契约与适用行为保持 PASS / Closed after recheck。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | PASS |

### CHK-006: 取消语义规则映射待查

- 依据与缺口：CR-002 虽引用订单契约，但违反条件没有取消状态保持或拒绝写入；现有 CR-001/003/004 亦未明确覆盖。CHK-005 直接依据确认契约可执行，但不能报告缺失项目规则映射已经通过。
- 初审与当前结论：Pending check / **UNVERIFIED**，没有授权擅自补写 Code Review Rules。
- 恢复条件：Main 回传项目规则适用性确认，或有权方决定规则维护时机并交付明确映射。届时沿原编号核对条款、触发条件、实际取证路径及违反判据。规则维护是否需要由用户决定。
- 整改与 Task：仅进一步查明映射，不是产品实现整改；责任为 Main 协调。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | 重新读取 CR-001～004，取消拒绝语义未新增明确违反判据；实现修复及 AC-2 通过只关闭 CHK-005，不证明项目规则映射已补齐。Main 明确未获新规则维护授权；没有新事实可消除映射疑点。UNVERIFIED / Pending check；继续沿本项恢复条件处理，不擅自增改规则。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | UNVERIFIED；映射待查 |

### CHK-007: 验证资产约束适用性

- 依据与对象：通用测试隔离与可控验证、Blueprint ARC-3、验收指南。checks/acceptance.py 和 tests/test_order.py 均使用标准库及正式模块，临时文件数据库、固定订单编号与独立目录；连接 finally/addCleanup 关闭，临时目录清理。
- 初审：**PASS**（结构及本轮验证条件）。测试边界为本地真实 SQLite；故障替代仅限审查方连接包装。测试断言对应确认行为；现有单元测试缺少取消检查，完整功能覆盖交集成测试执行者，不能以原有两例单测通过替代验收。
- 逐项适用：依赖边界、确定性/数据、结构/框架、断言、执行诊断适用；各场景临时目录隔离，无重试、无并行共享状态。后台恢复、时间随机性、CI 环境差异 N/A：无相应机制或 CI 装配输入，未推定 CI 已验证。初始证据记录运行版本、环境、原始结果及清理成功。
- 计划与判据：修复后复查验证资产变更，不以修改预期绕过契约；按原版本/场景关联保留首轮失败及复验结果。正式集成覆盖、统计与 Test Gate 由测试报告负责。
- 整改：Not applicable；Implementation Tasks 不适用。
- 初审状态：Conforming / PASS（初始版本）。


| Batch / Time / Reviewer | Action and evidence | Conclusion |
|---|---|---|
| fixed / 2026-11-15 / `/root/order_architecture_check` | 新增集成脚本在修复前已冻结，哈希与 Main 工单一致；原断言未改为迁就实现。每个本地场景独立临时文件、finally 关闭连接，缺失/异常/隔离检查直接使用正式模块，AC-3 明确保留阻塞。扩展单测只在测试资产内包装连接，不污染正式依赖。本轮审查33项通过且临时数据已清理、前后哈希一致。结构与本轮验证条件 PASS / Conforming；整体覆盖统计由集成测试负责。 依据 [复核原始证据](review-fixed.json) 与上述固定源码快照。 | PASS |

## 3. Gate and Remaining Work

- 初审 Review Gate：**FAIL**，适用版本 `89df9f629407a6b572c6f65c87fc9768e0f52f5d`。CHK-001、CHK-005 失败；CHK-002/003/004/007 通过；CHK-006 待查，N/A 不计通过。
- 当前修复版 Review Gate：**UNVERIFIED**。CHK-001/002/003/004/005/007 为 PASS，原产品及职责偏差均已复核消除；CHK-006 映射待查，不能报告全通过。初审 FAIL 保留上文，未以复核结果覆盖。
- 独立复核入口：`python -B -c "exec(open('docs/test-reports/order/review-probe.txt').read())"`；[可复跑审查脚本](review-probe.txt) 与 [33/33 PASS 原始输出](review-fixed.json) 仅为验证资产。依赖、职责及规则适用性另经本记录逐项语义审查，不能单凭执行计数推定通过。
- 行为保持交接：实际实施归 [T001](../../../specs/order/plan.md)，Bugfix 定向验证归 [Bugfix 报告](bugfix.md)。本角色独立覆盖取消零写入、paid 持久化、missing、异常和非 cancelled 既有提交行为。[修复版集成原始证据](evidence/fixed-integration.json) 已落盘为 19 PASS、0 FAIL、1 BLOCKED；[运行版本及命令](evidence/fixed-execution.json) 与本次源码快照一致。[正式修复版集成报告](fixed.md) 的 Test Gate 为 BLOCKED（AC-3）；本 Review 引用该独立结论，不代签测试或发布门禁。
- 剩余工作：CHK-006 由 Main 协调项目规则适用性确认或维护决定，接续条件见原检查项。无剩余产品整改目标；如源码再次变化，按影响沿原编号复核。
- 集成准备：本地场景可执行，文件 SQLite 无外部依赖。AC-3 缺少端点和权限仍阻塞，恢复需有权人员提供真实服务端点及调用授权；不以本地检查或审查证据替代。架构 Review 不等于正式发布证据。
- 写后检查：已运行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/architecture-review.md`，1 文件、0 errors、0 warnings。已读回核对来源、契约行为、N/A 范围、初审/复核版本和证据，CHK-006 保持未验证；机械检查不证明产品或整轮 Gate 通过。
