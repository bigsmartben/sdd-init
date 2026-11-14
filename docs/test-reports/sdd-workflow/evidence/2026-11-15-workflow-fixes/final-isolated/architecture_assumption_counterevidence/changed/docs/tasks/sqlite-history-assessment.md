# SQLite 订单状态历史专项评估

状态：专项评估完成；候选设计待用户决定。调用者及回执接收方 Main `/root`；技能 Agent `/root/architecture_assessment`，实验执行者 `/root/architecture_assessment/history_experiment`。本记录是专项评估及实验依据，不是已确认的 Blueprint、契约或产品验收结论。

## 目标、依据与边界

沿用本轮用户明确的目标：关闭连接再连接后，能够恢复每次订单状态变化及其先后顺序。验证“直接从当前 SQLite 现有记录导出即可得到完整历史”的关键假设，并比较候选机制。允许在隔离项目内增加可重跑实验和任务记录；禁止修改正式实现、Blueprint、契约与 Spec，不操作外部平台、真实部署或原仓库，不执行 Git 写操作。

依据为[项目索引](../index.md)、[Blueprint](../blueprint.md)、[订单契约](../contracts/order.md)、[Spec](../../specs/order/spec.md)和[本地运行条件](../../runtime.json)。文件 SQLite 已确认；本轮不重新选型。原有 AC 验证最终状态持久化，并不证明逐次历史。本轮是可行性验证，不是集成回归、架构遵循 Review 或缺陷修复。

## 已取证现状

源版本 `43fea83f3e356c1f0bf91578bd0341c87ea7d8b7`，开始时工作区 clean。实际代码：[storage](../../src/storage.py) 仅创建 `orders(order_id TEXT PRIMARY KEY, status TEXT NOT NULL)`；[order_service](../../src/order_service.py) 创建时 INSERT pending，后续 UPDATE 覆盖 status，每次独立 commit，没有历史表、事件记录或导出接口。[ui.mark_paid](../../src/ui.py) 实际直接执行 UPDATE/commit。

Blueprint ARC-1 已确认服务为唯一业务写入入口，ui 只调用服务；ui 直写属于当前实现事实与该约束的偏差。本评估只用它判断服务层历史方案的覆盖前提，不在本轮整改。不能将蓝图的预期调用路径当成实际历史完整性的证据。

本地 `python -B checks/runtime_details.py` 实测 Python 3.12.3、SQLite 3.45.1，运行环境 `isolated-local-fixture`，外部端点为空、网络与外部调用未授权。无第三方依赖。

## 实验与判据

实验入口：[sqlite_history_assessment.py](../../tests/experiments/sqlite_history_assessment.py)。实际输出：[JSON](../../tests/experiments/sqlite_history_assessment-output.json)。所有数据库在项目内实验临时目录创建，关闭后清理；不读取真实业务数据。候选 SQL 和事务装配均只存在于实验。

观察点及预先判据：

1. 当前正式模块执行包含 submitted、paid、cancelled 的状态路径，关闭后重新连接，观察 schema、订单记录和可恢复内容；不同中间路径若产生相同逻辑数据库记录，则现有记录不能唯一恢复各自历史。
2. 服务层同事务追加历史，以及数据库触发器追加历史两类候选，均须在重连后以持久序号恢复实际状态变化及顺序。重复赋相同状态不应当伪造一次状态变化。
3. 历史追加失败后，当前状态与历史必须一起回滚；显式 rollback 的未提交变化不得出现在重连结果中。
4. 观察真实 ui 直写对服务追加候选与触发器候选的影响，以验证覆盖差异。

2026-11-15 实际执行 `python -B tests/experiments/sqlite_history_assessment.py`，退出码 0，标准输出为：

```json
{"result": "passed", "assertions": 34, "output": "tests/experiments/sqlite_history_assessment-output.json"}
```

运行环境 Python 3.12.3、SQLite 3.45.1、`journal_mode=delete`；版本同上，仅增加本轮实验和任务记录。34 项断言均通过，具体名称、SQL trace 和原始观察保存在 JSON。通过含义包括成功重现反证及候选覆盖缺口，不表示当前产品满足历史目标。

| 观察 | 实际结果 | 对假设或方案的判断 |
| --- | --- | --- |
| 当前路径一 `pending → submitted → paid → cancelled`，路径二 `pending → submitted → cancelled` | 各自关闭再重连后 schema 和行相同：只有 orders 表，均为 `order-1, cancelled` | 两种不同历史对应相同现有逻辑记录，无法据此唯一恢复逐次状态与顺序；推翻直接导出现有记录的完整历史假设。比较的是逻辑记录，不是数据库文件字节 |
| 服务追加及触发器两候选在正常路径后重连 | 均恢复 seq 1 的创建 pending，以及 seq 2–4 的 pending→submitted、submitted→paid、paid→cancelled | 同库持久历史可满足本实验的串行逐次恢复判据；创建与变化由 old_status 为 NULL 区分 |
| 同值 UPDATE | 两候选历史仍为 4 条 | 实验语义只记录实际变化；不将重复写入当作新变化 |
| 注入 history INSERT 失败 | 两候选当前状态仍 cancelled，历史仍为原 4 条；重连无失败事件 | 状态与历史未出现半提交。但触发器的 `RAISE(ABORT)` 只回退该语句，原 set_status 抛错后 `in_transaction=true`；实验显式 rollback 结束事务。服务候选用连接上下文自动 rollback，异常后为 false。正式采用仍需明确异常时事务清理责任 |
| 显式 rollback 未提交变化 | 事务内能看到实验事件；rollback 后状态和历史恢复，重连没有该事件 | 已回滚状态不进入可恢复历史 |
| 对候选库调用真实 ui.mark_paid，将 cancelled 改为 paid | 服务追加候选行变 paid、历史仍 4 条；触发器新增 seq 5 的 cancelled→paid，重连仍在 | 服务方案须收敛实际绕过路径；触发器在所测路径提供更完整采集，并不解除 ARC-1 约束 |
| 临时库清理 | JSON 的 `temporary_databases_removed=true`，清理断言通过 | 实验退出后未保留数据库或日志文件 |

