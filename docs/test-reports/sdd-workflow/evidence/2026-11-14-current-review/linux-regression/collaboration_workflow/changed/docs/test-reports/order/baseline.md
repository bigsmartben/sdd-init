# Test Report — 订单产品 baseline

## 1. Test Goals and Basis

- **批次／类型／执行者／时间**：baseline；独立全功能集成回归；sdd-test-loop Agent；2026-11-14，精确 UTC 时间见原始证据。
- **目标**：验证当前快照的新建、取消、提交、公开付款、异常／组合／恢复与外部回执核验条件。
- **依据**：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[本轮指南](../../../specs/order/quickstart.md)。架构遵循由独立 Review 判定。

## 2. Test Scope and Plan

- **范围**：指南的 14 个用例，覆盖 AC-1/2/3、新建、取消、现存订单付款、合法状态、缺失对象、数据库异常、跨订单及恢复。无 UI、无已确认性能阈值；不增加重复提交等未规定语义。
- **安排**：独立执行者编写 checks/integration.py，仅调用正式 src 公开函数和真实文件 SQLite；依指南常规推导数据与错误注入。既有 acceptance 与两项单元测试另行实跑。
- **完成判据**：全部适用功能点满足且真实证据齐备才 PASS；失败和阻塞完整记录可结束本轮执行。
- **确认来源**：Main 本次委派明确转交用户已确认范围、当前及修复后实际快照、隔离本地 Python+文件 SQLite、Spec 与公开入口判据。未重复确认。

## 3. Test Environment

- **实际版本**：Git `95cfcb31cf183d04b7ba1359a8dfe80d28608b00`；基线 src 无未提交修改；验证脚本和测试文档为本轮新增。逐个 src 和脚本 SHA-256 见[原始证据](evidence/baseline-integration.json)，执行前后源哈希一致。
- **环境与入口**：当前隔离项目；Python 3.12.3，SQLite 3.45.1；`python -B checks/integration.py`。
- **真实／模拟**：正式服务、storage、公开 ui 适配和真实文件 SQLite；query_only 是实际数据库写入限制，无模拟结果。AC-3 未调用外部服务。

## 4. Test Setup and Data

- **准备**：标准库直接运行，无依赖安装。每项新建临时文件数据库。
- **数据**：ORDER-1；订单-β 检查非空 Unicode 编号与多实体隔离；空串、None、0 检查类型／空值。现存订单付款前态含 pending/submitted/cancelled，依据契约对现存订单统一 paid 的要求。
- **恢复**：所有用例 finally 关闭连接，临时目录自动删除；RECOVERY-1 内恢复 query_only 后成功重提。
- **缺口**：runtime external_endpoint=null、external_call_authorized=false、network_access_in_this_run=false；AC-3 阻塞。仅有权人员提供端点、权限和真实调用路径后可恢复。

## 5. Execution and Coverage Summary

- **执行**：14 个用例全部形成结果；10 PASS、3 FAIL、0 Not run、1 BLOCKED，总计 14。已执行的 13 项中通过 10 项；外部阻塞不计为通过。
- **需求覆盖**：AC-1 与本地新建、取消、付款、合法状态、错误传播和恢复已实测；AC-2 及组合失败；AC-3 仅完成前置条件核对，真实回执未验证。范围内功能全部映射到指南，不代表全部通过。
- **辅助运行**：[既有 acceptance](evidence/baseline-acceptance.json) 显示 AC-1 PASS、AC-2 FAIL、AC-3 BLOCKED，退出 1；[既有单测](evidence/baseline-unit.txt) 两项通过，退出 0。完整 integration 退出 1。[运行事实](evidence/baseline-runtime.json)只补充版本，不推定结果。

## 6. Test Details

