# 订单架构审查记录

## 范围、依据与快照

实际调用者及回执接收方为 Main；审查者为独立 sdd-refactor Agent `/root/review`。本轮仅审查新建、取消、提交、公开 `ui.mark_paid`、AC-3 的相关架构，授权终点为本记录和专属证据；未获授权自行整改、改写规则、调用外部服务或部署。

依据为 [Blueprint](../../blueprint.md) ARC-1～4、[订单契约](../../contracts/order.md)、[项目规则](../../code-review-rules.md) CR-001～004、[Spec](../../../specs/order/spec.md) 和 TASK.txt。共享架构规范用于筛选检查范围，未确认的推荐策略不作为门禁。

初审版本：`a8f4cf7154b9e81d9b4ab62b8cd0cecddb36eec5`，src 无未提交修改；并行工作的文档不影响源码快照。环境为隔离本地 Python 3.12.3 / SQLite 3.45.1 / 临时文件 SQLite，无网络、端点和外部调用权限。初审执行 UTC 时间、源码 SHA-256、实际回读、异常与临时数据清理见 [原始证据](evidence/review-initial.json)。

## 规则适用性与映射

| 共享规范对象 | 适用性 | 项目映射、依据与范围 |
| --- | --- | --- |
| 模块边界与依赖，工程骨架 | 适用 | ARC-1/3，CR-001/003；检查 src 实际模块、全部写入和装配，见 CHK-001/003。无生成模板机制，无需新增层或模块。 |
| 状态权威与业务实体持久化 | 适用 | ARC-1/2，CR-001/002；文件 SQLite 为权威，服务业务写入，第二连接和重开回读，见 CHK-001/002。无缓存、副本、多节点合并。 |
| 业务与运行保障分工 | 不适用专项机制 | 契约明示没有重试、后台恢复、限流或运行控制，不臆设策略及对应规则。业务状态职责已由 CHK-001 覆盖。 |
| 接口与交互语义 | 适用同步/失败/取消路径 | ARC-2 与契约，CR-002 覆盖持久化完成和异常传播，CHK-002；AC-2 与不存在订单属于业务判据，缺陷另交 Main。异步、超时、迟到、多任务并发不在已确认设计中。 |
| 观测数据与日志契约 | 不适用 | 蓝图及契约无产品日志采集、传输、保存机制；检查输出 JSON 为验收证据，不能视为产品观测能力。 |
| 观测影响与故障隔离 | 不适用 | 没有观测组件、导出、缓冲或质量预算，不能宣称已验证遥测隔离或新增相关要求。 |
| 环境边界与运行装配 | 适用 | ARC-4，CR-004，CHK-004；runtime.json、src 与 checks 实际本地调用链。 |
| 正式实现与测试实现隔离 | 适用 | ARC-3，CR-003，CHK-003；测试可以调用 src，src 不得依赖测试身份及配置。 |
| 测试设计与执行 | 适用本轮本地取证条件 | 文件 SQLite、临时初始化/清理、公开调用、实际状态断言和快照关联，CHK-003。时间/随机业务逻辑、外部模拟、并行共享、重试和 CI 平台专项无适用机制。 |

CR-001～004 对适用 ARC 决定的映射有效，无须维护项目规则。共享规范中不适用的专项能力不构成缺项。测试工具自身的详细功能覆盖由集成报告判定，本 Review 不替代 Test Gate。

## 稳定检查项与初审

### CHK-001：服务写入职责与 UI 边界

- 依据及路径：CR-001、ARC-1；`ui.mark_paid → order_service.set_status → SQL/commit`，并检查所有 src 状态写入位置。
- 初审：**FAIL / Unfixed**。`src/ui.py:5–6` 直接 UPDATE 和 commit，绕过服务；order_service 为新建、取消、提交提供业务写入，storage 仅连接、建表。paid 可持久化不证明职责符合。
- 影响：存在独立架构偏差；并发现 mark_paid 对不存在订单返回 None，未按契约抛 ValueError，此业务缺陷交 Main 登记，不能把架构偏差本身当作业务缺陷或默认获得重构权限。
- 恢复及复核：只有 Main 交付已授权的实际候选快照后复核；核对 UI 仅调用服务、所有状态 SQL 的业务入口与 storage 职责，公开 paid 正常结果仍为 paid、缺失订单按契约异常、数据库异常向上传播。审查者不得自行修改 src。
- 工单及行为保持：当前无架构整改工单，实施方式与 Task 由 Main 及实施执行者决定；业务验收由独立集成执行者关联实际候选版本。

