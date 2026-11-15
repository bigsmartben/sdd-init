# Test Report — 订单产品 fixed 全量复验

## 1. Test Goals and Basis

- **批次／类型／执行者／时间**：fixed；独立全功能集成复验；sdd-test-loop Agent，非修复实施者；2026-11-14T15:15:58 UTC。
- **目标**：修复后全量验证订单产品，核验两原 Issue 及其必要回归。
- **依据**：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[全功能指南](../../../specs/order/quickstart.md)、[原基线](baseline.md)、[修复计划](../../plans/order-bugfix/plan.md)。

## 2. Test Scope and Plan

- **范围**：沿用已确认全范围 14 项；覆盖所有本地功能、异常、恢复与组合，以及真实外部回执 AC-3 的前置条件。无 UI、无需主观反馈，未规定的状态流转语义不扩充。
- **安排**：完整重跑相同 checks/integration.py（脚本 SHA-256 与基线相同），另实跑原 acceptance、现有全部单测及 runtime_details；不以实施者的局部自验代替本轮。
- **完成标准**：全部范围判据满足、真实证据齐备才能整轮 PASS；本地 Issue 按原失败场景与必要回归独立关单。
- **确认来源**：Main 延续用户已确认修复后当前实际快照、本地环境、Spec／公开入口及全范围；此次仅纳入已授权修复，无变更判据。

## 3. Test Environment

- **实际版本**：HEAD `95cfcb31cf183d04b7ba1359a8dfe80d28608b00` 加未提交修复；order_service SHA-256 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，ui `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`。storage 与 __init__ 未变；完整哈希见[证据](evidence/fixed-integration.json)。运行前后源稳定为 true。
- **环境与入口**：当前隔离项目 Python 3.12.3、SQLite 3.45.1，`python -B checks/integration.py`；无安装、外部平台或部署操作。
- **真实／模拟**：正式 src 服务、storage、ui 和真实文件数据库；query_only 的数据库故障实际发生，无替身组件。AC-3 没有调用或模拟外部服务。

## 4. Test Setup and Data

- **准备与数据**：完全依指南：逐用例独立临时 SQLite 文件；ORDER-1、订单-β；非法编号空串／None／0；缺失订单 MISSING；真实 query_only 写保护与恢复。
- **数据恢复**：连接最终关闭、临时目录自动清理；RECOVERY-1 在同一连接完成失败及恢复后的成功提交。
- **准备缺口**：AC-3 仍缺真实端点、外部调用授权与调用路径；配置无变化，未向网络发请求。

## 5. Execution and Coverage Summary

- **实际覆盖**：完整重跑 14 项；13 PASS、0 FAIL、0 Not run、1 BLOCKED。13 个可执行本地场景全部通过；AC-3 仅前置条件核验，真实回执仍未验证。
- **版本影响**：service 提交分支和 ui 状态写入路径改变；不复用基线通过项作为修复版本结论，全部 14 项重新执行。与基线对照：AC-2、ISOLATION-1、MISSING-1 从 FAIL 转 PASS；其余 10 项仍 PASS；AC-3 仍 BLOCKED。
- **辅助结果**：[原 acceptance](evidence/fixed-acceptance.json) AC-1/2 PASS、AC-3 BLOCKED，退出 3；[全部单测](evidence/fixed-unit.txt) 7/7 PASS，退出 0；[runtime](evidence/fixed-runtime.json) 事实与实际快照匹配。integration 退出 3。

## 6. Test Details

全部实际步骤、预期及数据沿用指南，逐项来源与原始观察如下。下列全部行适用第 3 节同一实际修复快照。

