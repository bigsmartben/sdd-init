# 订单验收指南

## 1. 目标与依据

按 [Spec](spec.md) 与 [接口契约](../../docs/contracts/order.md) 验证新建、取消、提交、公开付款的结果、文件持久化及异常传播，并单列 AC-3 真实外部回执。范围、当前实际快照后修复后快照、本地 Python + 文件 SQLite 已由 Main 启动指令确认。例行非法值、缺失对象、只读数据库及 commit 失败覆盖由执行者从契约推导，不增加业务规则。没有 UI，不需要人工视觉确认；本轮未定义性能阈值。

## 2. 版本、环境和真实入口

- 在当前隔离项目根目录执行，Python 3.11+，仅标准库，无依赖安装。
- 实测版本以每批报告中的 Git HEAD、产品源码 SHA-256 和相关未提交改动为准。先运行 `python -B checks/runtime_details.py`。
- 使用真实 `src` 模块和每场景独立临时 SQLite 文件，没有模拟服务。
- 执行 `python -B checks/acceptance.py` 得 AC-1/2/3 JSON；退出 0 全过、1 有失败、3 无失败但有阻塞。
- 执行 `python -B tests/order_regression.py` 得补充契约覆盖 JSON；退出 0 全过、1 有失败。精确筛选见该命令 `--help`。
- `python -B -m unittest discover -s tests -v` 是既有局部单测补充，不能替代公开入口集成验收。

## 3. 场景与观察点

每个本地场景自行新建临时目录、建表与测试订单，关闭连接后重开读取状态；结果必须来自实际函数返回、实际异常和真实数据库。无凭据、共享账户或人工数据准备。

| 功能 / 场景依据 | 操作 | 通过判据与证据 |
|---|---|---|
| AC-1，新建提交 | `python -B checks/acceptance.py --scenario AC-1` | 新建 pending 后提交返回 true，关闭重开 submitted；保留 JSON |
| AC-2，取消提交组合 | `python -B checks/acceptance.py --scenario AC-2` | 取消后提交 false，关闭重开 cancelled；保留 JSON |
| AC-3，外部真实回执 | `python -B checks/acceptance.py --scenario AC-3` | 当前配置只报告 BLOCKED；本地运行器不执行外部调用，不产生外部通过结论 |
| 新建与输入边界 | 补充运行器的新建、非法编号、重复创建用例 | pending 持久化；空字符串、None、数字抛 ValueError；重复编号 IntegrityError 且旧状态保留 |
| 取消与重复取消 | 补充运行器取消用例 | 重开 cancelled，重复取消仍 cancelled |
| 公开付款与组合 | 补充运行器从 pending/submitted/cancelled 付款用例 | `ui.mark_paid` 后重开 paid，保持现存订单可标记 paid 的既有行为 |
| 缺失对象异常 | 补充运行器 read/cancel/submit/set_status/mark_paid 的缺失订单用例 | 每个公开操作抛 ValueError，不创建缺失行、不改变既有行 |
| 数据库写错误传播 | 补充运行器五种写操作的 SQLite query_only 用例 | 真实 SQLite 抛 OperationalError，原文件状态保持，无成功返回 |
| 提交 commit 失败 | 补充运行器另一连接持有读锁、busy_timeout=0 的提交用例 | commit 抛 OperationalError；测试调用方 rollback、释放锁并重开后仍 pending；不要求产品自动 rollback |

稳定 O-编号、逐项数据与实际观察由补充运行器 JSON 给出，报告将每个编号映射至上述功能。合法状态以契约为准，不推断 paid/submitted 再提交等未定义语义。

## 4. 失败、隔离与恢复

场景内连接通过 finally 关闭；临时目录退出时删除，无持久共享数据。锁场景由测试调用方 rollback、关闭锁连接后清理；失败也执行同样复位。每次重跑使用全新文件，不在原文件上叠加结果。数据库异常不转为成功。

AC-3 恢复条件：有权人员提供真实测试服务端点、调用权限及允许网络访问的环境，并提供该服务真实协议与回执判据；Main 交接实际可调用入口后再接续。现有 CLI 永远不发外部请求，配置齐备也不构成真实验收。当前缺少端点、权限、网络授权，不访问外部、不配置服务、不取凭据、不部署。它不能被本地文件 SQLite 结果替代。

## 5. 批次结果

[首次快照 Test Report](../../docs/test-reports/order/initial.md) 记录实际版本、覆盖、原始证据、缺陷和 Test Gate；修复后结果另建批次并保留首轮失败。

[修复后独立集成复验](../../docs/test-reports/order/retest.md) 记录同一场景在修复后实际快照的独立全量结果。
