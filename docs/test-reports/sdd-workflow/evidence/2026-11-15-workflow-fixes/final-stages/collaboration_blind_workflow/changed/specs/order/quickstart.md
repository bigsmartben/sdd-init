# 订单验收指南

依据：[订单需求](spec.md) AC-1、AC-2、AC-3 及[函数契约](../../docs/contracts/order.md)。范围为本地无 UI 的 CLI／库产品，覆盖新建、取消、提交、状态写入、现存订单 paid 持久化、已约定异常和真实外部回执。无需人工视觉确认。

## 1. 版本与准备

在本次隔离项目根目录运行，Python 3.11+ 与标准库 SQLite，无额外依赖。当前修复候选 `src/order_service.py` SHA-256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`。执行 `python -B checks/runtime_details.py` 核对真实 Python、SQLite、配置及源文件哈希；该命令只提供环境事实。

每个本地场景使用全新临时目录中的 SQLite 文件，常规数据 `ORDER-1`、不存在编号 `MISSING`，非法新建输入为空串、None、整数。这些数据从非空字符串约束和缺失订单异常条款推导。测试结束关闭数据库并清理临时目录；锁冲突检查先 rollback 再关闭。运行不需要账户、外部端点或网络权限。

## 2. 可复跑场景

| 功能 / 场景 | 操作入口与前置 | 判断点 / 证据 |
|---|---|---|
| AC-1 新建后提交 | `python -B checks/acceptance.py --scenario AC-1`；新文件数据库 | 返回 true，关闭重开后 submitted；保存 JSON 及退出码。 |
| AC-2 取消后提交 | `python -B checks/acceptance.py --scenario AC-2`；新建后取消 | 返回 false，关闭重开后 cancelled；保存 JSON 及退出码。 |
| AC-3 真实外部回执 | `python -B checks/acceptance.py --scenario AC-3` | 当前入口仅检查 runtime.json 并返回 BLOCKED，不发送外部请求，不能核验真实回执。 |
| CT-01～CT-04 持久化及 paid 保持 | `python -B docs/test-reports/order-integration/contract_checks.py` | 通过公开函数创建、取消、写四个合法状态、标记现存订单 paid；独立文件连接读取已提交状态。 |
| CT-05～CT-10 输入与缺失订单 | 同一契约检查入口，逐项查看 case | 空串、None、整数创建应抛 ValueError；读取、取消、提交、状态写入、paid 的缺失订单异常应为 ValueError。 |
| CT-11～CT-12 数据库错误与恢复 | 同一入口；关闭连接及真实 SQLite 读锁 | 数据库异常向上传播；被锁 commit 不返回成功，读者仍看到 pending，rollback 后持久状态 pending。 |
| CT-13 取消不可被提交覆盖 | 同一入口；观察 SQL trace 和变化数 | false，零写入，无事务开启，持久状态 cancelled。 |
| CT-14 本地操作无网络 | 同一入口；Python socket 审计 | 本地实际操作不发生连接、解析或发包事件；不替代外部回执测试。 |

`python -B checks/acceptance.py` 执行全部 AC。退出码 0 为全部通过、1 为存在失败、3 为无失败但存在阻塞。契约检查入口退出码 0 为全部通过、1 为存在失败，逐项 JSON 为实际结果。

`python -B docs/test-reports/order-integration/run_batch.py` 在精确匹配上述候选哈希后执行三个 AC、契约检查和环境检查，保存原始 stdout、stderr、各子进程退出码及前后哈希到本批次目录。该记录器自身正常结束不代表子检查通过；以 execution.json 的各项退出码和报告 Gate 为准。再次运行会覆盖同名证据，保留历史批次时应先另存该目录。

## 3. 失败与恢复

本地每次复跑自动创建全新数据。发生断言或数据库异常时，查看逐项结果和 stderr，修复授权范围内的测试准备问题后重跑；产品缺陷交 Main，不调整已确认判据。不存在订单的 ValueError 条款与正常操作需订单存在的前置分别适用于异常、正常路径。

AC-3 必须由有权人员提供真实测试服务端点、调用权限及可核验回执方式，并具备获授权的真实调用入口后恢复。现有 acceptance.py 不进行外部调用，配置就绪也不能单凭该脚本宣告通过。本轮不得自行获取凭据、配置服务、部署或用本地／模拟回执替代。

## 4. 结果引用

实际版本、逐项结果、原始证据、缺陷、未验证范围及 Test Gate 见[集成报告](../../docs/test-reports/order-integration/report.md)。原 BUG-001 的独立定向复验见[修复复验报告](../../docs/test-reports/order-cancel/bugfix-retest.md)，不能替代整轮集成。
