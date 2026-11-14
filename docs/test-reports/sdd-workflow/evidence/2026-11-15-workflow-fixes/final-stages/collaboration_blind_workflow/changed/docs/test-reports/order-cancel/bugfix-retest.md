# BUG-001 定向复验

## 结果与实际对象

2026-11-14 UTC，`/root/bugfix` 独立于实施者 `/root/bugfix/coder` 执行定向复验，BUG-001 全部关单判据通过。此结论仅覆盖 [原 Issue](../../issues/BUG-001.md)，不代替集成 Test Gate 或架构 Review Gate。

实际修复文件 `src/order_service.py` SHA256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；复验前后所有 src 哈希一致，见 [独立实测原始证据](independent-retest.json)。Python 3.12.3、SQLite 3.45.1、本地临时文件数据库；无外部服务调用。完整候选依据与测试哈希见 [候选环境](candidate-environment.json)。

## 原故障、归因与实施

[修复前 AC-2](baseline-ac2.json) 返回 true 且重开文件为 submitted；[SQL 轨迹](baseline-causal-trace.json) 证明取消先成功持久化，submit 随后无条件 UPDATE/COMMIT。候选仅对 cancelled 增加返回 false 分支，其余路径保持原样。[实施 Plan](../../plans/order-cancel-fix.md) 记录 Task、最小修复和局部验证；[修复前新增回归测试](regression-before-fix.json) 确认仅取消判据失败。修复后 [6 项单测](candidate-tests.json) 与 [AC-1](candidate-ac1.json)、[AC-2](candidate-ac2.json) 均通过。

## 独立定向复验

执行者直接调用正式模块，用每轮独立临时文件 SQLite 重建数据；前后关闭并重开连接。公开原场景与原夹具完全一致，不是模拟回执。以下结果及 source 哈希均在独立原始证据中。

| 判据 | 操作与观察 | 结果 |
| --- | --- | --- |
| 取消后提交 | create → cancel → submit；提交 SQL 仅 SELECT、total_changes 增量 0；重开文件 cancelled，返回 false | PASS |
| 正常提交 | `python -B checks/acceptance.py --scenario AC-1`；true、重开 submitted，exit 0 | PASS |
| 原缺陷入口 | `python -B checks/acceptance.py --scenario AC-2`；false、重开 cancelled，exit 0 | PASS |
| paid 保持 | create → ui.mark_paid → 关闭重开；paid | PASS |
| 不存在订单 | submit(MISSING) 抛 ValueError | PASS |
| 真实 commit 失败 | 新建 pending；第二连接 BEGIN/SELECT 保持读锁，写连接 busy_timeout=0；submit 的 UPDATE 可见于写连接，但 COMMIT 抛 OperationalError，读连接仍 pending；调用者 rollback 后重开 pending | PASS |

可复跑局部资产：`python -B -m unittest discover -s tests -v`（含取消不写、重开及真实 commit 失败检查），并分别执行上述 AC-1／AC-2 命令。调用者仍负责关闭连接及异常后事务处理；本修复没有改变失败事务语义。

## 状态、缺口与接续

原场景恢复、必要定向回归通过，无该修复引入的未解决问题；需求明确无需人工视觉判断，原 Issue 可按授权关闭。集成测试、架构检查由 Main 独立调度。AC-3 缺少端点和外部授权，不能以本地结果替代；ui 既有直接 SQL 偏差不在本缺陷修复范围内。恢复相应项须由 Main 取得所需授权或决定后另行接续。

文档机械检查覆盖本报告与原 Issue；结果保存于 [校验输出](bugfix-doc-check.json)。语义核对：原缺陷范围、已确认行为、源哈希、SQL 实测和状态依据一致，未把局部通过写成全产品 Gate 通过。
