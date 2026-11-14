# Test Report — 订单修复后全功能集成复验

## 1. 测试目标与依据

- 批次：ORDER-FIXED；类型：修复后全功能集成复验；执行者：原独立测试技能 Agent `/root/order_integration`；实测 UTC 时间见[回执](evidence/fixed-execution.json)（2026-11-14；项目会话日期标示 2026-11-15）。
- 依据：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[Quickstart](../../../specs/order/quickstart.md)、[原批次](initial.md)、原 ORDER-001/002、[修复 Task](../../../specs/order/plan.md)、[Bugfix 归因及定向复验](bugfix.md)。
- 目的：在实际修复快照验证原失败恢复、必要回归和完整订单范围；不以 Bugfix 自验替代独立集成结果。

## 2. 范围与计划

沿用 Main 已确认的新建、取消、提交、公开 mark_paid、AC-3、Python + 文件 SQLite、主要路径及判据。Main 本次接续明确使用修复后未提交源码快照；没有改变需求或环境。原两缺陷均关联状态入口，范围共20项且可完整复跑，因此20项全部重新取证，未复用初始通过结果来代替当前结果。测试资产及预期冻结；未新增状态规则。

完成标准仍为全范围所有适用判据及必要真实证据满足方可 PASS。人工视觉验收不适用；架构符合性归独立架构记录。

## 3. 实际版本与环境

HEAD 仍为 `89df9f629407a6b572c6f65c87fc9768e0f52f5d`，加未提交修复，不能仅用 HEAD 区分初始版本。实际源码 SHA256：

| 文件 | 修复快照 SHA256 |
|---|---|
| src/order_service.py | 3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb |
| src/ui.py | 4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909 |
| src/storage.py | 6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9 |
| src/__init__.py | 10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded |

冻结测试脚本 checks/order_integration.py SHA256 `496fa99f09e2c5d0796678ac580ffa49553e155f266a68673b68e58e93e1bc99` 与初始批次一致；运行前核对交接哈希，运行前后脚本与源码哈希一致。测试 Agent 未修改 src 或测试预期。[回执](evidence/fixed-execution.json) 保存实际 src diff、工作区状态与现行单测哈希；[运行事实](evidence/fixed-runtime.json) 保存完整源码哈希与配置。

Python 3.12.3，SQLite 3.45.1，真实正式 src + 标准库文件 SQLite，运行环境 isolated-local-fixture。外部端点 null、授权 false、网络许可 false。没有模拟组件或网络调用。

### 运行条件事实与证据复用

来源：2026-11-15 用户在本轮同一记录中的补充确认。运行仍为同一隔离项目、本地文件 SQLite；AC-3 端点与权限未变化；实现、接口、环境和数据均未改变。此处关联用户提供的事实，不是新增运行观测；本次仅归并文档，未执行新测试，也未重新采集运行信息或计算哈希。第3节快照、原始执行时间及以下证据保持原批次归属。

在上述不变条件及原已确认判据下，可继续复用：

| 原证据 | 可复用的证明范围与限制 |
|---|---|
| [完整复验逐项输出](evidence/fixed-integration.json)、[原AC输出](evidence/fixed-acceptance.json) | 原修复快照的19项本地通过结果，包括两原故障、持久化、异常及多订单回归；AC-3仅证明当时阻塞，不能证明真实外部回执 |
| [执行回执](evidence/fixed-execution.json)、[运行事实与哈希](evidence/fixed-runtime.json) | 原测试实际版本、装配、环境、入口与退出码；本次不变事实由用户确认，不将原采集时间改为本次时间 |
| [8项单测](evidence/fixed-unittest.txt)、[Bugfix定向复验](bugfix.md) | 原快照对应的局部与定向补证，继续支持两原Issue关闭依据，不替代完整集成结果 |
| [架构复核记录](architecture-review.md)、[复核原始证据](review-fixed.json) | 原修复快照的职责、持久化、异常及依赖检查；CHK-006规则映射待查仍保留，不能据运行条件不变判为已解决 |
| [初始批次](initial.md)及其原始证据 | 仅复用为修复前缺陷和处理历史，不替代修复后版本的通过证据 |

