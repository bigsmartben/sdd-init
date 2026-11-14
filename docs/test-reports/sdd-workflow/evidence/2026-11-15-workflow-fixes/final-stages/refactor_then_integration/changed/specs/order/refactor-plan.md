# Plan — 付款适配职责对齐

本轮已完成付款适配及直接相关局部测试，4 项付款用例 PASS；实施结果与证据维护于下列唯一 Task。[Review](../../docs/test-reports/order/mark-paid-review.md#3-gate-与集成准备) 已记录原架构角色对 CHK-001～004 复核 PASS、技能独立付款行为保持 4/4 PASS；MAP-001～003 仍为 UNVERIFIED，最终 Review Gate 为 UNVERIFIED，不阻止具备条件的本地集成场景执行。

## 1. 目标与依据

- **目标与范围**：`ui.mark_paid` 使用现有 `order_service.set_status`，保留 paid、公开返回 None、文件持久化、缺失 ValueError 和数据库异常传播。只修改 `src/ui.py`、`tests/test_order.py` 与本 Plan；不修取消提交，不执行全产品集成，不写 Git、不访问外部服务。
- **上游工单**：[Review CHK-001 与 CHK-002、验收计划](../../docs/test-reports/order/mark-paid-review.md#chk-001付款状态写入职责)。适用依据为 [Blueprint ARC-1～4](../../docs/blueprint.md#架构边界) 与[订单契约](../../docs/contracts/order.md)。已有确认和实施授权由实际调用者 `/root/refactor` 交接。
- **当前实现**：基线 HEAD `76e8f410e7adeb3cb702dc1f89bb5129bf381c60`；UI 读取后直接 UPDATE/commit，服务的 `set_status` 已提供同样的存在性检查、写入和 commit。测试已有付款持久化用例，但未关闭原连接重开、未断言 None，也未覆盖异常。

## 2. Task 清单

### T001：付款适配职责对齐

- **依据**：原 Review CHK-001 整改目标及 CHK-002 保持判据，沿用上游验收计划。
- **改动范围**：`src/ui.py`、`tests/test_order.py`、新建本 Plan。
- **实施方案**：UI 直接调用已有 `set_status(connection, order_id, "paid")`，保留隐式 None 返回；不改变服务和存储。付款局部测试使用独立临时文件库，成功后关闭原连接再重开；缺失场景断言 ValueError；真实只读 SQLite 连接验证写入异常；测试侧代理只转发 execute 并在 commit 抛 OperationalError，验证异常传播及新连接仍读到 pending。正式代码不增加测试开关。已读取服务实现，确认现有入口满足所需时序，无影响方案的未知项。
- **依赖**：无前置 Task；实施授权及验收方案已由调用者提供。
- **完成条件与局部验证**：上述四个公开入口场景通过，paid/None/持久化及异常可观察行为保持；UI 不再直接执行 SQL 或 commit。唯一测试入口为 `python -B -m unittest discover -s tests -p test_order.py -k mark_paid -v`；只执行付款相关局部测试。文档检查仅本 Plan。
- **状态**：Complete。
- **结果与证据**：2026-11-15，本地 Python 3.12.3 / SQLite 3.45.1，基线 HEAD 加本工作树改动；执行上述唯一付款入口，退出码 0，`Ran 4 tests in 0.059s / OK`。`test_mark_paid_is_persisted` 覆盖 None 与关闭重开 paid；`test_mark_paid_missing_order` 覆盖 ValueError 及原订单 pending；`test_mark_paid_readonly_database` 覆盖真实只读库 OperationalError 及原状态保持；`test_mark_paid_commit_failure` 覆盖 commit OperationalError 向上传播及新连接未读到未提交的 paid。UI diff 仅改服务导入和调用，服务实现未改。原初审基线和已知范围外 AC-2 失败见 Review，本文未重跑该场景。

本次局部验证代码快照 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| src/ui.py | `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8` |
| src/order_service.py（未改） | `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` |
| tests/test_order.py | `10d712d2a6db76b9ca747fe8a3d4b80717a261d1eae6f6b6f76945e38b803187` |

## 3. 交付检查

- **目标覆盖与完成**：T001 实施及付款局部自验完成，覆盖 CHK-001 整改目标和 CHK-002 的 paid/None/持久化/异常行为判据；不代替阶段验收或关闭 Review。
- **写后核对**：正文与上游工单、代码 diff 和实际测试输出核对一致，Task 编号与引用保持唯一；机械检查入口 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/refactor-plan.md`，仅检查本 Plan。首检发现 DOC008（Review 章节锚点漏掉标题数字），已修复；复查 0 errors / 0 warnings，退出码 0。机械通过不替代语义与阶段验收。
- **阻塞与接续**：无。
- **后续项**：原架构角色对 CHK-001～004 的复核及技能 Agent 对 CHK-001/002 的付款行为保持验收均已 PASS，详见 [Review 原检查项结果](../../docs/test-reports/order/mark-paid-review.md#2-检查项工单与验收方案)。MAP-001～003 仍为 UNVERIFIED；全产品集成、规则映射维护时机与范围外取消提交缺陷由 Main 安排，本 Plan 不替代其阶段结论。
