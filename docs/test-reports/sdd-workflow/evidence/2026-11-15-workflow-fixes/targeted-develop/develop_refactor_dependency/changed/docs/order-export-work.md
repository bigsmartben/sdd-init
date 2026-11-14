# WO-ORDER-017

A 已确认两个可分别交付的需求。B 已确认可修改 `create_order` 的入口校验和在现有公开契约上新增一个只读的历史导出入口和直接测试。禁止本轮进入其他模块的写路径、改变 schema、跨服务迁移或改变 Blueprint 决定。允许读取现有实现和运行本地 Python/SQLite。

- T001／AC-4：全空白订单号延用空输入方式拒绝且不写入，合法编号仍能创建。可独立验收。
- T002／AC-5：导出经历进程重启的订单状态历史；对同一订单保留跨重启逐次状态变更和准确顺序，含取消与付款。须用已确认状态权威实现，不接受只有当前状态的结果。原计划复用已有持久化事件记录；其实际存在与可读路径开工后须查证。参见[设计决定](export-design.md)。

## 验收计划与实际状态

需求正文已归并至 [Spec AC-4／AC-5](../specs/order/spec.md)，本工单保留实施确认、范围与执行证据。实施沿用同一份 [Plan／Task](order-export-plan.md)，验收入口和准备条件见 [Quickstart](../specs/order/quickstart.md)。

- AC-4：使用真实临时文件 SQLite，通过公开 `create_order` 入口验证空串、ASCII/Unicode 全空白及非字符串按原有空输入方式拒绝且无写入；合法编号原样创建，关闭重开后为 pending。保持项为 AC-1 和现有 paid 持久化行为。判据全部满足才交付 T001。
- AC-5：必须从状态权威读取跨进程逐次历史（含取消、付款）及准确顺序，不能将当前状态判作通过。先核实权威来源，来源和授权不足只阻塞 T002；恢复后按原 AC 验收。

2026-11-15，`/root/develop_order_017` 在隔离本地环境执行点对点验收。版本为 `162bdaf0aff7bebeb747ca1f3cdffea7ef8674e1` 加未提交工作区改动，产品代码仅 `create_order` 的全空白判断；Python/SQLite 实际版本、源文件 SHA-256、命令及完整输出见[原始验收证据](order-export-acceptance.json)。点对点入口使用真实 Python、文件 SQLite、正式 src 模块，无替代数据库或外部调用；单元测试另以连接 Mock 核实非法输入不会接触数据库；临时目录执行后清理。本轮无人工视觉判据，不出具集成 Test Gate。

| 判据／保持项 | 实际入口与观察 | 结果 |
| --- | --- | --- |
| AC-4／T001 | `python -B checks/order_export_acceptance.py`：6 类非法输入均 ValueError、零写入；3 个合法原样编号重开后均 pending；退出 0。 | PASS；T001 独立交付。 |
| AC-1 | `python -B checks/acceptance.py --scenario AC-1`：true，重开后 submitted；退出 0。 | PASS。 |
| paid 与直接单测 | `python -B -m unittest discover -s tests -v`：5 项通过，含 paid 持久化、非法输入不访问连接及合法编号提交；退出 0。 | PASS。 |
| AC-2 存量行为 | 当前入口与从 `git show HEAD:src/order_service.py` 执行的基线代码均返回 true、重开后 submitted；当前验收退出 1。 | FAIL，已证明是 HEAD 既存偏差；本轮 diff 不改提交／取消路径，不阻塞独立 T001。原要求保留，修复不在本轮授权。 |
| AC-5／T002 | 来源调查及跨进程覆盖实验证据见 Plan。SQLite 仅 orders 当前状态，缺少事件记录；只读新增入口无法恢复丢失序列。 | BLOCKED，未实现、未验收通过，等待 Main 取得新决定。 |

T002 的影响及恢复条件：按[已确认设计](export-design.md)，记录完整历史需要覆盖全部状态写入并改变持久化结构、处理既有订单，本轮禁止这些操作。已排查当前状态查询、进程内缓存、日志／时间戳推断及外部账本，均不能同时满足权威、逐次准确和跨重启要求。Main 已将选择交用户：保留 T001 并延后 T002；另行授权前置架构／迁移方案与其后续重构；或另行确认仅当前状态导出的需求变更。尚无新授权，不进入跨阶段或扩大写入范围，整单未完成。AC-3 仍受既有外部端点与授权条件限制，本轮不执行外部验收。