本次未产生新增场景或执行批次，不增加执行次数与通过项数。第5～8节仍为原实测结论：19 PASS、0 FAIL、1 BLOCKED，Test Gate保持BLOCKED；AC-3端点和权限未变化，其真实回执缺口与恢复条件保持。架构Review Gate保持UNVERIFIED。后续若版本、接口、数据、环境、判据或测试方法变化，须先评估影响，仅复用仍适用部分。

## 4. 准备与数据

原资产以公开调用入口驱动，每项独立临时目录和真实数据库，使用 ORDER-1、ORDER-2、ORDER-3、MISSING，非法编号为空串、None、整数；关闭连接测试真实 SQLite 异常。数据推导依据与复位见 Quickstart，无凭据或依赖安装。结束关闭连接及删除临时目录；无工具/环境异常，未改配置。AC-3 缺少真实组件及授权，只阻塞该项。

## 5. 执行与覆盖汇总

- 完整20项：**19 PASS、0 FAIL、0 Not run、1 BLOCKED**，合计20。可执行本地项19/19通过，全范围通过率19/20，不等同全范围验收通过。
- 功能映射：新建 INT-01/INVALID-*；提交 AC-1；取消保护 AC-2；公开 paid INT-02；服务写入 INT-03；不存在订单 MISSING-*；数据库异常 CLOSED-*；多订单隔离 INT-04；真实外部回执 AC-3。
- 原失败复验：AC-2 返回 false、提交前后及重开均 cancelled；MISSING-MARK_PAID 抛 ValueError，现存订单保持 pending，缺失编号仍不存在。原判据及全部本地回归通过，Main 确认 Bugfix 释放写入权后，两原 Issue 已按授权更新为 Closed after retest。
- 原验收入口同版复跑：AC-1/AC-2 PASS，AC-3 BLOCKED，退出3，见[原AC输出](evidence/fixed-acceptance.json)。完整入口退出3；[现行8项单测](evidence/fixed-unittest.txt) 全PASS，退出0，运行事实命令退出0；命令和退出码见执行回执。单测是辅助结果，不替代逐项集成证据。

## 6. 逐项执行结果

每项实际版本均为第3节工作区快照；JSON 保存完整中间观察、预期、结果匹配和异常类型。

