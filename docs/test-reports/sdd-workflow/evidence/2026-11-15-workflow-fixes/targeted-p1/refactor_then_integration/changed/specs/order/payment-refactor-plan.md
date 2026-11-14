# Plan — 订单付款适配职责对齐

## 1. Goal and Basis

- **Goal and scope** — CHK-001：公开 `ui.mark_paid(connection, order_id)` 将付款状态写入委派给既有服务，保持 None 返回、文件 SQLite paid 持久化、缺失订单及数据库错误传播。仅修改 `src/ui.py`、`tests/test_order.py` 直接付款测试和本 Plan；不修改取消提交行为。
- **Upstream work** — [CHK-001 原工单及验收计划与方案](../../docs/test-reports/order/payment-alignment-review.md#chk-001-付款写入职责与实际服务调用链)、[Blueprint ARC-1～4](../../docs/blueprint.md#架构边界)、[订单契约](../../docs/contracts/order.md)。目标和方案授权由实际调用者 `/root/refactor` 交接，沿用已有确认。
- **Current implementation** — `src/ui.py` 现已委派 `order_service.set_status`，由服务完成存在性检查、UPDATE 和 commit。原 UI 直接写入的缺口与新增测试的失败/复验证据见 T001。

## 2. Task List

### T001: 付款适配委派与局部保持检查

- **Basis** — [CHK-001](../../docs/test-reports/order/payment-alignment-review.md#chk-001-付款写入职责与实际服务调用链)；ARC-1 服务唯一写入入口，ARC-2 文件持久化和异常，ARC-3 正式模块不依赖测试，ARC-4 无网络。
- **Change scope** — `src/ui.py`；`tests/test_order.py` 直接付款测试；本 Plan 为新增唯一实施记录。
- **Implementation** — UI 导入服务模块并调用 `order_service.set_status(connection, order_id, "paid")`，不显式返回服务结果，保持 None。测试使用 mock wraps 调用真实服务并断言参数，同时关闭重开文件 SQLite 核验 paid。覆盖 pending/submitted/cancelled/paid 初态、缺失订单不插入、只读写入失败时仍 pending，以及关闭连接错误传播。先补测试确认委派缺口，再实施重跑。无需新依赖或配置。
- **Dependencies** — None。
- **Completion criteria and local verification** — `python -B -m unittest discover -s tests -v` 全部通过；付款测试覆盖 CHK-001 局部行为和实际服务调用。读回 UI 确认无 SQL/commit。按修改及直接引用范围机械检查 Plan 和 Review；架构复核及独立行为保持验收结果已回收，见 Delivery Checks。
- **Status** — Complete（实施与局部自验终点）。
- **Results and evidence** — 2026-11-15，Python 3.12.3 / SQLite 3.45.1；HEAD `663483bf7d8f869aad8d57a5de920e790e5c8dbc` 上未提交的授权文件改动。原 UI + 新付款测试执行 `python -B -m unittest discover -s tests -v`，退出 1；共 5 个测试方法，付款持久化方法的 4 个初态子例均失败：`Expected 'set_status' to be called once. Called 0 times.`；其余 4 个方法通过。替换 UI 委派后同命令退出 0，`Ran 5 tests in 0.110s / OK`。5 个方法包含 4 个付款方法（持久化方法含 4 个初态子例，共 7 个付款场景）及原正常提交方法。每种初态均用独立临时文件 SQLite，mock wraps 验证真实服务调用与参数 `(connection, "ORDER-PAID", "paid")`，返回 None，关闭重开仍 paid；缺失订单未插入且现存订单仍 pending；只读库抛 OperationalError，当前连接及关闭重开后均 pending；关闭连接抛 ProgrammingError。所有数据在测试后清理，无网络。`git diff --check` 退出 0。

源码 SHA-256（便于后续复核版本一致性）：

| 文件 | SHA-256 |
| --- | --- |
| `src/ui.py` | `1b43c863d5f9dd8100d3c5a9f0dade6cde3e020502d780bf933cb489a122c63c` |
| `src/order_service.py`（未改） | `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` |
| `src/storage.py`（未改） | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| `tests/test_order.py` | `dae0643b33eb9c9de92603036b73893ba267f124e91c902889caf07bbb7e8a7e` |

## 3. Delivery Checks

- **Goal coverage and completion** — T001 完成。实际改动仅 UI 委派、直接付款测试及本 Plan；读回 UI 已无状态 SQL/commit，服务/存储和正常提交测试未改。局部证据覆盖 CHK-001 委派参数、None、文件持久化及错误传播；同一交付哈希的独立架构复核和公开入口行为保持验收均已回收 PASS，CHK-001 为 Closed after recheck，权威结果见 [Review](../../docs/test-reports/order/payment-alignment-review.md#chk-001-付款写入职责与实际服务调用链)。
- **Blockers and next actions** — 无阻塞。写后语义核对：依据和追溯链接明确，唯一 Task 编号及固定锚点保留，局部范围未扩大。机械检查命令：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/payment-refactor-plan.md docs/test-reports/order/payment-alignment-review.md`，退出 0，2 个 Markdown 文件，0 errors / 0 warnings；只作机械检查，不替代独立复核。
- **Coverage gaps and applicable follow-up** — 本付款整改无剩余待验项；[Review Gate 为 PASS](../../docs/test-reports/order/payment-alignment-review.md#3-gate-and-remaining-work)。全功能集成回归、取消提交和外部服务证据不属本局部批次，按 Review 跨阶段事项由 Main 接续，不据本 Plan 认定全产品 Test Gate。
