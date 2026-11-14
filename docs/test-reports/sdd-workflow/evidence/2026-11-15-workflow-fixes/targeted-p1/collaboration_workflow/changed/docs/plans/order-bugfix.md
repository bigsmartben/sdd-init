# Plan — 订单缺陷修复及局部自验

两处修复已完成，2 项单测、AC-1/2 和 O-07～O-20 共 14 项局部回归均通过；Bugfix 定向复验已通过，原测试 Agent [独立集成复验](../test-reports/order/retest.md) 已完成，22 个本地场景通过，AC-3 保持外部阻塞。实现与证据见 T001。

## 1. Goal and Basis

- **目标与授权**：恢复取消后提交保护及付款缺失对象异常；调用者 `/root/order_bugfix` 已交接 Main 确认的实施授权。仅修改 `src/order_service.py`、`src/ui.py`，维护本 Plan 和 `bugfix-local-*` 局部证据。隔离本地 Python / 文件 SQLite；不改测试资产，不执行网络、部署或 Git 提交。
- **上游依据**：[ORDER-001](../issues/ORDER-001.md)、[ORDER-002](../issues/ORDER-002.md) 的验收计划与方案，[Spec](../../specs/order/spec.md) AC-1/2，[订单契约](../contracts/order.md) 的存在性、持久化与异常语义，[Blueprint](../blueprint.md) ARC-1/2/3/4。
- **归因与证据**：`submit_order` 读取后无条件调用 `set_status`，覆盖 cancelled；`ui.mark_paid` 直接 UPDATE/commit，绕过服务存在性检查。[首轮 CLI](../test-reports/order/evidence/initial-acceptance.json) AC-2 为 true/submitted；[首轮回归](../test-reports/order/evidence/initial-regression.json) O-14 exception=null；[首轮环境与源码指纹](../test-reports/order/evidence/initial-runtime-after.json) 标识修复前版本。当前源代码核实支持上述归因，无需新架构决定。

## 2. Task List

### T001: 恢复取消保护和服务付款入口并验证

- **Basis**：原 ORDER-001/002 及以上归因证据；原 Issue 的验收计划与方案。
- **Change scope**：`src/order_service.py`、`src/ui.py`；新建本 Plan 和局部证据。
- **Implementation**：`submit_order` 读到 cancelled 立即返回 False，不执行状态写入或 commit；其他状态沿用现有提交行为。`ui.mark_paid` 调用现有 `order_service.set_status(connection, order_id, "paid")`，保留公开签名、隐式 None 返回、付款持久化和异常向上传播。仅恢复已确认服务唯一写入口。
- **Dependencies**：无。
- **Completion criteria and local verification**：现有 `python -B -m unittest discover -s tests -v` 通过；CLI 分别运行 `python -B checks/acceptance.py --scenario AC-1` 和 `--scenario AC-2`，结果为 true/submitted、false/cancelled；复用 `python -B tests/order_regression.py --case O-07 O-08 O-09 O-10 O-11 O-12 O-13 O-14 O-15 O-16 O-17 O-18 O-19 O-20` 全部 PASS，覆盖文件 SQLite 付款关闭重开、缺失对象无副作用、真实 query_only 和 commit 读锁异常。记录命令 stdout/stderr/exit、环境、HEAD 与产品源 SHA256。文档 CLI 检查本 Plan，并语义读回。
- **Status**：Complete。
- **Results and evidence**：实际修复为 HEAD `fc366da8aff900abc000129676514d994ca5c671` 上未提交工作树，Python 3.12.3 / SQLite 3.45.1；[实际版本及全部产品 SHA256](../test-reports/order/evidence/bugfix-local-version.json)。`src/order_service.py` SHA256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，`src/ui.py` 为 `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`。测试资产执行前后指纹一致。
- **局部覆盖**：[单测](../test-reports/order/evidence/bugfix-local-unittest.json) 2/2 PASS；[AC-1](../test-reports/order/evidence/bugfix-local-ac1.json) true/submitted PASS，[AC-2](../test-reports/order/evidence/bugfix-local-ac2.json) false/cancelled PASS；[原回归资产定向执行](../test-reports/order/evidence/bugfix-local-regression.json) O-07～O-20 14/14 PASS，所有命令 exit=0，完整 stdout/stderr 保存在证据。O-14 为 ValueError 且原有行和重开后行保持 pending；O-15～19 真实 query_only 导致 OperationalError；O-20 真实 commit 读锁抛 OperationalError，调用方 rollback 后重开 pending。首轮失败证据保留，未发现归因反证。

## 3. Delivery Checks

- **Goal coverage and completion**：T001 已完成两项原缺陷恢复和约定局部检查，保持付款 paid 持久化、缺失对象及数据库异常传播。文档机械检查入口为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . --format json docs/plans/order-bugfix.md`，[检查回执](../test-reports/order/evidence/bugfix-local-doc-check.json)。语义读回核对了原 Issue、归因证据、实现范围、完成判据、实际版本、局部覆盖和待验边界；上游已回传[独立集成复验](../test-reports/order/retest.md)，补充原故障与完整本地回归通过证据。
- **Blockers and next actions**：当前无实施阻塞。
- **Coverage gaps and applicable follow-up**：Bugfix Skill 已完成原编号定向复验，见 [定向报告](../test-reports/order/bugfix.md)；原测试 Agent 已在同一实际快照按原 Issue 验收计划和 [Quickstart](../../specs/order/quickstart.md) 完成[独立全产品集成复验](../test-reports/order/retest.md)：23 场景 22 PASS、0 FAIL、1 BLOCKED，仅 AC-3；另 2 单测 PASS。执行前后源码和验证资产指纹一致。AC-3 因 [环境条件](../../runtime.json) 无外部端点和授权保持阻塞，本轮不执行。架构审查按 Main 单独安排。