| 用例 / 判据 | 前置数据 | 实际步骤 | 预期 | 实际 | 判定 | 证据 / 版本 | Issue |
|---|---|---|---|---|---|---|---|
| INT-01 / pending creation persistence | 独立临时文件数据库 | created status → status after close and reopen | pending；pending | pending；pending | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| AC-1 / Spec AC-1 | 独立临时文件数据库 | created status → submit result → status after submit → status after close and reopen | pending；True；submitted；submitted | pending；True；submitted；submitted | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| AC-2 / Spec AC-2 | 独立临时文件数据库 | created status → cancelled status before submit → cancel persisted before submit → submit result → status after submit → status after close and reopen | pending；cancelled；cancelled；False；cancelled；cancelled | pending；cancelled；cancelled；False；cancelled；cancelled | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | [ORDER-001](../../issues/ORDER-001.md) |
| INT-02 / existing mark_paid persistence | 独立临时文件数据库 | created status → status after mark_paid → status after close and reopen | pending；paid；paid | pending；paid；paid | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| INT-03 / set_status persistence | 独立临时文件数据库 | status after set_status → status after close and reopen | paid；paid | paid；paid | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| INVALID-EMPTY / nonempty string order ID | 独立临时文件数据库 | create invalid order ID → rows after rejected create → persisted rows after reopen | {'exception_family': 'ValueError'}；[]；[] | {'message': 'order_id is required'} / ValueError；[]；[] | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| INVALID-NONE / nonempty string order ID | 独立临时文件数据库 | create invalid order ID → rows after rejected create → persisted rows after reopen | {'exception_family': 'ValueError'}；[]；[] | {'message': 'order_id is required'} / ValueError；[]；[] | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| INVALID-INTEGER / nonempty string order ID | 独立临时文件数据库 | create invalid order ID → rows after rejected create → persisted rows after reopen | {'exception_family': 'ValueError'}；[]；[] | {'message': 'order_id is required'} / ValueError；[]；[] | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| MISSING-READ / missing order raises ValueError | 独立临时文件数据库 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| MISSING-CANCEL / missing order raises ValueError | 独立临时文件数据库 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| MISSING-SUBMIT / missing order raises ValueError | 独立临时文件数据库 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| MISSING-SET_STATUS / missing order raises ValueError | 独立临时文件数据库 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| MISSING-MARK_PAID / missing order raises ValueError | 独立临时文件数据库 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | [ORDER-002](../../issues/ORDER-002.md) |
| CLOSED-CREATE / database exceptions propagate | 独立临时文件数据库 | write on closed connection → original persisted status → failed create remains absent | {'exception_family': 'Error'}；pending；{'exception_family': 'ValueError'} | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| CLOSED-CANCEL / database exceptions propagate | 独立临时文件数据库 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| CLOSED-SUBMIT / database exceptions propagate | 独立临时文件数据库 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| CLOSED-SET_STATUS / database exceptions propagate | 独立临时文件数据库 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| CLOSED-MARK_PAID / database exceptions propagate | 独立临时文件数据库 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| INT-04 / multiple order isolation | 独立临时文件数据库 | second order submit result → independent states before close → independent states after reopen | True；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'}；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'} | True；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'}；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'} | PASS | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |
| AC-3 / Spec AC-3: authorized real external service receipt | 独立临时文件数据库 | 只读 runtime.json，未访问网络 | 获授权真实外部测试服务回执 | 端点未配置、无调用授权；本轮禁网。恢复须 Main 对齐真实环境及执行路径 | BLOCKED | [JSON](evidence/fixed-integration.json) / 修复工作区哈希 | 无 |

## 7. 原 Issue 与批次影响

| Issue | 原场景 | 当前证据与影响 |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2 | 取消保护恢复，AC-1及全部本地必要回归通过，具备本地关单证据 |
| [ORDER-002](../../issues/ORDER-002.md) | MISSING-MARK_PAID | 缺失异常恢复，现存 paid、DB异常及其他入口保持，具备本地关单证据 |

原失败在 initial.md 和 initial-* 留存；Bugfix 与实施自验分别引用 bugfix.md 和 Plan。Issue 状态由各原记录维护，测试报告不将整轮阻塞解释为本地缺陷复现。

## 8. 结论、人工反馈与 Gate

**Test Gate：BLOCKED**，适用第3节实际修复版本和当前隔离环境的完整订单范围。所有本地功能及两原缺陷回归通过；AC-3 是完整范围内必需真实外部回执，尚未验证，因此不能判 PASS。

没有 UI、视觉判断或其他必需人工反馈项。AC-3 恢复条件：有权方提供获授权真实测试服务端点、调用权限、网络执行许可及真实调用入口，Main 对齐受影响环境与步骤后续测；仅补配置或复跑当前禁止外呼的 fixture 不能解除阻塞。本轮没有外部操作或部署。两本地 Issue 可依据本批次与修复定向证据独立关闭，AC-3 不构成它们的关单条件，也不受关单影响。

写后核对：读回与 Spec、契约、原批次、原 Issue 和实际 JSON 对照，版本、20项统计、原失败恢复及阻塞条件一致。对 fixed.md、Quickstart、索引和两原 Issue 的机械检查为5文件、0错误、0警告；检查范围及原始回执见 [文档检查](evidence/fixed-doc-check.json)。机械通过仅证明文档结构与引用，无替代业务判定。

文档检查首次写证据文件前因引用目标尚不存在报 DOC007，见[首次检查](evidence/fixed-doc-check-first.json)；目标落盘后复查通过，不涉及测试脚本、产品实现或业务断言变动。