- 候选复核（UTC 2026-11-14 16:25，审查者 `/root/review`）：**PASS / Closed after recheck**。实际 `ui.mark_paid` 仅调用 `order_service.set_status(connection, order_id, "paid")`；全部状态 INSERT/UPDATE 仅在服务 create_order/set_status，storage 仅 CREATE TABLE 与连接，src 无其他状态写入入口。[候选证据](evidence/review-candidate.json) 保留哈希、依赖、写入位置及实际公开调用。pending/cancelled/submitted/paid 均可持久化 paid，缺失订单 ValueError，写入和实际 commit 失败传播符合契约；行为保持参见独立 [复验结果](retest-results.json) PAID、MISSING、DB-ERROR 与 [复验单测](retest-unit.txt)。
- 实际实施归属：[行为修复 Plan T001](../../plans/order-fixes.md)，其修复缺失对象异常复用服务入口时同时消除了本架构偏差；审查者没有派发或执行独立重构。

### CHK-002：持久化完成与失败传播

- 依据及路径：CR-002、ARC-2、订单契约；新建、取消、提交、set_status/mark_paid 的 SQL 与 commit、第二文件数据库连接回读、关闭重开。
- 初审：**PASS / Conforming**（限定持久化完成/异常传播架构判据）。新建 pending、正常提交 submitted、取消 cancelled、标记 paid 均第二连接可见；最终 paid 关闭重开仍可见。SQLite query_only 写入拒绝使四个公开路径均向上传播 OperationalError；源码未捕获异常转为成功，commit 在成功返回前。
- 保留差异：取消后提交实际返回 true、状态 submitted，与 AC-2 不符；这是原有业务缺陷而非须保持的预期，已交 Main。此项 PASS 不代表 AC-2 或全部函数业务契约通过。提交 commit 本身故障本轮没有单独注入，失败不转成功同时依据无异常吞噬的源码路径，不扩张为全部 SQLite 故障矩阵已验。
- 复核计划：候选到位后沿同一路径核查写入、commit 顺序和异常；复用满足快照条件的证据，补验取消后提交 false/cancelled、禁止取消后的写入。业务判据见 Spec/契约，独立验收由 Main 转交。
- 整改工单：此架构项无需整改，业务问题归原 Issue/Task。

- 候选复核：**PASS / Conforming**。候选保留 create/set_status 的 execute→commit 顺序，异常无吞噬；cancelled submit 直接 False，真实 SQLite trace 仅 SELECT，关闭重开仍 cancelled。[独立集成证据](retest-results.json) 覆盖 AC-1 正常提交、AC-2 零写入、CREATE/CANCEL/SET-STATUS 与 DB-ERROR。[本审查实际 commit 故障证据](evidence/review-candidate.json) 使用真实文件 SQLite 的 authorizer 拒绝 COMMIT：create/cancel/submit/set_status/mark_paid 均抛 DatabaseError，第二连接看到原 pending 和行数 1，没有成功回执；故障后原连接存在未提交事务，由调用者显式 rollback 再关闭并清理。此证据仅为 SQLite 授权拒绝 commit，不宣称覆盖磁盘故障/全部数据库故障；[局部单测](retest-unit.txt) 的 commit 代理另只证明传播机制。
- 业务差异恢复：初审 AC-2 原缺陷已在候选由独立集成复验 PASS，原缺陷事实保留，不作为须保持的行为。实施见同一 Plan T001。

### CHK-003：实际装配与测试隔离

