# 订单验收指南

## 1. 验收目标和范围

依据：[订单 Spec](spec.md)、[订单函数契约](../../docs/contracts/order.md)。范围为已确认的提交、取消、付款及外部回执路径，含本地真实组件组合、错误与持久化。本项目没有 UI，无需人工视觉验收。付款保持行为以契约为准；下列扩展场景是从已确认契约推导的常规数据、异常及组合覆盖，不新增业务规则。

## 2. 环境与入口

在生成的隔离项目根目录执行，Python 3.11+、标准库 SQLite，无需安装依赖、账号、后台服务或网络。产品候选为 `1c6b8ab84d68d21144d549aa4eb717903896a828`，本批次仅改测试工具和文档。用 `git rev-parse HEAD` 与 `git diff -- src runtime.json` 核对；用 `python -B checks/runtime_details.py` 查看实际 Python/SQLite、配置及产品 SHA-256，和报告中的证据核对。版本变化后不能直接沿用旧报告。

```sh
python -B checks/integration_runner.py
python -B checks/integration_runner.py --scenario AC-1
python -B checks/acceptance.py
python -B checks/runtime_details.py
python -B -m unittest discover -s tests -v
```

CI 正式入口是 `checks/integration_runner.py`；`acceptance.py` 使用同一实际场景执行器。每个场景使用独立临时目录和文件 SQLite，构造 `ORDER-1`（编号边界场景例外），连接均关闭后清理。真实组件为 src 的服务、付款适配函数和 SQLite；不替换产品实现或预存业务结果。工具语义单测中的 mock 不提供产品验收证据。

## 3. 场景与判据

将下表 ID 代入 `python -B checks/integration_runner.py --scenario <ID>` 单独复跑；不传 ID 则执行全部。观察 JSON 的 `result`、`expected`、`actual` 和中间状态，并同时记录进程退出码。每项证据须关联实际版本和环境；本轮原始输出见报告。

| 场景 / 依据 | 实际操作和前置数据 | 预期与关键观察点 |
| --- | --- | --- |
| AC-1 | pending → submit → 关闭并重开 | 返回 true，状态 submitted |
| AC-2 | pending → cancel → submit → 关闭并重开 | 返回 false，仍为 cancelled |
| AC-3 | 读取 runtime.json 的端点和调用授权 | 真实授权外部服务回执；条件未就绪时 BLOCKED，不访问网络 |
| LOCAL-create | create → 关闭并重开 | pending |
| LOCAL-cancel | create → cancel → 关闭并重开 | cancelled |
| PAID-pending | 创建 pending 前置状态 → ui.mark_paid → 关闭并重开 | paid；付款结果持久化 |
| PAID-submitted | 创建 submitted 前置状态 → ui.mark_paid → 关闭并重开 | paid；付款结果持久化 |
| PAID-cancelled | 创建 cancelled 前置状态 → ui.mark_paid → 关闭并重开 | paid；付款结果持久化 |
| MISSING-read_status | 对不存在订单调用 read_status | ValueError；不创建订单 |
| MISSING-set_status | 对不存在订单调用 set_status | ValueError；不创建订单 |
| MISSING-cancel_order | 对不存在订单调用 cancel_order | ValueError；不创建订单 |
| MISSING-submit_order | 对不存在订单调用 submit_order | ValueError；不创建订单 |
| MISSING-mark_paid | 对不存在订单调用 mark_paid | ValueError；不创建订单 |
| INVALID-empty | create 的编号分别为空字符串、None、整数（按场景选择） | ValueError；无新增行 |
| INVALID-none | create 的编号分别为空字符串、None、整数（按场景选择） | ValueError；无新增行 |
| INVALID-integer | create 的编号分别为空字符串、None、整数（按场景选择） | ValueError；无新增行 |
| VALID-single | create 合法单字符或 Unicode 编号 → 关闭并重开 | pending；编号原样保存 |
| VALID-unicode | create 合法单字符或 Unicode 编号 → 关闭并重开 | pending；编号原样保存 |
| LOCK-create | 独立 SQLite 连接持有写锁 → 调用 create → 释放锁并重开 | OperationalError 向上传播，无成功返回，持久状态不变 |
| LOCK-cancel | 独立 SQLite 连接持有写锁 → 调用 cancel → 释放锁并重开 | OperationalError 向上传播，无成功返回，持久状态不变 |
| LOCK-submit | 独立 SQLite 连接持有写锁 → 调用 submit → 释放锁并重开 | OperationalError 向上传播，无成功返回，持久状态不变 |
| LOCK-set_status | 独立 SQLite 连接持有写锁 → 调用 set_status → 释放锁并重开 | OperationalError 向上传播，无成功返回，持久状态不变 |
| LOCK-paid | 独立 SQLite 连接持有写锁 → 调用 paid → 释放锁并重开 | OperationalError 向上传播，无成功返回，持久状态不变 |
| CLOSED-read_status | 关闭连接后读取订单 | ProgrammingError 向上传播 |
| LOCAL-no-network | socket guard 中执行新建、提交、取消、set_status、付款及读取 | 无网络调用；最终 paid |

## 4. 异常与复位

退出码为 0（所有所选场景 PASS）、1（至少一个 FAIL，优先于 BLOCKED）、3（没有 FAIL 但存在 BLOCKED）。JSON 中外部回执 BLOCKED 不等于已取真实服务证据。入口输出完整业务结果而返回 1/3，说明工具可运行；不能据此声称 Test Gate PASS。

每次执行重新构造数据，不依赖前一场景或历史数据库；写锁场景释放占锁连接后检查状态并清理。普通场景异常捕获为 FAIL 后继续其余场景。发现产品失败保留判据，按原场景复验修复版本；本轮产品冻结。

AC-3 当前由 runtime.json 表明端点缺失、调用未授权、本轮禁网络，保持 BLOCKED。恢复需要有权人员提供真实已授权外部测试服务端点、调用权限和允许联网的测试环境，再由 Main 协调实测；不能只改配置后把本地模拟视为回执，也不能在本轮自行配置、获取凭据或访问服务。

## 5. 结果与进度

[本轮集成报告](../../docs/test-reports/order/integration-2026-11-15.md)记录实际结果、工具原始失败与恢复、产品版本和 Test Gate；[当前状态](../../docs/status.md)引用其结论。局部单测不能替代完整集成结果，运行条件哈希也不证明场景已执行。
