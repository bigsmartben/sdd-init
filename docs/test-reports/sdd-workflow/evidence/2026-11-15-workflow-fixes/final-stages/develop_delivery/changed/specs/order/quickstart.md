# 订单验收指南

依据：[Spec](spec.md) AC-1、AC-2、AC-3。执行者在生成的隔离项目目录操作，使用 Python 3.11+ 与标准库 SQLite；无需安装依赖。每个本地场景使用新临时目录中的 SQLite 文件和订单 `ORDER-1`，执行后关闭连接并删除该临时目录。无需人工视觉确认。

| 场景 | 操作 | 判断点 |
|---|---|---|
| AC-1 | `python -B checks/acceptance.py --scenario AC-1` | 提交返回 true，重开数据库后状态 submitted。 |
| AC-2 | `python -B checks/acceptance.py --scenario AC-2` | 取消后提交返回 false，重开数据库后状态 cancelled。 |
| AC-3 | `python -B checks/acceptance.py --scenario AC-3` | 检查 runtime.json 的端点和授权；未就绪时返回 BLOCKED，不访问网络。 |

`python -B checks/acceptance.py` 执行全部场景并逐项输出 JSON。退出码为 0（全部通过）、1（存在失败）或 3（无失败但存在阻塞）。局部单元测试入口为 `python -B -m unittest discover -s tests -v`，不能替代上表验收。

运行条件证据可以使用 `python -B checks/runtime_details.py` 只读补查。该入口输出实际 Python、SQLite 版本、配置事实与源文件哈希，不推定未运行场景的结果。AC-3 恢复条件是由有权人员提供已授权测试服务端点和调用权限；本轮不得自行配置外部服务或获取凭据。

## 订单号校验点对点验收

本轮只覆盖 [Spec](spec.md) AC-4、AC-5、AC-6 及直接受影响的 AC-1、paid 持久化保持行为。实施者在 B 确认后局部自验，sdd-develop 技能 Agent 收到实现回执后从公开调用入口逐项验收；实际版本与结果见 [Plan](plan.md#交付核对与接续)。环境沿用上文 Python／SQLite 条件，不需要外部服务、网络或人工视觉反馈。

从项目根目录执行以下命令。每个非法输入使用独立的临时文件数据库，先创建合法订单，比较失败前后及重开后的完整订单集合；合法编号场景也重开验证。临时目录在场景结束后删除。

```bash
python -B - <<'PY'
from pathlib import Path
import tempfile
from src import order_service as service, storage

invalid = ['', ' ', '\t', '\n', '\u3000', ' \t\n\u3000 ', None, 0, False, []]
valid = ['ORDER-2', ' ORDER-3 ', '\tORDER-4\n', '\u3000订单-5\u3000']
def rows(connection):
    return connection.execute('SELECT order_id, status FROM orders ORDER BY order_id').fetchall()

for value in invalid:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'orders.sqlite'
        connection = storage.connect(path)
        try:
            service.create_order(connection, 'EXISTING-1')
            before = rows(connection)
            try:
                service.create_order(connection, value)
            except ValueError as error:
                assert str(error) == 'order_id is required', repr(value)
            else:
                raise AssertionError(('unexpected acceptance', repr(value)))
            assert rows(connection) == before, repr(value)
        finally:
            connection.close()
        connection = storage.connect(path)
        try:
            assert rows(connection) == before, repr(value)
        finally:
            connection.close()
    print('PASS invalid', repr(value))

for value in valid:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'orders.sqlite'
        connection = storage.connect(path)
        try:
            assert service.create_order(connection, value) is None
            assert service.read_status(connection, value) == 'pending'
        finally:
            connection.close()
        connection = storage.connect(path)
        try:
            assert rows(connection) == [(value, 'pending')], repr(value)
            assert service.read_status(connection, value) == 'pending'
        finally:
            connection.close()
    print('PASS valid', repr(value))
PY
python -B -m unittest discover -s tests -v
python -B checks/acceptance.py --scenario AC-1
```

通过判据：非法输入全部输出 PASS，异常消息匹配且原订单集合不变；合法输入全部输出 PASS，原始订单号和 pending 状态重开后保持；单元测试与 AC-1 均通过。实施后新增定向单测应覆盖同样判据，不能仅用单测替代以上入口验收。失败时保留命令输出、实际版本和失败数据，修正原 Task 后复验；结果归 [Plan](plan.md) 或其引用的测试记录。

旧 AC-2、AC-3 不是本轮完成条件，不因本轮局部通过而宣称通过或修复。AC-2 的既有实现偏差及 AC-3 外部条件见 Plan。
