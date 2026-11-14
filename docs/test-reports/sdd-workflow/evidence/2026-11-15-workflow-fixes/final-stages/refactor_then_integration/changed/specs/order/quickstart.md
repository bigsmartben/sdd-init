# 订单验收指南

## 范围与运行条件

依据：[订单需求](spec.md)、[公开函数契约](../../docs/contracts/order.md)。本轮覆盖新建、取消、提交、公开付款和 AC-3。已有授权覆盖隔离项目内、本地 Python 3.11+ 与文件 SQLite；无需依赖安装、UI 或人工视觉确认。以公开函数协同及重开文件数据库后的业务结果判断，不以局部单测代替集成。

目标为 `76e8f410e7adeb3cb702dc1f89bb5129bf381c60` 加第一阶段付款整改的实际工作树；在项目根运行 `git rev-parse HEAD`、`git status --short`、`python -B checks/runtime_details.py` 并核对[集成报告](../../docs/test-reports/order/integration-20261115.md)的源文件哈希。`src.ui.mark_paid → src.order_service.set_status → sqlite3.Connection → 文件 SQLite` 均使用真实组件；其余操作直接走公开服务入口。没有模拟服务或外部回执。除下述只读连接、真实数据库锁、关闭连接和 SQLite authorizer 拒绝 COMMIT 的受控故障注入外，不替换组件。

## 场景与判据

前三项沿用原入口 `python -B checks/acceptance.py --scenario AC-1`（或 AC-2、AC-3）；全部执行用 `python -B checks/acceptance.py`，退出码 0 全通过、1 存在失败、3 无失败但有阻塞。下方扩展脚本同时运行三项及派生覆盖，各场景独立临时文件和数据，所有连接最终关闭、目录删除。常规数据和异常组合由契约推导；未规定的业务转换不另定判据。

| 场景 | 前提与操作 | 通过判据及观察点 |
|---|---|---|
| AC-1 | 新建 ORDER-1，提交，再关闭重开 | 返回 true，状态 submitted 持久化 |
| AC-2 | 新建，取消，提交，再关闭重开 | 提交 false，仍 cancelled；保留原判据 |
| AC-3 | 读取 runtime.json，核对外部端点和授权 | 必须由获授权真实服务核验回执；当前缺条件只报 BLOCKED，不访问网络 |
| IT-01 | 新建后重开 | pending 持久化 |
| IT-02 | 新建后取消、重开，再次取消、重开 | cancelled 持久化，重复取消仍 cancelled |
| IT-03 | 分别准备 pending、submitted、cancelled、paid 的现存订单，再公开付款并重开 | mark_paid 返回 None，各状态均成为 paid，重复付款保持 paid |
| IT-04 | 在含一个 pending 订单的库调用 read_status、cancel_order、submit_order、mark_paid，目标为 MISSING | 各抛 ValueError，现存订单重开后仍 pending |
| IT-05 | 真实只读 SQLite 连接依次调用新建、取消、提交、付款 | 各抛 sqlite3.Error，不返回成功；重开后原订单 pending，新订单不存在；恢复可写连接后付款持久化 paid |
| IT-06 | 真实第二连接 BEGIN IMMEDIATE 持锁；操作连接 timeout=0；依次新建、取消、提交、付款 | 各抛数据库异常，未提交；每次 rollback 后观察原订单仍 pending；释放锁后公开新建/提交及付款均可持久化 |
| IT-07 | 关闭连接后分别新建、取消、提交、付款 | 各抛数据库异常；重开后原状态 pending；新连接取消后 cancelled 持久化 |
| IT-08 | 四订单分别保持 pending、取消、提交、付款并重开 | 分别 pending/cancelled/submitted/paid，无跨订单覆盖 |
| IT-10 | 真实 SQLite authorizer 只拒绝 COMMIT，依次新建、取消、提交、付款；每次失败后 rollback | 各抛数据库异常，其他连接仍读取原 pending 且无新订单；解除 authorizer 后公开付款持久化 paid |
| IT-09 | 非空 Unicode 与含 SQL 引号/分隔符的合法订单号，分别新建、提交、付款并重开 | 标识可区分，提交 true，最终 paid，表及另一订单仍可读取 |

输入 `''`、None、42 超出非空字符串前提，重复新建也没有已确认返回值/异常类型；下方脚本另行输出实现事实，不将其当作新增验收要求或 Gate 场景。数据库异常不意味着自动回滚；调用者关闭或 rollback 后恢复，不对未确认的自动重试/事务策略作断言。没有已确认性能阈值，不作性能验收。

