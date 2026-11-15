# Plan — CHK-001 付款适配层架构整改

## 1. Goal and Basis

- **目标与范围**：在 `src/ui.py` 通过既有 `order_service.set_status` 写入 paid，保持公开函数签名、None 返回、持久化、异常传播及调用者连接管理。仅修改该文件、`tests/test_order.py` 的直接付款测试和本 Plan；不修改服务、取消、提交、checks、运行配置、规则或共享工作流，不新增模块或状态限制。
- **上游工单**：[Review CHK-001 及架构复核、行为保持方案](payment-review.md#chk-001-付款状态写入职责)，已确认需求与方案沿用调度方授权。依据 [Blueprint ARC-1](../../blueprint.md#架构边界)、[接口契约](../../contracts/order.md)、[CR-001](../../code-review-rules.md) 及 [Spec](../../../specs/order/spec.md)。AC-1 保持；AC-2 为既有缺陷，交 Main，禁止将其失败当作保持目标或在本轮修复。
- **当前实现**：基线 HEAD `7a90ae57739b7ae93b554e0bd409259ab949a51e`；ui 先 read_status 再直接 UPDATE/commit；现有 set_status 已执行同样校验、写入和提交。基线局部测试结果沿用 Review 的 2 tests / OK。接单时 Review 等阶段文档已为未跟踪文件，归调度方维护。

## 2. Task List

### T001: 经既有服务写入付款状态并验证公开行为

- **依据**：CHK-001 的架构与行为保持判据，引用上游 Review 的同一验收方案。
- **改动范围**：`src/ui.py`、`tests/test_order.py` 直接付款测试、本 Plan（新建）。保留既有正常提交单测。
- **实施方案**：ui 引入并调用既有 set_status(connection, order_id, "paid")，不显式返回服务结果；测试使用独立临时文件 SQLite 验证公开入口。仅 commit 异常使用包装真实连接的 mock，SQL、读取、其他数据库失败均使用真实 SQLite。无需服务变更或新增模块。
- **依赖**：无。
- **完成条件与局部检查**：公开 mark_paid 正常返回 None，调用者连接可用，关闭重开仍 paid；现有状态不新增限制；missing 抛 ValueError 且连接仍可用；真实 query_only 写入失败传播且状态保持；commit 失败传播且调用者可决定 rollback/close。运行 `python -B -m unittest discover -s tests -v`，既有正常提交测试保持通过。局部结果供原架构审查者源码复核及调度方行为保持验收，不代替正式复核或全产品集成。
- **状态**：Complete。
- **结果与证据**：2026-11-14，基于 HEAD `7a90ae57739b7ae93b554e0bd409259ab949a51e` 的未提交工作区；Python 3.12.3、SQLite 3.45.1，独立临时文件库，无外部端点。ui 已仅调用既有 set_status，服务源码未改。`python -B -m unittest discover -s tests -v`：6 tests，全部 OK，耗时 0.152s，退出 0。局部测试逐项结果如下：

  | 实际测试 | 对应判据与观察结果 | 结果 |
  | --- | --- | --- |
  | test_mark_paid_is_persisted | 返回 None；原连接仍可读取 paid；调用者关闭后重开文件库读取 paid | PASS |
  | test_mark_paid_keeps_existing_status_inputs | pending、submitted、cancelled、paid 均可经公开入口标记 paid，无新增状态限制 | PASS |
  | test_mark_paid_missing_order_raises | missing 抛 ValueError: order not found；连接可继续读取原订单 pending | PASS |
  | test_mark_paid_database_write_failure_propagates | 真实 SQLite PRAGMA query_only=ON 拒绝写入，OperationalError 传播，原状态 pending | PASS |
  | test_mark_paid_commit_failure_propagates | 仅替代 commit 抛出指定 OperationalError；异常原样传播，真实 SQL 留在调用者事务，另一个连接仍见 pending；调用者 rollback 后 pending | PASS |
  | test_normal_submit | 原有正常提交返回 true，状态 submitted | PASS |

  代码 SHA-256：`src/ui.py` 为 `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`；`tests/test_order.py` 为 `0805f5dd55bd83f6464ce9c4d0a09189fb7209f6173004e370779c969bb71b7c`；未改服务 `src/order_service.py` 为 `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`。局部执行无失败；未执行 AC-2/AC-3 集成验收，沿用上游已记录的缺陷及授权缺口。

## 3. Delivery Checks

- **目标覆盖与完成**：T001 已完成；CHK-001 所需实现与局部行为覆盖齐备，正式架构复核与行为保持验收待调度方执行。
- **阻塞与下一步**：无。Plan 已读回并与上游判据及代码 diff 核对：无需求、架构或授权扩展，证据仅描述本轮局部自验；`git diff --check` 退出 0；`git diff -- src/order_service.py` 无输出。`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/payment-plan.md` 检查 1 个 Markdown，0 errors、0 warnings，退出 0（仅机械检查）。
- **待验与后续**：原 payment_architect 按 Review CHK-001 执行真实源码架构复核；调度方按同项方案验收公开行为；Main 后续组织全产品集成及处理范围外 AC-2、AC-3。本轮不访问网络。