- 依据及路径：CR-003、ARC-3；检查 src 全部 imports、src/ui/storage/service 的实际调用、checks/acceptance.py、checks/runtime_details.py 和 tests/test_order.py。
- 初审：**PASS / Conforming**。src 唯一外部 import 为标准库 sqlite3；正式运行无 tests/checks、测试身份、夹具配置依赖。checks/tests 调用 src，临时文件连接由调用方关闭，临时目录清理已确认。模块职责语义的 UI 写入偏差单列 CHK-001，不因目录存在而判为符合。
- 复核计划：实际修复版本再次追踪新增 imports 与调用装配，确保无动态测试加载、测试特判、模拟外部回执；取证以公开入口实际结果而非仅无异常。
- 整改工单：无需；没有生成脚手架、模板、构建 package 或后台入口，不要求新增。

- 候选复核：**PASS / Conforming**。逐个追踪 src、现有 checks/acceptance.py、runtime_details.py、新增 checks/order_regression.py 和 tests/test_order.py；正式路径新增依赖仅 `ui → order_service`，storage 仅标准库 sqlite3，src 无测试 import/动态加载/测试特判。新增 CommitProbe 仅在 tests，不进入正式链。回归运行器只调用正式公开接口和实际临时 SQLite，AC-3 委托原验收的阻塞分支，无模拟成功。候选导入及 SQL 位置见专属证据，独立运行命令、原始结果与前后稳定快照见 [复验命令](retest-commands.json)、[结果](retest-results.json)、[快照](retest-snapshot.json)。

### CHK-004：本地环境与外部证据边界

- 依据及路径：CR-004、ARC-4；runtime.json、src 全部调用链、acceptance.py 的 AC-3 分支。
- 初审：**PASS / Conforming**。src 无网络调用；外部端点为 null、授权 false、网络 false；AC-3 分支只读配置返回 BLOCKED，没有伪造外部服务结果。
- 行为结果及恢复条件：AC-3 **BLOCKED**，须获授权的真实端点、权限、配置及可访问的独立运行环境。此阻塞不影响本地新建/取消/提交/paid 的开测；不以本地持久化结果代替外部回执。
- 复核计划：候选到位后核对实际配置和新增调用，继续保留真实服务缺口。不启动外部调用，不写入服务凭据或部署配置。
- 整改工单：无需。

- 候选复核：**PASS / Conforming**。runtime 配置与本地依赖边界未变；src 新增代码无外部调用，测试输出未冒充真实服务回执。独立复验 AC-3 仍 BLOCKED（端点未配置、无权限），符合 ARC-4 的证据边界。恢复仍须独立授权及真实服务条件，不改变本地代码伪造结果。

## Gate 与后续条件

初审 Review Gate：**FAIL**，对应初审快照；适用项目检查 4 项，3 PASS、1 FAIL（CHK-001），不适用专项不计 PASS。该结论为历史初审事实，后续候选结论如下。

候选 Review Gate：**PASS**，CHK-001～004 共 4 项全部通过，不适用专项不计 PASS。候选是原 HEAD 加未提交修复，不能与初审 clean HEAD 混同；[实际修复快照](bugfix-snapshot.json)、[独立复验快照](retest-snapshot.json) 与本审查候选证据的全部 src SHA-256 完全一致。关键文件 order_service 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，ui 为 `c4a9e5b0789129c89bb71387e2aaed619944d115aff5a53c7fb5320fcbff88ae`。规则、Blueprint 与接口未被改写；无剩余适用架构偏差。

本地集成就绪：同一隔离 Python/临时文件 SQLite 环境，公开服务/UI 函数及 `python -B checks/order_regression.py` 为运行入口。独立复验 12 场景中 11 PASS、0 FAIL、1 BLOCKED，另 6 单测 PASS；AC-2 与 missing_paid 原缺陷修复，相关原有正常行为及持久化、异常回归通过。整轮 **Test Gate BLOCKED**，仅 AC-3 缺少真实端点/权限/网络条件；本地场景可测且已复验通过。Review PASS 不替代外部真实服务回执、整轮集成通过或正式发布授权。需外部授权或新配置时由 Main 处理；本审查仅写记录和专属证据。