## 完整复跑命令

从项目根执行以下 Python。每条 JSON 记录保留中间观察、实际结果与判断；脚本结尾输出覆盖统计并按上述退出码返回。为便于自动复跑，也可提取本节唯一 Python 代码块后以 `python -B -` 执行，不需写入测试文件。

```python
import json
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from checks.acceptance import run
from src import order_service as svc, storage, ui

results = []
@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix="order-integration-") as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        try:
            yield path, connection
        finally:
            connection.close()

def status(path, key="ORDER-1"):
    connection = storage.connect(path)
    try:
        return svc.read_status(connection, key)
    finally:
        connection.close()

def raises(kind, action):
    try:
        action()
    except kind as error:
        return type(error).__name__ + ": " + str(error)
    raise AssertionError("Expected " + kind.__name__)

def check(case, action):
    try:
        observed = action()
        row = {"scenario": case, "result": "PASS", "observed": observed}
    except Exception as error:
        row = {"scenario": case, "result": "FAIL", "error": repr(error)}
    results.append(row)
    print(json.dumps(row, ensure_ascii=False))

def create():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        c.close()
        actual = status(path)
        assert actual == "pending", actual
        return {"reopened": actual}

def cancel():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        svc.cancel_order(c, "ORDER-1")
        first = status(path)
        svc.cancel_order(c, "ORDER-1")
        c.close()
        second = status(path)
        assert (first, second) == ("cancelled", "cancelled")
        return {"after_cancel": first, "after_repeat_and_reopen": second}

def paid():
    observations = {}
    for initial in ("pending", "submitted", "cancelled", "paid"):
        with fixture() as (path, c):
            svc.create_order(c, "ORDER-1")
            if initial == "submitted":
                assert svc.submit_order(c, "ORDER-1") is True
            elif initial == "cancelled":
                svc.cancel_order(c, "ORDER-1")
            elif initial == "paid":
                ui.mark_paid(c, "ORDER-1")
            assert status(path) == initial
            returned = ui.mark_paid(c, "ORDER-1")
            c.close()
            actual = status(path)
            assert returned is None and actual == "paid"
            observations[initial] = {"returned": returned, "reopened": actual}
    return observations

def missing():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        observations = {}
        for action in (svc.read_status, svc.cancel_order, svc.submit_order, ui.mark_paid):
            observations[action.__name__] = raises(ValueError, lambda: action(c, "MISSING"))
        c.close()
        assert status(path) == "pending"
        observations["unrelated_reopened"] = "pending"
        return observations

def mutations(c):
    return {"create": lambda: svc.create_order(c, "NEW"),
            "cancel": lambda: svc.cancel_order(c, "ORDER-1"),
            "submit": lambda: svc.submit_order(c, "ORDER-1"),
            "paid": lambda: ui.mark_paid(c, "ORDER-1")}

def unchanged(path):
    assert status(path) == "pending"
    raises(ValueError, lambda: status(path, "NEW"))

def readonly():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        ro = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        try:
            observations = {name: raises(sqlite3.Error, action) for name, action in mutations(ro).items()}
        finally:
            ro.close()
        unchanged(path)
        observations["before_recovery"] = status(path)
        ui.mark_paid(c, "ORDER-1")
        c.close()
        observations["after_recovery"] = status(path)
        assert observations["after_recovery"] == "paid"
        return observations

def locked():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        blocker = sqlite3.connect(path)
        writer = sqlite3.connect(path, timeout=0)
        try:
            blocker.execute("BEGIN IMMEDIATE")
            observations = {}
            for name, action in mutations(writer).items():
                observations[name] = raises(sqlite3.Error, action)
                writer.rollback()
                unchanged(path)
            observations["before_unlock"] = status(path)
            blocker.rollback()
            svc.create_order(writer, "NEW")
            assert svc.submit_order(writer, "NEW") is True
            ui.mark_paid(writer, "ORDER-1")
        finally:
            writer.close()
            blocker.close()
        c.close()
        observations["after_unlock"] = {"ORDER-1": status(path), "NEW": status(path, "NEW")}
        assert observations["after_unlock"] == {"ORDER-1": "paid", "NEW": "submitted"}
        return observations

def closed():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        c.close()
        observations = {name: raises(sqlite3.Error, action) for name, action in mutations(c).items()}
        unchanged(path)
        observations["before_recovery"] = status(path)
        recovered = storage.connect(path)
        try:
            svc.cancel_order(recovered, "ORDER-1")
        finally:
            recovered.close()
        observations["after_recovery"] = status(path)
        assert observations["after_recovery"] == "cancelled"
        return observations

def commit_failure():
    with fixture() as (path, c):
        svc.create_order(c, "ORDER-1")
        def authorizer(operation, first, second, database, source):
            return sqlite3.SQLITE_DENY if operation == sqlite3.SQLITE_TRANSACTION and first == "COMMIT" else sqlite3.SQLITE_OK
        c.set_authorizer(authorizer)
        observations = {}
        try:
            for name, action in mutations(c).items():
                observations[name] = raises(sqlite3.Error, action)
                unchanged(path)
                c.rollback()
                unchanged(path)
        finally:
            c.set_authorizer(None)
        observations["after_rollback"] = status(path)
        ui.mark_paid(c, "ORDER-1")
        c.close()
        observations["after_recovery"] = status(path)
        assert observations["after_recovery"] == "paid"
        return observations

def isolation():
    with fixture() as (path, c):
        for key in ("P", "C", "S", "D"):
            svc.create_order(c, key)
        svc.cancel_order(c, "C")
        assert svc.submit_order(c, "S") is True
        ui.mark_paid(c, "D")
        c.close()
        actual = {key: status(path, key) for key in ("P", "C", "S", "D")}
        assert actual == {"P": "pending", "C": "cancelled", "S": "submitted", "D": "paid"}
        return actual

def identifiers():
    with fixture() as (path, c):
        keys = ("订单-一", "x'; DROP TABLE orders;--")
        for key in keys:
            svc.create_order(c, key)
            assert svc.submit_order(c, key) is True
            ui.mark_paid(c, key)
        c.close()
        actual = {key: status(path, key) for key in keys}
        assert all(value == "paid" for value in actual.values())
        return actual

for case in ("AC-1", "AC-2", "AC-3"):
    row = run(case)
    results.append(row)
    print(json.dumps(row, ensure_ascii=False))
for case, action in (("IT-01", create), ("IT-02", cancel), ("IT-03", paid),
                     ("IT-04", missing), ("IT-05", readonly), ("IT-06", locked),
                     ("IT-07", closed), ("IT-08", isolation), ("IT-09", identifiers),
                     ("IT-10", commit_failure)):
    check(case, action)
# Diagnostic observations only, outside the acceptance case count.
with fixture() as (path, c):
    observations = {}
    for value in ("", None, 42):
        try:
            svc.create_order(c, value)
            observations[repr(value)] = "returned without exception"
        except Exception as error:
            observations[repr(value)] = type(error).__name__ + ": " + str(error)
    svc.create_order(c, "ORDER-1")
    try:
        svc.create_order(c, "ORDER-1")
        observations["duplicate"] = "returned without exception"
    except Exception as error:
        observations["duplicate"] = type(error).__name__ + ": " + str(error)
    c.rollback()
    observations["reopened"] = status(path)
    print(json.dumps({"diagnostic_only": observations}, ensure_ascii=False))
counts = {state: sum(row["result"] == state for row in results)
          for state in ("PASS", "FAIL", "NOT_RUN", "BLOCKED")}
print(json.dumps({"total": len(results), "counts": counts, "cleanup": "all fixture contexts exited"}))
raise SystemExit(1 if counts["FAIL"] else 3 if counts["BLOCKED"] else 0)
```

## 失败恢复与人工／外部待验

本地数据均为每场景新建文件，无共享数据迁移。连接关闭后删除临时目录，失败亦执行 finally；重跑以上命令即可重建。只读场景换回原可写连接，锁场景释放锁并 rollback，关闭场景新建连接后验证恢复。原 AC-2 失败须在另行获准的修复阶段处理；集成阶段不得更改代码或放宽断言。

AC-3 不以本地 submitted 或脚本输出替代真实回执。恢复须由有权人员提供真实测试服务端点、权限和外部调用授权，随后补足实际外部调用步骤并仅对受影响事项通过 Main 对齐。当前批次不访问网络、不取凭据、不部署。人工视觉验收不适用；外部服务回执核验仍待验。

实际结果、版本、缺陷和 Gate 归[集成报告](../../docs/test-reports/order/integration-20261115.md)。局部入口 `python -B -m unittest discover -s tests -v` 仅辅助回归，不代替本指南。
