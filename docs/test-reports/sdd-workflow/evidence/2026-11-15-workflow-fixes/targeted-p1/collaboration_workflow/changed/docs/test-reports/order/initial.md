# Test Report — 订单首次快照

## 1. 测试目标与依据

批次 initial，完整功能点集成回归，执行者独立技能 Agent `/root/order_test`；时间见原始证据 UTC 时间戳。依据 [Spec](../../../specs/order/spec.md)、[接口契约](../../contracts/order.md) 与本轮 [Quickstart](../../../specs/order/quickstart.md)。目标是在修复前实际快照记录全部适用功能状态，保留原始失败。

## 2. 范围与计划

Main 启动指令已确认：新建、取消、提交、公开付款、AC-3；当前实际版本后修复后实际版本；本地 Python + 文件 SQLite；公开 CLI/库入口。按先 AC-1/2/3，再补充契约覆盖及既有单测执行。常规边界与真实数据库错误从契约推导。全部适用项满足且证据齐备才可 PASS。架构内部职责遵循由 Main 另派 Review；不作为本报告业务失败依据。

## 3. 实际环境与版本

- HEAD `fc366da8aff900abc000129676514d994ca5c671`；开始时工作区干净，首轮期间产品 `src` 无改动。测试资产和文档为本轮新增/修改。
- Python 3.12.3 / SQLite 3.45.1，标准库，隔离本地环境，无依赖安装；真实服务模块与真实临时文件数据库，无模拟组件。
- [版本记录](evidence/initial-version.json)、[运行事实与产品源指纹](evidence/initial-runtime.json)。源码哈希是实际快照标识，未把仅 HEAD 相同解释为源码相同。
- `external_endpoint=null`、`external_call_authorized=false`、`network_access_in_this_run=false`；没有外部请求。

## 4. 数据与准备

每场景临时 SQLite 文件，常规订单 ORDER-1；补充运行器使用独立订单标识，数据见原始输出。空字符串/None/数字是非空字符串约束的反例；重复编号、缺失对象、query_only 写错误、读锁导致 commit 失败均是既有契约异常的常规覆盖。失败与成功均关闭连接并删除目录；锁场景由调用方显式 rollback 后清理。无人工数据或视觉验收。准备缺口仅 AC-3 的真实外部环境。

## 5. 覆盖统计

共 23 个范围内场景：20 PASS、2 FAIL、0 Not run、1 BLOCKED，四类合计 23；22 个本地可执行项全部执行。补充 20 项中 19 PASS / 1 FAIL；既有 2 项单测通过，独立补充，不重复计数。AC-1/2 本地行为、新建、取消、公开付款、缺失订单、写错误与 commit 错误均已获得实际证据；AC-3 外部行为只完成阻塞记录，没有真实回执证据。本轮无性能指标，无中途产品源码变化。

[补充运行器](../../../tests/order_regression.py) 的资产 SHA-256 随 [原始执行记录](evidence/initial-regression.json) 留存；[首轮后运行事实](evidence/initial-runtime-after.json) 与初始全部产品源码哈希一致。

## 6. 逐项结果

| Case / 依据 | 前置与操作 | 预期 | 实际结果 | Verdict | 证据 / 版本 | Issue |
|---|---|---|---|---|---|---|
| AC-1 | 新建后提交、关闭重开 | true/submitted | true/submitted | PASS | [CLI](evidence/initial-acceptance.json)，本报告快照 | 无 |
| AC-2 | 新建、取消、提交、关闭重开 | false/cancelled | true/submitted | FAIL | [CLI](evidence/initial-acceptance.json)，本报告快照 | [ORDER-001](../../issues/ORDER-001.md) |
| AC-3 | 只读 runtime 配置，不发请求 | 缺外部条件时保留阻塞 | 端点空、无权限 | BLOCKED | [CLI](evidence/initial-acceptance.json)，本报告快照 | 无，环境阻塞 |

