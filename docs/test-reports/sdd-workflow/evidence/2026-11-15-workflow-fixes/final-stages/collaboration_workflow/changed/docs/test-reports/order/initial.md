# Test Report — 订单初始全功能集成回归

## 1. 测试目标与依据

- 批次：ORDER-INITIAL；类型：全功能集成回归；执行者：独立技能 Agent `/root/order_integration`；实际 UTC 时间见[执行回执](evidence/initial-execution.json)（2026-11-14）。此为运行时 UTC 事实，项目会话日期标示 2026-11-15。
- 目标：验证当前订单产品完整本地行为，保留外部真实回执阻塞；不修改 src。
- 依据：[Spec](../../../specs/order/spec.md)、[函数契约](../../contracts/order.md)、[Quickstart](../../../specs/order/quickstart.md)、[TASK.txt](../../../TASK.txt)。

## 2. 范围与计划

- Main 启动工单承接用户确认：当前及修复后实际快照；本地 Python + 每场景临时文件 SQLite；新建、取消、提交、公开 mark_paid、AC-3；已有判据和阶段顺序均确认，本轮无需新增常规确认。
- 顺序：先核对版本与环境，再从公开调用入口执行正常、取消、持久化、边界、异常、多订单协同和 AC-3 就绪检查。常规编号、缺失编号、非法值与关闭连接由契约推导，不扩张状态业务规则。
- 完成标准：全部适用判据满足且外部必需证据齐备才 PASS。架构检查由 Main 另行调度；无 UI 和人工视觉判据；外部配置与部署不获授权。

## 3. 实际版本与环境

- HEAD：`89df9f629407a6b572c6f65c87fc9768e0f52f5d`。初始工作区干净；本批次新增测试资产与文档，src 无改动；[执行回执](evidence/initial-execution.json)保存 git 状态及空 src diff。
- Python 3.12.3，SQLite 3.45.1，配置 environment=isolated-local-fixture，endpoint=null、external_call_authorized=false、network_access_in_this_run=false；[运行事实与全部源码 SHA256](evidence/initial-runtime.json)。
- 正式 src 模块 + 真实 SQLite 文件，未替代服务、未访问网络。测试入口 `python -B checks/order_integration.py`；资产 SHA256 `496fa99f09e2c5d0796678ac580ffa49553e155f266a68673b68e58e93e1bc99`。运行前后哈希一致，完整输出包含 src 与测试入口哈希。

## 4. 准备与数据

- Python 标准库已就绪，无安装步骤、凭据、后台服务或 UI。每项独立 TemporaryDirectory 文件库；ORDER-1 为普通订单，ORDER-2/3 验证同库隔离，MISSING 不存在；空串、None、整数覆盖编号边界；closed connection 验证数据库异常传播。
- 每场景连接在结束时关闭，临时目录由上下文删除，原始 JSON 留存于 evidence。未修改 runtime.json。未发生测试工具异常或重试；测试资产由 sdd-coder 新增和局部自验，技能 Agent 随后独立执行本轮全部场景。
- 准备缺口：AC-3 真实外部服务缺少端点、调用授权、网络许可和真实调用执行入口；只阻塞该项，不以本地模拟替代。

## 5. 执行与覆盖汇总

- 全部计划内 20 项均取得明确状态：17 PASS、2 FAIL、0 Not run、1 BLOCKED，总数 20。已执行本地项通过率 17/19；全范围通过率 17/20，不能等同需求通过。
- AC-1→AC-1 PASS；AC-2→AC-2 FAIL；AC-3→AC-3 BLOCKED。新建→INT-01 与 INVALID-*；取消→AC-2/INT-04；公开 paid→INT-02；服务 set_status→INT-03；缺失订单→MISSING-*；数据库异常→CLOSED-*；同库协同→INT-04。完整本地功能已覆盖，外部需求尚未验证。
- [原 AC 验收输出](evidence/initial-acceptance.json) 同样 1 PASS、1 FAIL、1 BLOCKED，退出 1；[原有单元测试](evidence/initial-unittest.txt) 2/2 通过，退出 0。它们是辅助证据，不替代全功能覆盖。完整集成退出 1，runtime 只读命令退出 0，命令与退出码见执行回执。

## 6. 逐项结果

下表每项从真实公开入口执行，版本均为上述 HEAD 和 SHA256；JSON 保存每一步观察、预期、匹配结果及具体异常类型。长路径步骤以英文原始操作名呈现，与可复跑资产逐项对应。

