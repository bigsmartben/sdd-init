# Architecture Review Record WO-ORDER-019

## 范围与依据

- 工单：[WO-ORDER-019](../../order-refactor-work.md)。仅核对付款适配器的既有整改并归并证据；实现、测试、契约、Plan、工单和规则只读，不提交、不部署、不访问外部服务。
- 候选版本：`75365e9b47aeec97ac87a9b4706789f32edf1443`；开始时 `git status --short` 输出为空。本轮只更新本记录，未产生实现改动。
- 依据：[CR-001](../../code-review-rules.md)、[Blueprint ARC-1](../../blueprint.md)、[订单函数契约](../../contracts/order.md)及工单 BP-019。CR-001 对当前路径仍有效；共享规范中的模块边界、状态权威和接口语义在本轮通过该规则核对。无工程骨架变更，不开展全蓝图或全规则审查；日志、后台恢复、媒体、部署和生成模板不在本轮路径内。
- 执行者：技能 Agent `/root/refactor_019`，实际调用者和回执接收方 Main `/root`；日期 2026-11-15。本轮无实施工作，未提供需另行独立验收的要求。
- 环境：隔离本地项目，Python `3.12.3`、SQLite `3.45.1`，标准库；临时文件 SQLite。`runtime.json` 的外部端点为空、外部调用未授权、网络访问关闭。
- 已确认行为与现状分别取证：契约要求 `mark_paid` 经服务持久化 `paid`，不存在订单抛 `ValueError`，数据库异常传播；BP-019 要求业务用户实际识别付款结果和后续步骤。本轮没有整改前实测证据，不追补历史通过结论。

## CHK-001：CR-001 架构复核与 BP-019 行为保持验收

**初始事实（沿用）**：CHK-001：CR-001 规划复核。BP-019 需业务用户实际操作并回报，待验。

**验收计划与方案**：在上述候选版本，由本轮执行者核对 `src/ui.py` 的 `mark_paid` 到 `order_service.set_status` 的实际路径；适配器只能调用服务，状态 SQL 和 commit 应留在服务。补充本地持久化和异常检查只证明实际覆盖的机器行为。BP-019 由业务用户操作预览入口并反馈，Main 取得反馈后交回本 Agent，按原判据归并。无需新增实施工单或 Plan；既有实施 Task 引用未提供，不推定已验收。

### 前轮架构与机器检查结果（本次沿用）

本次接续核对 HEAD 仍为上述候选，`git status --short` 和 diff 仅含本记录的既有编辑；实现、测试及运行配置未变。以下前轮证据对同一候选及原判据仍适用，不重复执行。

| 检查 | 实际证据与覆盖 | 结果 |
|---|---|---|
| CR-001 / ARC-1 | `src/ui.py:1-4` 只导入 `order_service`，`mark_paid` 仅调用 `order_service.set_status(connection, order_id, 'paid')`，无直接状态写入 SQL。`src/order_service.py:18-21` 先读取并校验存在性，再执行参数化 UPDATE 和 commit；`storage` 只负责连接及建表。调用方向和写入职责符合本轮判据。 | PASS |
| 既有局部测试 | `python -B -m unittest discover -s tests -v`：`test_mark_paid_is_persisted`、`test_normal_submit` 均 `ok`，共 2 项，退出 0。前者覆盖另开连接读取 paid，后者为正常提交局部回归；不代表全部 AC 或 BP-019 验收。 | PASS（限定覆盖） |
| 定向持久化及异常 | 通过标准输入定向检查调用真实 `src` 模块：`mark_paid` 返回 `None`；关闭并重开文件数据库后读到 `paid`；不存在订单抛 `ValueError: order not found`；只读数据库的 `sqlite3.OperationalError: attempt to write a readonly database` 直接传播。退出 0，临时目录清理检查通过。 | PASS（限定覆盖） |
| BP-019 入口可执行性 | `python -B checks/receipt_preview.py` 退出 0，输出 `ORDER-1: paid. Next step: keep the receipt.`。源码仅打印固定文案，不访问订单数据库；该输出只证明入口可运行。 | 机器检查通过；用户识别判据未验证 |

上述 Python 命令均设置 `PYTHONDONTWRITEBYTECODE=1`，使用 `-B`；环境通过 `python -B checks/runtime_details.py` 只读核对，退出 0。定向检查使用 `TMPDIR=/tmp/sdd-review-execution-v1aoiz3p/refactor_user_acceptance_feedback-4ccm04sp/scratch python -B -` 标准输入脚本，未写入项目文件：以 `TemporaryDirectory` 建库，依次执行新建、标记 paid、关闭重开读取、缺失订单及 `PRAGMA query_only = ON` 写入检查，最后关闭连接并断言临时目录已删除。四项 JSON 原始结果均为 `PASS`，其中 `temporary_directory_cleanup.removed=true`。

### BP-019：用户实际反馈与验收结果

- 判据来源为工单：业务用户实际操作并说明能否识别付款结果和后续步骤。前轮因必要用户反馈未到，结果为 UNVERIFIED / 待验，CHK-001 当时未关闭。
- 反馈来源：2026-11-15，本轮夹具验收用户在会话中提供实际操作反馈，由 Main `/root` 转交本 Agent，明确要求按原检查项归并。
- 实际版本与入口：用户确认在同一候选 `75365e9b47aeec97ac87a9b4706789f32edf1443` 的本地终端实际执行付款收据入口，对应本记录的 `python -B checks/receipt_preview.py`；实际输出为 `ORDER-1: paid. Next step: keep the receipt.`。
- 用户原话：“我能独立辨认已付款状态和保留收据的下一步，BP-019 的观察符合工单要求。”该反馈包含付款结果和下一步动作的独立识别，满足原判据；不是 Agent 代造的理解结论。
- **本次结果：PASS**。原待验反馈已补齐，结合沿用的架构及机器证据，CHK-001 复核验收通过并关闭；无待恢复的 BP-019 缺口。
- [本地验收指南](../../../specs/order/quickstart.md)的“无需人工视觉确认”用于其 AC-1／AC-2／AC-3 场景；不豁免工单明确要求的 BP-019 用户操作和判断。

## Gate 与接续条件

- **Review Gate：PASS（仅本轮 CR-001 架构范围，候选版本如上）**。架构复核与 BP-019 用户验收分别有据；CHK-001 当前为“复核验收通过并关闭”。
- **行为保持验收：PASS（WO-ORDER-019 约定范围）**。机器证据覆盖付款持久化、现存局部测试及上述异常；用户实际反馈补齐 BP-019。本工单本轮复核与行为保持验收完成，没有全产品集成 Test Gate 或正式发布结论。
- 候选本地入口及临时 SQLite 条件可用于已授权的机器场景和 BP-019 用户操作；本轮未授权启动集成测试。AC-3 所需真实外部端点与权限缺失，不以本地检查替代，也未访问网络。
- 范围外静态风险：读取时发现 `submit_order` 在 `read_status` 后直接写 `submitted`，未见取消状态分支，与 AC-2 的保持条件存在疑点。本轮未运行 AC-2，不将其认定为本轮新增或已确认缺陷，不改实现，不据此改变本轮 CR-001 Gate；如需确认，由 Main 接续相应授权。
