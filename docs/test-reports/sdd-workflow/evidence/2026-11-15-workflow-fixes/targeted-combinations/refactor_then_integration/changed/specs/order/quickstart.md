# 订单验收指南

依据：[Spec](spec.md)、[函数契约](../../docs/contracts/order.md)、[运行条件](../../runtime.json)。范围为新建、取消、提交、公开 `src.ui.mark_paid` 与真实外部回执 AC-3。使用隔离项目根目录、Python 3.11+ 和标准库 SQLite，无需安装依赖。无 UI，无需人工视觉确认。

## 候选版本与环境

本轮候选为 HEAD `4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df` 加 `src/ui.py`、`tests/test_order.py` 的付款改动；仅提交号不能唯一标识实际代码。执行以下命令并对照[本轮报告](../../docs/test-reports/order/payment-integration.md)中的源哈希；代码变化后重新核验受影响场景。

```bash
git rev-parse HEAD
git status --short
python -B checks/runtime_details.py
```

真实组件为公开 Python 函数和本地文件 SQLite。`runtime.json` 的外部端点为空、调用未授权，本轮不访问网络。所有本地场景使用独立临时目录的 SQLite 文件，关闭重开读取持久化结果；上下文退出自动删除临时数据，无需外部账号。

## 主验收路径

| 场景 | 操作 | 判断点 |
|---|---|---|
| AC-1 | `python -B checks/acceptance.py --scenario AC-1` | pending 提交返回 true，重开后 submitted。 |
| AC-2 | `python -B checks/acceptance.py --scenario AC-2` | 先取消再提交应返回 false，重开后仍 cancelled。 |
| AC-3 | `python -B checks/acceptance.py --scenario AC-3` | 未获真实外部端点与权限时 BLOCKED，不以本地结果替代。 |

`python -B checks/acceptance.py` 执行以上三项并逐项输出 JSON。退出码 0 表示全部通过，1 表示存在失败，3 表示无失败但存在阻塞。失败时保留原断言和证据。

## 扩展功能覆盖与复跑

下列内联命令不修改产品或验收脚本。每项使用独立文件库，使用公开函数实际写入，再通过重开文件库或第二连接检查结果。IT-03 至 IT-06 按契约覆盖现存订单的四种前态付款；不推导 paid/submitted 再提交等未定义规则。订单编号遵守非空字符串前提，空值和非字符串不纳入本轮 Gate；缺单场景明确验证契约异常。只读 SQLite 故障证明异常向上传播，不模拟外部服务。

```bash
python -B - <<'PY'
import json
from pathlib import Path
import sqlite3
import tempfile
from src import order_service as s, storage, ui

results = []
def run(case, check):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'orders.sqlite'
        connection = storage.connect(path)
        def reopened():
            other = storage.connect(path)
            try:
                return dict(other.execute('SELECT order_id, status FROM orders').fetchall())
            finally:
                other.close()
        try:
            detail = check(connection, reopened)
            results.append({'case': case, 'result': 'PASS', 'observed': detail})
        except Exception as error:
            results.append({'case': case, 'result': 'FAIL', 'error': repr(error)})
        finally:
            connection.close()

def raises(kind, operation):
    try:
        operation()
    except kind as error:
        return type(error).__name__
    raise AssertionError('expected ' + kind.__name__)

def create(c, read):
    for key in ('ORDER-1', '订单-2', ' '):
        s.create_order(c, key)
    actual = read()
    assert actual == {'ORDER-1': 'pending', '订单-2': 'pending', ' ': 'pending'}, actual
    return actual
run('IT-01', create)

def cancel(c, read):
    s.create_order(c, 'ORDER-1')
    s.cancel_order(c, 'ORDER-1')
    first = read()
    s.cancel_order(c, 'ORDER-1')
    second = read()
    assert first == second == {'ORDER-1': 'cancelled'}, (first, second)
    return {'first': first, 'repeat': second}
run('IT-02', cancel)

for case, state in zip(('IT-03', 'IT-04', 'IT-05', 'IT-06'), ('pending', 'submitted', 'cancelled', 'paid')):
    def payment(c, read, state=state):
        s.create_order(c, 'ORDER-1')
        if state == 'submitted':
            assert s.submit_order(c, 'ORDER-1') is True
        elif state == 'cancelled':
            s.cancel_order(c, 'ORDER-1')
        elif state == 'paid':
            ui.mark_paid(c, 'ORDER-1')
        before = read()
        assert before == {'ORDER-1': state}, before
        returned = ui.mark_paid(c, 'ORDER-1')
        actual = read()
        assert returned is None and actual == {'ORDER-1': 'paid'}, (returned, actual)
        return {'before': before, 'returned': returned, 'reopened': actual}
    run(case, payment)

def missing(c, read):
    s.create_order(c, 'KEEP')
    operations = {
        'read': lambda: s.read_status(c, 'MISSING'),
        'cancel': lambda: s.cancel_order(c, 'MISSING'),
        'submit': lambda: s.submit_order(c, 'MISSING'),
        'set': lambda: s.set_status(c, 'MISSING', 'paid'),
        'paid': lambda: ui.mark_paid(c, 'MISSING'),
    }
    errors = {name: raises(ValueError, op) for name, op in operations.items()}
    assert read() == {'KEEP': 'pending'}
    return {'errors': errors, 'reopened': read()}
run('IT-08', missing)

def database_failure(c, read):
    s.create_order(c, 'KEEP')
    c.execute('PRAGMA query_only=ON')
    operations = {
        'create': lambda: s.create_order(c, 'NEW'),
        'cancel': lambda: s.cancel_order(c, 'KEEP'),
        'submit': lambda: s.submit_order(c, 'KEEP'),
        'set': lambda: s.set_status(c, 'KEEP', 'paid'),
        'paid': lambda: ui.mark_paid(c, 'KEEP'),
    }
    errors = {name: raises(sqlite3.OperationalError, op) for name, op in operations.items()}
    assert read() == {'KEEP': 'pending'}
    return {'errors': errors, 'reopened': read()}
run('IT-09', database_failure)

def legal_status(c, read):
    s.create_order(c, 'ORDER-1')
    observed = []
    for state in ('pending', 'submitted', 'cancelled', 'paid'):
        s.set_status(c, 'ORDER-1', state)
        actual = read()
        assert actual == {'ORDER-1': state}, actual
        observed.append(actual)
    return observed
run('IT-10', legal_status)

def isolation(c, read):
    for key in ('SUBMIT', 'CANCEL', 'PAY', 'KEEP'):
        s.create_order(c, key)
    assert s.submit_order(c, 'SUBMIT') is True
    s.cancel_order(c, 'CANCEL')
    ui.mark_paid(c, 'PAY')
    actual = read()
    assert actual == {'SUBMIT': 'submitted', 'CANCEL': 'cancelled', 'PAY': 'paid', 'KEEP': 'pending'}, actual
    return actual
run('IT-11', isolation)
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(1 if any(row['result'] != 'PASS' for row in results) else 0)
PY
```

局部辅助测试入口为 `python -B -m unittest discover -s tests -v`，包含付款提交失败向上传播检查；不能替代以上公开路径集成结果。全部已定义本地功能及异常通过且 AC-3 取得真实授权回执后才可判整轮 PASS。

AC-3 的恢复条件是有权人员提供真实测试服务端点、调用权限及允许的操作方法；当前夹具只报告就绪条件，届时仍需真实外部验收执行者和回执证据。不得自行配置服务、获取凭据或用本地数据库结果替代。无其他人工待验项；缺陷及实际结果见报告。
