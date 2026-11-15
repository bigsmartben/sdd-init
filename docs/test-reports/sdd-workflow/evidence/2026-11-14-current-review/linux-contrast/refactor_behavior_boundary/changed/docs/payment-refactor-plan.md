# Plan — 付款适配层 CR-001 整改

## 1. Goal and Basis

- **Goal and scope** — 将公开 `ui.mark_paid(connection, order_id)` 的付款状态写入委托给既有 `order_service.set_status`，保持 `None` 返回、paid 持久化、缺失订单 `ValueError`、数据库异常透传及调用者连接所有权。仅修改 `src/ui.py`、`tests/test_order.py` 的付款局部测试和本 Plan；不改服务、新建、取消、提交逻辑，不提交 Git。
- **Upstream work** — 调度方工单 CHK-001 / CR-001；已确认 [Blueprint ARC-1](blueprint.md#架构边界) 明确付款经既有服务写入；适用[订单契约](contracts/order.md)与 [Spec 的付款行为保持要求](../specs/order/spec.md)。架构审查和业务行为保持验收由调度方与独立审查者组织，[CHK-001 验收计划与方案及审查证据](test-reports/payment/2026-11-14-review.md#chk-001-付款写入边界)由技能 Agent 唯一持有。
- **Current implementation** — 基线 HEAD `67323a6acbf00ea121b84c4916dd8b85ccdeb9fd` 中 `src/ui.py:mark_paid` 先调用 `read_status`，随后直接 UPDATE、commit；整改后 UI 只委托既有 `src/order_service.py:set_status`，服务继续承担存在性检查、写入和提交。

## 2. Task List

### T001: 付款适配委派及局部行为保持

- **Basis** — CHK-001 / CR-001 整改工单、上述 ARC-1 和订单契约；不扩大至 AC-2 修复或测试。
- **Change scope** — `src/ui.py`；`tests/test_order.py` 中直接付款局部测试；新建 `docs/payment-refactor-plan.md`。
- **Implementation** — 先补付款行为测试，在未改 UI 时运行基线并记录；已收到技能正式开工允许，将 UI 的直接 SQL、commit 替换为 `set_status(connection, order_id, "paid")`，保留隐式 `None` 返回；运行同一测试并核对范围。复用现有服务，不引入连接关闭、捕获异常或额外状态限制。
- **Dependencies** — 无 Task 依赖；调度方正式开工通知已收到。
- **Completion criteria and local verification** — 公开付款调用覆盖现存 pending、submitted、cancelled、paid 到 paid，返回 None、重复调用、重开文件数据库可见 paid；缺失订单 ValueError 且不新增；SQLite UPDATE 及 commit 失败向上传播且不返回成功；连接保持调用者可用。入口为 `python -B -m unittest discover -s tests -p test_order.py -v`，付款局部测试与原有测试一并执行。独立架构审查者确认 UI → set_status → SQLite 调用链且 UI 无 SQL/commit；技能另从公开入口执行临时文件 SQLite 行为保持验收，本地自验不替代上述两项独立结果。Plan 写后执行文档 CLI 检查及人工语义核对。
- **Status** — Complete（实现、局部自验、独立架构复核及技能行为保持验收均已完成；CHK-001 已关闭）。
- **Results and evidence** — 工作树基于上述 HEAD，无提交，Python 3.12.3 / SQLite 3.45.1。UI 整改前补全付款测试，运行 `python -B -m unittest discover -s tests -p test_order.py -v`：5 tests / 0.082s / OK；整改后同命令：5 tests / 0.081s / OK。两次均为四项付款测试及原有正常提交测试，未新增提交或 AC-2 测试。`git diff --check`：exit 0。
  - 基线 UI SHA256：`1a6052d6ba2fa2fd34999433ac5068231ab79a173aaeb41a17358872fcd691ae`；改后 UI：`54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`。
  - 两次使用相同测试 SHA256：`d64d686323a90b732b9d992700f02cb25c9f44868496e09e342d58bbca33fb81`；服务未改，SHA256：`96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`。
  - 持久化测试以四状态子场景通过公开 mark_paid 调用两次并从另一文件连接读取 paid，同时验证原连接继续可用。缺失订单未新增。UPDATE 失败由真实 SQLite 触发器 RAISE(ABORT) 验证；commit 失败由包装真实连接的 Mock 注入 OperationalError，验证同一异常实例透传、不关闭连接，调用者回滚后原连接和重开连接仍为 pending。commit 故障局部测试为注入验证。
  - 调度方回传的[独立架构复核与技能行为保持验收](test-reports/payment/2026-11-14-review.md#chk-001-付款写入边界)：原审查者 CHK-001 架构复核 PASS；技能从公开入口验证四状态、重复调用、关闭重开、缺失订单、真实 UPDATE 异常及调用者连接保持，均 PASS。技能另使用启用外键的 SQLite、延迟外键子表和 AFTER UPDATE 触发器插入无父键记录，构造真实 commit 失败；`IntegrityError: FOREIGN KEY constraint failed` 透传，原连接 paid 尚未提交、另一连接仍读 pending，调用者 rollback 后 pending 且子表为空，PASS。上述独立证据由调度方持有，本次仅更新 Plan 引用，未重跑测试。
  - 文档校验：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/payment-refactor-plan.md`：1 文件、0 errors、0 warnings。人工核对同一 T001、工单边界、依据及局部验证与独立验收的区别。Plan 更新命令曾因 shell 解释反引号遗漏证据文字，并额外重跑同一测试（5 tests / 0.128s / OK）；已使用直接补丁修复文字，代码未受影响。

## 3. Delivery Checks

- **Goal coverage and completion** — T001 实现与局部自验完成；独立架构复核及技能行为保持验收均 PASS，CHK-001 已关闭。改动限定 UI、付款测试及本 Plan。
- **Blockers and next actions** — T001 无实施或验收阻塞；CHK-002～006 缺少有效项目规则映射，整体 Review Gate 仍 UNVERIFIED，后续恢复交 Main 协调，结果见[阶段 Gate](test-reports/payment/2026-11-14-review.md#3-gate-与集成准备)。
- **Coverage gaps and applicable follow-up** — 本工单无待验判据；整体 Gate 的规则映射缺口不属于 T001 实现失败。运行环境为 Python 标准库、临时文件 SQLite，无网络。外部服务、AC-2 缺陷及集成回归不属于本工单。
