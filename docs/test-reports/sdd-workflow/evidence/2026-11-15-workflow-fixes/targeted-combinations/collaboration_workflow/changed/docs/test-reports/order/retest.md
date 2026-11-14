# Test Report — 订单修复后全功能集成复验

## 1. 测试目标与依据

批次 ORDER-RETEST；类型为修复后全功能点集成回归，沿用 [初测](initial.md) 全部 12 场景。实际调用者与回执方 Main `/root`，独立执行者原测试技能 Agent `/root/integration`；执行 UTC 时间见 [实际快照](retest-snapshot.json) 的 time_utc。本批次确认原 [ORDER-001](../../issues/ORDER-001.md)、[ORDER-002](../../issues/ORDER-002.md) 恢复及受影响行为保持。

判据沿用 [Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[指南](../../../specs/order/quickstart.md)，不增加业务定义。Bugfix 归因与局部验证分别见 [候选快照](bugfix-snapshot.json)、[局部检查](bugfix-results.json)；本报告是独立复验，不以实施者证据替代本次执行。

## 2. 范围与安排

Main 续派确认沿用原范围、环境、公开入口和判据，目标为修复实际工作区快照，无新增常规确认事项。全部本地场景重跑，同时保留 AC-3 阻塞。范围含新建、取消、提交、公开 mark_paid、set_status、输入边界、不存在对象、数据库错误。

AC-2 加强测试观测：在公开 submit 调用前后读取 total_changes，记录 SQLite trace，关闭重开数据库；用于核实契约已有“不写入”，并非新增业务标准。其余场景沿用同一入口和断言。整体 PASS 仍需全部范围满足，AC-3 真实外部证据缺失时不得 PASS。未改 src 或 tests；本 Agent 仅加强 checks 的取证并维护指南和报告。

## 3. 测试环境与实际版本

- Git HEAD 仍为 `a8f4cf7154b9e81d9b4ab62b8cd0cecddb36eec5`；不能将该 HEAD 单独视为修复版本。实际运行是未提交 src/order_service.py、src/ui.py 修复，另有 Bugfix 补充的 tests/test_order.py。逐源文件哈希、tests/checks 哈希和完整源/单测 diff 见 [复验快照](retest-snapshot.json)。
- order_service SHA-256：`3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；ui：`c4a9e5b0789129c89bb71387e2aaed619944d115aff5a53c7fb5320fcbff88ae`。与 Bugfix 候选源快照逐项一致，执行前后再次核对源哈希稳定。
- 相对初测，仅上述两个源文件哈希变化；storage、__init__ 和 runtime 未变。变化分别影响取消提交保护、付款公开入口及其异常。初测证据只证明原始版本，不复用作本批通过证据；全部 12 场景重新执行。
- Python 3.12.3、SQLite 3.45.1；本地隔离环境、每场景真实临时文件 SQLite、正式 src 模块。无服务替身或外部调用。runtime 与初测完全一致，端点 null、调用未授权、运行网络关闭。

运行条件补充来源：2026-11-15 用户在本轮同一记录中明确确认，运行仍为同一隔离项目、本地文件 SQLite；AC-3 端点和权限没有变化，实现、接口、环境和数据均未改变。此事实由 Main `/root` 归并，仅关联本批已有快照和证据；本次未执行新测试、运行探测或重新采集哈希，不新增执行批次，不改写原执行时间及原始输出。

## 4. 准备与数据

准备无缺口，本地无需安装依赖；ORDER-1、ORDER-2、MISSING、空串、None、0 等常规数据与取值依据沿用指南。每场景独立临时目录与文件 SQLite，finally 关闭连接后目录自动清理。AC-1、AC-2 明确关闭重开数据库，其他持久化检查用独立连接观察已提交结果。

DB-ERROR 使用真实 SQLite query_only，证明写入失败传播及最终状态保持；单测另以委托真实 SQLite 的 commit 代理注入异常，仅作为模拟 commit 边界的补充，不将代理结果称为真实磁盘故障。外部环境未就绪只影响 AC-3。

## 5. 执行与覆盖汇总

实际完整重跑计划 12 场景，PASS 11、FAIL 0、NOT RUN 0、BLOCKED 1，合计 12。场景内参数观测不重复计数。范围内本地新建、取消、提交、付款及全部已确认异常路径均已执行；AC-3 未完成真实核验。需求覆盖与通过率分别判断，11/12 不等同于整轮验收通过。

- `python -B checks/order_regression.py`：退出码 3，逐项结果见 [原始 JSON](retest-results.json)。
- `python -B -m unittest discover -s tests -v`：6 个测试通过，退出码 0，[真实输出](retest-unit.txt)。覆盖取消不写/不 commit、mark_paid 缺失对象/现存状态、commit 异常等辅助检查。
- 两次命令及退出码见 [执行记录](retest-commands.json)。完整运行源快照对应本批所有结果，没有只使用实施者结果或以单测代替集成。

## 6. 逐项结果

每项命令为 `python -B checks/order_regression.py --scenario <场景>`；全量命令实际按顺序执行相同函数，详细观测见 [retest-results.json](retest-results.json)，产品版本均为第 3 节修复快照。

| 场景 / 依据 | 前置与步骤 | 预期 | 实际结果 | 结论 | Issue |
| --- | --- | --- | --- | --- | --- |
| CREATE / 新建契约 | 空库 create、独立读 | pending 持久化 | pending | PASS | 无 |
| AC-1 / Spec | create、submit、关库重开 | true / submitted | true / submitted | PASS | ORDER-001 必要回归 |
| CANCEL / 取消契约 | create、cancel、独立读 | cancelled 持久化 | cancelled | PASS | ORDER-001 必要回归 |
| AC-2 / Spec 与契约 | create、cancel、trace submit、关库重开 | false、cancelled、不写入 | false，前后 cancelled，total_changes=0，trace 仅一条 SELECT | PASS | [ORDER-001](../../issues/ORDER-001.md) |
| PAID-PENDING / paid 契约 | pending 后公开 ui.mark_paid | paid 持久化 | pending 中间态、paid | PASS | ORDER-002 必要回归 |
| PAID-CANCELLED / paid 契约 | cancelled 后公开 ui.mark_paid | paid 持久化 | cancelled 中间态、paid | PASS | ORDER-002 必要回归 |
| PAID-SUBMITTED / paid 契约 | submitted 后公开 ui.mark_paid | paid 持久化 | submitted 中间态、paid | PASS | ORDER-002 必要回归 |
| SET-STATUS / 服务契约 | 新建后 set_status paid | paid 持久化 | paid | PASS | ORDER-002 必要回归 |
| INVALID-ID / 输入契约 | 空串、None、0 新建 | ValueError，空库 | 均 ValueError，0 行 | PASS | 必要回归 |
| MISSING / 不存在对象契约 | 空库 cancel、submit、set_status、公开 ui.mark_paid | 均 ValueError | 四项均 ValueError | PASS | [ORDER-002](../../issues/ORDER-002.md) |
| DB-ERROR / 异常契约 | query_only 下五入口写入、回滚、独立读 | 异常传播、不返回成功，原状态保持 | 五项均 OperationalError，pending，1 行 | PASS | 两 Issue 必要回归 |
| AC-3 / Spec | runtime 端点和授权检查 | 获授权真实服务回执 | 未配置端点、未授权，未调用网络 | BLOCKED | 无产品缺陷 |

初测两个失败均保留在原报告，不覆盖原始 JSON。AC-2 的新观测加强契约证据而未放宽原 false/cancelled 判据。MISSING 直接调用原公开 ui.mark_paid，不以内层 set_status 替代。

## 7. 原 Issue 与关单依据

| 原 Issue | 初测与复验关联 | 本批结论 |
| --- | --- | --- |
| [ORDER-001](../../issues/ORDER-001.md) | 初测 AC-2 true/submitted；修复快照 AC-2 false/cancelled，零写入 | 原场景恢复；AC-1、取消、paid、输入、数据库异常等必要回归通过，具备本地缺陷关单证据 |
| [ORDER-002](../../issues/ORDER-002.md) | 初测公开 mark_paid 不抛异常；修复快照公开入口 ValueError | 原场景恢复；现存状态 paid 持久化及数据库异常传播、AC-1/2 均通过，具备本地缺陷关单证据 |

Main 交回原 Issue 写入权后，原 Issue 已追加本批独立全量复验历史及快照，保留 Bugfix 的定向关闭历史并保持 Closed；本报告提供关单证据。AC-3 不属于这两个本地缺陷的修复判据，因此不妨碍相应本地缺陷关单，但仍阻止全范围 Test Gate PASS。

## 8. 结论与限制

修复快照的本地全部已确认行为通过；本次修复未在已执行范围引入回归。完整范围 Test Gate 为 **BLOCKED**，适用于第 3 节实际修复快照、本地 Python + 文件 SQLite、12 场景；仅剩 AC-3 缺真实外部证据。初测 Gate FAIL 保留为历史，不因本次通过覆盖。

依据第 3 节用户补充的未变化事实，沿用原判据，已有证据的对象和适用条件未发生变化，可继续复用如下证据；均保留原版本、覆盖和执行时间，不作为本次新实测：

| 既有证据 | 可复用范围及限制 |
| --- | --- |
| [复验结果](retest-results.json)、[实际快照](retest-snapshot.json)、[命令记录](retest-commands.json) | 继续支持修复版本的 11 项本地场景通过、原缺陷恢复和必要回归；AC-3 仅复用条件缺失的 BLOCKED 事实，不证明真实外部回执。 |
| [6 项单测输出](retest-unit.txt)、[定向修复报告](bugfix-verification.md) | 继续作为各自覆盖范围内的辅助和定向证据，支持原 Issue 关单依据；代理 commit 异常仍仅证明其注入条件下的机制。 |
| [架构审查记录](architecture-review.md)及其候选证据 | 实现、接口及装配环境未变，原候选四项检查和 Review Gate PASS 继续适用；不扩展为外部服务验证或发布授权。 |
| [初测报告](initial.md)及原始证据 | 继续证明修复前版本的失败与修复对照历史，不能作为修复版本通过的证据。 |

本次补充不改变覆盖统计、两项 Issue 的 Closed 状态或 Gate：Test Gate 仍为 BLOCKED，Review Gate 沿用原记录的 PASS。AC-3 的恢复条件未满足，仍需按下述条件接续。

恢复条件：有权人员提供已授权真实外部测试端点、调用权限和可用网络环境，并具备核验真实回执的执行入口；Main 再协调相应测试。当前授权禁止网络和外部配置，未尝试取得凭据或模拟外部成功。人工视觉验收不适用，没有待补本地人工反馈；外部真实回执仍待验。本结论不替代架构 Review Gate 或发布授权。
