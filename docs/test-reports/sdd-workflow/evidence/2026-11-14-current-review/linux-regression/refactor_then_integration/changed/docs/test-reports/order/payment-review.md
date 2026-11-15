# Architecture Review Record — 付款路径架构对齐

## 1. 范围与基线

目标是按已确认 [Blueprint](../../blueprint.md)、[订单契约](../../contracts/order.md) 和 [CR-001](../../code-review-rules.md)，将标记付款状态写入职责归回现有服务，保持公开调用行为。授权代码范围为 `src/ui.py` 与 `tests/test_order.py` 的直接付款测试；取消、提交实现和外部环境不在整改范围。用户已确认需求、依据及方案边界。

初始版本为 `7a90ae57739b7ae93b554e0bd409259ab949a51e`，工作区干净。环境为隔离本地 Python 3.12.3、SQLite 3.45.1，逐场景临时文件数据库，无外部端点或网络授权。初审由独立 `payment_architect` 执行，实施由 `payment_coder` 执行，行为保持验收由阶段技能 Agent 执行；项目没有额外独立性要求。

行为判据来自契约及 [Spec](../../../specs/order/spec.md)：公开 `ui.mark_paid(connection, order_id)` 正常返回 None，将存在订单写为 paid 并 commit；关闭重开仍为 paid；缺失订单抛 ValueError，数据库异常向上传播；连接由调用者关闭，不增加网络、日志、重试、部署或运行依赖。不新增状态限制。AC-1 保持；AC-2 是明确需求，原有失败不得当作应保持结果。

2026-11-14 修改前定向基线：`python -B -m unittest discover -s tests -v` 为 2 tests / OK。公开付款临时文件库检查实际返回 None、重开状态 paid；MISSING 抛 `ValueError: order not found`；启用 `PRAGMA query_only=ON` 后付款抛 `OperationalError: attempt to write a readonly database`。`python -B checks/acceptance.py --scenario AC-2` 单独执行结果为 FAIL、退出 1：accepted=true、persisted_status=submitted，预期 false/cancelled。该既有业务缺陷已交 Main，付款整改不修改服务。

## 2. 适用规则与检查项

| 共享规范 | 项目映射及适用性 | 检查项 |
| --- | --- | --- |
| 模块边界与依赖、付款状态写入权威 | CR-001 / ARC-1，有效，覆盖实际 ui → set_status 调用及 SQL 归属 | CHK-001 |
| 状态权威与持久化、接口失败语义 | ARC-2 与契约已有确认，CR-001 未完整映射，待维护项目规则 | CHK-002 |
| 同步公开接口与副作用 | 契约、ARC-4，项目规则映射缺失 | CHK-003 |
| 测试隔离与可控验证 | ARC-3，项目规则映射缺失 | CHK-004 |
| 环境边界与运行装配 | ARC-2、ARC-4，项目规则映射缺失 | CHK-005 |
| 运行保障机制、观测数据与日志、观测故障隔离 | 不适用：Blueprint 明确无后台恢复、限流、产品日志或观测机制；不将机制缺少记为实现 PASS | 不适用 |
| 工程骨架 | 现有 ui/order_service/storage 边界适用并入 CHK-001；无生成模板、无新增模块或分层 | CHK-001 |

CR-001 的设计依据、变更触发、取证路径及违规条件仍有效。未完整映射的 CHK-002～005 保留 UNVERIFIED（项目规则待查），同时记录 Blueprint/契约补查事实。恢复条件为用户决定维护时机并授权生成或更新规则，随后按有效规则复核；本轮不修改规则，不宣称全蓝图 PASS。

### CHK-001: 付款状态写入职责

- 依据与初审：CR-001 / ARC-1。初始 `src/ui.py` 引入 read_status，校验后直接 UPDATE 与 commit，绕过既有 `order_service.set_status`；初审 FAIL。现有服务已经负责读取校验、UPDATE 和 commit，无须修改服务实现。
- 整改工单：仅调整付款适配实现经现有 set_status 写 paid，UI 不直接执行状态 SQL 或 commit；保持模块、公开函数签名、返回与异常语义。代码及直接付款测试交 `payment_coder`，[同一 Plan／Task](payment-plan.md)。共享文件归属：coder 仅写 ui.py、付款测试及 Plan；本技能 Agent 写本 Review 和最小索引；架构角色只读。所有执行者保留他人改动。
- 验收计划：coder 实施局部自验；实现就绪后原 architect 沿真实源码调用链复核；技能 Agent 从公开调用入口验收行为。架构检查不以 mock 断言单独代替源码审查。
- 架构复核方案：检查 ui 只调用现有 set_status(connection, order_id, paid)，服务负责校验、SQL 和 commit；无测试或运行器依赖、无新增模块或装配；确认服务、取消和提交源码未变。通过判据为 CR-001/ARC-1 满足。
- 行为保持方案：新临时文件 SQLite 创建现存订单，从公开 mark_paid 调用验证返回 None；关闭并重开读取 paid，调用者仍拥有连接；missing 抛 ValueError；真实只读 SQLite 写失败以及 commit 失败传播。回归既有正常提交局部单测；不把局部证据当全产品集成。
- 当前状态：Closed after recheck / PASS。原 architect 源码复核及技能 Agent 公开入口行为保持验收均通过；实施方案与局部证据见同一 Plan T001。

