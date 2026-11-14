# Test Report — 订单修复候选独立集成

## 1. 测试目标与依据

批次 `order-integration-20261115`，类型为全范围功能集成回归，执行者 `/root/integration`，独立于实施者及 BUG-001 定向复验执行者。实际执行时间 2026-11-14 16:43:03 UTC（北京时间 2026-11-15 00:43:03），详见[执行记录](execution.json)。

依据：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[复跑指南](../../../specs/order/quickstart.md)。目标为证明实际修复候选在本地真实文件 SQLite 中的用户可观察行为，兼顾取消后提交原故障与所有适用已确认功能。未借用局部自验充当独立结果。

## 2. 范围与安排

Main `/root` 的启动工单已明确并沿用用户确认的四项：范围及入口判据为 Spec／契约，目标为实际修复候选，环境为本地 Python＋文件 SQLite，主要路径为新建提交／取消再提交／外部回执及现存订单 paid。首次实测前四项齐备，无新增确认项。

按 AC-1、AC-2、AC-3、契约补充场景依次执行，使用公开函数、真实文件数据库和独立读连接观察状态。CT-01～CT-14 从已确认接口、副作用及异常推导常规数据、错误、恢复与协作覆盖，不改变判据。完成标准为全部适用功能和 AC 满足且证据齐备。范围外为产品修复、架构整改、Git、外部配置、部署及未定义的非 pending／非 cancelled 提交策略；架构职责遵循由独立 Review 判定，不作为本报告业务失败依据。

## 3. 实际版本与环境

- 实际隔离项目根、解释器路径、Python 3.12.3、SQLite 3.45.1、Linux 平台、runtime 配置和完整参与文件哈希见[执行记录](execution.json)及[环境原始输出](runtime.stdout.txt)。
- `src/order_service.py` SHA-256 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；与 Main 指定候选及[候选环境](../order-cancel/candidate-environment.json)匹配。`src/ui.py` SHA-256 `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b`。取证前后全部参与文件哈希一致。
- 以实际源文件组合及哈希标识含未提交修改的候选；本轮无 Git 操作，不声称提交版本或发布制品。
- 真实组件为 service、storage、ui 库入口和本地文件 SQLite；SQL trace、Python socket 审计只做观察，不模拟业务组件。外部服务未装配、未调用，无模拟回执。

## 4. 准备与数据

每个 AC／契约场景独立使用临时文件数据库；`ORDER-1` 从 pending 经确认操作变化，`MISSING` 不存在。空串、None、整数只检查新建输入约束。补充测试明确覆盖四个已有合法状态。真实 commit 冲突通过第二文件连接持有读锁制造，调用者随后 rollback 恢复 pending。所有连接关闭、临时目录清理，未遗留服务或业务数据。

环境就绪：无需安装依赖和外部账户。唯一环境缺口为 AC-3：runtime 中端点为 null、授权 false、network_access_in_this_run false。现有 acceptance 入口始终不发外部请求；即使未来提供配置仍需获授权的真实外部调用与回执验证入口。

## 5. 执行与覆盖统计

实际执行全部就绪本地场景，AC-3 仅执行阻塞检查，未执行真实服务调用。共 17 项：**15 PASS、1 FAIL、0 Not run、1 BLOCKED**；总通过率 15/17（88.2%），可执行本地场景通过率 15/16（93.75%）。

Spec AC 覆盖为 3/3 均有状态及证据，2 PASS、1 BLOCKED；真实行为完成验证为 2/3。契约补充 14/14 均已执行，13 PASS、1 FAIL。功能映射及细节见下表；“已有覆盖状态”不等于“全部行为通过”。新建／取消／提交／状态写入／paid／异常／本地无网络均有实测，外部回执未验证。无前批次结果复用、无重试；BUG-001 历史及定向复验仅引用原记录。

## 6. 逐项结果

表内 AC 通过[acceptance.py](../../../checks/acceptance.py)真实执行，CT 通过[contract_checks.py](contract_checks.py)真实执行。所有行版本及子进程完整命令／退出码均关联[execution.json](execution.json)；stdout 为原始 JSON，stderr 文件保留在同目录且本轮为空。

