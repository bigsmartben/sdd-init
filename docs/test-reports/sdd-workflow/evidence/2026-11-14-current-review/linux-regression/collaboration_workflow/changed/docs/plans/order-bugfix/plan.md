# Plan — ORDER-001 / ORDER-002 本地修复

## 1. 目标与依据

修复 [ORDER-001](../../issues/ORDER-001.md) 与 [ORDER-002](../../issues/ORDER-002.md)，沿用各 Issue 的验收方案、[Spec AC-1/AC-2](../../../specs/order/spec.md)和[函数契约](../../contracts/order.md)。保持接口及现存订单付款行为，不新增提交状态策略。付款写入按 [ARC-1](../../blueprint.md#架构边界)委派既有服务入口；关联[原 Review CHK-001 / CR-001](../../test-reports/order/local-review.md#chk-001订单状态写入权威与工程边界)及[CHK-005 异常契约](../../test-reports/order/local-review.md#chk-005契约状态与错误语义)，独立架构复核由调度方接续。

基线实现：`submit_order` 读取后无条件提交；`ui.mark_paid` 直接 UPDATE，无缺失检查。基线及修复工作树 HEAD 均为 `95cfcb31cf183d04b7ba1359a8dfe80d28608b00`，已有[基线集成证据](../../test-reports/order/evidence/baseline-integration.json)。修复尚未提交，以本轮证据的实际源 SHA-256、测试 SHA-256 及限定源码／测试 diff 标识快照。本轮无外部调用。

## 2. Task

### T001: 恢复取消提交与缺失付款契约

- **依据**：原 ORDER-001 / ORDER-002 的验收方案、AC-1/AC-2、函数契约；归因与局部证据写入[本轮证据](../../test-reports/order/evidence/bugfix-local.json)。
- **改动范围**：`src/order_service.py`、`src/ui.py`、`tests/test_order.py`；本 Plan 和局部 JSON 证据。Issue 状态归 Bugfix 调度方；集成、指南、Review 和索引归独立执行者。
- **实施方案**：先补充定向回归并运行，确认两个缺陷；SQLite 逐句 trace 显示取消已经落盘，提交仍执行 UPDATE submitted 与 COMMIT，另一订单不变，排除取消未持久化、读取错误及错误对象过滤。缺失付款执行零行 UPDATE 与 COMMIT，不走存在性检查；其余四入口缺失测试通过，排除共用服务检查故障。实际修复为取消状态直接返回 false；付款委派现有 `set_status(..., "paid")`。该入口已校验存在性且 commit，不需要新增接口或异常转换。未加入 submitted/paid 再提交规则。
- **依赖**：无。
- **完成判据与局部检查**：`TMPDIR="$PWD/.local-tmp" python -B -m unittest discover -s tests -v`；取消提交 false 且无 UPDATE/COMMIT、文件状态保持 cancelled；pending 提交在第二文件连接读取 submitted；三种现存前态付款持久 paid；五个缺失对象入口 ValueError；数据库写异常原样传播、状态保持并可恢复；另一订单未提交事务不被提交。临时目录限定在工作区，执行后已清空。保留修复前失败与修复后结果、源哈希和差异。
- **状态**：Complete。
- **结果与证据**：2026-11-14，Python 3.12.3 / SQLite 3.45.1。修复前 7 测试有 3 失败（取消两场景、缺失 mark_paid），退出 1；修复后 7 测试全部通过，退出 0。证据 `before_fix` / `after_fix` 保留全文、逐项测试名、SQL trace 与归因反证。修复后取消提交只有一次 SELECT、changed_rows=0、返回 false，第二连接仍 cancelled，另一订单 pending；缺失付款只有 SELECT 并抛 ValueError。实际源哈希在运行前后稳定。独立完整集成、原 Issue 定向复验与 CHK-001/CHK-005 架构复核由调度方接续；AC-3 缺少真实端点及授权，不在本轮执行范围。

## 3. 交付检查

- **目标覆盖**：T001 已完成，两个原缺陷及相关本地回归通过；不代替独立集成或 Review。
- **阻塞与接续**：本地实施无阻塞。已先交源哈希与命令结果，供原测试 Agent 独立复验。
- **待验项与入口**：按原 Issue 方案及现有 `checks/integration.py` 接续；AC-3 保留外部环境阻塞。证据使用实际工作树快照，不将 HEAD 等同于未提交修复。
- **文档语义检查**：本 Plan 引用原 Issue、适用 Spec/契约、原 Review 检查项；归因、方案与局部结果各归正确记录，Issue 状态历史留原 Issue。机械检查限定本 Plan，命令为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/plans/order-bugfix/plan.md`；实际结果见本轮 JSON 的 `document_check`。不检查远程链接或全仓文档。