| 批次 / 执行者 | 范围与方法 | 版本及实际证据 | 结论 |
| --- | --- | --- | --- |
| 初审 / payment_architect | ui → service 源码链及工程边界 | 初始 HEAD，UI 直接 UPDATE/commit | FAIL |
| 整改后 / payment_coder | Plan T001 实施与局部测试 | ui 通过现有 set_status；6 tests / OK，服务未变 | 局部自验 PASS |
| 复核 / payment_architect | 实读源码、diff、依赖与工程骨架 | ui 无 SQL/commit，set_status 校验、UPDATE、commit；无新增模块，diff check 退出 0 | CHK-001 架构复核 PASS |
| 保持验收 / payment_refactor | 临时文件库经公开 mark_paid 调用，独立断言正常/异常/恢复 | 四种原状态均 paid、返回 None、关闭重开 paid；missing ValueError；真实只读写失败 OperationalError；commit 故障原样传播，另连接 pending，调用者 rollback 后 pending | 付款行为保持 PASS |

### CHK-002: 持久化完成与失败传播

初审源码事实：ui 和现有服务实际写入文件 SQLite 并 commit；无异常转成功。整改后原 architect 确认服务仍执行真实 SQL/commit 且不捕获异常；技能 Agent 已按 CHK-001 公开付款正常、missing、真实写失败与 commit 失败方案验收，均通过。依据 ARC-2/契约；项目规则映射仍缺，状态 UNVERIFIED，不另派扩围修改。

### CHK-003: 公开接口及副作用

初审源码事实：同步 mark_paid 签名和返回 None，调用者管理连接，无网络、日志或重试；整改不得新增状态限制。整改后公开签名、None 返回、连接归属、各原状态付款结果均通过保持验收；源码无新增副作用。依据契约/ARC-4；项目规则映射仍缺，状态 UNVERIFIED。

### CHK-004: 正式实现与测试隔离

初审源码事实：src 仅依赖正式模块与标准库；checks/tests 调用 src，测试独立临时文件数据库并清理连接。整改后原 architect 实读确认 Mock 仅位于 tests、正式依赖链无测试资产；临时文件库与连接清理沿用，断言覆盖可观察结果及异常。依据 ARC-3；项目规则映射仍缺，状态 UNVERIFIED。

### CHK-005: 环境与运行装配

初审源码/配置事实：文件 SQLite、同步库调用，runtime 无外部端点且未授权外部访问。整改后原 architect 确认 storage、runtime、checks 及服务 diff 为空，无运行配置、依赖或存储装配改动。依据 ARC-2/ARC-4；项目规则映射仍缺，状态 UNVERIFIED。

## 3. Gate 与接续

Review Gate：UNVERIFIED，原因是 CHK-002～005 的项目规则映射待查；CR-001 所覆盖付款路径的 CHK-001 已完成整改、独立架构复核及公开行为保持验收，闭环 PASS。此限制不改变 Spec/契约的公开行为判据，可继续已授权本地集成，不作为发布依据，不宣称全蓝图 PASS。

交付版本为初始 HEAD 加未提交工作区改动。SHA-256：`src/ui.py` = `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`；`tests/test_order.py` = `0805f5dd55bd83f6464ce9c4d0a09189fb7209f6173004e370779c969bb71b7c`。服务哈希仍为 `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`。仅新增本 Review、同一 Plan，索引维护两项导航；未改产品服务、checks、runtime、规则或共享工作流。

2026-11-14 技能 Agent 独立行为验收使用上述候选、Python 3.12.3 / SQLite 3.45.1、一个全新临时目录中的文件 SQLite：分别创建 pending/submitted/cancelled/paid 的付款订单，经公开 mark_paid 断言 None/paid，关闭原连接再重开断言 paid；MISSING 调用捕获 `ValueError: order not found`；启用 query_only 后捕获 `OperationalError: attempt to write a readonly database` 并确认原状态 pending；包装真实连接仅令 commit 抛 OperationalError，确认同一异常传播、另一连接 pending、调用者 rollback 后 pending。命令为 `python -B -` 内联断言脚本，全部断言通过、退出 0，无网络。该证据与 Plan 的可复跑同判据测试互相对应。复跑入口 `python -B -m unittest discover -s tests -v` 在本候选实际为 6 tests / OK、退出 0；`git diff --check` 退出 0，服务/storage diff 为空。`python -B checks/runtime_details.py` 实测环境与以上源哈希一致。

集成准备：本地标准库环境已就绪，目标候选由上述哈希确定；可使用既有 [验收指南](../../../specs/order/quickstart.md) 接续全产品 AC-1/2/3 并独立出具 Test Gate，记录本 Review 限制。规则维护由 Main 向用户告知并由用户决定时机，不阻止本地集成取证。

范围外发现：AC-2 基线实测不符合既定判据，交 Main 后续集成登记；AC-3 端点与授权缺失，需有权人员提供才能真实核验，本轮不访问网络。

文档写后检查：已读回 Review、Plan、索引与实际 diff，确认初审/整改/复核事实、行为判据及待查映射分别保留。最终机械检查命令为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/payment-review.md docs/test-reports/order/payment-plan.md docs/index.md`；结果为 Checked 3 Markdown files: 0 errors, 0 warnings，退出 0（仅机械检查）。语义结论限本轮授权付款整改，无规则维护或产品范围扩张。
