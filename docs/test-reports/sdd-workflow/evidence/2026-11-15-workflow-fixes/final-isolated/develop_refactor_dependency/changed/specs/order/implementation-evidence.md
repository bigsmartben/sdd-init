# WO-ORDER-017 实施与局部验证证据

本批由 `/root/develop_order017/implement_order017` 于 2026-11-15 执行，回执接收方为 `/root/develop_order017`。依据[原工单](../../docs/order-export-work.md)、[导出设计](../../docs/export-design.md)与[同一 Plan](plan.md)，这是实施者局部自验和可行性调查，不是正式点对点验收或集成 Gate。

## 实际版本与环境

HEAD 为 `cd451ab5d5da81d51e5eb55a805008d1a62b1dce`，未提交工作区。Python 3.12.3、SQLite 3.45.1，本地真实文件 SQLite，无网络或模拟服务。产品差异仅 `src/order_service.py` 的 create_order 判空条件；直接测试新增于 `tests/test_order.py`。其他执行者的文档与验收资产修改未回滚。

验证时产品／直接测试 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| src/order_service.py | `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b` |
| tests/test_order.py | `805ec0a2e62de65a215d05dca92c2aaaf658323daaaaed59634db1f4a7060e50` |
| src/storage.py（只读未修改） | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| src/ui.py（只读未修改） | `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b` |

## T001／AC-4

入口校验使用 `not order_id.strip()`；实际插入仍使用原始编号。错误类型和消息沿用空输入的 `ValueError("order_id is required")`。

运行入口：`python -B -m unittest discover -s tests -v`。数据使用每个测试自己的临时目录及文件库，并在测试结束关闭连接、清理目录。

- 修改产品代码前，新增测试运行退出 1：4 个测试中拒绝场景失败，空格、制表／换行／回车、全角／不换行空格均未抛出 ValueError；SQL trace 显示 3 次 INSERT 及 COMMIT（共 9 条事务／写入语句）。合法编号测试与两个既有测试通过。
- 修改后同入口退出 0：4 个测试全部通过。拒绝场景覆盖空字符串、ASCII／Unicode 全空白、None、整数；SQL trace 为空，另开连接读取仅保留原有 `ORDER-1/pending`。合法编号 `  ORDER-2\t` 原值保存并从另开连接读到 pending。
- 两个既有测试保留，普通提交返回 true、读到 submitted，付款可从另开连接读到 paid。未修复或扩大 submit_order／mark_paid 既有行为。

本项局部完成，正式 AC-4 与跨进程验收由调度方执行。

## T002／AC-5

静态核查入口：`rg -n 'event|history|trigger|journal|CREATE|INSERT|UPDATE|connect\(|status' src tests docs/contracts/order.md`，并通读 `src/storage.py`、`src/order_service.py`、`src/ui.py`。存储仅建 `orders(order_id,status)`；create_order 插入当前态，set_status 更新覆盖当前态，cancel_order 调用 set_status，submit_order 覆盖为 submitted，mark_paid 直接更新 paid。不存在事件保存代码或读取历史接口。

复跑跨进程证据（在仓库根运行，无外部依赖）：

```python
import os, sqlite3, subprocess, sys, tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / 'orders.sqlite'
    child = '''
import sys
from src import order_service as service, storage, ui
connection = storage.connect(sys.argv[1])
service.create_order(connection, 'HISTORY-1')
service.cancel_order(connection, 'HISTORY-1')
ui.mark_paid(connection, 'HISTORY-1')
connection.close()
'''
    subprocess.run([sys.executable, '-B', '-c', child, str(database)], check=True)
    connection = sqlite3.connect(database)
    print(connection.execute('SELECT type, name, sql FROM sqlite_master ORDER BY name').fetchall())
    print(connection.execute('SELECT * FROM orders').fetchall())
    print(connection.execute('PRAGMA journal_mode').fetchone())
    print(sorted(os.listdir(directory)))
    connection.close()
```

实际子进程正常退出后父进程重开观察：

```text
[('table', 'orders', 'CREATE TABLE orders (order_id TEXT PRIMARY KEY, status TEXT NOT NULL)'), ('index', 'sqlite_autoindex_orders_1', None)]
[('HISTORY-1', 'paid')]
('delete',)
['orders.sqlite']
```

由此不能还原 pending→cancelled→paid，也不能区别同一最终 paid 状态的其他历史。真实数据库中无额外事件表／视图／触发器；仅一行当前态且无顺序字段。SQLite 文件本身不提供契约化逐次事件来源。

AC-5 保留 Blocked：未新增历史导出入口，不将当前态快照伪装成历史。约束内唯一现有可读路径是 read_status，但它只能返回当前状态，不能满足 AC-5；日志、时间戳推测、进程内缓存或另建账本均不符合已确认设计，无等价只读替代路径。

影响与恢复条件：T001 可独立验收。T002 需上层提供真实、可访问且含跨重启准确顺序的权威事件来源；或另行确认架构／迁移方案并授权持久化事件结构、覆盖创建／取消／提交／付款的全量写路径与既有当前态数据处理，再续派同一 Task。当前数据已丢失的旧历史不能靠只读新增入口恢复。未经授权未修改 schema、其他写路径或 Blueprint。

## 文档核对

执行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/plan.md specs/order/implementation-evidence.md`：退出 0，2 个 Markdown 文件，0 errors／0 warnings（仅机械检查）。语义核对保留两个稳定编号、AC-4／AC-5 不降级，局部结果与正式验收明确分开。
