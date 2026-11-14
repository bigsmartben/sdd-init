# 订单用户验收指南

## 1. 目标与范围

依据 [订单需求](spec.md)、[订单函数契约](../../docs/contracts/order.md)及根目录 [测试工单](../../TASK.txt)，在当前隔离订单环境验收 AC-1 正常提交、AC-2 取消后拒绝提交、AC-3 真实外部回执。补充核验已明确要求保持的 paid 行为、订单编号边界、不存在订单和数据库异常。无图形界面，不需要人工视觉判断；不改变业务判据。

## 2. 版本、环境与入口

本批目标及实测版本为 `5cf8f4dfb11879bf0f82e0808cb71dfc0c2b6932`。从本隔离项目根目录运行，先执行：

```bash
git rev-parse HEAD
git status --short
python -B checks/runtime_details.py
```

核对 HEAD 与 [版本及文件哈希](../../docs/test-reports/order/2026-11-15-evidence/version.json)一致。运行 `runtime_details.py` 得到的源文件 SHA-256 应与本批一致；文档变化不改变受测代码。不同版本需另立批次并分析影响，勿覆盖本批证据。

环境由 [runtime.json](../../runtime.json)定义为 `isolated-local-fixture`，Python 标准库和文件 SQLite；每个场景使用独立临时数据库，无外部账户。本批 Python 3.12.3、SQLite 3.45.1。根目录 `src` 为真实受测模块，无替身组件。无常驻进程、无需部署。文件系统须允许建立临时文件；异常测试使用 SQLite 原生只读事务设置模拟数据库拒写，不替代业务模块。

本轮 `external_endpoint=null`，`external_call_authorized=false`，`network_access_in_this_run=false`。AC-3 的 CLI 只报告就绪条件，不访问真实服务。不得配置凭据、调用外部服务或用本地成功冒充外部证据。

## 3. 场景与复跑步骤

先执行现有真实验收入口：

```bash
python -B checks/acceptance.py --scenario AC-1
python -B checks/acceptance.py --scenario AC-2
python -B checks/acceptance.py --scenario AC-3
python -B checks/acceptance.py
python -B -m unittest discover -s tests -v
```

验收命令退出码：0 为所选场景通过；1 为存在失败；3 为存在阻塞。全量命令在失败与阻塞并存时返回 1，必须同时阅读逐项 JSON。unittest 是辅助证据，不能代替 AC-2、AC-3。

| Case / 需求依据 | 前置与操作 | 预期及观察 | 必要证据 |
|---|---|---|---|
| AC-1 / Spec AC-1 | CLI 新建 ORDER-1，提交，关闭并重开文件数据库 | accepted=true，persisted_status=submitted | CLI JSON、版本、退出码 |
| AC-2 / Spec AC-2 | CLI 新建 ORDER-1，取消，再提交，重开数据库 | accepted=false，persisted_status=cancelled | CLI JSON、版本、退出码 |
| AC-3 / Spec AC-3 | 检查真实端点和授权后，从真实外部测试服务取得提交回执 | 真实回执符合约定；本环境缺少前提则 BLOCKED | 就绪 JSON；以后恢复需真实服务证据，CLI 本身不足 |
| TC-4 / Spec paid、创建契约 | 下方补充命令：新建 P，观察 pending，调用 mark_paid，重开数据库 | 初始 pending、最终 paid | supplemental JSON 中初始状态和持久化状态 |
| TC-5 / 非空字符串编号 | 下方补充命令：以空字符串、None、整数调用 create_order | 均 ValueError；未创建数据 | 异常类别与数据库行数 |
| TC-6 / 不存在订单异常契约 | 下方补充命令：无订单时调用 read_status、cancel_order、submit_order、set_status、mark_paid | 五个操作均 ValueError；无订单新增 | 各入口异常类别与数据库行数 |
| TC-7 / 数据库异常向上传播 | 下方补充命令：query_only=ON，分别调用 create_order、cancel_order、submit_order、set_status、mark_paid | 均传播 SQLite 异常；现存订单保持 pending | 异常类别、状态、无新增订单 |