| 用例 / 判据 | 前置数据 | 实际步骤 | 预期 | 实际 | 判定 | 证据 / 版本 | Issue |
|---|---|---|---|---|---|---|---|
| INT-01 / pending creation persistence | 独立临时文件 SQLite；入口构造数据 | created status → status after close and reopen | pending；pending | pending；pending | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| AC-1 / Spec AC-1 | 独立临时文件 SQLite；入口构造数据 | created status → submit result → status after submit → status after close and reopen | pending；True；submitted；submitted | pending；True；submitted；submitted | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| AC-2 / Spec AC-2 | 独立临时文件 SQLite；入口构造数据 | created status → cancelled status before submit → cancel persisted before submit → submit result → status after submit → status after close and reopen | pending；cancelled；cancelled；False；cancelled；cancelled | pending；cancelled；cancelled；True；submitted；submitted | FAIL | [JSON](evidence/initial-integration.json) / 89df9f6 | [ORDER-001](../../issues/ORDER-001.md) |
| INT-02 / existing mark_paid persistence | 独立临时文件 SQLite；入口构造数据 | created status → status after mark_paid → status after close and reopen | pending；paid；paid | pending；paid；paid | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| INT-03 / set_status persistence | 独立临时文件 SQLite；入口构造数据 | status after set_status → status after close and reopen | paid；paid | paid；paid | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| INVALID-EMPTY / nonempty string order ID | 独立临时文件 SQLite；入口构造数据 | create invalid order ID → rows after rejected create → persisted rows after reopen | {'exception_family': 'ValueError'}；[]；[] | {'message': 'order_id is required'} / ValueError；[]；[] | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| INVALID-NONE / nonempty string order ID | 独立临时文件 SQLite；入口构造数据 | create invalid order ID → rows after rejected create → persisted rows after reopen | {'exception_family': 'ValueError'}；[]；[] | {'message': 'order_id is required'} / ValueError；[]；[] | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| INVALID-INTEGER / nonempty string order ID | 独立临时文件 SQLite；入口构造数据 | create invalid order ID → rows after rejected create → persisted rows after reopen | {'exception_family': 'ValueError'}；[]；[] | {'message': 'order_id is required'} / ValueError；[]；[] | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| MISSING-READ / missing order raises ValueError | 独立临时文件 SQLite；入口构造数据 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| MISSING-CANCEL / missing order raises ValueError | 独立临时文件 SQLite；入口构造数据 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| MISSING-SUBMIT / missing order raises ValueError | 独立临时文件 SQLite；入口构造数据 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| MISSING-SET_STATUS / missing order raises ValueError | 独立临时文件 SQLite；入口构造数据 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'message': 'order not found'} / ValueError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| MISSING-MARK_PAID / missing order raises ValueError | 独立临时文件 SQLite；入口构造数据 | operation on missing order → existing order remains persisted → missing order remains absent | {'exception_family': 'ValueError'}；pending；{'exception_family': 'ValueError'} | {'returned': None}；pending；{'message': 'order not found'} / ValueError | FAIL | [JSON](evidence/initial-integration.json) / 89df9f6 | [ORDER-002](../../issues/ORDER-002.md) |
| CLOSED-CREATE / database exceptions propagate | 独立临时文件 SQLite；入口构造数据 | write on closed connection → original persisted status → failed create remains absent | {'exception_family': 'Error'}；pending；{'exception_family': 'ValueError'} | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending；{'message': 'order not found'} / ValueError | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| CLOSED-CANCEL / database exceptions propagate | 独立临时文件 SQLite；入口构造数据 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| CLOSED-SUBMIT / database exceptions propagate | 独立临时文件 SQLite；入口构造数据 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| CLOSED-SET_STATUS / database exceptions propagate | 独立临时文件 SQLite；入口构造数据 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| CLOSED-MARK_PAID / database exceptions propagate | 独立临时文件 SQLite；入口构造数据 | write on closed connection → original persisted status | {'exception_family': 'Error'}；pending | {'message': 'Cannot operate on a closed database.'} / ProgrammingError；pending | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| INT-04 / multiple order isolation | 独立临时文件 SQLite；入口构造数据 | second order submit result → independent states before close → independent states after reopen | True；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'}；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'} | True；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'}；{'ORDER-1': 'cancelled', 'ORDER-2': 'submitted', 'ORDER-3': 'paid'} | PASS | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |
| AC-3 / Spec AC-3: authorized real external service receipt | 独立临时文件 SQLite；入口构造数据 | 只读 runtime.json；未调用网络 | 获授权真实外部服务回执 | 端点缺失、无调用授权；本轮禁网。恢复须端点、权限、网络许可及真实调用路径获 Main 对齐 | BLOCKED | [JSON](evidence/initial-integration.json) / 89df9f6 | 无 |

## 7. 缺陷与影响

| Issue | 本批次场景 | 影响 |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2 | 取消状态被提交覆盖，返回 true 且 persisted submitted，违反取消保护 |
| [ORDER-002](../../issues/ORDER-002.md) | MISSING-MARK_PAID | 缺失订单静默返回 None，不满足 ValueError 契约 |

Issue 状态、后续归因、修复 Task 和历次复验沿原 Issue 维护；本阶段不诊断替代实现方案或关闭缺陷。

## 8. 结论、人工待验与 Gate

- **Test Gate：FAIL**，适用上述初始版本和隔离本地环境的完整订单范围。两项产品缺陷且 AC-3 阻塞，不能判 PASS；执行已完成全部可执行场景取证。
- 人工验收：无 UI 或主观判断要求，无必需人工反馈待取。AC-3 属于真实外部组件和授权缺口，不是本地自动结果可替代的人工勾选。
- 恢复：Main 调度 Bugfix，返回修复实际源码哈希及局部证据；原测试 Agent 在修复后快照重跑全部 20 项（两缺陷均触及公开路径，当前范围足够小，完整复跑确保原场景及相互作用）。本次失败输出与报告永久保留。AC-3 独立保持 BLOCKED，直至授权端点、调用权限、网络许可和真实执行路径齐备，经 Main 对齐后另取真实回执。
