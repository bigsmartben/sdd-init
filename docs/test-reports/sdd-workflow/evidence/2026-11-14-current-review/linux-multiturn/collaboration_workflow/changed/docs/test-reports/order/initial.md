# Test Report — 订单全功能集成初轮

## 1. Test Goals and Basis

- 批次：initial；类型：全产品集成回归；执行者：独立 sdd-test-loop integration Agent；日期：2026-11-14。
- 目标：检查当前版本的新建、取消、提交、公开付款、持久化、异常和协同行为，识别本地可修复缺陷并记录外部恢复条件。
- 依据：[Spec](../../../specs/order/spec.md)、[函数契约](../../contracts/order.md)、[本轮 Quickstart](../../../specs/order/quickstart.md)；不修改已确认判据。

## 2. Test Scope and Plan

- Main 启动指令已承接用户确认的范围、依次当前及修复后实际快照、本地 Python + 文件 SQLite 环境、主要真实公开调用路径与 Spec/契约判据，四项明确，无新增常规确认事项。
- 覆盖 I01–I16，按指南执行正常、异常、边界、付款协同、多订单隔离和外部回执检查。没有性能阈值或视觉要求；重复提交、paid 后提交没有明确判据，不推定行为。
- 完成标准：全部适用功能和确认判据满足且必要真实证据齐备，才可判整轮 Test Gate PASS。完整失败/阻塞结束本轮取证不等于验收通过。

## 3. Test Environment

- 实际 HEAD：`9701a4d79766e124c202c9b258ad18a458a26cd8`。本轮执行前产品 src 无未提交改动；本轮仅新增测试和文档资产。
- Python 3.12.3，SQLite 3.45.1；环境 `isolated-local-fixture`。精确四个 src 文件 SHA-256 见[集成原始证据](evidence/initial-integration.json)及[运行事实](evidence/initial-runtime.json)。上述哈希界定本轮实际快照，不以 Git HEAD 单独代替。
- 真实组件：公开 Python 函数、标准库 SQLite、临时文件数据库及关闭后重开读取。无模拟组件，无网络调用、真实外部回执、部署或外部平台操作。

## 4. Test Setup and Data

- 授权目录内 `.tmp/order-tests` 作为 TMPDIR，每例独立 SQLite 文件；执行结束临时文件和目录自动删除，空父目录保留。初探一次曾使用默认 tempfile；已清理，正式留证全部在项目 TMPDIR 重新执行。
- 常规数据和异常注入依据详见 Quickstart；全部本地连接可用，PRAGMA query_only 用于真实数据库拒写，而非替代异常。
- 环境缺口仅 AC-3：`external_endpoint=null`、`external_call_authorized=false`、`network_access_in_this_run=false`。

## 5. Execution and Coverage Summary

- 执行范围：15 个本地功能用例全部实际运行，1 个外部回执场景检查前置后阻塞。总 16：PASS 13、FAIL 2、Not run 0、BLOCKED 1。
- 要求覆盖与通过率区分：全部本地功能已覆盖，但 AC-2 与付款缺失订单异常不满足；AC-3 仅前置检查，真实外部行为未覆盖。
- 公开 checks 结果为 AC-1 PASS、AC-2 FAIL、AC-3 BLOCKED；AC-1/AC-2 与 I02/I04 同一场景的补充证据不额外计数。[公开输出](evidence/initial-acceptance.json)。[现有单元测试](evidence/initial-unit.txt) 2 个通过，但未发现上述集成缺陷。
- 所有本轮逐项值见 JSON；修复后需对新快照全量重跑，初轮结果仅证明原快照。

## 6. Test Details

统一实际步骤与数据见 Quickstart 同编号行及 `tests/integration_order.py`，统一版本见第 3 节。证据引用含完整输入顺序、中间状态、预期与实际；表内保留关键结果。

