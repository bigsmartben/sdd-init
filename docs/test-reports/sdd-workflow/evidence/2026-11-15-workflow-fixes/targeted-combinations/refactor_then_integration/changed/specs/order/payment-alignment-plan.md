# Plan — 付款适配职责对齐

## 1. Goal and Basis

- **Goal and scope** — 仅调整 `src/ui.py` 的付款适配职责并补充 `tests/test_order.py` 的直接局部测试；保留签名、None 返回、paid 持久化、异常传播与调用者连接生命周期。不修改服务、取消后提交、配置或规则。
- **Upstream work** — [付款 Review 工单](../../docs/test-reports/order/payment-alignment-review.md#2-review-checks-and-follow-up) CHK-001～004 及其架构复核与行为保持验收方案；[订单契约](../../docs/contracts/order.md)、[Blueprint](../../docs/blueprint.md#架构边界) ARC-1～4、[Spec](spec.md)。需求与方案已确认，实际调度方 `/root/payment_refactor`。
- **Current implementation** — 基线 HEAD `4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df`。`ui.mark_paid` 自行读取、UPDATE、commit；现有 `order_service.set_status` 已实现相同的读取、UPDATE、commit 和异常传播，无需改动服务。

## 2. Task List

### T001: 付款适配职责对齐与局部自验

- **Basis** — 上述 CHK-001 的整改工单；CHK-002～004 的保持判据。局部自验不代替独立架构复核与技能 Agent 行为保持验收。
- **Change scope** — `src/ui.py`、`tests/test_order.py` 和本 Plan（新建）。
- **Implementation** — UI 通过现有 `order_service.set_status(connection, order_id, "paid")` 委派状态写入，不返回服务结果、不处理异常、不关闭连接。使用真实临时文件 SQLite 验证关闭重开后的持久化、缺失订单和只读数据库失败；用包裹真实连接的测试替身使 commit 抛异常，验证异常原样传播且未发生持久化、连接由调用者继续管理。测试替身仅放 tests。
- **Dependencies** — 无。
- **Completion criteria and local verification** — `python -B -m unittest discover -s tests -v` 通过；直接覆盖正常 None 返回、关闭重开 paid、缺失订单 ValueError、SQLite 写入失败、commit 失败及连接生命周期。UI 源码只调用现有服务。对本 Plan 执行文档 CLI 并人工核对链接、范围和待验项。
- **Status** — Complete（实施与局部自验）。
- **Results and evidence** — 2026-11-15，在基线 HEAD `4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df` 的未提交工作树执行 `python -B -m unittest discover -s tests -v`，退出 0，5/5 PASS。`test_mark_paid_is_persisted` 验证 None 返回、调用者可继续读取并自行关闭连接、重开后 paid；`test_mark_paid_missing_order` 验证 ValueError 与原状态；`test_mark_paid_database_failure_propagates` 用真实只读 SQLite 验证 OperationalError 上抛且状态仍 pending；`test_mark_paid_commit_failure_propagates` 验证相同异常对象上抛、连接未关闭、未提交修改对另一个连接不可见且调用者可 rollback。原正常提交单测继续 PASS。局部证据覆盖 CHK-001～002 的付款行为保持判据，源码改动保持 CHK-003～004 的边界；正式复核与验收仍由上游执行。基线单测 2/2 PASS 和历史 AC-2 偏差见原 Review 第 1 节，不将历史偏差写成保持判据。
- **Actual version** — `src/ui.py` SHA-256 `1b43c863d5f9dd8100d3c5a9f0dade6cde3e020502d780bf933cb489a122c63c`；`tests/test_order.py` SHA-256 `24f31eae7e6ae3f5c15430f9afa1b8d4e045f8c093f9f25f95f3718df7ecc87e`。

## 3. Delivery Checks

- **Goal coverage and completion** — T001 完成，实际代码与测试仅修改授权两文件。`git diff --check` 退出 0。本 Plan 的文档检查命令为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/payment-alignment-plan.md`，退出 0，1 文件、0 errors、0 warnings（仅机械检查）；人工核对依据引用、稳定编号、局部证据与待验边界一致，无正文冲突。
- **Blockers and next actions** — 无实施阻塞。
- **Coverage gaps and applicable follow-up** — 独立审查者按原 Review CHK-001～004 复核；技能 Agent 按原方案执行业务保持验收。集成 AC-1～3 与 Test Gate 属后续阶段，AC-2 已知失败不在本次修复范围，AC-3 外部端点与授权仍缺失。运行入口为项目根目录、本地 Python 3.11+、标准库与可写临时目录；参考[验收指南](quickstart.md)。