常规数据和异常由契约推导：ORDER-1/P 为非空字符串，空字符串及非字符串验证输入边界；缺失 ID 验证异常；只读事务验证数据库异常。下方命令仅调用公开函数并观察真实数据库，不保存或修改测试代码。可直接复制整段到项目根目录执行：

<!-- supplemental-command:start -->
```bash
python -B - <<'PY'
import json, sqlite3, tempfile
from pathlib import Path
from src import order_service as service, storage, ui

results = []
def exception_name(action):
    try:
        action()
    except Exception as error:
        return type(error).__name__
    return None

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'orders.sqlite'
    connection = storage.connect(path)
    try:
        service.create_order(connection, 'P')
        initial = service.read_status(connection, 'P')
        ui.mark_paid(connection, 'P')
    finally:
        connection.close()
    connection = storage.connect(path)
    try:
        persisted = service.read_status(connection, 'P')
    finally:
        connection.close()
    results.append({'case': 'TC-4', 'result': 'PASS' if (initial, persisted) == ('pending', 'paid') else 'FAIL', 'initial': initial, 'persisted': persisted})

with tempfile.TemporaryDirectory() as directory:
    connection = storage.connect(Path(directory) / 'orders.sqlite')
    try:
        errors = [exception_name(lambda value=value: service.create_order(connection, value)) for value in ('', None, 7)]
        count = connection.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
        results.append({'case': 'TC-5', 'result': 'PASS' if errors == ['ValueError'] * 3 and count == 0 else 'FAIL', 'errors': errors, 'row_count': count})
        actions = {'read_status': lambda: service.read_status(connection, 'missing'), 'cancel_order': lambda: service.cancel_order(connection, 'missing'), 'submit_order': lambda: service.submit_order(connection, 'missing'), 'set_status': lambda: service.set_status(connection, 'missing', 'paid'), 'mark_paid': lambda: ui.mark_paid(connection, 'missing')}
        errors = {name: exception_name(action) for name, action in actions.items()}
        count = connection.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
        results.append({'case': 'TC-6', 'result': 'PASS' if all(value == 'ValueError' for value in errors.values()) and count == 0 else 'FAIL', 'errors': errors, 'row_count': count})
    finally:
        connection.close()

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'orders.sqlite'
    connection = storage.connect(path)
    try:
        service.create_order(connection, 'P')
        connection.execute('PRAGMA query_only=ON')
        actions = {'create_order': lambda: service.create_order(connection, 'NEW'), 'cancel_order': lambda: service.cancel_order(connection, 'P'), 'submit_order': lambda: service.submit_order(connection, 'P'), 'set_status': lambda: service.set_status(connection, 'P', 'paid'), 'mark_paid': lambda: ui.mark_paid(connection, 'P')}
        errors = {name: exception_name(action) for name, action in actions.items()}
    finally:
        connection.close()
    connection = storage.connect(path)
    try:
        status = service.read_status(connection, 'P')
        count = connection.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    finally:
        connection.close()
    results.append({'case': 'TC-7', 'result': 'PASS' if all(value == 'OperationalError' for value in errors.values()) and status == 'pending' and count == 1 else 'FAIL', 'errors': errors, 'persisted': status, 'row_count': count})
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(1 if any(row['result'] == 'FAIL' for row in results) else 0)
PY
```
<!-- supplemental-command:end -->

## 4. 失败与恢复

临时目录在连接关闭后自动清理，重跑会创建全新数据库，无需改动实现、测试或运行配置。进程异常中断时确认没有遗留连接，仅清理该次自建临时目录，不删除其他数据。数据库拒写仅作用于临时连接，连接关闭即解除。

AC-2 或其他判据不符时保留失败，不在本工单修复。修复需要另行授权；修复后按原编号复验，并回归正常提交、paid 与异常路径。AC-3 恢复需要 Main 另行取得真实测试端点、外部操作与网络授权以及可执行的服务回执判据；当前 CLI 永远只输出阻塞，因此还需提供真实外部验证入口。本轮不做这些操作。

## 5. 结果引用

本批实际结果、Gate、缺陷及恢复条件见 [集成测试报告](../../docs/test-reports/order/2026-11-15.md)；逐项输出归报告相邻 evidence 目录。执行结果与未来人工反馈分别记录，不以本指南中的预期代替结果。
