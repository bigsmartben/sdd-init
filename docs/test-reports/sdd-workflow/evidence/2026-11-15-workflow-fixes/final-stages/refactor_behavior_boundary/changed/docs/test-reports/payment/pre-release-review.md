# Architecture Review Record — 标记付款发布前对齐

## 1. 范围、依据与行为基线

- 目标：本地多需求订单候选的 `ui.mark_paid` 按已确认服务状态入口对齐；代码和测试仅付款适配实现及直接相关局部测试。不修改提交业务规则、配置、共享工作流、索引或项目审查规则，不执行全产品集成或外部调用。
- 依据：[Blueprint ARC-1–4](../../blueprint.md#架构边界)、[订单契约](../../contracts/order.md)、[CR-001](../../code-review-rules.md)、[Spec](../../../specs/order/spec.md)、[Quickstart](../../../specs/order/quickstart.md)。用户已有范围、方案与实施授权；无新增需求或架构决定。
- 初始版本：`b5c93159b3ee3d78ded2a26147a1f7b2a3acb19e`，初始工作区 clean。候选以该提交加本轮工作区 diff 和源文件 SHA-256 标识，不创建提交。
- 环境：2026-11-15，隔离本地，Python 3.12.3、SQLite 3.45.1；临时目录内文件数据库，调用者关闭连接，场景结束删除目录。实际审查执行者 `/root/refactor/architecture_review`，实施与行为验收分别取证；项目无额外独立性要求。
- 可写文档仅本记录及一份 Plan／Task；报告由技能 Agent 维护，Plan 由实施执行者维护。索引不在授权写入范围内，Plan 直接引用本记录。

### 保持判据与修改前事实

已确认保持判据：公开签名不变，现存订单付款后持久化 `paid`、返回 `None`；缺失订单抛 `ValueError`，数据库异常向上传播且不报成功。订单提交 AC-1 的业务及实现保持不变，本轮不执行该场景；AC-2 是已确认要求，缺陷不能作为保持预期。无已确认额外性能阈值。

| 证据 | 基线版本、入口与数据 | 实际结果 |
| --- | --- | --- |
| E-B1 | `b5c9315`；`python -B -m unittest discover -s tests -p test_order.py -k mark_paid -v`，临时文件库及 ORDER-1 | 1/1 PASS，第二连接读取 paid |
| E-B2 | `b5c9315`；Python heredoc 从 `ui.mark_paid` 公开调用；新建 ORDER-1，付款、关闭重开；MISSING；`PRAGMA query_only=ON` 后付款 | 返回 None、重开 paid；缺失抛 ValueError(`order not found`)；写失败抛 OperationalError(`attempt to write a readonly database`)，状态仍 paid |
| E-H1 | `b5c9315`；`python -B checks/acceptance.py --scenario AC-2` | exit 1，FAIL；accepted=true / persisted_status=submitted，判据 false / cancelled。历史业务缺陷，仅影响参考，不修复 |
| E-R1 | `b5c9315`；`python -B checks/runtime_details.py` | Python 3.12.3 / SQLite 3.45.1；external_endpoint=null、external_call_authorized=false、network_access_in_this_run=false；无外部访问 |

## 2. 检查项、工单与复核

初审执行者 `/root/refactor/architecture_review` 只读返回以下稳定检查项。CR-001 的设计依据、触发条件、取证链及违反条件有效，完整映射本轮 ARC-1；ARC-2–4 的适用共享指导缺少项目规则映射。补充路径检查与实际测试不能消除该映射缺口；用户决定是否及何时更新规则，本轮不更新。

| 共享指导／项目依据 | 适用性及项目映射 | 检查项／结论 |
| --- | --- | --- |
| 模块边界与依赖、状态权威；ARC-1 | 适用，CR-001 有效；UI→服务→SQLite | CHK-001，初审 FAIL，待整改 |
| 业务实体持久化、接口交互同步完成／失败；ARC-2、契约 | 适用，CR 映射缺失 | CHK-002，待查 UNVERIFIED |
| 正式／测试隔离、适用测试设计；ARC-3 | 适用，CR 映射缺失 | CHK-003，待查 UNVERIFIED |
| 环境边界与运行装配；ARC-4 | 适用，CR 映射缺失 | CHK-004，待查 UNVERIFIED |
| 限流、熔断、重启、重放等运行保障机制 | 不适用，蓝图和实现无此机制，本轮不引入 | 不计 PASS |
| 产品观测数据、日志契约、观测故障隔离 | 不适用，蓝图明确无正式观测系统；命令 JSON 为测试输出 | 不计 PASS |
| 异步、并发、迟到回调、后台恢复、媒体、生成模板 | 不适用，已确认同步函数交互且无上述机制 | 不计 PASS |

工程骨架核对限定实际付款调用链与现有 src/tests/checks 职责；本轮不新增模块、package、生成模板或运行装配，不执行全蓝图骨架审查。

### CHK-001：付款状态写入职责

- 依据与对象：CR-001 / ARC-1，`src/ui.py` → `src/order_service.py:set_status` → SQLite commit。
- 初审事实：基线 UI 自行执行 UPDATE 和 commit，绕过已有服务入口，FAIL；付款实际结果见 E-B1 / E-B2。
- 整改目标和边界：仅将付款适配调用接到已有 `set_status(connection, order_id, 'paid')`，不修改服务、存储、提交规则或公开语义；直接相关测试可补充真实数据库异常与持久化判据。
- 验收计划：初审者在实施自验后复核实际工作区；技能 Agent 在同一版本从公开付款入口执行行为保持验收。无需用户操作。
- 架构方案：核对 UI 无状态 SQL/commit，沿调用链确认服务执行存在性检查、UPDATE 和 commit；检查函数签名和正式依赖链无改变。必须符合 CR-001。
- 行为方案：临时文件 SQLite 新建 ORDER-1，公开付款返回 None、关闭重开后 paid；MISSING 抛 ValueError 且不新增记录；真实 query_only 写失败抛 OperationalError、不返回成功、状态保持原值。临时库销毁；不运行全产品测试。
- 实施工单：CHK-001；由 `/root/refactor/implementation` 维护 [Plan／Task](../../payment-refactor-plan.md) T001，现 Complete。初审 FAIL 保留，整改版本复核结论见下表。

| 批次／执行者 | 对象与方法 | 版本、实际结果与证据 | 结论 |
| --- | --- | --- | --- |
| E-L1；2026-11-15；implementation | 付款局部测试 `python -B -m unittest discover -s tests -p test_order.py -k mark_paid -v` | b5c9315 + 本轮 diff；5/5 PASS，exit 0（0.061s）；覆盖返回 None、关闭重开 paid、缺失无新增、关闭连接读错、query_only 写错、事务锁 commit 错。锁失败后回滚并从第二连接重新读取 pending，资源 finally 清理 | 局部自验 PASS；初次同为5/5，补强清理后复验；无失败 |
| E-A1；2026-11-15；refactor 技能 Agent | 独立公开 `ui.mark_paid` 调用；临时文件库 ORDER-1，执行与 E-B2 相同步骤并断言 | UI SHA-256 54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8；成功返回 None、关闭重开 paid；MISSING 抛 ValueError(`order not found`)；query_only 抛 OperationalError(`attempt to write a readonly database`)，状态仍 paid。3/3 PASS，exit 0，连接关闭及临时目录清理 | 行为保持 PASS；读错及 commit 错复用同版本 E-L1 |
| E-V1；2026-11-15；原 architecture_review 审查者 | 只读复核实际 diff、UI→服务→持久化和正式依赖链，核对候选 UI SHA | UI 仅调用已有 set_status，无 SQL/commit；服务统一存在性检查、UPDATE、commit。签名、None 返回、异常传播不变；服务、storage、runtime 未改 | CHK-001 架构复核 PASS，结合 E-A1 关闭；初审 FAIL 已整改 |

付款候选身份：基线 `b5c93159b3ee3d78ded2a26147a1f7b2a3acb19e` 加本轮未提交工作区；`src/ui.py` SHA-256 为 E-A1 所列，`tests/test_order.py` SHA-256 为 `af4d119a062b59a5a05761df84ff01ebf3983efc774a03858f1f1f4256c8226b`。服务源码 SHA-256 `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`、storage SHA-256 `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` 均与基线相同。故未变更 AC-1 所依赖提交实现，但本轮无 AC-1 运行结论。

### CHK-002：持久化与接口失败语义映射待查

- 依据：ARC-2、订单函数契约；对象为付款服务入口的存在性检查、UPDATE、commit 和异常传播。
- 初审事实：UI 基线与服务入口均先验证存在，再写入并 commit，无异常捕获；静态路径相符。E-B1 / E-B2 提供基线部分行为证据，不能将映射判为通过。
- 验收计划与方案：实施自验后，原审查者追踪目标版本调用及异常路径，技能从 CHK-001 公开入口方案验 paid、缺失及写失败；不执行订单提交验收。补充检查事实另记，规则映射仍 UNVERIFIED。
- 当前：待查 UNVERIFIED，无业务整改工单。恢复条件为用户决定生成／更新适用项目规则并完成授权内规则维护，随后依已确认规则复核；此项不阻止 CHK-001 已就绪实施或付款局部运行。
- E-V1 补充复核：目标链无异常捕获、提前成功、重试或连接关闭，存在性检查在写前，读／写／commit 异常直接传播；静态契约符合，E-A1 与 E-L1 提供运行保持证据；规则映射仍待查。

### CHK-003：正式与测试隔离映射待查

- 依据：ARC-3；对象为 src 正式依赖、tests/checks 临时数据库及连接生命周期。
- 初审事实：UI→服务，storage→sqlite3；无 src→tests/checks。原测试的临时目录和连接均清理；静态补查符合已确认设计。
- 验收计划与方案：原审查者在付款改后核对 src 导入及配置无测试身份或测试替代；核对新增付款测试用真实文件库或声明的失败替代并清理资源。观察实际职责和契约断言，不以目录名称替代判断。
- 当前：待查 UNVERIFIED，无业务整改工单。恢复条件同 CHK-002 的规则维护决定及复核；设计补查事实不等同映射关闭。
- E-V1 补充复核：正式链无测试运行器、身份或配置；新增付款测试采用真实文件 SQLite、关闭／只读／事务锁场景，事务和连接 cleanup/finally 清理。E-L1 的5/5是实施执行者实际运行结果，审查者未重复运行；映射仍待查。

### CHK-004：环境与网络边界映射待查

- 依据：ARC-4；对象为本地 SQLite 连接所有权、正式运行依赖及 runtime 配置。
- 初审事实：src 无外部调用，E-R1 配置端点 null、授权 false、网络 false；本地库连接由调用者提供。此补查不能证明 AC-3 外部真实场景。
- 验收计划与方案：原审查者在目标版本核对 src 无网络／凭据／配置替代，付款不改变连接所有权；只读复用 E-R1 的未改配置，不发外部请求。
- 当前：待查 UNVERIFIED，无业务整改工单。恢复条件同 CHK-002 的规则维护决定及复核；AC-3 另需具备真实外部开测条件。
- E-V1 补充复核：付款仅用传入连接，不打开／关闭连接，无网络、凭据、配置替代引入；runtime 未改，可复用 E-R1。静态本地符合不代表 AC-3 通过；映射仍待查。

## 3. Gate、剩余项与集成准备

- Review Gate：**UNVERIFIED，非 PASS**。CHK-001 初审 FAIL 已整改，原审查者架构复核 PASS 且行为保持 PASS，关闭；CHK-002／003／004 因适用规则映射缺失而待查。补充事实符合设计，不能将整体 Gate 改为通过。本轮技术整改已完成，完整架构对齐门禁未关闭；用户决定规则维护时机后按原编号接续。
- 行为保持：**PASS**，同一候选 E-A1 公开调用 3/3，加 E-L1 付款局部5/5；未产生全产品验收或发布通过结论。
- 历史偏差：E-H1 的 AC-2 不属于付款整改；沿 Main 交另行缺陷修复授权，修复及定向复验后才可恢复该场景的符合性判断。
- 集成准备：上述工作区候选的付款路径具备本地运行条件，入口为公开 `src.ui.mark_paid(connection, order_id)` 或 E-L1 局部命令；Python 3.11+、标准库 SQLite、可写临时目录、调用者提供已建表且含现存订单的文件库连接，并负责关闭连接即可开测。映射待查影响完整架构门禁关闭，不使本地付款候选不可运行；项目未规定该门禁须先 PASS 才能启动局部集成。
- AC-1 提交源码未改，指南入口保留为 `python -B checks/acceptance.py --scenario AC-1`，本轮未运行，不推定通过；后续需相应集成授权与临时数据库条件。AC-2 可复跑 E-H1 但已知不符合已确认要求，该场景符合性受阻；需另行授权缺陷修复及定向复验，不能凭本轮付款通过恢复。AC-3 因端点、调用权限和网络授权均不具备而 BLOCKED；需有权人员提供获授权真实测试端点、调用许可及网络执行授权，并有对应真实调用执行入口后在相应阶段取证；当前 checks 入口只报阻塞、不发外部调用，不可用本地结果替代。
- 全产品集成 Test Gate、外部真实证据与正式发布均未执行，本轮不得宣称整体候选已可发布。
- 文档写后检查：本记录与唯一 Plan 的链接、编号、初审历史、版本、证据归属、待查恢复条件已读回核对；仅这些文档执行机械校验，结果在交付回执报告。项目规则、索引、Spec、Blueprint、契约与运行配置均未改。
