# Test Report — 订单修复后全功能集成复验

## 1. Test Goals and Basis

- 批次：fixed；类型：修复后独立全产品集成复验；执行者：原 sdd-test-loop integration Agent（未修改 src）；日期：2026-11-14。
- 目标：复验 [BUG-001](../../issues/BUG-001.md)、[BUG-002](../../issues/BUG-002.md) 原故障，并重跑全部范围及受影响回归。
- 依据：[Spec](../../../specs/order/spec.md)、[函数契约](../../contracts/order.md)、[Quickstart](../../../specs/order/quickstart.md)。历史事实保留于[初轮](initial.md)，不覆盖原失败。

## 2. Test Scope and Plan

- Main 已确认修复冻结版就绪并要求相同已确认范围、环境和公开路径的完整接续。仍覆盖 I01–I16，无新增业务标准或外部授权。
- 顺序：全部本地文件 SQLite 公开函数场景 → 原 checks 全部 AC → 现有与新增单元测试 → 运行事实和工作树核对。
- 通过标准沿用 Quickstart；本地全部通过可支持原本地 Issue 关闭，但完整 Test Gate 还需 AC-3 真实外部回执。

## 3. Test Environment

- HEAD：`9701a4d79766e124c202c9b258ad18a458a26cd8` 加未提交修复。[实际源码差异](evidence/fixed-source.diff)、[工作树](evidence/fixed-worktree.txt)。
- 精确 SHA-256：order_service `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；ui `c4a9e5b0789129c89bb71387e2aaed619944d115aff5a53c7fb5320fcbff88ae`；storage `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9`；__init__ `10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded`。
- Python 3.12.3 / SQLite 3.45.1；真实文件数据库，调用公开 storage、order_service、ui 入口。未模拟 SQLite、未访问网络或外部平台。[运行事实](evidence/fixed-runtime.json)。
- 运行条件补充（2026-11-14，来源：用户在同一记录中的补充确认）：运行仍为同一隔离项目、本地文件 SQLite；AC-3 端点和权限没有变化，仍缺获授权端点与调用权限。实现、接口、环境和数据均未改变。本次仅归并该事实，未执行新测试或运行探测；上述版本、哈希和运行输出均为原批次证据，不是本次重新测得。

## 4. Test Setup and Data

- 沿用 Quickstart 常规数据与临时文件隔离；全部测试设置 `TMPDIR="$PWD/.tmp/order-tests"`。连接正常就绪，每例结束关闭并清理自身临时目录，不清除其他执行者资产。
- 边界：空字符串、None、非字符串、重复订单、缺失订单、只读数据库、非 ASCII 非空 ID、多订单。测试代码和方法与初轮相同，不修改断言迎合实现。
- 缺口：AC-3 仍没有外部端点和调用权限；当前夹具始终不访问外部服务。

## 5. Execution and Coverage Summary

- 本轮总数 16：PASS 15、FAIL 0、Not run 0、BLOCKED 1。全部可执行场景重新取证，未复用初轮执行结果证明新快照。
- 本地功能覆盖完整，15/15 通过。完整需求中 AC-3 真实回执仍未覆盖；不能用本地通过率代替全范围通过。
- [公开 checks](evidence/fixed-acceptance.json)：AC-1 PASS、AC-2 PASS、AC-3 BLOCKED；退出语义为 3。其本地结果与 I02/I04 为同一场景的补充，不重复计数。
- [单元补充](evidence/fixed-unit.txt)：9/9 PASS，由本 Agent 实际重跑；不替代文件 SQLite 集成证据。
- 实现只改取消提交保护与付款服务调用，可能影响提交、现存/缺失付款、异常传播；故全量重跑 I01–I15，并检查协同、隔离、持久化和数据库异常。

### 补充事实后的证据复用

依据第 3 节用户补充确认，本次无实现、接口、环境或数据变化，既有判据与测试方法沿用；未发现需要补验的影响。本次没有新增执行结果或计数，继续复用以下同一修复快照的证据：

| 既有证据 | 可复用范围与边界 |
|---|---|
| [集成 JSON](evidence/fixed-integration.json)、[公开 checks](evidence/fixed-acceptance.json) | I01–I15 的本地功能、原故障及受影响回归仍有证据支持；AC-1/AC-2 PASS，AC-3 仍仅有前置检查的 BLOCKED 证据，不证明真实外部回执。 |
| [单元输出](evidence/fixed-unit.txt)、[独立定向 JSON](../../issues/evidence/bugfix-retest.json) | 原 9 项单元测试及 8 项定向检查继续支持各自覆盖的局部行为、SQL/commit 异常传播；不另计集成用例，也不代替外部核验。 |
| [运行事实](evidence/fixed-runtime.json)、[源码差异](evidence/fixed-source.diff)、[工作树](evidence/fixed-worktree.txt) | 保留原执行时版本、装配和条件的可追溯依据；本次条件未变来自用户确认，不将这些历史输出表述为新探测。 |
| [架构检查记录](2026-11-14-review.md) | 同快照、同装配的 CHK-001～004 复核与 Review Gate PASS 可继续引用；本次未重新执行架构检查。 |

[初轮证据](initial.md)仍仅用于追溯修复前失败，不能代替修复快照的通过证据。两项本地 Issue 的关单依据保持有效；本报告完整 Test Gate 仍为 **BLOCKED**，AC-3 恢复条件沿用第 8 节。

## 6. Test Details

每行的完整前置、命令和通过标准沿用 Quickstart 同编号场景；实际版本统一为第 3 节。原始 JSON 保存关键中间值、返回值、重开文件后的持久化值及预期值。[本轮集成原始证据](evidence/fixed-integration.json)。

| Case / 依据 | 前置与实际操作 | 预期 | 本轮实际 | Verdict | 证据 | Issue |
|---|---|---|---|---|---|---|
| I01 / 创建 | 新文件创建 ORDER-1，关闭重开 | pending | pending | PASS | fixed-integration JSON | 无 |
| I02 / AC-1 | pending 提交，关闭重开 | true、submitted | true、submitted | PASS | JSON、公开 checks | 无 |
| I03 / 取消 | pending 取消，关闭重开 | cancelled | cancelled | PASS | JSON | 无 |
| I04 / AC-2 | 取消、读中间值、再提交、关闭重开 | false、cancelled | 中间 cancelled，返回 false，重开 cancelled；原 true/submitted 已恢复 | PASS | JSON、公开 checks；对照初轮 I04 | BUG-001 |
| I05 / 付款 | pending 公开付款，关闭重开 | paid | paid | PASS | JSON | BUG-002 回归 |
| I06 / 协同 | 提交、读 submitted、公开付款，重开 | true、最终 paid | true、submitted 后 paid | PASS | JSON | 两 Issue 回归 |
| I07 / 现存付款 | 取消、读 cancelled、公开付款，重开 | paid | cancelled 后 paid | PASS | JSON | BUG-002 回归 |
| I08 / 输入 | 空、None、整数创建 | 三次 ValueError、零行 | 符合 | PASS | JSON | 无 |
| I09 / 重复键 | 同 ID 再创建，重开 | IntegrityError、原 pending | 符合 | PASS | JSON | 无 |
| I10 / 取消缺失 | cancel_order(MISSING) | ValueError、零行 | 符合 | PASS | JSON | 回归 |
| I11 / 提交缺失 | submit_order(MISSING) | ValueError、零行 | 符合 | PASS | JSON | 回归 |
| I12 / 付款缺失 | ui.mark_paid(MISSING) | ValueError、零行 | ValueError、零行；原无异常已恢复 | PASS | JSON；对照初轮 I12 | BUG-002 |
| I13 / 写入缺失 | set_status(MISSING, paid) | ValueError、零行 | 符合 | PASS | JSON | BUG-002 回归 |
| I14 / 数据库异常 | query_only 后依次取消、提交、付款，重开 | 三次 OperationalError、原 pending | 符合，无成功吞错 | PASS | JSON | 两 Issue 回归 |
| I15 / 隔离与边界 | 取消 A、提交 订单-二，另连接读取 | true、cancelled/submitted | 符合 | PASS | JSON | 两 Issue 回归 |
| I16 / AC-3 | checks 读取实际配置 | 授权真实服务回执 | endpoint_configured=false、authorized=false，未调用外部服务 | BLOCKED | fixed-acceptance、fixed-runtime | 环境条件 |

补充异常证据：[Bugfix 独立定向 JSON](../../issues/evidence/bugfix-retest.json) 由 bugfix Agent 执行，8 PASS，实际源码哈希与本轮相同；其中 commit 失败使用真实文件 SQLite deferred FK 产生 IntegrityError，随后由调用者 rollback 恢复。它证明异常上传和调用者恢复，不宣称产品新增自动回滚，也不把该局部证据计入本轮 16 例。原 Bugfix 方案、自验与诊断归[计划 T001](../../../specs/order/plan.md)。

## 7. Related Issues and Impact

| Issue | 原故障与回归 | 结论 |
|---|---|---|
| [BUG-001](../../issues/BUG-001.md) | I04/AC-2 恢复，I02/I03/I06/I14/I15 等全量回归 | 本地关单所需证据齐备；AC-3 不属于本地故障判据 |
| [BUG-002](../../issues/BUG-002.md) | I12 恢复，I05–I07/I10/I11/I13/I14 等全量回归 | 本地关单所需证据齐备，无必需人工反馈 |

本轮未发现新实现缺陷。架构判定见独立[架构检查记录](2026-11-14-review.md)，本报告不以架构符合性代替业务验收。

## 8. Test Conclusion and Limitations

- 本地完整功能复验通过：15 PASS，两个原故障恢复，必要回归通过，无本地未测项。
- 完整声明范围 Test Gate：**BLOCKED**，适用于第 3 节实际修复源码快照及本地文件 SQLite 环境。原始 JSON 与公开 checks 支持本地结论，AC-3 缺真实证据使整轮不能 PASS。
- 恢复条件：由有权人员提供获授权真实测试服务端点、调用权限和实际可调用回执入口，再于授权环境执行 I16 并留证；现有 checks 不联网，不能仅改配置后宣称通过。配置、凭据获取、真实部署均未执行。
- 人工反馈：无 UI 或主观体验要求，无必需人工验收待补；外部前置条件缺失另作阻塞。
