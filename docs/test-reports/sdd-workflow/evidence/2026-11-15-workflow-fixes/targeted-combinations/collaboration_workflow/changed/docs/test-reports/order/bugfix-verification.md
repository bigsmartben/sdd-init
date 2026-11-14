# Bugfix — ORDER-001 / ORDER-002 定向复验

2026-11-14T16:24:37Z，执行者 `/root/bugfix`，实际调用者 Main `/root`。本报告为缺陷归因、局部自验及定向复验；不判定整轮 Test Gate 或 Review Gate。

## 实际版本与环境

基于 HEAD `a8f4cf7154b9e81d9b4ab62b8cd0cecddb36eec5` 的未提交 src/tests 修复；[实际快照](bugfix-snapshot.json) 包含完整 diff、Python/SQLite 版本及全部源哈希。临时文件 SQLite 每场景隔离，本轮无外部调用、配置或部署操作。产品文件哈希：

| 文件 | SHA-256 |
| --- | --- |
| src/order_service.py | 3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb |
| src/ui.py | c4a9e5b0789129c89bb71387e2aaed619944d115aff5a53c7fb5320fcbff88ae |

## 归因与变更

[修复前证据](bugfix-diagnosis.json) 在同一环境复现两项原故障：AC-2 为 true/submitted，MISSING 的 mark_paid 无异常。submit_order 丢弃读出的状态并无条件写 submitted，是取消被覆盖的直接原因；ui.mark_paid 直接 UPDATE，不调用服务存在检查，SQLite 的零行 UPDATE 不报错，是缺失对象静默成功的直接原因。其他缺失对象服务入口 ValueError，支持问题位于 UI 调用路径而非数据库初始化。

修复为读取 cancelled 后直接 False；公开 mark_paid 调用既有 order_service.set_status(..., paid)。现存订单 paid 结果与服务入口保持，未新增状态或接口。[实施工单](../../plans/order-fixes.md) T001。

## 定向复验与原始证据

[原始运行结果](bugfix-results.json) 逐条保留实际命令、退出码及 stdout/stderr；所有列项退出码均为 0。

| 覆盖 | 实际结果 / 证明范围 |
| --- | --- |
| 原 ORDER-001 / AC-2 | 公开 submit 返回 false，关闭重开文件数据库 cancelled |
| 无写入边界 | unittest 的真实 SQLite SQL trace 仅 SELECT；公开 submit 的 commit 代理调用计数为 0；关闭重开仍 cancelled |
| 原 ORDER-002 / MISSING | 公开 ui.mark_paid、cancel、submit、set_status 对不存在对象均 ValueError |
| 受影响 paid | checks 覆盖 pending/cancelled/submitted；unittest 另含已有 paid，公开 ui.mark_paid 后另开连接均 paid |
| AC-1、CREATE、CANCEL、SET-STATUS、INVALID-ID | 所有原有返回、状态、输入异常及持久化判据通过 |
| DB-ERROR | 真实 SQLite query_only 写入失败，create/cancel/submit/set_status/mark_paid 均传播 OperationalError，持久状态及条数保持 |
| commit 失败传播 | CommitProbe 转交真实 SQLite SQL，在 commit 方法注入 OperationalError；五个写入口均向上传播，无成功返回；第二连接保持原持久状态，随后由测试调用者 rollback |
| unittest | 6 个测试通过，含上述边界及已有两项正常路径 |
| diff | git diff --check 通过 |

复跑入口：`python -B checks/order_regression.py --scenario <场景>`，场景依次 AC-1、AC-2、MISSING、PAID-PENDING、PAID-CANCELLED、PAID-SUBMITTED、DB-ERROR、CREATE、CANCEL、SET-STATUS、INVALID-ID；`python -B -m unittest discover -s tests -v`。

## 状态与局限

原场景和必要定向回归证据齐备，两项原 Issue 由获授权的 Bugfix 关闭。commit 代理属于局部机制证据，不是实际磁盘或 SQLite 引擎 commit 故障的实测；实际 SQLite 错误证据仅覆盖 query_only 写入受限。保持调用者负责连接及事务清理的既有契约，本次未增加回滚、重试、日志或网络行为。未定义状态提交行为不新增判据。

独立全产品集成及架构复核由 Main 续派原 Agent；本次未运行 AC-3，外部真实服务所需端点和权限仍由原批次处理，局部通过不代替该证据。
