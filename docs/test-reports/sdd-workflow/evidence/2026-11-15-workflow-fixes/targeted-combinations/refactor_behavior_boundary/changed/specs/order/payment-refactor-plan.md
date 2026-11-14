# Plan — 付款状态写入职责整改

## 1. Goal and Basis

- **Goal and scope** — 完成 CHK-001：公开 `ui.mark_paid(connection, order_id)` 经现有 `order_service.set_status` 写入 paid，保持签名、None 返回、文件持久化和异常传播。只修改 `src/ui.py`、`tests/test_order.py` 及本 Plan；不修改服务业务、取消后提交、规则、外部服务或部署，不提交 Git。
- **Upstream work** — [原 Review CHK-001 工单及验收步骤](../../docs/test-reports/payment/pre-release-review.md#chk-001-付款状态写入职责)、[Blueprint ARC-1](../../docs/blueprint.md#架构边界)、[订单函数契约](../../docs/contracts/order.md)、[Spec 付款行为及 AC-1](spec.md)。已获调用者授权实施与局部自验；调用者已组织完成原审查者架构复核及技能独立付款行为验收，结果见原 Review。
- **Current implementation** — `src/ui.py:mark_paid` 调用 `src/order_service.py:set_status`，存在性检查、UPDATE/commit 留在现有服务中。`tests/test_order.py` 的五个测试覆盖原正常提交，以及付款关闭重开持久化、None、缺失订单、写入及 commit 故障传播；修改前事实和结果见原 Review 及 T001 证据。

## 2. Task List

### T001: 付款适配整改及局部自验

- **Basis** — [CHK-001](../../docs/test-reports/payment/pre-release-review.md#chk-001-付款状态写入职责)；ARC-1 要求服务独占状态写入；订单契约要求 paid 持久化、缺失订单 ValueError 和数据库异常传播。保持 Spec 付款行为及正常提交 AC-1；AC-2 原有失败不属于本任务。
- **Change scope** — `src/ui.py`、`tests/test_order.py`；新建 `specs/order/payment-refactor-plan.md`。
- **Implementation** — 将 UI 中的读取、SQL 和 commit 替换为现有 `set_status(connection, order_id, "paid")` 调用，保留隐式 None 返回。保留正常提交测试；付款测试明确断言 None 并关闭原连接后重开文件数据库读取 paid。增加缺失订单、SQLite `query_only` 失败及只拦截 commit 的连接代理故障测试；代理转发真实连接 execute，异常断言取自契约，不替代业务模块。不更改正式服务，无方案未知项。
- **Dependencies** — None。
- **Completion criteria and local verification** — UI 无直接状态 SQL/commit；运行 `python -B -m unittest tests.test_order -v`，上述契约测试及保留的正常提交测试均通过。核对限定文件 diff；对本 Plan 和直接引用它的原 Review 执行文档 CLI 机械校验并人工核对事实。局部测试不替代原审查者架构复核或技能 Agent 的独立行为保持验收。
- **Status** — Complete。
- **Results and evidence** — 实测版本为 HEAD `d6c721fd731eb800b8e405789894fb7bc72cf422` 加本轮限定工作区改动；Python 3.12.3、SQLite 3.45.1、本地标准库，无安装、无网络，每个测试新临时目录文件 SQLite 并清理。修改前 `python -B -m unittest tests.test_order -v`：2 tests，OK，退出 0；修改后同入口：5 tests，OK，退出 0（0.063s）。付款持久化测试断言 None、关闭原连接再重开读取 paid；缺失订单断言 ValueError；query_only 写失败断言 OperationalError 且仍 pending；commit 代理保留真实 execute，断言原 OperationalError 实例向上传播，显式 rollback 后关闭重开仍 pending。现有正常提交测试原样保留，仅覆盖 true 和当前连接读取 submitted，未执行独立 AC-1 验收，不宣称覆盖 AC-1 全部步骤。`git diff --check` 退出 0；限定 diff 仅两个代码／测试文件及本 Plan。代码 SHA-256：`src/ui.py` = `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`；`tests/test_order.py` = `61dc56da1ab302c862515721e16a4fe4a95e019de3b1eebb5e16f05751a63f1c`。原 Review 为其他执行者所有，仅读取、不修改。

## 3. Delivery Checks

- **Goal coverage and completion** — T001 实施及局部自验完成：UI 仅调用 set_status，服务未改；付款契约四项检查及保留的正常提交测试通过。已核对限定 diff、Plan 引用、编号、上游条件与证据，未改变业务判据。
- **Document checks** — `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/payment-refactor-plan.md docs/test-reports/payment/pre-release-review.md`：Checked 2 Markdown files，0 errors、0 warnings，退出 0，仅机械检查；人工核对 Plan 与原工单、实测输出、文件边界及收敛后的验收范围一致。
- **Blockers and next actions** — 无实施阻塞；CHK-005 规则映射缺口不阻塞本工单，交调用者处理。
- **Architecture recheck and behavior acceptance** — 调用者回传：原架构审查者对上述同一 HEAD 加相同代码哈希复核，CHK-001 PASS 可关闭，CHK-002～004 技术 PASS。技能 Agent 独立通过公开付款入口验收关闭重开 paid／None、缺失订单、真实 SQLite 只读写失败及 commit 代理原异常传播，四场景均 PASS；版本及证据归 [原 Review CHK-001](../../docs/test-reports/payment/pre-release-review.md#chk-001-付款状态写入职责)。局部实施自验、架构复核及付款行为保持验收已完成。
- **Coverage gaps and applicable follow-up** — [CHK-005](../../docs/test-reports/payment/pre-release-review.md#chk-005-共享适用条款的项目规则映射) 规则映射仍 UNVERIFIED，整体 Review Gate 为 UNVERIFIED，不宣称全范围通过；后续由 Main 协调用户决定。调用者已收敛本轮范围为付款保持和现有局部测试，不另跑 `checks/acceptance.py --scenario AC-1`，独立 AC-1 验收未执行。已知 AC-2 原有失败沿用原 Review 参考，本轮不复跑、不修、不新增测试锁定该错误；AC-3 缺外部端点及授权，本轮不执行、不判定集成 Gate。复跑局部证据只需 Python 3.11+、标准库 SQLite 和临时目录写权限。
