# 订单用户验收指南

## 1. 验证目标与范围

依据 [Spec](spec.md)、[函数契约](../../docs/contracts/order.md) 和 [工单](../../TASK.txt)，覆盖新建提交、取消后拒绝提交、外部回执，以及 paid 保持、非空编号、缺失订单和数据库异常传播。没有图形界面，无需人工视觉验收。

## 2. 环境与启动

在当前隔离项目根目录运行，版本为 `6d5e6b6737cc61d38206817f58876c7f65473a21`。运行 `git rev-parse HEAD`、`git status --short`、`python -B checks/runtime_details.py` 核对提交、未提交改动和源文件指纹。Python 3.12.3，仅依赖标准库；实际 SQLite 版本见报告原始运行信息。[环境](../../runtime.json) 为 `isolated-local-fixture`。

每个场景新建临时文件 SQLite；数据 ORDER-1、空字符串、None、MISSING 从非空编号和缺失订单契约推导。目录自动清理。当前无外部端点、授权或网络；禁止外部调用。

## 3. 场景验证

| 用例／依据 | 操作 | 观察与通过判据 |
| --- | --- | --- |
| C01／AC-1 | `python -B checks/acceptance.py --scenario AC-1` | accepted=true，关闭重开后 submitted |
| C02／AC-2 | `python -B checks/acceptance.py --scenario AC-2` | 取消后 accepted=false，关闭重开仍 cancelled |
| C03／AC-3 | `python -B checks/acceptance.py --scenario AC-3` | 当前只能显示 BLOCKED；通过需真实获授权外部服务回执 |
| C04／paid 保持 | 下方命令创建、mark_paid、重开文件 | paid |
| C05／非空编号 | 下方命令以空字符串、None 新建 | 均抛 ValueError，订单数不变 |
| C06／缺失订单 | 下方命令读取、取消、提交、set_status、mark_paid 不存在订单 | 均抛 ValueError，订单数为零 |
| C07／数据库异常 | 下方命令关闭连接，再调用上述接口和新建 | 均传播 sqlite3.Error，不返回成功 |
| C08／新建及取消持久化 | 下方命令新建重开、取消重开 | 依次 pending、cancelled |

运行全部 AC：`python -B checks/acceptance.py`。退出码 0 为所选场景通过，1 为存在失败，3 为无失败但有阻塞；全量 JSON 的逐场景结果须保留。辅助回归 `python -B -m unittest discover -s tests -v` 不替代整轮验收。

以下为可直接粘贴的补充操作，不新增测试文件。保存 JSON 标准输出作为 C04—C08 证据，各行 result 为判定；该命令退出码不汇总业务结果。

```bash
python -B - <<'PY'
import json, sqlite3, tempfile
from pathlib import Path
from src import order_service as s, storage, ui
results = []
def observe(fn):
    try:
        return {"returned": fn()}
    except Exception as error:
        return {"exception": type(error).__name__, "message": str(error)}
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    def opened(name):
        return storage.connect(root / (name + ".sqlite"))
    c = opened("paid")
    s.create_order(c, "ORDER-1")
    ui.mark_paid(c, "ORDER-1")
    c.close()
    c = opened("paid")
    status = s.read_status(c, "ORDER-1")
    c.close()
    results.append({"case": "C04", "persisted_status": status, "result": "PASS" if status == "paid" else "FAIL"})
    c = opened("invalid")
    observations = [observe(lambda value=value: s.create_order(c, value)) for value in ("", None)]
    count = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    c.close()
    passed = count == 0 and all(row.get("exception") == "ValueError" for row in observations)
    results.append({"case": "C05", "inputs": ["", None], "observations": observations, "order_count": count, "result": "PASS" if passed else "FAIL"})
    c = opened("missing")
    operations = {"read_status": lambda: s.read_status(c, "MISSING"), "cancel_order": lambda: s.cancel_order(c, "MISSING"), "submit_order": lambda: s.submit_order(c, "MISSING"), "set_status": lambda: s.set_status(c, "MISSING", "paid"), "mark_paid": lambda: ui.mark_paid(c, "MISSING")}
    observations = {name: observe(fn) for name, fn in operations.items()}
    count = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    c.close()
    passed = count == 0 and all(row.get("exception") == "ValueError" for row in observations.values())
    results.append({"case": "C06", "observations": observations, "order_count": count, "result": "PASS" if passed else "FAIL"})
    c = opened("closed")
    s.create_order(c, "ORDER-1")
    c.close()
    operations = {"create_order": lambda: s.create_order(c, "ORDER-2"), "read_status": lambda: s.read_status(c, "ORDER-1"), "cancel_order": lambda: s.cancel_order(c, "ORDER-1"), "submit_order": lambda: s.submit_order(c, "ORDER-1"), "set_status": lambda: s.set_status(c, "ORDER-1", "paid"), "mark_paid": lambda: ui.mark_paid(c, "ORDER-1")}
    observations = {name: observe(fn) for name, fn in operations.items()}
    passed = all(isinstance(getattr(sqlite3, row.get("exception", ""), None), type) and issubclass(getattr(sqlite3, row["exception"]), sqlite3.Error) for row in observations.values())
    results.append({"case": "C07", "observations": observations, "result": "PASS" if passed else "FAIL"})
    c = opened("states")
    s.create_order(c, "ORDER-1")
    c.close()
    c = opened("states")
    pending = s.read_status(c, "ORDER-1")
    s.cancel_order(c, "ORDER-1")
    c.close()
    c = opened("states")
    cancelled = s.read_status(c, "ORDER-1")
    c.close()
    results.append({"case": "C08", "reopened_states": [pending, cancelled], "result": "PASS" if (pending, cancelled) == ("pending", "cancelled") else "FAIL"})
print(json.dumps(results, ensure_ascii=False, indent=2))
PY
```

## 4. 失败与恢复

每次运行新建临时目录，关闭连接后退出自动清理，无共享数据库状态。C07 只关闭自己的连接。失败保留实际输出与版本，不修改代码、测试或判据。AC-3 恢复需后续单独授权的外部端点、访问权限、网络环境与真实调用入口，不能用本地提交或配置检查代替真实回执。

## 5. 结果引用

见 [本轮测试报告](../../docs/test-reports/order/20261114.md) 与 [Status](../../docs/status.md)。报告记录原始证据、缺陷及 Gate。
