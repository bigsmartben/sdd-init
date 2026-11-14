# Test Report — 订单缺陷归因、修复与定向复验

## 1. 目标、执行者与边界

2026-11-15，Main `/root` 调度 Bugfix Agent `/root/order_bugfix`；实施与局部自验委派专业角色 `/root/order_bugfix/coder`。依据 [原工单](../../../TASK.txt)、[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[T001 与验收计划](../../../specs/order/plan.md)、原 [ORDER-001](../../issues/ORDER-001.md) 和 [ORDER-002](../../issues/ORDER-002.md)。Bugfix Agent 独立归因、定向复验，未实施产品改动。

仅本地 Python 和真实临时文件 SQLite；无网络、外部平台、部署或 Git 写操作。范围为取消提交和 missing paid 恢复及直接受影响的持久化、异常、隔离回归。整轮集成、架构复核及 Test Gate 由 Main 另行接续原执行者；AC-3 不纳入本阶段结果。

## 2. 初始复现与因果验证

初始提交 `89df9f629407a6b572c6f65c87fc9768e0f52f5d`，Python 3.12.3 / SQLite 3.45.1；完整初始 src 哈希见 [归因证据](evidence/bugfix-diagnosis.json)。原始集成失败仍见 [初始报告](initial.md)，未覆盖或删去。

| Issue | 候选原因与可区分预测 | 实际观测与结论 |
|---|---|---|
| ORDER-001 | submit 无条件写入；预测读取后发生 UPDATE/commit，非读取/重开失真；若无 UPDATE 或更新前即为非 cancelled，则需重查 | 已 create→cancel 后 submit：true，SQL trace 有两次 SELECT、UPDATE submitted 和 COMMIT，total_changes +1，重开 submitted。直接代码路径丢弃 read_status 结果，验证为状态决策缺失 |
| ORDER-002 | UI 直接 SQL 未检查存在性；预测 missing 执行零行 UPDATE/commit 返回 None，服务同类调用则抛 ValueError；若走服务仍静默则需修订归因 | missing mark_paid 无异常返回 None，trace 为 UPDATE/commit、changes 0。代码绕过现有 set_status 的 read_status 存在性检查，验证为入口绕过；沿现有服务恢复职责和异常 |

## 3. 实施与自验

实施范围、版本及局部结果由同一 [T001](../../../specs/order/plan.md) 记录。`submit_order` 对 cancelled 提前返回 false，非 cancelled 沿用既有路径；`ui.mark_paid` 通过现有 `order_service.set_status` 写入 paid。签名和返回语义保持，未改冻结 checks 或运行配置。

实施者补充必要单测；同一测试修复前 3 处失败见 [red](evidence/bugfix-coder-red.json)，修复后 `python -B -m unittest discover -s tests -v` 8/8 通过见 [green](evidence/bugfix-coder-green.json)。覆盖原失败、缺失入口、无写入/commit、paid 持久化、隔离、非 cancelled 既有路径及真实 SQLite 写入/commit 故障。

修复版本为基础 HEAD 加本地未提交改动；完整 src 哈希见 [独立复验证据](evidence/bugfix-retest.json)。其中 order_service 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，ui 为 `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`。冻结 checks 哈希仍为 `496fa99f09e2c5d0796678ac580ffa49553e155f266a68673b68e58e93e1bc99`。

## 4. 独立定向复验

入口：`python -B docs/test-reports/order/evidence/bugfix-retest.py`。真实临时文件数据库新建 CANCEL、NORMAL、PAID、OTHER，按原公开调用路径运行；关闭连接重开，finally 清理。SQL trace 和 total_changes 用于验证无状态写入/commit；无修改产品或替代数据库。

实际执行 17 项，17 PASS、0 FAIL、0 BLOCKED、0 Not run，退出码 0，实测时间 `2026-11-14T16:45:58Z`（北京时间 2026-11-15）。环境 Python 3.12.3 / SQLite 3.45.1。逐项结果与源码版本见 [复验 JSON](evidence/bugfix-retest.json)，可复跑入口源码见 [复验脚本](evidence/bugfix-retest.py)。

| 覆盖 / 原判据 | 数量 | 实际结果 |
|---|---|---|
| ORDER-001 / AC-2 原 create→cancel→submit | 1 | false、立即 cancelled、changes=0，trace 仅 SELECT，无写入/commit |
| AC-1 pending 提交 | 1 | true、submitted |
| ORDER-002 原公开 missing mark_paid | 1 | ValueError、changes=0，trace 仅 SELECT，无写入/commit |
| 现存 paid、返回 None、多订单隔离 | 1 | paid、OTHER 保持 pending |
| 非 cancelled 既有 submitted/paid 提交路径 | 2 | 仍 true/submitted；仅保留既有语义，未定义新转移规则 |
| missing read/cancel/submit/set_status | 4 | 全部 ValueError |
| 关闭重开全部订单状态 | 1 | cancelled/submitted/paid/pending 分别保持，隔离正确 |
| 关闭连接 create/read/cancel/submit/set_status/mark_paid | 6 | 全部 ProgrammingError 上抛，无静默成功 |

上述为工单范围的定向复验，不运行或替代完整冻结集成批次。临时目录清理成功，未留下运行数据库；无人工视觉或外部反馈判据。

## 5. 结论与接续条件

本阶段不生成整轮 Test Gate。原 Issue 的状态依据实际定向复验证据更新，后续独立整轮复验由 Main 接续。AC-3 仍需有权方提供真实端点和执行权限；不以本地证据替代。架构 CHK-001/005 修复相关复核及 CHK-006 规则映射待查由原架构执行者接续，不擅自修改规则或架构决定。

写后核对：已对照原 Issue、Spec/契约、实际 diff、版本哈希及证据，语义保持且未扩展授权；文档机械检查范围为本报告、Plan 和两个原 Issue，0 errors、0 warnings。机械检查不代替实测或独立整轮结论。
