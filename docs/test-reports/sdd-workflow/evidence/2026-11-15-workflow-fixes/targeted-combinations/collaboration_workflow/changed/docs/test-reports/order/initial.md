# Test Report — 订单初始全功能集成回归

## 1. 测试目标与依据

批次 ORDER-INITIAL；类型为全功能点集成回归；执行者为独立技能 Agent `/root/integration`，实际调用者与回执方 Main `/root`。执行时间 2026-11-14T16:21:34Z（上海时间 2026-11-15 00:21）。依据 [Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[验收指南](../../../specs/order/quickstart.md) 和用户 TASK.txt。目标为初始真实快照完整取证并交 Main 协调实现缺陷；本阶段不修改产品代码。

## 2. 范围与安排

范围为新建、取消、提交、公开 mark_paid、set_status、输入边界、不存在对象、真实数据库写入错误和 AC-3。Main 启动工单已明确沿用用户确认的范围、当前实际快照后再修复快照、本地 Python + 文件 SQLite、Spec 和公开入口判据，无新增常规确认事项。

从既有契约推导正常、异常与状态组合数据；paid 测试保持将现存订单标记 paid 的行为。未为未定义的重复创建、paid 后提交等状态添加判据。完整范围执行，所有适用功能必须满足且外部真实证据就绪方可 PASS。无 UI、无人工视觉判断、无性能阈值；架构符合性由 Main 分派的架构阶段负责。

## 3. 测试环境

- 产品版本：Git HEAD `a8f4cf7154b9e81d9b4ab62b8cd0cecddb36eec5`，执行时 `git diff -- src runtime.json` 为空；测试新增 `checks/order_regression.py`，未改变产品。初次接单 git clean；执行时 Main 另写 docs/status.md，非运行输入。
- 实际 Python、SQLite、runtime.json 与逐源文件 SHA-256 见 [运行事实](initial-runtime.json)。入口为 `python -B checks/order_regression.py`，退出码 1；原有单测 `python -B -m unittest discover -s tests -v` 退出码 0。
- 真实组件：src.order_service、src.ui、src.storage、标准库 SQLite、每场景文件数据库。无产品替身。DB-ERROR 使用真实 query_only 限制写入，仅验证该故障条件；不声称覆盖所有 commit 故障。
- AC-3 端点 null、授权 false、运行网络 false；仅读取配置并输出 BLOCKED，未调用网络，也未以本地结果替代外部证据。

## 4. 数据与准备

每场景创建 TemporaryDirectory 和 SQLite 文件，连接关闭后自动删除目录。ORDER-1 为常规现存对象，ORDER-2 为异常新建对象，MISSING 为不存在对象；空串、None、0 直接来自非空字符串输入限制。没有外部凭据、部署或依赖安装。

准备成功，无本地环境阻碍。query_only 案例先建立 pending，再拒绝所有五个写入口，rollback 后从另一个连接读取最终文件状态。AC-1、AC-2 关闭并重开数据库验证；其他持久化案例通过独立连接验证 commit 后可见性。AC-3 未具备真实端点与授权。

## 5. 执行与覆盖汇总

计划并实际记录 12 个稳定场景：PASS 9、FAIL 2、NOT RUN 0、BLOCKED 1，总数 12；每个场景计数一次，场景内参数观测不重复计数。功能覆盖为本地全部已确认入口及适用异常均已执行，AC-3 已确认阻塞，不能计为真实外部核验。通过率 9/12 不等同于需求完全满足。

全部逐项原始观测见 [JSON 证据](initial-results.json)。原有 2 个单测通过见 [单测输出](initial-unit.txt)，其未覆盖 AC-2 和 mark_paid 不存在对象，故不替代集成结论。没有测试工具失败后放宽断言或重写产品行为。

## 6. 逐项结果

下表均为第 3 节产品版本、环境，操作命令为 `python -B checks/order_regression.py --scenario <场景>`；完整步骤与复位见 [指南](../../../specs/order/quickstart.md)，逐项观测见 [原始证据](initial-results.json)。

| 场景 / 依据 | 前置与实际步骤 | 预期 | 实际 | 结论 | 证据 / Issue |
| --- | --- | --- | --- | --- | --- |
| CREATE / 新建契约 | 空库 create，再独立连接读 | pending 持久化 | pending | PASS | initial-results.json CREATE |
| AC-1 / Spec | create、submit、关库重开读 | true / submitted | true / submitted | PASS | initial-results.json AC-1 |
| CANCEL / 取消契约 | create、cancel、独立读 | cancelled 持久化 | cancelled | PASS | initial-results.json CANCEL |
| AC-2 / Spec | create、cancel、submit、关库重开读 | false / cancelled | true / submitted | FAIL | [ORDER-001](../../issues/ORDER-001.md) |
| PAID-PENDING / paid 契约 | 新建 pending 后公开 ui.mark_paid | paid 持久化 | pending 中间态、paid | PASS | initial-results.json PAID-PENDING |
| PAID-CANCELLED / paid 契约 | 取消后公开 ui.mark_paid | paid 持久化 | cancelled 中间态、paid | PASS | initial-results.json PAID-CANCELLED |
| PAID-SUBMITTED / paid 契约 | 提交后公开 ui.mark_paid | paid 持久化 | submitted 中间态、paid | PASS | initial-results.json PAID-SUBMITTED |
| SET-STATUS / 服务契约 | 新建后 set_status paid | paid 持久化 | paid | PASS | initial-results.json SET-STATUS |
| INVALID-ID / 输入契约 | 空串、None、0 各 create | 均 ValueError、空库 | 均符合，0 行 | PASS | initial-results.json INVALID-ID |
| MISSING / 对象契约 | 空库 cancel、submit、set_status、ui.mark_paid | 均 ValueError | 前三项符合，mark_paid 无异常 | FAIL | [ORDER-002](../../issues/ORDER-002.md) |
| DB-ERROR / 数据库异常契约 | 新建后 query_only，依次五写入口并 rollback | 异常传播、原订单 pending、不新增 | 五项均 OperationalError，pending，1 行 | PASS | initial-results.json DB-ERROR |
| AC-3 / Spec | 读取 runtime 端点和权限 | 真实获授权服务回执 | 端点缺失、无权限、无网络，未调用外部 | BLOCKED | initial-results.json AC-3 |

AC-2 初测已直接证明违反返回和最终状态；修复后另补提交不写入的 trace/total_changes 观测，不用初测推定修复版本的结果。

## 7. 问题及影响

| Issue | 场景 | 影响 |
| --- | --- | --- |
| [ORDER-001](../../issues/ORDER-001.md) | AC-2 | 取消可被提交覆盖，不符合已确认业务 |
| [ORDER-002](../../issues/ORDER-002.md) | MISSING | 公开 mark_paid 对不存在订单静默返回，不符合异常契约 |

两个原 Issue 已交 Main，产品修复归独立 Bugfix 阶段。AC-3 是已知环境与授权阻塞，不虚构为产品缺陷。

## 8. 结论与限制

本批次全范围状态已完整记录，Test Gate 为 **FAIL**，适用于上述初始产品快照、本地隔离 Python + 文件 SQLite、12 场景覆盖：存在 2 个实现失败及 1 个外部阻塞。不是发布结论或架构 Gate。

恢复本地失败需要 Main 交回实际修复快照和归因/局部验证证据，由原测试 Agent `/root/integration` 全量复验并保留本批失败历史。AC-3 需要有权人员提供真实外部测试端点、调用权限及可用网络环境，并具备真实回执执行入口；本轮未授权获取凭据或配置外部服务。

人工反馈：本地 CLI/库范围无需人工视觉操作，没有用自动结果冒充人工反馈。外部真实回执仍未验证，即使本地修复全部通过，含 AC-3 的整轮 Test Gate 仍不能 PASS。