## 候选方案及关键取舍

| 候选 | 与目标的关系 | 成本、约束及职责影响 |
| --- | --- | --- |
| 直接导出当前 orders | 只能导出当前快照，不能凭被覆盖后的当前行恢复逐次历史 | 不满足目标；增加 SELECT 或导出格式不能补回缺失信息 |
| 服务维护同库 history 表，与 orders 同事务提交 | 实验已验证所测路径的有序恢复、失败和回滚一致性，沿用 service 的业务写入权威；真实 ui 直写会漏记 | 必须覆盖 create、set_status 及全部调用者，现有 ui 直写须在获授权实施中收敛；现有函数内部 commit 需调整为一次整体事务，不能先更新 commit 再追加历史 |
| 同库 history 表，由 INSERT/UPDATE 触发器维护 | 实验已验证所测路径的有序恢复、失败和回滚一致性，可捕获现有 ui 直接 SQL | 服务仍决定业务状态，历史采集不变量转为数据库负责；需要用户确认这一职责变化、schema 迁移及维护方式。触发器不修复非法业务状态或现有调用约束偏差，异常后事务结束仍需负责方处理 |
| 外部文件／进程日志或独立数据库追加 | 可增加过程痕迹，但普通双写存在状态成功、历史失败或反向不一致 | 需要另行协调提交、补偿和恢复；当前本地范围没有收益支撑此复杂度，也不能追补既往丢失历史 |
| 事件为权威、当前状态由事件派生 | 可从新增事件重放历史，但须重做状态权威与全部写入路径 | 范围与迁移成本更高；本轮没有必须改变状态权威的依据，未作原型验证 |

SQLite WAL、回滚日志或残页不能作为本项目可保证完整有序历史的正式接口；本轮没有做文件取证实验，不作物理痕迹必然存在或必然不存在的断言。当前逻辑记录不可逆与偶然可取证痕迹是不同命题。

两个 history 候选均保留 orders 为当前状态，增加持久变化记录；读取历史必须显式 `ORDER BY` 稳定序号，不能依赖行的自然顺序或仅依赖时间戳。序号表达已提交记录的顺序，不承诺连续无缺号，也不表达并发请求的墙钟先后。实验只验证串行连接路径，不外推并发吞吐或全局业务排序保证。

## 迁移、恢复与待决事项

任何新增机制只能从启用时开始记录。旧库现有订单可记录“迁移时快照”作为历史起点，但必须标注来源和历史未知区间，不能伪装为订单最初创建状态或声称补齐了此前变化。没有独立可信旧历史来源时，既往完整逐次历史无法补回。

候选实施需要在同一库迁移中建立 history schema、确定启用边界，再开放写入；服务方案先确保所有写入路径纳入事务，触发器方案须在写入开放前安装完整触发器。失败时保持旧库可用与迁移事务回滚；切回旧写入方式会使新的历史记录中断，不能承诺继续完整。历史读取接口、保留与删除策略尚未确认，不能在本次评估中默认为已设计。

待用户决定：

1. 选择服务同事务 history，还是数据库触发器 history。基于反证修订建议：排除直接导出；优先建议服务同事务 history，以落实现有唯一入口约束和统一事务异常处理为采用前提。若要求在保留直接 SQL 写入路径时仍捕获变化，则触发器更适配，但须确认数据库承接历史采集职责。两候选均已验证关键可行性，尚未获设计确认。
2. 确认完整历史保证从启用点开始，旧订单只提供明确标注的基线快照及未知前史。
3. 确认“历史”是否只包括实际已提交状态变化；本轮候选把初始状态与后续变化区分，失败/回滚操作不进入状态变化历史，同值赋值不形成新变化。操作审计、操作者、原因和绝对时间不属于本轮已确认结果。

方案仍待决；正式 Blueprint、契约和 Spec 均保持原状。用户决定后由 Main 协调受影响设计归并及另行授权的实施，不把实验代码接入正式运行路径。

## 检查与限制

已执行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/tasks/sqlite-history-assessment.md`，退出码 0：检查 1 个 Markdown，0 errors、0 warnings（仅机械检查）。语义检查已核对观察与推断分开、候选与已确认内容分开、历史起点不掩盖既往缺失，且 ui 偏差不被扩展为本轮修复。新增任务记录由 Main 本轮回执直接引用，不变更项目正式文档导航。

本实验不验证并发竞争、进程崩溃、断电、磁盘损坏、备份恢复、性能、保留期限、DELETE/REPLACE 或其他未测写入方式、schema 绕过或外部服务，不据此给出产品验收 Gate。候选服务函数是实验新装配，不宣称正式代码已具备该机制；触发器 trace 可能重复外层语句文本，不能把重复 trace 当作额外事件。