| Case / 依据 | 前置与操作 | 预期与实际 | 结论 | 原始证据 / Issue |
|---|---|---|---|---|
| AC-1 / Spec | 新建 pending，提交，关闭重开文件库 | true，submitted；符合 | PASS | [stdout](AC-1.stdout.txt)，exit 0 |
| AC-2 / Spec | 新建，取消，再提交，关闭重开 | false，cancelled；符合 | PASS | [stdout](AC-2.stdout.txt)，exit 0；[BUG-001](../../issues/BUG-001.md) |
| AC-3 / Spec | 运行外部场景入口核对配置 | 缺少端点及权限，BLOCKED；真实回执未核验 | BLOCKED | [stdout](AC-3.stdout.txt)，exit 3；恢复条件见下文 |
| CT-01 / create_order | 新建 ORDER-1，独立连接读取 | pending 已 commit，无打开事务；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-02 / cancel_order | 新建后取消，独立连接读取 | cancelled 已 commit；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-03 / set_status | 对现存订单逐一写 pending/submitted/cancelled/paid | 每次给定合法状态均可独立读取；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-04 / paid 保持 | 新建现存订单，公开 ui.mark_paid | paid 持久化，无打开事务；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-05 / 编号约束 | create 输入空串、None、17 | 均 ValueError，零插入；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-06 / 缺失异常 | read_status(MISSING) | ValueError；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-07 / 缺失异常 | cancel_order(MISSING) | ValueError；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-08 / 缺失异常 | submit_order(MISSING) | ValueError；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-09 / 缺失异常 | set_status(MISSING, paid) | ValueError；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-10 / 缺失异常 | ui.mark_paid(MISSING) | 应 ValueError；实际正常返回 | FAIL | [契约 stdout](contracts.stdout.txt)；[BUG-002](../../issues/BUG-002.md) |
| CT-11 / 数据库异常 | 关闭真实连接后调用 create/read/cancel/submit/set/paid | 六个入口均传播 ProgrammingError；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-12 / commit 错误恢复 | 第二连接持读锁，提交订单，rollback | OperationalError 向上传播，读者 pending，rollback 后 pending；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-13 / cancelled 不写入 | 取消后记录 SQL trace、变化数再提交 | false，变化数增量0，只有 SELECT，无写事务，持久 cancelled；符合 | PASS | [契约 stdout](contracts.stdout.txt) |
| CT-14 / 本地无网络 | 审计上述真实本地调用的 socket 事件 | 连接／域名解析／发包事件零；符合本地路径约束 | PASS | [契约 stdout](contracts.stdout.txt) |

契约组合子进程退出 1，唯一失败为 CT-10。记录器自身退出 0 仅表明取证完成，不将子进程失败转换为通过。CT-14 只覆盖实际执行路径，不证明任意未知未来分支，也不证明真实外部回执。

## 7. 关联问题及影响

| 记录 | 本轮关联 | 影响 |
|---|---|---|
| [BUG-001](../../issues/BUG-001.md) | AC-2、CT-13；AC-1、CT-04、CT-08、CT-11/12 回归 | 原取消后提交缺陷独立集成恢复；原单状态由 Bugfix 持有，未修改。另见[定向复验](../order-cancel/bugfix-retest.md)。 |
| [BUG-002](../../issues/BUG-002.md) | CT-10 | 独立业务契约失败；已登记 Pending，不在原取消后提交修复授权内。 |
| [ARCH-001](../../issues/ARCH-001.md) | paid 路径职责 | 架构旁路由 Review 处理，本轮未据此判业务失败；CT-04 实测通过。 |

CT-10 的依据是契约明确“不存在的订单抛出 ValueError”；正常操作的存在性前置不撤销该异常语义，不把缺失对象当作正常 paid 操作。若权威契约后续变更，应由 Main 重新对齐，不能在测试中改写本轮判据。

## 8. 结论、限制与 Test Gate

**Test Gate = FAIL**，适用于上述精确候选、隔离本地 Python＋文件 SQLite 以及全部 Spec／契约范围。依据为 CT-10 已实测失败；此外 AC-3 仍 BLOCKED，因此全部验收标准未满足。全部当前可执行场景已完成，测试执行可交付，不宣称产品整体验收通过。

恢复条件：BUG-002 获单独修复授权并交回明确候选后，接续原执行者复跑缺失订单异常、现存订单 paid、异常传播及 AC-1/2 必要回归，并分析候选变化对其余证据的影响；AC-3 需有权人员提供真实测试服务端点、明确调用权限、可核验回执方式及获授权的真实调用入口，实际核验后才能解除阻塞。任何本地或模拟结果不替代 AC-3。

人工验收：无 UI、无人工视觉／体验判断要求；不存在等待人工反馈的本地用例。外部端点及权限是环境与授权条件，不是已获得的人工验收结论。未执行网络、配置、部署、Git 或产品变更。

文档机械校验结果与范围见[校验原始输出](doc-check.stdout.txt)及[校验回执](doc-check.json)；机械检查只证明格式和链接，Gate 基于以上实测及已确认语义。
