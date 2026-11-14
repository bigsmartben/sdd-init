# Test Report — 订单修复后独立集成复验

## 1. 测试目标与依据

批次 retest，执行者原独立测试技能 Agent `/root/order_test`；实际 UTC 时间见各原始记录。Main 已授权在修复后冻结源码快照完整重跑原 23 场景及 2 项单测。依据 [Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[Quickstart](../../../specs/order/quickstart.md)、[首轮报告](initial.md) 与原 [ORDER-001](../../issues/ORDER-001.md) / [ORDER-002](../../issues/ORDER-002.md)。本报告独立验证全部产品功能，不以实施者局部自验或 Bugfix 定向结论代替。

## 2. 范围与计划

沿用已确认的新建、取消、提交、公开付款和 AC-3 范围、公开 CLI/库入口、本地 Python + 文件 SQLite 环境，目标为 Main 交接的修复后实际快照。场景及判据未改变：AC-1/2/3 与 O-01～20 原编号全量重跑；既有 2 单测独立补充。受影响的取消保护、付款存在性检查及正常、异常、边界、组合、持久化均包括在内。纯架构约束遵循交 Main 另派 Review。

完成判据仍为全部适用范围满足且必需证据齐备才可 PASS；外部 AC-3 不得由本地结果替代。原始失败完整保留在首轮报告和原始证据，本批不覆盖首轮事实。

## 3. 实际环境与版本

HEAD `fc366da8aff900abc000129676514d994ca5c671` 加未提交产品修复，Python 3.12.3 / SQLite 3.45.1。隔离本地，使用真实 `src`、真实每场景临时文件数据库，无模拟或网络调用。完整指纹、Git 差异与未提交状态见 [复验版本](evidence/retest-version.json)，[实际运行事实](evidence/retest-runtime.json)。

| 产品文件 | 本批 SHA-256 |
|---|---|
| src/__init__.py | `10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded` |
| src/order_service.py | `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb` |
| src/storage.py | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| src/ui.py | `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909` |

与 [Bugfix 实际版本](evidence/bugfix-local-version.json) 逐项吻合。执行前后产品及测试入口全部哈希一致，见 [执行后指纹](evidence/retest-version-after.json)。变更仅 cancelled 提交短路 false、ui 付款经已有服务 set_status，其他产品文件及测试断言保持；本批全量重跑，不复用旧版本场景结果作为新快照通过证据。

## 4. 数据与准备

数据和隔离沿用 Quickstart 与原测试资产：每场景独立临时目录及 SQLite 文件，正常订单 ORDER-1、缺失 MISSING、非法编号空字符串/None/7。真实 query_only 拒绝写入，真实读锁与 busy_timeout=0 导致 commit 失败；由测试调用方显式 rollback 后核对重开 pending，不新增产品自动 rollback 要求。成功与失败均 finally 关闭连接、临时目录退出清理；本次未出现清理异常。

环境配置仍 `external_endpoint=null`、`external_call_authorized=false`、`network_access_in_this_run=false`，AC-3 实际调用准备不满足。无人工视觉或体验验收、无性能阈值项。

## 5. 覆盖与统计

23 个原范围场景：**22 PASS、0 FAIL、0 Not run、1 BLOCKED**，合计 23；22 个可执行本地场景全部重跑并通过。另 2 项既有单测通过，不重复计入场景总数。功能覆盖包括新建、取消、提交、付款、缺失对象、数据库写和 commit 错误；AC-3 只验证了阻塞事实，未取得外部真实回执，因此功能点覆盖状态不能解释为全范围通过。

公开 CLI 退出 3（有阻塞但无失败），补充运行器退出 0，单测退出 0。与首轮相比 AC-2 从 FAIL 恢复为 PASS，O-14 从 FAIL 恢复为 PASS，其他本地项仍 PASS，AC-3 保持 BLOCKED。没有测试资产修订或中途源码变化。

## 6. 逐项执行与证据

| Case / 依据 | 实际操作与数据 | 预期 | 实际结果 | Verdict | 证据 / 实际版本 | Issue |
|---|---|---|---|---|---|---|
| AC-1 | 新建 pending → submit → 关闭重开；原 CLI 全量运行 | true/submitted | true/submitted | PASS | [CLI](evidence/retest-acceptance.json)，本批指纹 | 无 |
| AC-2 | 新建 → cancel → submit → 关闭重开；原 CLI 全量运行 | false/cancelled | false/cancelled | PASS | [CLI](evidence/retest-acceptance.json)，本批指纹 | [ORDER-001](../../issues/ORDER-001.md) |
| AC-3 | 读取当前 runtime，不发请求 | 缺端点及授权时 BLOCKED | 端点未配置、未授权；无真实回执 | BLOCKED | [CLI](evidence/retest-acceptance.json)，本批指纹 | 无，外部环境缺口 |
| O-01 / 契约 create_order | `create pending survives reopen`；原运行器全量执行 | `{"persisted_status":"pending"}` | `{"persisted_status":"pending"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-02 / 契约 create_order | `create rejects id ''`；原运行器全量执行 | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-03 / 契约 create_order | `create rejects id None`；原运行器全量执行 | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-04 / 契约 create_order | `create rejects id 7`；原运行器全量执行 | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-05 / 契约 create_order | `duplicate create preserves cancelled order`；原运行器全量执行 | `{"exception":"IntegrityError","status":"cancelled","persisted_status":"cancelled"}` | `{"exception":"IntegrityError","status":"cancelled","persisted_status":"cancelled"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-06 / 契约 cancel_order | `cancel persists and repeated cancel persists`；原运行器全量执行 | `{"first_persisted_status":"cancelled","repeat_persisted_status":"cancelled"}` | `{"first_persisted_status":"cancelled","repeat_persisted_status":"cancelled"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-07 / Spec 付款 / 契约 mark_paid | `mark_paid from pending`；原运行器全量执行 | `{"initial_status":"pending","persisted_status":"paid"}` | `{"initial_status":"pending","persisted_status":"paid"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-08 / Spec 付款 / 契约 mark_paid | `mark_paid from submitted`；原运行器全量执行 | `{"initial_status":"submitted","persisted_status":"paid"}` | `{"initial_status":"submitted","persisted_status":"paid"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-09 / Spec 付款 / 契约 mark_paid | `mark_paid from cancelled`；原运行器全量执行 | `{"initial_status":"cancelled","persisted_status":"paid"}` | `{"initial_status":"cancelled","persisted_status":"paid"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-10 / 契约缺失订单 ValueError | `read rejects missing order without side effects`；原运行器全量执行 | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-11 / 契约缺失订单 ValueError | `cancel rejects missing order without side effects`；原运行器全量执行 | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-12 / 契约缺失订单 ValueError | `submit rejects missing order without side effects`；原运行器全量执行 | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-13 / 契约缺失订单 ValueError | `set_status rejects missing order without side effects`；原运行器全量执行 | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-14 / 契约缺失订单 ValueError | `mark_paid rejects missing order without side effects`；原运行器全量执行 | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | [ORDER-002](../../issues/ORDER-002.md) |
| O-15 / 契约数据库异常传播 | `create propagates SQLite query_only failure`；原运行器全量执行 | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-16 / 契约数据库异常传播 | `cancel propagates SQLite query_only failure`；原运行器全量执行 | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-17 / 契约数据库异常传播 | `submit propagates SQLite query_only failure`；原运行器全量执行 | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-18 / 契约数据库异常传播 | `set_status propagates SQLite query_only failure`；原运行器全量执行 | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-19 / 契约数据库异常传播 | `mark_paid propagates SQLite query_only failure`；原运行器全量执行 | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |
| O-20 / 契约数据库异常传播 | `submit commit blocked by read lock propagates error; caller rolls back`；原运行器全量执行 | `{"locked_status":"pending","exception":"OperationalError","status_after_caller_rollback":"pending","persisted_status":"pending"}` | `{"locked_status":"pending","exception":"OperationalError","status_after_caller_rollback":"pending","persisted_status":"pending"}` | PASS | [补充JSON](evidence/retest-regression.json)，本批指纹 | 无 |

各 O-编号可由 `python -B tests/order_regression.py --case O-编号` 定向复跑。O-20 的实际异常 `OperationalError: database is locked`；rollback 前连接内可见 submitted、活动事务 true 为辅助观察，调用方 rollback 后和关闭重开后均 pending，异常未转为提交成功。

[原有单测](evidence/retest-unittest.json) 2/2 PASS：正常提交、付款持久化；与公开集成结果分开记录。各 JSON 保留实际命令、UTC 时间、stdout/stderr 和退出码。

## 7. 相关 Issue 与影响

| Issue | 原场景与必要回归 | 本批事实 |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2 原故障，AC-1 及 O-01～20 全量回归 | 原故障恢复，取消仍 cancelled；本地回归全部通过 |
| [ORDER-002](../../issues/ORDER-002.md) | O-14 原故障，O-07～09 现存订单付款、O-10～20 异常及全量回归 | 缺失付款 ValueError、原数据不变；付款 paid 持久化与异常传播全部通过 |

两原 Issue 已由 Bugfix 定向复验关闭；本批向 Main 补充独立全产品集成证据，不直接改 Issue 状态。没有新产品缺陷。AC-3 阻塞本身不构成实现缺陷。

## 8. 结论、人工反馈与 Test Gate

**全范围 Test Gate：BLOCKED。** 实际快照及本地环境中的全部 22 个可执行场景通过，两原故障恢复、必要及完整本地回归通过；但范围包含的 AC-3 仍没有真实外部回执证据，不能判 PASS。架构 Review 另行判定，不能替代本 Gate。

人工体验反馈不适用。AC-3 恢复需要有权人员提供真实测试服务端点、调用权限、允许网络访问的环境，以及真实协议/回执判据和可执行调用入口；现有 AC-3 CLI 始终不发外部请求，仅修改配置也不能取得真实证据。Main 补齐条件并重新交接后，从原 AC-3 接续，核对版本/环境影响并仅复用仍有效的本地证据。当前不访问外部、不修改凭据、不部署。

文档机械校验覆盖本报告与更新指南，结果见 [检查记录](evidence/retest-doc-check.json)；语义核对确认 23 场景完整、总数准确、实际版本绑定、初始失败保留、本地通过与外部阻塞分别陈述，未引入新判据。
