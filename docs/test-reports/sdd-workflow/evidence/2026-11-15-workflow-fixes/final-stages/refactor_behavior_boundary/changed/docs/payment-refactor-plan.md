# Plan — 付款状态写入职责对齐

T001 已完成：付款入口调用已有服务，5 项局部测试全部通过。实施交付时待验的 CHK-001 现已完成原审查者架构复核 PASS 和独立行为保持验收 3/3 PASS，检查项已关闭，见[报告 E-V1／E-A1](test-reports/payment/pre-release-review.md)。整体 Review Gate 仍为 UNVERIFIED，CHK-002–004 规则映射待查。

## 1. Goal and Basis

- **Goal and scope** — 执行已授权 CHK-001，将 `ui.mark_paid` 接到已有服务入口；只修改 `src/ui.py`、`tests/test_order.py` 的付款局部测试及本 Plan。保持公开签名、返回 None、付款持久化 paid、缺失订单 ValueError 和数据库异常传播；不修改服务、storage、订单提交行为，不增加网络或重试。
- **Upstream work** — [原检查项与验收计划、方案](test-reports/payment/pre-release-review.md) 的 CHK-001；[订单函数契约](contracts/order.md)；[Blueprint ARC-1–4](blueprint.md#架构边界)。需求、方案与实施授权沿用调度方已确认输入，无新增决定。
- **Current implementation** — 初始提交 `b5c93159b3ee3d78ded2a26147a1f7b2a3acb19e`。`ui.mark_paid` 先调用 read_status，然后自行 UPDATE/commit；服务已有 set_status 可复用。上游 E-B1/E-B2 已记录付款成功、缺失和真实只读错误的行为基线。

## 2. Task List

### T001: 将付款适配接到服务并验证直接契约

- **Basis** — CHK-001 及上述契约、ARC-1–4；调度方已组织原审查者架构复核及独立行为保持验收，结果见报告 E-V1／E-A1。
- **Change scope** — `src/ui.py`；`tests/test_order.py` 内付款测试；新增本 Plan。
- **Implementation** — 导入现有 set_status，并以 `(connection, order_id, "paid")` 调用；保留函数签名及隐式 None 返回。付款局部测试使用临时文件 SQLite，验证关闭重开持久化、缺失无新增，以及真实只读、关闭连接读取错误和事务锁导致的 commit 错误。锁测试设置 busy_timeout=0，持有第二连接读事务阻止写事务 commit，完成后回滚写事务及读事务，从第二连接新读确认 pending；finally 再回滚写事务并释放第二连接；不以 mock 镜像调用实现。
- **Dependencies** — 无；同一文件的修改串行执行。
- **Completion criteria and local verification** — UI 不再自行写 SQL/commit；`python -B -m unittest discover -s tests -p test_order.py -k mark_paid -v` 通过。局部覆盖返回值、持久化、缺失订单与数据库异常传播；不运行订单提交、全套测试或网络。代码职责的正式符合性与独立行为验收在实施回执时待验，现已分别由 E-V1／E-A1 完成。
- **Status** — Complete。
- **Results and evidence** — 2026-11-15，Python 3.12.3 / SQLite 3.45.1；上述付款局部命令 exit 0，5/5 PASS（初次 0.054s；补强事务清理和第二连接新读后复验 0.061s）。测试分别验证关闭重开 paid 且返回 None、缺失抛 ValueError 且记录未变、已关闭连接抛 ProgrammingError、query_only 写入抛 OperationalError 且仍 pending、第二连接读事务使 commit 抛 OperationalError 并由测试回滚写、读事务，从第二连接重新读取 pending，finally 保证回滚及连接释放。无失败或阻塞。初始提交加本轮工作区 diff 为实际候选，不创建提交；`src/ui.py` SHA-256 为 `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`，`tests/test_order.py` 为 `af4d119a062b59a5a05761df84ff01ebf3983efc774a03858f1f1f4256c8226b`。与上游付款基线 1/1 PASS 对应，保留原成功结果并补充错误边界。

## 3. Delivery Checks

- **Goal coverage and completion** — T001 完成。实际产品改动仅 UI 导入和一次服务调用，签名未变；服务、storage 和提交测试未改。付款测试扩展到五项，局部结果支持契约保持；[报告 E-V1／E-A1](test-reports/payment/pre-release-review.md) 已固化同一候选的原审查者架构复核 PASS 和技能 Agent 公开付款行为保持验收 3/3 PASS，CHK-001 已关闭。
- **Blockers and next actions** — CHK-001 无未完成项。实施回执时已将待复核、待验收事项交调度方，现已完成；本次仅同步 Plan 状态，无代码测试变更或重跑。Plan 写后核对确认 Task、上游引用、版本和证据一致，未引入新判据或决定。
- **Coverage gaps and applicable follow-up** — [原验收计划与方案及当前 Gate](test-reports/payment/pre-release-review.md) 的 CHK-001 验收已完成；CHK-002–004 适用规则映射仍待查，整体 Review Gate 为 UNVERIFIED，完整门禁未关闭，后续由 Main 协调规则维护决定及相应复核。订单提交、AC-2 历史偏差、外部服务及全产品 Test Gate 不属于本 Task；本 Plan 的完成不代表全产品验收或发布通过。