| Case / Requirement basis | Preconditions / Data | Method and actual steps | Expected outcome and criteria | Actual outcome and differences | Verdict | Evidence / Actual version | Issue reference |
|---|---|---|---|---|---|---|---|
| NEW-1 / Spec 编号／契约 create_order | 每项独立文件 SQLite | 空文件库；新建 ORDER-1 后另开连接；命令见指南 | pending | `{"state":"pending"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| NEW-2 / Spec 非空字符串 | 每项独立文件 SQLite | 空串、None、0 分别新建；命令见指南 | 各抛 ValueError | `[{"exception":"ValueError","expected":"ValueError","matches":true},{"exception":"ValueError","expected":"ValueError","matches":true},{"exception":"ValueError","expected":"ValueError","matches":true}]` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| AC-1 / Spec AC-1 | 每项独立文件 SQLite | pending 提交并重开；命令见指南 | true/submitted | `{"before":"pending","accepted":true,"persisted":"submitted"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| CANCEL-1 / 契约 cancel_order | 每项独立文件 SQLite | pending 取消并重开；命令见指南 | cancelled | `{"persisted":"cancelled"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| AC-2 / Spec AC-2 | 每项独立文件 SQLite | 取消后提交并重开；命令见指南 | false/cancelled | `{"before":"cancelled","accepted":false,"persisted":"cancelled"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | [ORDER-001](../../issues/ORDER-001.md) |
| PAID-1 / Spec mark_paid | 每项独立文件 SQLite | pending 付款并重开；命令见指南 | paid | `{"before":"pending","persisted":"paid"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| PAID-2 / Spec mark_paid | 每项独立文件 SQLite | submitted 付款并重开；命令见指南 | paid | `{"before":"submitted","persisted":"paid"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| PAID-3 / Spec mark_paid | 每项独立文件 SQLite | cancelled 付款并重开；命令见指南 | paid | `{"before":"cancelled","persisted":"paid"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| STATUS-1 / 契约 set_status | 每项独立文件 SQLite | 逐个写入四个合法状态并重开；命令见指南 | 请求状态均持久化 | `[{"requested":"submitted","persisted":"submitted"},{"requested":"cancelled","persisted":"cancelled"},{"requested":"paid","persisted":"paid"},{"requested":"pending","persisted":"pending"}]` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| MISSING-1 / 契约对象缺失 | 每项独立文件 SQLite | 空库分别读取／取消／提交／设置状态／付款；命令见指南 | 全部 ValueError | `{"read_status":{"exception":"ValueError","expected":"ValueError","matches":true},"cancel_order":{"exception":"ValueError","expected":"ValueError","matches":true},"submit_order":{"exception":"ValueError","expected":"ValueError","matches":true},"set_status":{"exception":"ValueError","expected":"ValueError","matches":true},"mark_paid":{"exception":"ValueError","expected":"ValueError","matches":true}}` | PASS | [原始 JSON](evidence/fixed-integration.json) | [ORDER-002](../../issues/ORDER-002.md) |
| DB-1 / 契约数据库异常 | 每项独立文件 SQLite | query_only=ON 后分别调用五个写入接口；命令见指南 | 全部 OperationalError；原状态 pending | `{"create_order":{"exception":"OperationalError","expected":"OperationalError","matches":true},"cancel_order":{"exception":"OperationalError","expected":"OperationalError","matches":true},"submit_order":{"exception":"OperationalError","expected":"OperationalError","matches":true},"set_status":{"exception":"OperationalError","expected":"OperationalError","matches":true},"mark_paid":{"exception":"OperationalError","expected":"OperationalError","matches":true},"persisted":"pending"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| ISOLATION-1 / Spec AC-2＋付款＋非空编号 | 每项独立文件 SQLite | 两单交叉取消、付款、提交；命令见指南 | false/cancelled；另一单 paid | `{"accepted":false,"first":"cancelled","second":"paid"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | [ORDER-001](../../issues/ORDER-001.md) |
| RECOVERY-1 / 契约异常＋AC-1 | 每项独立文件 SQLite | 数据库写失败后 rollback 并恢复可写后重提；命令见指南 | 先异常，后 true/submitted | `{"failure":{"exception":"OperationalError","expected":"OperationalError","matches":true},"accepted_after_recovery":true,"persisted":"submitted"}` | PASS | [原始 JSON](evidence/fixed-integration.json) | 无 |
| AC-3 / Spec AC-3 | 每项独立文件 SQLite | 读取 runtime 就绪条件，未发外部调用；命令见指南 | 缺端点权限须 BLOCKED | `{"environment":"isolated-local-fixture","database":"per-scenario temporary SQLite file","external_endpoint":null,"external_call_authorized":false,"network_access_in_this_run":false}` | BLOCKED | [原始 JSON](evidence/fixed-integration.json) | 无 |

AC-3 阻塞影响真实外部回执判据，恢复需有权人员提供真实端点、调用权限及受授权的真实调用入口；现有本地检查即使配置补齐也不能代替该实测。

## 7. Related Issues and Impact

| Issue reference | Related cases in this batch | Issue summary and impact on this batch's conclusion |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2、ISOLATION-1；AC-1、付款、数据库异常与恢复回归 | 原失败入口恢复 false/cancelled，两单隔离保持；必要本地回归全部通过，具备本地关单证据 |
| [ORDER-002](../../issues/ORDER-002.md) | MISSING-1、PAID-1/2/3、DB-1及全量本地回归 | 原公开付款缺失对象抛 ValueError；现存对象仍 paid 且持久化，数据库异常传播正确，具备本地关单证据 |

## 8. Test Conclusion and Limitations

- **结论**：两项本地缺陷原场景恢复，13 个本地集成用例和 7 个单元用例通过，无观察到的修复回归；本轮本地 Issue 关单有独立实际证据。
- **剩余未验**：AC-3 真实外部回执无端点及调用权限，未实测、未模拟，阻塞不等于实现缺陷。前置条件具备后按原 Spec 恢复真实核验。
- **人工确认**：本地无 UI 或主观反馈，不适用；缺外部授权不转写为人工验收通过。
- **Test Gate**：BLOCKED，适用本报告实际修复源哈希、当前本地 Python／文件 SQLite、已确认全范围。全部可执行本地项通过仍不足以覆盖 AC-3，故整轮不能 PASS。架构 Gate 引用[独立审查](local-review.md)，不由本报告替代。
