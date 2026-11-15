# 订单验收指南

## 1. 验证目标与范围

依据：[Spec](spec.md)、[函数契约](../../docs/contracts/order.md)。覆盖新建、取消、提交、公开付款、异常与边界、持久化和多订单协同，以及 AC-3 外部回执。本项目没有图形 UI，不需要人工视觉验收。重复提交、paid 后提交没有确认判据，本指南不新增其状态语义。

## 2. 环境与启动

在当前隔离项目根目录，使用 Python 3.11+ 和标准库 SQLite，无额外依赖。目标为 Main 指定的当前或修复后实际源码快照；每轮报告记录 HEAD、src SHA-256、相关未提交修改与实际 Python/SQLite。可用 `git status --short`、`git rev-parse HEAD` 及 `python -B checks/runtime_details.py` 核对。

```bash
mkdir -p .tmp/order-tests
TMPDIR="$PWD/.tmp/order-tests" python -B tests/integration_order.py
TMPDIR="$PWD/.tmp/order-tests" python -B checks/acceptance.py
TMPDIR="$PWD/.tmp/order-tests" python -B -m unittest discover -s tests -v
python -B checks/runtime_details.py
```

集成脚本每个场景新建临时目录下的真实 SQLite 文件，使用公开 `src.order_service`、`src.ui.mark_paid` 与 `src.storage.connect`，结束关闭连接和删除临时数据。新建 ORDER-1，及用于隔离验证的 A、订单-二；空值/非字符串、重复键、缺失订单和只读数据库由契约推导，均为本地常规测试数据。没有模拟数据库或外部网络。集成脚本退出 0 表示全部本地用例通过、1 表示至少一个失败；公开 checks 退出码为 0 全通过、1 有失败、3 无失败但有阻塞。局部单元测试只能补充证据。

## 3. 场景验证

下列场景由上述集成脚本一次执行，逐项输出 JSON。状态持久化用例关闭原连接并重开文件；I15 另开连接读取已提交状态。每轮保留完整 JSON、版本哈希及公开 checks 输出。

| Case / 功能依据 | 前置数据 | 公开操作与观察 | 通过判据 |
|---|---|---|---|
| I01 / 创建契约 | 新文件数据库 | create_order，read_status，关闭重开 | pending 已持久化 |
| I02 / AC-1 | 新建 ORDER-1 | submit_order，关闭重开读取 | 返回 true，submitted |
| I03 / 取消契约 | 新建 ORDER-1 | cancel_order，关闭重开 | cancelled |
| I04 / AC-2 | 新建 ORDER-1 | 取消后先读取 cancelled，再 submit_order，关闭重开 | 返回 false，仍 cancelled |
| I05 / 公开付款 | pending 订单 | ui.mark_paid，关闭重开 | paid |
| I06 / 提交与付款协同 | pending 订单 | 提交、观察 submitted、公开付款、关闭重开 | 提交 true，最终 paid |
| I07 / 现存订单付款 | pending 订单 | 取消、观察 cancelled、公开付款、关闭重开 | 最终 paid，保持 Spec 既有任何现存订单付款行为 |
| I08 / 输入边界 | 新文件数据库 | 依次用空字符串、None、整数新建 | 每项 ValueError，零行 |
| I09 / 重复键异常 | 新建 ORDER-1 | 同 ID 再新建，关闭重开 | SQLite IntegrityError 向上传播，原记录 pending |
| I10 / 取消异常 | 无 MISSING 订单 | cancel_order(MISSING) | ValueError，零行 |
| I11 / 提交异常 | 无 MISSING 订单 | submit_order(MISSING) | ValueError，零行 |
| I12 / 付款异常 | 无 MISSING 订单 | ui.mark_paid(MISSING) | ValueError，零行 |
| I13 / 服务写入异常 | 无 MISSING 订单 | set_status(MISSING, paid) | ValueError，零行 |
| I14 / 数据库异常 | 新建订单，PRAGMA query_only=ON | 依次取消、提交、付款，关闭重开 | 三次 OperationalError 向上传播，订单 pending |
| I15 / 多订单与非空字符串边界 | A 和 订单-二 | 取消 A，提交另一个，另开连接读取 | true；分别 cancelled、submitted |
| I16 / AC-3 | runtime.json 外部条件 | `python -B checks/acceptance.py --scenario AC-3` | 获授权真实服务回执；缺端点或权限为 BLOCKED，禁止用本地结果代替 |

另执行原始 `checks/acceptance.py`，AC-1/AC-2 分别补强 I02/I04，以同一业务场景计数，避免重复计算。数据库或内部读取仅辅助观察；判定来自公开操作结果及真实持久化。

## 4. 失败与恢复

本地每例数据隔离，重跑命令自动新建文件；不接触原仓、已安装工作流或外部平台。临时目录由 Python 清理，`.tmp/order-tests` 可保持为空。实现失败由对应 Issue 跟踪，修复后按实际新哈希重跑全部本地场景及公开 checks，保留初轮失败证据。

AC-3 当前没有端点和权限。本轮不得配置外部服务或获取凭据；恢复需有权人员提供已授权测试服务端点、调用权限及真实回执入口。当前 checks 夹具始终阻塞且不会联网，即使配置字段改变也不能充当真实服务验收，需在授权环境准备可访问真实服务的验收入口后再执行。

## 5. 结果与进度

[初轮集成报告](../../docs/test-reports/order/initial.md)、[修复后集成复验](../../docs/test-reports/order/fixed.md)、[BUG-001](../../docs/issues/BUG-001.md)、[BUG-002](../../docs/issues/BUG-002.md)。报告记录实际执行结果、外部阻塞和 Gate；后续修复版本另建批次，保留历史失败。
