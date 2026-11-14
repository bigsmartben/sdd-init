# Plan — 取消订单提交修复

BUG-001 最小修复及局部自验完成：取消后提交返回 false，无写入，重开文件数据库仍为 cancelled。6 项单测与 AC-1／AC-2 均通过；独立定向复验由调度方接续。

## 1. 目标与依据

- 目标：恢复 [AC-2](../../specs/order/spec.md)，取消后提交返回 false、不写入，重开文件数据库仍为 cancelled。
- 范围：仅修改 `src/order_service.py`、必要的 `tests/test_order.py` 及本 Plan 和原始证据。保留接口、pending 提交、paid 持久化、异常传播；其他提交状态维持现状。
- 已确认边界：隔离项目、本地 Python 和文件 SQLite；不进行 Git、外部调用、部署或架构整改，不修改 ui。
- 契约：[订单函数契约](../contracts/order.md)。直接适用蓝图：[ARC-2／ARC-3／ARC-4](../blueprint.md#架构边界)；ARC-1 的 ui 偏差由调度方另行取证，不在本任务修复。
- 基线事实：`submit_order` 丢弃读取状态，无条件经 `set_status` 写入 submitted 并 commit。基线 SQL 轨迹证实取消已落盘后仍被覆盖。候选实现对 cancelled 提前返回 false。

## 2. Task 清单

### T001: 恢复取消后提交的既定行为

- 依据：[BUG-001 与验收方案](../issues/BUG-001.md#修复工单与验收计划)、Spec AC-2、订单函数契约；[归因 SQL 轨迹](../test-reports/order-cancel/baseline-causal-trace.json)。
- 改动范围：`src/order_service.py`、`tests/test_order.py`；本 Plan 和 `docs/test-reports/order-cancel/` 为新增证据资产。
- 实施方案：读取现存状态为 cancelled 时直接返回 false；其余状态沿用既有路径。先添加定向测试证明缺口，再作最小实现并复验。
- 依赖：无 Task 依赖；实施前置已满足：调度方提供就绪 Issue 与实施接续指令。
- 完成判据和局部验证：取消提交 false、无新增数据库变更、重开仍 cancelled；AC-1 pending 提交及 paid 持久化保持；不存在订单 ValueError、读写数据库异常继续传播。运行 unittest 和 AC-1／AC-2，原始命令、输出、exit 与哈希落盘。AC-3 不在本地替代验证范围。
- 状态：Complete（最小修复、局部自验及证据已完成）。
- 结果与证据：[基线环境及哈希](../test-reports/order-cancel/baseline-environment.json)、[AC-2 FAIL，exit 1](../test-reports/order-cancel/baseline-ac2.json)、[原有单测 2 项 PASS，exit 0](../test-reports/order-cancel/baseline-tests.json)。

- 失败与复验：[新增测试先在原实现运行](../test-reports/order-cancel/regression-before-fix.json)，6 项中仅取消测试因返回 true 失败，exit 1；最小实现后 [6 项单测通过](../test-reports/order-cancel/candidate-tests.json)，exit 0。真实 SQLite commit 失败使用另一连接的显式读事务阻塞提交，观察写连接未提交的 submitted、读连接 pending，抛出原始 OperationalError；调用者显式 rollback 后重开仍 pending。不存在订单与关闭连接读取异常也通过。
- 修复版本：[候选环境及全量适用文件哈希](../test-reports/order-cancel/candidate-environment.json)。`src/order_service.py` SHA256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；`tests/test_order.py` SHA256 为 `05bb0ea75b613ea4d2ad0a0f7251e4b3f0b8f19d5db0b9693d4de5d75bb8c5d3`。与基线对比，storage、ui、checks、Spec、契约、Blueprint、runtime 均未改动。
- 判据覆盖：[AC-1 PASS](../test-reports/order-cancel/candidate-ac1.json)、[AC-2 PASS](../test-reports/order-cancel/candidate-ac2.json)，各 exit 0，均关闭并重开文件数据库；[取消 SQL 轨迹](../test-reports/order-cancel/candidate-causal-trace.json) 只有 SELECT。单测另外断言无新增数据库变更和事务，paid 持久化保持。

## 3. 交付核对

- 目标覆盖：T001 完成，产品只增加 cancelled 提前返回；增加 4 项必要回归，原有 2 项保持通过。非 pending、非 cancelled 的 submit 路径保持原状。
- 阻塞与接续条件：无实施阻塞；调度方以同一源哈希执行 BUG-001 独立定向复验。若复验失败，沿原 Issue 和本 Plan 继续；异常试验的事务由测试显式 rollback 并关闭，临时目录自动清理。
- 待验：独立定向复验交调度方，执行入口与判据见 BUG-001 验收方案；本任务终点为本地候选及局部自验。真实外部 AC-3 需另行配置和授权，未执行；ui 架构偏差未整改。

- 写后核对：文档 CLI 显式检查本 Plan 与直接引用的 BUG-001，exit 0，0 errors、0 warnings，见 [机械检查原始输出](../test-reports/order-cancel/coder-doc-check.json)。语义人工核对确认保留 AC-2 判据、异常语义、修改边界和后续独立复验，未将局部结果当作 AC-3 或架构复核通过。
