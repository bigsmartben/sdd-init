# 订单验收指南

## 1. 验证目标与范围

依据 [Spec](spec.md)、[订单契约](../../docs/contracts/order.md) 和 [环境条件](../../runtime.json)，覆盖新建、取消、提交、公开 `ui.mark_paid`、服务 `set_status`、输入及不存在对象异常、数据库错误和 AC-3。无 UI，无需人工视觉判断。状态组合仅按已确认契约推导；不为 paid 后提交、重复新建等未定义行为新增判据。

## 2. 环境与入口

在当前隔离项目根目录执行。目标为初始实际快照及其修复后实际快照；每批用 `git rev-parse HEAD`、`git status --short` 和 `python -B checks/runtime_details.py` 记录提交、相关工作区差异及源文件 SHA-256，不能用 HEAD 单独代表未提交修复。

使用 Python 3.11+、标准库 SQLite，无需依赖安装。每场景创建独立临时文件数据库，使用订单 `ORDER-1`，异常新建用 `ORDER-2`，不存在对象用 `MISSING`。输入边界取空串、None 和整数，来自订单编号为非空字符串的条件。数据库故障用真实 SQLite `PRAGMA query_only = ON`，只证明写入受限时异常传播与状态保持，不模拟外部服务或产品实现。

```bash
python -B checks/order_regression.py
python -B checks/order_regression.py --scenario AC-2
python -B checks/runtime_details.py
python -B -m unittest discover -s tests -v
```

集成入口 JSON 中每场景含结果及观测；退出码 0 为全部通过，1 为存在失败，3 为无失败但存在阻塞。单测为辅助，不能替代集成回归。原 `checks/acceptance.py` 仍可单独执行 AC-1、AC-2、AC-3。

## 3. 场景验证

所有下表操作均由 `python -B checks/order_regression.py --scenario <场景>` 执行，实际调用 `src` 正式入口，保留返回、异常及数据库观测。

| 场景 / 依据 | 前置与操作 | 预期与证据 |
| --- | --- | --- |
| CREATE / 新建契约 | 空数据库，新建 ORDER-1；另开连接读取 | pending 已持久化 |
| AC-1 / 提交 | 新建后 submit；关闭并重开数据库 | 返回 true，submitted |
| CANCEL / 取消契约 | 新建后 cancel；另开连接读取 | cancelled 已持久化 |
| AC-2 / 取消后提交 | 新建、cancel、submit；关闭并重开数据库 | 返回 false，cancelled 不被覆盖；total_changes=0，提交 trace 仅 SELECT |
| PAID-PENDING / paid 契约 | 新建后公开 ui.mark_paid | pending 中间态、paid 持久化 |
| PAID-CANCELLED / paid 契约 | 新建、cancel、公开 ui.mark_paid | cancelled 中间态、paid 持久化 |
| PAID-SUBMITTED / paid 契约 | 新建、submit、公开 ui.mark_paid | submitted 中间态、paid 持久化 |
| SET-STATUS / 服务契约 | 新建后 set_status(..., paid) | paid 已持久化 |
| INVALID-ID / 输入契约 | 分别用空串、None、0 新建 | 均 ValueError，数据库无订单 |
| MISSING / 不存在对象契约 | 空数据库，分别 cancel、submit、set_status(paid)、公开 mark_paid | 均 ValueError，逐入口记录 |
| DB-ERROR / 数据库异常契约 | 新建 pending，启用 query_only；分别 create、cancel、submit、set_status、公开 mark_paid | 所有真实 SQLite 写入异常向上传播，不返回成功；回滚后文件数据库仍 pending 且只有原订单 |
| AC-3 / 外部回执 | 检查 runtime.json 的真实端点与授权 | 当前缺失时 BLOCKED，绝不由本地结果替代 |

## 4. 失败与恢复

每个场景独立，连接关闭后临时目录自动清理；复跑无需保留数据库。产品失败按原 Issue 处理并在修复实际快照上复验，不能放宽断言。AC-3 需要有权人员提供真实测试服务端点和调用权限，且运行环境允许网络，并具备可核验真实回执的执行入口；本轮无外部配置、凭据获取或网络调用授权。

## 5. 结果入口

[初测报告](../../docs/test-reports/order/initial.md) 记录逐项结果、实际版本和缺陷；[修复后复验报告](../../docs/test-reports/order/retest.md) 另行保留实际源哈希和完整复验结果。自动结果不代表人工反馈；本范围无需人工视觉验收。
