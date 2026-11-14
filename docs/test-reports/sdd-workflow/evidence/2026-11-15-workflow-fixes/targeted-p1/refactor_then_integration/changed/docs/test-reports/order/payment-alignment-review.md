# Architecture Review Record — 订单付款发布前对齐

## 1. Scope and Context

- 目标：在隔离本地候选中对齐公开 `src.ui.mark_paid` 的状态写入职责，保持已有公开行为。仅付款适配实现与直接相关局部测试可改；取消提交不在整改范围。
- 依据：[Blueprint ARC-1～4](../../blueprint.md#架构边界)、[订单契约](../../contracts/order.md)、[Spec](../../../specs/order/spec.md)、[CR-001](../../code-review-rules.md)。已确认目标、范围及方案授权由 Main 交接；无需重复确认。
- 规则有效性：独立 architect 确认 CR-001 有效覆盖付款职责，无本轮实质映射缺失；未提出规则维护决定。
- 初始版本：`663483bf7d8f869aad8d57a5de920e790e5c8dbc`，初始工作树干净。环境：2026-11-15，Python 3.12.3 / SQLite 3.45.1；每例新建临时文件 SQLite，关闭连接并清理，无网络。
- 修改前源快照：ui SHA-256 `1a6052d6ba2fa2fd34999433ac5068231ab79a173aaeb41a17358872fcd691ae`；order_service `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`；storage `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9`。运行 `python -B checks/runtime_details.py` 实测环境与哈希，非未运行场景的结果。
- 实际审查者：独立 `/root/refactor/architecture`（sdd-architect）；实施执行者 `/root/refactor/implementation`（sdd-coder）；行为保持验收由 `/root/refactor` 执行。审查者不参与实现。
- 基线：修改前从公开 `ui.mark_paid` 调用，返回 None；关闭重开数据库后 paid。缺失订单抛 ValueError('order not found')；`PRAGMA query_only=ON` 时抛 OperationalError('attempt to write a readonly database')，状态未变；已关闭连接抛 ProgrammingError('Cannot operate on a closed database.')。原 `python -B -m unittest discover -s tests -v` 两例通过。
- 已确认判据：现存订单调用后持久化 paid；缺失订单 ValueError；数据库异常向上传播；保持公开签名和原返回 None。取消后提交按 AC-2 判断，现状冲突不可作为付款保持预期。

## 2. Review Checks and Follow-up

| Rule ID | Applicability | Rationale and source | Check |
| --- | --- | --- | --- |
| CR-001 | Applicable | 付款路径变更，ARC-1 指定服务为写入唯一业务入口 | CHK-001 |

共享架构规范筛选：模块边界与依赖适用并映射 CR-001；状态权威/持久化、同步接口语义、环境装配与测试隔离为 CHK-001 支持路径（ARC-2/3/4）。工程骨架仅核对既有 ui/service/storage 职责和实际同步装配，无新模块、生成器或包结构变更。业务与运行保障分工不适用（本轮无后台、重试、恢复或流控）；观测数据与日志契约、观测影响及故障隔离不适用（蓝图无产品观测链，checks JSON 仅测试输出）。不适用项不计通过，不推定对应机制已实现。

### CHK-001: 付款写入职责与实际服务调用链

- 依据与对象：CR-001、ARC-1；`src/ui.py` → `src/order_service.py:set_status` → SQLite；ARC-2/3/4 为受影响路径支持约束。
- 初审事实：独立 architect 在初始版本确认 FAIL。`ui.py` 仅调用 read_status 后直接 UPDATE 与 commit，绕过既有 set_status 入口。职责偏差不改变已有 paid 结果。
- 整改工单：CHK-001；由 `/root/refactor/implementation`（sdd-coder）在 `src/ui.py` 中将状态写入交给既有服务 set_status(connection, order_id, 'paid')。UI 不执行状态 SQL 或 commit，不新增业务规则。只可改付款适配及 `tests/test_order.py` 中直接相关付款测试。
- 验收计划：实施执行者先完成同一 Plan 和局部自验；在实际整改版本由原独立 architect 复核；技能 Agent 在整改版从公开入口执行行为保持验收。两项均通过才关闭。
- 架构复核方案：读回 diff、UI 和 set_status；追踪写入实际装配。通过条件为 UI 调用现有服务入口且无 SQL/commit，服务唯一负责状态写入；正式路径不依赖 checks/tests，不新增网络或配置装配，SQLite 持久化仍由服务 commit；实际执行证据证明原连接、订单和 paid 传入服务而非仅同名封装，原正常提交局部测试仍通过。
- 行为保持方案：每项使用独立临时文件 SQLite，从公开 ui.mark_paid 调用。验证返回 None、pending/submitted/cancelled/paid 初态最终 paid、关闭重开仍 paid；缺失订单 ValueError 且未插入，写入失败 OperationalError 且不返回成功、数据未变；关闭连接错误原样传播。若局部测试已有同版本同条件证据可引用，技能补验实际公开入口。
- 实施工单：[Plan / T001](../../../specs/order/payment-refactor-plan.md#t001-付款适配委派与局部保持检查)。
- 局部自验：实施者先补测试在原 UI 上运行，四初态均因服务调用次数 0 而失败；整改后 `python -B -m unittest discover -s tests -v` 退出 0，5 个测试方法（7 付款场景及原正常提交）通过；`git diff --check` 退出 0。方案、任务与完整局部证据见同一 Plan。
- 行为保持实际结果：技能 Agent 在下述交付哈希上独立运行公开入口脚本，4 个初态逐一用真实 set_status 的 wraps 核对原连接、订单、paid 参数，None 返回与关闭重开 paid 均通过；missing 未插入并抛原 ValueError，pending 只读失败仍 pending 并抛 OperationalError，closed 抛原 ProgrammingError；共 7 场景 PASS。与基线一致，取消后付款是既有合法状态覆盖，未改变 AC-2 的取消后提交判据。可复跑入口为 `python -B -m unittest discover -s tests -v`，四初态、委派及错误断言保存在直接付款测试中。
- 当前状态：Closed after recheck，PASS。原独立 architect 已回读原检查项、Plan、diff 和实际装配：ui → set_status → read_status → 服务 UPDATE/commit，无 UI 旁路，正式实现未新增测试依赖、网络或观测机制；独立单测退出 0（5 tests / OK）。行为保持验收同一哈希 PASS。

| Batch / Reviewer | Action | Snapshot, actual results, evidence | Conclusion |
| --- | --- | --- | --- |
| 初审 / architecture | 语义追踪 CR-001 实际调用链 | 初始 HEAD，ui 直接 UPDATE/commit | FAIL，已派发整改 |
| 整改 / implementation | T001、局部单测、真实服务参数与文件持久化 | 下述 ui/test 哈希，5 测试方法通过；先前预期失败保留于 Plan | 局部 PASS，等待独立复核 |
| 保持验收 / refactor | 公开入口独立脚本，原异常和四初态重开验证 | 下述 ui 哈希，7 场景全部 PASS；临时目录退出后清理 | 行为保持 PASS |
| 独立复核 / architecture | 读回真实调用链、diff、依赖，并运行 `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v` | 下述 ui/test 哈希匹配；service/storage 未改；5 tests in 0.115s / OK | CHK-001 PASS，无剩余偏差 |

## 3. Gate and Remaining Work

- Review Gate：PASS，仅针对下述版本的付款适用架构检查 CHK-001（1/1）；原初审 FAIL 已经技术整改、独立架构复核和公开入口行为保持验收关闭。不适用项不计通过；本结论不表示全产品集成通过。
- 本轮剩余整改：无。
- 跨阶段事项：初审读到 submit_order 无 cancelled 分支，与 AC-2 冲突；不在本次付款整改内，交 Main 后续集成按原判据取证。AC-3 无端点/授权，不能以本地 paid 代替真实外部证据。
- 集成版本：HEAD `663483bf7d8f869aad8d57a5de920e790e5c8dbc` 加本轮未提交工作树；代码与测试变更仅 `src/ui.py`、`tests/test_order.py`。文档仅本 Review 与唯一 Plan，不改索引。

| 文件 | 交付 SHA-256 |
| --- | --- |
| src/ui.py | `1b43c863d5f9dd8100d3c5a9f0dade6cde3e020502d780bf933cb489a122c63c` |
| src/order_service.py | `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` |
| src/storage.py | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| src/__init__.py | `10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded` |
| tests/test_order.py | `dae0643b33eb9c9de92603036b73893ba267f124e91c902889caf07bbb7e8a7e` |

- 集成准备：Python 3.11+、标准库 SQLite、每场景临时文件；公开入口 `ui.mark_paid`，原 `checks/acceptance.py` 提供 AC-1/2/3 入口。阶段2由 Main 单独启动，对上述实际候选完整新建/取消/提交/公开付款取证；AC-3 仅在端点和权限齐备后能验证。源码变化需重新判断证据适用性。不得据本记录认定全产品 Test Gate。

文档写后检查：本 Review 与唯一 Plan 的 Markdown 机械检查为 0 errors / 0 warnings；读回来源、原编号、规则筛选、版本/哈希与初审到复核证据，语义一致。链接核对仅本地存在性及锚点，不验证外部服务。