| Case / 依据 | 前置与实际步骤 | 预期 | 实际结果 | Verdict | Evidence / Actual version | Issue |
|---|---|---|---|---|---|---|
| I01 / 创建 | 新文件创建 ORDER-1，关闭重开 | pending | pending | PASS | [JSON](evidence/initial-integration.json)，本轮哈希 | 无 |
| I02 / AC-1 | 新建后提交，关闭重开 | true、submitted | true、submitted | PASS | JSON 与公开 checks，同本轮哈希 | 无 |
| I03 / 取消 | 新建后取消，关闭重开 | cancelled | cancelled | PASS | JSON，同本轮哈希 | 无 |
| I04 / AC-2 | 取消、读状态、再提交、关闭重开 | false、cancelled | 中间 cancelled，返回 true，重开 submitted | FAIL | JSON 与公开 checks，同本轮哈希 | [BUG-001](../../issues/BUG-001.md) |
| I05 / 付款 | pending 公开付款，关闭重开 | paid | paid | PASS | JSON，同本轮哈希 | 无 |
| I06 / 协同 | 提交后公开付款，关闭重开 | true、submitted 后 paid | true、submitted 后 paid | PASS | JSON，同本轮哈希 | 无 |
| I07 / 现存付款 | 取消后公开付款，关闭重开 | cancelled 后 paid | cancelled 后 paid | PASS | JSON，同本轮哈希 | 无 |
| I08 / 非空字符串 | 空、None、整数创建 | 三次 ValueError，零行 | 三次 ValueError，零行 | PASS | JSON，同本轮哈希 | 无 |
| I09 / 重复键 | 同 ID 再创建，关闭重开 | IntegrityError，原 pending | 符合 | PASS | JSON，同本轮哈希 | 无 |
| I10 / 取消缺失 | cancel_order(MISSING) | ValueError，零行 | 符合 | PASS | JSON，同本轮哈希 | 无 |
| I11 / 提交缺失 | submit_order(MISSING) | ValueError，零行 | 符合 | PASS | JSON，同本轮哈希 | 无 |
| I12 / 付款缺失 | ui.mark_paid(MISSING) | ValueError，零行 | 无异常，零行 | FAIL | JSON，同本轮哈希 | [BUG-002](../../issues/BUG-002.md) |
| I13 / 服务写入缺失 | set_status(MISSING, paid) | ValueError，零行 | 符合 | PASS | JSON，同本轮哈希 | 无 |
| I14 / 数据库失败 | 只读连接依次取消、提交、付款，重开 | 三次 OperationalError，仍 pending | 符合 | PASS | JSON，同本轮哈希 | 无 |
| I15 / 隔离 | 取消 A、提交 订单-二，另连接读 | true；cancelled、submitted | 符合 | PASS | JSON，同本轮哈希 | 无 |
| I16 / AC-3 | 原 checks 读取实际 runtime | 授权真实服务回执 | 缺端点和权限，未访问网络 | BLOCKED | [checks](evidence/initial-acceptance.json)、runtime，同本轮哈希 | 环境恢复条件见第 8 节 |

## 7. Related Issues and Impact

| Issue | Cases | 本轮影响 |
|---|---|---|
| [BUG-001](../../issues/BUG-001.md) | I04 / AC-2 | 取消保护被覆盖，本地行为失败 |
| [BUG-002](../../issues/BUG-002.md) | I12 | 公开付款缺失订单异常契约失败 |

未将外部阻塞误报为产品缺陷。未进行架构符合性判定，相关检查由 Main 另行调度。

## 8. Test Conclusion and Limitations

- 本轮目标快照、本地环境及完整范围 Test Gate：**FAIL**；13 PASS、2 FAIL、1 BLOCKED。全部可执行项已完成，没有靠阻塞停止可执行场景。
- 本地恢复：按两项原 Issue 修复，提供实际新源码快照及局部证据，再独立全量集成复验。产品行为失败解除前不能通过。
- 外部恢复：有权人员提供获授权真实测试服务端点、调用权限及真实回执入口后恢复 I16；现有 checks 永不联网，配置字段到位本身不等于真实验收通过。即使本地修复全部通过，AC-3 未获真实证据仍使完整范围不能 PASS。
- 人工验收：无图形 UI、无主观视觉判据，无需人工反馈；外部授权缺失属于环境阻塞。