| O-01 / 契约 create_order | `create pending survives reopen`；`python -B tests/order_regression.py --case O-01` | `{"persisted_status":"pending"}` | `{"persisted_status":"pending"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-02 / 契约 create_order | `create rejects id ''`；`python -B tests/order_regression.py --case O-02` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-03 / 契约 create_order | `create rejects id None`；`python -B tests/order_regression.py --case O-03` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-04 / 契约 create_order | `create rejects id 7`；`python -B tests/order_regression.py --case O-04` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | `{"exception":"ValueError","rows":[],"persisted_rows":[]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-05 / 契约 create_order | `duplicate create preserves cancelled order`；`python -B tests/order_regression.py --case O-05` | `{"exception":"IntegrityError","status":"cancelled","persisted_status":"cancelled"}` | `{"exception":"IntegrityError","status":"cancelled","persisted_status":"cancelled"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-06 / 契约 cancel_order | `cancel persists and repeated cancel persists`；`python -B tests/order_regression.py --case O-06` | `{"first_persisted_status":"cancelled","repeat_persisted_status":"cancelled"}` | `{"first_persisted_status":"cancelled","repeat_persisted_status":"cancelled"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-07 / Spec 付款 / 契约 mark_paid | `mark_paid from pending`；`python -B tests/order_regression.py --case O-07` | `{"initial_status":"pending","persisted_status":"paid"}` | `{"initial_status":"pending","persisted_status":"paid"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-08 / Spec 付款 / 契约 mark_paid | `mark_paid from submitted`；`python -B tests/order_regression.py --case O-08` | `{"initial_status":"submitted","persisted_status":"paid"}` | `{"initial_status":"submitted","persisted_status":"paid"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-09 / Spec 付款 / 契约 mark_paid | `mark_paid from cancelled`；`python -B tests/order_regression.py --case O-09` | `{"initial_status":"cancelled","persisted_status":"paid"}` | `{"initial_status":"cancelled","persisted_status":"paid"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-10 / 契约缺失订单 ValueError | `read rejects missing order without side effects`；`python -B tests/order_regression.py --case O-10` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-11 / 契约缺失订单 ValueError | `cancel rejects missing order without side effects`；`python -B tests/order_regression.py --case O-11` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-12 / 契约缺失订单 ValueError | `submit rejects missing order without side effects`；`python -B tests/order_regression.py --case O-12` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-13 / 契约缺失订单 ValueError | `set_status rejects missing order without side effects`；`python -B tests/order_regression.py --case O-13` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-14 / 契约缺失订单 ValueError | `mark_paid rejects missing order without side effects`；`python -B tests/order_regression.py --case O-14` | `{"exception":"ValueError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"exception":null,"rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | FAIL | [补充JSON](evidence/initial-regression.json)，本报告快照 | [ORDER-002](../../issues/ORDER-002.md) |
| O-15 / 契约数据库异常传播 | `create propagates SQLite query_only failure`；`python -B tests/order_regression.py --case O-15` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-16 / 契约数据库异常传播 | `cancel propagates SQLite query_only failure`；`python -B tests/order_regression.py --case O-16` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-17 / 契约数据库异常传播 | `submit propagates SQLite query_only failure`；`python -B tests/order_regression.py --case O-17` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-18 / 契约数据库异常传播 | `set_status propagates SQLite query_only failure`；`python -B tests/order_regression.py --case O-18` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-19 / 契约数据库异常传播 | `mark_paid propagates SQLite query_only failure`；`python -B tests/order_regression.py --case O-19` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | `{"query_only":1,"exception":"OperationalError","rows":[["ORDER-1","pending"]],"persisted_rows":[["ORDER-1","pending"]]}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |
| O-20 / 契约数据库异常传播 | `submit commit blocked by read lock propagates error; caller rolls back`；`python -B tests/order_regression.py --case O-20` | `{"locked_status":"pending","exception":"OperationalError","status_after_caller_rollback":"pending","persisted_status":"pending"}` | `{"locked_status":"pending","exception":"OperationalError","status_after_caller_rollback":"pending","persisted_status":"pending"}` | PASS | [补充JSON](evidence/initial-regression.json)，本报告快照 | 无 |

O-20 的真实失败消息为 `database is locked`；调用方 rollback 前同连接可见 submitted 且活动事务为 true，仅作观测，不是新增自动 rollback 要求。调用方显式 rollback 后及重开后均 pending。所有场景临时连接和目录已完成上下文清理；运行器未产生清理异常。

[既有单测原始输出](evidence/initial-unittest.json)：2 项通过，只证明其实际范围，不替代集成覆盖。

## 7. 问题与影响

| Issue | 相关场景 | 本批影响 |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2 | 取消状态被提交覆盖，集成失败 |
| [ORDER-002](../../issues/ORDER-002.md) | O-14 | 公开付款缺失对象未抛 ValueError，集成失败 |

实现修复由 Main 独立调度，本测试 Agent 不修改产品。AC-3 的阻塞本身不是实现缺陷，不另造产品 Issue。

## 8. 结论、人工反馈与 Test Gate

**Test Gate：FAIL**，适用于本报告 HEAD + 产品源指纹及本地 Python/文件 SQLite 范围，AC-2、O-14 实际失败；全部本地可执行场景已完成，首轮可结束。AC-3 同时 BLOCKED，不能宣告完整通过。无 UI，人工体验反馈不适用；外部端点与授权需要有权人员提供。

接续条件：Main 提供实际修复版本、改动边界和自验；原测试 Agent 在修复后新批次完整复跑，保留首轮事实。AC-3 还需真实测试端点、调用权限、网络允许、真实协议与回执判据及可调用入口。现有 AC-3 CLI 不发外部调用，不能充当恢复后的真实服务验收器；当前不访问外部、不部署、不修改凭据。

文档写后机械检查使用项目 `doc_check.py`，范围为本指南、报告、两个 Issue 与项目索引；结果见 [检查记录](evidence/initial-doc-check.json)。语义核对已确认：场景总数一致、结果保留首轮快照、失败与外部阻塞分开、未引入新业务判据。
