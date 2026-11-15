# Quickstart — 订单产品全功能点集成回归

## 1. Verification Goal and Scope

依据：[订单 Spec](spec.md)、[函数契约](../../docs/contracts/order.md)、[环境](../../runtime.json)。覆盖新建、取消、提交、公开 `ui.mark_paid`、文件 SQLite 持久化、合法状态写入、异常传播与恢复、跨订单组合及 AC-3。保持函数接口及确认行为；无图形 UI，无需人工视觉确认。未规定的重复提交、重复编号等业务规则不新增判断标准。

## 2. Setup and Launch

在当前隔离项目根目录，使用 Python 3.11+ 和标准库 SQLite，无需安装依赖。使用 `git rev-parse HEAD` 与 `python -B checks/runtime_details.py` 核对实际提交、运行时与源哈希；相关未提交实现以报告证据中的源哈希区分。

每个场景由验证脚本创建独立临时目录中的真实 SQLite 文件，结束时关闭连接并清理。测试数据是 `ORDER-1`，多订单场景另用 Unicode 非空编号 `订单-β`；空字符串、None、数字仅测试非空字符串约束。数据库异常使用真实 SQLite `PRAGMA query_only=ON`，无替身数据库。

完整入口：`python -B checks/integration.py`。逐项入口：`python -B checks/integration.py --case <下表编号>`。输出 JSON 包含逐项实际结果、时间、版本、测试脚本与源哈希、源运行前后稳定性、运行条件及统计。退出码 0 全通过、1 有失败、3 无失败但存在阻塞。

既有验收入口 `python -B checks/acceptance.py` 执行 AC-1/2/3；既有单元测试 `python -B -m unittest discover -s tests -v` 为辅助证据，不能替代完整覆盖。所有本地业务入口不访问网络；AC-3 在本轮缺少真实外部端点与调用授权，只报告阻塞。

## 3. Scenario Verification

每行以独立数据库起步，命令统一为 `python -B checks/integration.py --case 编号`。实际中间状态、错误类型与重开读取结果见该命令 JSON 的 `observed`。

| Feature / Scenario / AC | Preconditions | Action or command | Expected outcome and observation | Required evidence |
|---|---|---|---|---|
| NEW-1 / 新建 | 空文件库 | 新建 ORDER-1，另开连接读取 | pending 已持久化 | pending 重开读取结果 |
| NEW-2 / 编号边界 | 空文件库 | 分别以空串、None、0 新建 | 均抛 ValueError | 各输入异常类型 |
| AC-1 / 提交 | 新建 pending | submit_order，再重开读取 | 返回 true，submitted | 提交前状态、返回值、持久化状态 |
| CANCEL-1 / 取消 | 新建 pending | cancel_order，再重开读取 | cancelled | 持久化状态 |
| AC-2 / 取消不可覆盖 | 新建并取消 | submit_order，再重开读取 | 返回 false，保持 cancelled | 取消后中间状态、返回值及最终状态 |
| PAID-1 / 公开付款 | 现存 pending | ui.mark_paid，再重开读取 | paid | 前态与持久化状态 |
| PAID-2 / 提交后付款 | pending 提交 | ui.mark_paid，再重开读取 | paid | submitted 前态及 paid 结果 |
| PAID-3 / 取消后付款 | pending 取消 | ui.mark_paid，再重开读取 | paid，沿用契约对现存订单的要求 | cancelled 前态及 paid 结果 |
| STATUS-1 / 合法状态入口 | 现存订单 | 依次 set_status 为 submitted、cancelled、paid、pending | 各状态均持久化 | 每次请求与另开连接结果 |
| MISSING-1 / 对象缺失 | 空文件库 | 调用 read_status、cancel_order、submit_order、set_status、ui.mark_paid | 均抛 ValueError | 分接口异常结果 |
| DB-1 / 写入异常 | pending，连接 query_only=ON | 对 create/cancel/submit/set_status/mark_paid 调用真实接口 | sqlite3.OperationalError 向上传播，原订单仍 pending | 各接口异常类型及持久化状态 |
| ISOLATION-1 / 组合与编号边界 | ORDER-1 与订单-β | 第一单取消，第二单付款，再提交第一单 | 第一单 false/cancelled，第二单 paid | 两单最终状态和提交返回值 |
| RECOVERY-1 / 故障恢复 | pending，query_only=ON | 提交失败、rollback、query_only=OFF，再提交 | 首次数据库异常；恢复后 true/submitted | 首次错误、恢复后返回值与持久化 |
| AC-3 / 真实外部回执 | 已授权真实测试服务 | 读取当前 runtime 条件；本轮缺权限不发网络请求 | 当前 BLOCKED；不得以本地或模拟结果代替真实服务 | 配置事实、未发请求说明和恢复条件 |

这些正常、异常、边界与组合步骤由已确认 Spec 和契约推导，没有新增业务语义。所有状态验证通过正式读取入口及新连接观察真实文件数据库提交结果。

## 4. Failures and Recovery

每个用例自动清理临时数据库，复跑即重新准备，无需手动恢复产品数据。RECOVERY-1 在同一真实连接内恢复可写状态后重试，证据保留失败与恢复两个阶段。数据库异常向上传播；不转为成功。

AC-3 恢复需有权人员提供真实外部测试服务端点、调用权限及受授权的实际调用路径。当前入口不会调用外部服务，即使配置后来补齐也不能据其输出宣称 AC-3 通过；届时须在获授权环境中执行真实回执核验并留证。本轮不自行配置服务、获取凭据或部署。

## 5. Results and Progress References

- [修复快照全量复验](../../docs/test-reports/order/fixed.md)
- [当前基线报告](../../docs/test-reports/order/baseline.md)
- [ORDER-001](../../docs/issues/ORDER-001.md)
- [ORDER-002](../../docs/issues/ORDER-002.md)

实际修复后批次由报告索引定位，基线失败证据保留。