| Case / Requirement basis | Preconditions / Data | Method and actual steps | Expected outcome and criteria | Actual outcome and differences | Verdict | Evidence / Actual version | Issue reference |
|---|---|---|---|---|---|---|---|
| NEW-1 / Spec 编号／契约 create_order | 每项独立文件 SQLite | 空文件库；新建 ORDER-1 后另开连接；命令见指南 | pending | `{"state":"pending"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| NEW-2 / Spec 非空字符串 | 每项独立文件 SQLite | 空串、None、0 分别新建；命令见指南 | 各抛 ValueError | `[{"exception":"ValueError","expected":"ValueError","matches":true},{"exception":"ValueError","expected":"ValueError","matches":true},{"exception":"ValueError","expected":"ValueError","matches":true}]` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| AC-1 / Spec AC-1 | 每项独立文件 SQLite | pending 提交并重开；命令见指南 | true/submitted | `{"before":"pending","accepted":true,"persisted":"submitted"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| CANCEL-1 / 契约 cancel_order | 每项独立文件 SQLite | pending 取消并重开；命令见指南 | cancelled | `{"persisted":"cancelled"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| AC-2 / Spec AC-2 | 每项独立文件 SQLite | 取消后提交并重开；命令见指南 | false/cancelled | `{"before":"cancelled","accepted":true,"persisted":"submitted"}` | FAIL | [原始 JSON](evidence/baseline-integration.json) | [ORDER-001](../../issues/ORDER-001.md) |
| PAID-1 / Spec mark_paid | 每项独立文件 SQLite | pending 付款并重开；命令见指南 | paid | `{"before":"pending","persisted":"paid"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| PAID-2 / Spec mark_paid | 每项独立文件 SQLite | submitted 付款并重开；命令见指南 | paid | `{"before":"submitted","persisted":"paid"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| PAID-3 / Spec mark_paid | 每项独立文件 SQLite | cancelled 付款并重开；命令见指南 | paid | `{"before":"cancelled","persisted":"paid"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| STATUS-1 / 契约 set_status | 每项独立文件 SQLite | 逐个写入四个合法状态并重开；命令见指南 | 请求状态均持久化 | `[{"requested":"submitted","persisted":"submitted"},{"requested":"cancelled","persisted":"cancelled"},{"requested":"paid","persisted":"paid"},{"requested":"pending","persisted":"pending"}]` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| MISSING-1 / 契约对象缺失 | 每项独立文件 SQLite | 空库分别读取／取消／提交／设置状态／付款；命令见指南 | 全部 ValueError | `{"read_status":{"exception":"ValueError","expected":"ValueError","matches":true},"cancel_order":{"exception":"ValueError","expected":"ValueError","matches":true},"submit_order":{"exception":"ValueError","expected":"ValueError","matches":true},"set_status":{"exception":"ValueError","expected":"ValueError","matches":true},"mark_paid":{"exception":null,"expected":"ValueError","matches":false}}` | FAIL | [原始 JSON](evidence/baseline-integration.json) | [ORDER-002](../../issues/ORDER-002.md) |
| DB-1 / 契约数据库异常 | 每项独立文件 SQLite | query_only=ON 后分别调用五个写入接口；命令见指南 | 全部 OperationalError；原状态 pending | `{"create_order":{"exception":"OperationalError","expected":"OperationalError","matches":true},"cancel_order":{"exception":"OperationalError","expected":"OperationalError","matches":true},"submit_order":{"exception":"OperationalError","expected":"OperationalError","matches":true},"set_status":{"exception":"OperationalError","expected":"OperationalError","matches":true},"mark_paid":{"exception":"OperationalError","expected":"OperationalError","matches":true},"persisted":"pending"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| ISOLATION-1 / Spec AC-2＋付款＋非空编号 | 每项独立文件 SQLite | 两单交叉取消、付款、提交；命令见指南 | false/cancelled；另一单 paid | `{"accepted":true,"first":"submitted","second":"paid"}` | FAIL | [原始 JSON](evidence/baseline-integration.json) | [ORDER-001](../../issues/ORDER-001.md) |
| RECOVERY-1 / 契约异常＋AC-1 | 每项独立文件 SQLite | 数据库写失败后 rollback 并恢复可写后重提；命令见指南 | 先异常，后 true/submitted | `{"failure":{"exception":"OperationalError","expected":"OperationalError","matches":true},"accepted_after_recovery":true,"persisted":"submitted"}` | PASS | [原始 JSON](evidence/baseline-integration.json) | 无 |
| AC-3 / Spec AC-3 | 每项独立文件 SQLite | 读取 runtime 就绪条件，未发外部调用；命令见指南 | 缺端点权限须 BLOCKED | `{"environment":"isolated-local-fixture","database":"per-scenario temporary SQLite file","external_endpoint":null,"external_call_authorized":false,"network_access_in_this_run":false}` | BLOCKED | [原始 JSON](evidence/baseline-integration.json) | 无 |

AC-3 影响外部回执判据；恢复需独立真实调用授权、端点和可执行调用路径，禁止用本地结果替代。完整中间观察、分接口异常与源版本在对应 JSON 行中。

## 7. Related Issues and Impact

| Issue reference | Related cases in this batch | Issue summary and impact on this batch's conclusion |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2、ISOLATION-1 | 取消被提交覆盖，原返回值和持久化状态均失败 |
| [ORDER-002](../../issues/ORDER-002.md) | MISSING-1 | 公开付款缺失订单无异常；其他接口正确 |

## 8. Test Conclusion and Limitations

- **结论**：当前快照不满足全功能验收；两项本地缺陷已交 Main 修复，基线真实失败保留。
- **未验证**：AC-3 真实外部回执缺端点及权限，未发请求、未模拟。修复后需全量重跑 14 项并按实际源哈希建立新批次。
- **人工确认**：无 UI 或主观体验判据，无待收集人工验收反馈；外部服务前置条件属于授权阻塞。
- **Test Gate**：FAIL，适用当前提交及基线源哈希、当前隔离本地环境和上述范围；同时保留 AC-3 BLOCKED。即使修复本地缺陷，未获得外部真实证据前整轮仍不能 PASS。
