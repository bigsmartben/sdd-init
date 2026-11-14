# 订单验收指南

## 1. 目标和范围

依据：[Spec](spec.md) AC-1、AC-2、AC-3 及新建、取消、提交、公开付款保持要求，[订单契约](../../docs/contracts/order.md)。本轮覆盖全部本地功能及其组合、边界和数据库异常；AC-3 必须是真实获授权外部服务回执。本项目无 UI 页面，无人工视觉验收。

## 2. 版本、环境和入口

目标为 HEAD `663483bf7d8f869aad8d57a5de920e790e5c8dbc` 加付款对齐工作树，代码变更仅 `src/ui.py`、`tests/test_order.py`。先执行 `git rev-parse HEAD`、`git diff -- src tests` 和 `python -B checks/runtime_details.py`；源哈希与[本轮报告](../../docs/test-reports/order/payment-integration.md#3-test-environment)匹配后再复跑。其他版本需重新判断证据适用性。

从隔离项目根执行，Python 3.11+、标准库 SQLite，无需安装依赖；本轮实测 Python 3.12.3 / SQLite 3.45.1。`runtime.json` 应为本地文件库、无端点、无外部授权、无网络。各场景新建临时文件 SQLite，关闭连接后重开读取，最后关闭并删除目录。普通 ID、含 Unicode/引号字符串、空值和非法类型、重复 ID、多订单、缺失订单、只读和关闭连接均由契约推导，不增补新业务规则。只测试已有合法状态，不推定其他状态转换的业务含义。

原验收入口：

```bash
python -B checks/acceptance.py
python -B checks/acceptance.py --scenario AC-1
python -B checks/acceptance.py --scenario AC-2
python -B checks/acceptance.py --scenario AC-3
```

全量入口退出 0 表示全部通过，1 表示存在失败，3 表示无失败但有阻塞。AC-3 入口仅检查前置条件，绝不产生真实服务通过证据。

## 3. 场景和通过判据

| 功能 / 场景 | 数据、步骤 | 预期与证据 |
| --- | --- | --- |
| AC-1 新建提交 | 原入口，新建 pending，再 submit，关闭重开 | true / submitted |
| AC-2 取消后提交 | 原入口，新建、取消、submit，关闭重开 | false / cancelled，禁止覆盖 |
| AC-3 外部回执 | 原入口核对配置；真实测试另需端点和授权 | 缺少前提时 BLOCKED，不能模拟 |
| B01 新建和持久化 | 普通 ID 与 Unicode/引号 ID，各 create 后重开 | 两者 pending，字符串原样保存 |
| B02 新建输入边界 | 空字符串、None、整数、bytes | 每次 ValueError，重开无行 |
| B03 重复订单 | 同 ID 创建两次，捕获异常后 rollback、重开 | IntegrityError，原订单仍 pending |
| B04 缺失订单 | read、set_status、cancel、submit、公开 mark_paid | 各 ValueError，无插入，无其他订单变更 |
| B05 取消及重复取消 | 新建、cancel、观察中间态、再次 cancel、重开 | 中间及最终 cancelled |
| B06 合法状态入口 | set_status 逐次写 pending/submitted/cancelled/paid，每次重开 | 每次精确持久化给定状态 |
| B07 pending 付款 | create 后公开 mark_paid，重开 | 返回 None，paid |
| B08 提交再付款 | create、submit true、观察 submitted、mark_paid、重开 | 返回 None，paid |
| B09 取消再付款 | create、cancel、观察 cancelled、mark_paid、重开 | 返回 None，paid（既有付款保持要求） |
| B10 重复付款 | create、mark_paid、观察 paid、再次 mark_paid、重开 | 返回 None，paid |
| B11 多订单协同 | 同文件三订单分别 submit/cancel/mark_paid，重开 | 分别 submitted/cancelled/paid，互不串扰 |
| B12 写入异常 | pending，PRAGMA query_only=ON，逐一 create/set/cancel/submit/mark_paid，重开 | 各 OperationalError，无伪成功，原 pending、无新增行 |
| B13 连接关闭 | pending，close 后逐一 create/read/set/cancel/submit/mark_paid，重开 | 各 ProgrammingError，无状态变更 |
| B14 失败恢复 | pending、只读 submit 失败并观察 pending，重开正常连接再 submit、重开 | 先异常、pending，再 true/submitted |

B01—B14 用下面完整取证内容复跑；它从公开库入口调用真实 src/storage/SQLite，无 mock。把内容保存到项目外授权 scratch 的 `order_integration.py`，然后从项目根运行：

```bash
python -B /tmp/sdd-review-execution-7z3ofaey/refactor_then_integration-rv6k1dkq/scratch/order_integration.py
```

每项输出实际中间态、重开数据或异常及 `cleaned`；全部 PASS 时退出 0，否则退出 1。此脚本仅取证，不写入正式 tests/checks 或产品实现。

```python
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

sys.path.insert(0, str(Path.cwd()))
from src import order_service as s, storage, ui


def raises(kind, action):
    try:
        action()
    except kind as error:
        return f"{type(error).__name__}: {error}"
    raise AssertionError(f"expected {kind.__name__}")


def run(case):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        def reopen():
            nonlocal connection
            connection.close()
            connection = storage.connect(path)
        def snapshot():
            return connection.execute("SELECT order_id,status FROM orders ORDER BY order_id").fetchall()
        evidence = {}
        try:
            if case == "B01":
                for oid in ("ORDER-1", "订'单;--"):
                    s.create_order(connection, oid)
                reopen()
                assert snapshot() == [("ORDER-1", "pending"), ("订'单;--", "pending")]
                evidence["reopened"] = snapshot()
            elif case == "B02":
                evidence["errors"] = [raises(ValueError, lambda oid=oid: s.create_order(connection, oid)) for oid in ("", None, 42, b"id")]
                reopen()
                assert snapshot() == []
                evidence["reopened"] = snapshot()
            elif case == "B03":
                s.create_order(connection, "ORDER-1")
                evidence["error"] = raises(sqlite3.IntegrityError, lambda: s.create_order(connection, "ORDER-1"))
                connection.rollback()
                reopen()
                assert snapshot() == [("ORDER-1", "pending")]
                evidence["reopened"] = snapshot()
            elif case == "B04":
                s.create_order(connection, "ORDER-1")
                actions = (lambda: s.read_status(connection, "MISSING"), lambda: s.set_status(connection, "MISSING", "paid"), lambda: s.cancel_order(connection, "MISSING"), lambda: s.submit_order(connection, "MISSING"), lambda: ui.mark_paid(connection, "MISSING"))
                evidence["errors"] = [raises(ValueError, action) for action in actions]
                reopen()
                assert snapshot() == [("ORDER-1", "pending")]
                evidence["reopened"] = snapshot()
            elif case == "B05":
                s.create_order(connection, "ORDER-1")
                s.cancel_order(connection, "ORDER-1")
                evidence["after_cancel"] = s.read_status(connection, "ORDER-1")
                assert evidence["after_cancel"] == "cancelled"
                s.cancel_order(connection, "ORDER-1")
                reopen()
                assert s.read_status(connection, "ORDER-1") == "cancelled"
                evidence["reopened"] = snapshot()
            elif case == "B06":
                s.create_order(connection, "ORDER-1")
                evidence["reopened_statuses"] = []
                for status in ("pending", "submitted", "cancelled", "paid"):
                    s.set_status(connection, "ORDER-1", status)
                    reopen()
                    actual = s.read_status(connection, "ORDER-1")
                    assert actual == status
                    evidence["reopened_statuses"].append(actual)
            elif case in ("B07", "B08", "B09", "B10"):
                initial = {"B07": "pending", "B08": "submitted", "B09": "cancelled", "B10": "paid"}[case]
                s.create_order(connection, "ORDER-1")
                if initial == "submitted":
                    assert s.submit_order(connection, "ORDER-1") is True
                elif initial == "cancelled":
                    s.cancel_order(connection, "ORDER-1")
                elif initial == "paid":
                    ui.mark_paid(connection, "ORDER-1")
                evidence["before"] = s.read_status(connection, "ORDER-1")
                assert evidence["before"] == initial
                result = ui.mark_paid(connection, "ORDER-1")
                assert result is None
                evidence["returned"] = result
                reopen()
                assert s.read_status(connection, "ORDER-1") == "paid"
                evidence["reopened"] = snapshot()
            elif case == "B11":
                for oid in ("ORDER-1", "ORDER-2", "ORDER-3"):
                    s.create_order(connection, oid)
                assert s.submit_order(connection, "ORDER-1") is True
                s.cancel_order(connection, "ORDER-2")
                ui.mark_paid(connection, "ORDER-3")
                reopen()
                assert snapshot() == [("ORDER-1", "submitted"), ("ORDER-2", "cancelled"), ("ORDER-3", "paid")]
                evidence["reopened"] = snapshot()
            elif case == "B12":
                s.create_order(connection, "ORDER-1")
                connection.execute("PRAGMA query_only=ON")
                actions = (lambda: s.create_order(connection, "ORDER-2"), lambda: s.set_status(connection, "ORDER-1", "paid"), lambda: s.cancel_order(connection, "ORDER-1"), lambda: s.submit_order(connection, "ORDER-1"), lambda: ui.mark_paid(connection, "ORDER-1"))
                evidence["errors"] = [raises(sqlite3.OperationalError, action) for action in actions]
                reopen()
                assert snapshot() == [("ORDER-1", "pending")]
                evidence["reopened"] = snapshot()
            elif case == "B13":
                s.create_order(connection, "ORDER-1")
                connection.close()
                actions = (lambda: s.create_order(connection, "ORDER-2"), lambda: s.read_status(connection, "ORDER-1"), lambda: s.set_status(connection, "ORDER-1", "paid"), lambda: s.cancel_order(connection, "ORDER-1"), lambda: s.submit_order(connection, "ORDER-1"), lambda: ui.mark_paid(connection, "ORDER-1"))
                evidence["errors"] = [raises(sqlite3.ProgrammingError, action) for action in actions]
                reopen()
                assert snapshot() == [("ORDER-1", "pending")]
                evidence["reopened"] = snapshot()
            elif case == "B14":
                s.create_order(connection, "ORDER-1")
                connection.execute("PRAGMA query_only=ON")
                evidence["error"] = raises(sqlite3.OperationalError, lambda: s.submit_order(connection, "ORDER-1"))
                evidence["after_failure"] = s.read_status(connection, "ORDER-1")
                assert evidence["after_failure"] == "pending"
                reopen()
                accepted = s.submit_order(connection, "ORDER-1")
                assert accepted is True
                evidence["retried"] = accepted
                reopen()
                assert s.read_status(connection, "ORDER-1") == "submitted"
                evidence["reopened"] = snapshot()
            else:
                raise ValueError(case)
        finally:
            connection.close()
    assert not path.exists()
    return {"case": case, "result": "PASS", "evidence": evidence, "cleaned": True}


results = []
for number in range(1, 15):
    case = f"B{number:02}"
    try:
        results.append(run(case))
    except Exception as error:
        results.append({"case": case, "result": "FAIL", "error": f"{type(error).__name__}: {error}"})
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(1 if any(row["result"] == "FAIL" for row in results) else 0)
```

## 4. 失败和复位

每次运行隔离临时目录，脚本 finally 关闭连接，离开目录后删除 SQLite 文件；重复订单异常显式 rollback 后重开，避免将失败事务当作持久化结果。异常结果必须向调用方传播，不能改写断言接受伪成功。只读失败后重新连接恢复正常本地写入能力。AC-2 失败保留原判据并登记 Issue，不在集成阶段修复实现。

AC-3 恢复须由有权人员提供真实外部测试端点、明确调用权限及可运行真实回执核验入口，再由 Main 对齐受影响环境和操作。当前不得自行配置端点、获取凭据或访问网络；本地结果及当前 AC-3 前置检查不能替代真实回执。

## 5. 结果引用

[本轮全功能集成报告](../../docs/test-reports/order/payment-integration.md)、[AC-2 Issue](../../docs/issues/ORDER-001.md)。局部测试 `python -B -m unittest discover -s tests -v` 只作辅助证据，不能替代本指南的全产品集成覆盖。架构结论见[独立 Review](../../docs/test-reports/order/payment-alignment-review.md)，实施见[唯一 Plan](payment-refactor-plan.md)。
