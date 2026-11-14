# Architecture Review Record — 订单当前版本

## 1. 范围与上下文

- 目标：按 [TASK](../../../TASK.txt) 对当前隔离订单版本做相关架构初审及修复后复核；仅审查，不直接整改。范围为 src、checks、tests、运行配置及实际调用关系，无外部调用授权。
- 依据：[Blueprint](../../blueprint.md) ARC-1～4、[Code Review Rules](../../code-review-rules.md) CR-001～004、[契约](../../contracts/order.md)、[Spec](../../../specs/order/spec.md)、[验收指南](../../../specs/order/quickstart.md)，以及共享 architecture-rules.md。已确认规则均有效；未确认的并发、幂等、产品日志策略不构成新门禁。
- 初审快照：HEAD `fc366da8aff900abc000129676514d994ca5c671`；初审开始 git status 为空，结束仅有并行阶段新增 docs/issues、docs/test-reports，产品源码无变化。
- 环境：2026-11-15（Asia/Shanghai），Python 3.12.3、SQLite 3.45.1；[runtime](../../../runtime.json) 指定逐场景临时文件 SQLite、无端点、无调用授权、禁网络。技能 Agent 实际运行 `python -B checks/runtime_details.py` 核对版本与源码哈希。
- 执行者：技能 Agent `/root/order_review`；独立专业审查者 `/root/order_review/architecture_initial`，调用者为技能 Agent，回执由 Main `/root` 接收汇总。专业审查者只读，未实施整改；集成测试由 Main 的另一个阶段独立组织。
- 行为基线：AC-1 true/submitted 且重开仍存；AC-2 false/cancelled 且不得写入；现存订单 mark_paid 后 paid 持久化；缺失订单 ValueError；数据库异常向上传播；函数签名及无网络行为保持。原有业务失败不得作为保持基线。

| 初审文件 | SHA256 |
| --- | --- |
| src/__init__.py | `10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded` |
| src/order_service.py | `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` |
| src/storage.py | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| src/ui.py | `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b` |
| runtime.json | `e25bd6e9530e59c71dc6cd82b01722c85c24f609e0e7f16f398afe3a4e97ea85` |
| checks/acceptance.py | `3068c25ce6dee0b604c70f97e48b7ac9dc703ee44a2190c561972e4f65625eb9` |
| checks/runtime_details.py | `28fd81e51f8a07c30ae728f0faafd766965181b6b8178f3933871cdd87ef388d` |
| tests/test_order.py | `dc3d5eb12ac351e9203c9ef0cebb1681b284215efabe2f95528c12dadf5e8311` |

### 修复后复核快照

Main 于本轮正式分发修复及局部证据后，原独立审查者完成第二批次只读复核（2026-11-15，Asia/Shanghai）；技能 Agent 另运行 runtime_details 和 git diff 独立核对。HEAD 仍为 `fc366da8aff900abc000129676514d994ca5c671`，加未提交修复：service SHA256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，ui 为 `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`。其他 src、runtime、checks、原单测均与初审相同。新增回归资产 `tests/order_regression.py` SHA256 为 `d21f4caeffe9a341e3e60611e743a3ec5d97773028923bb1599b342ecdbb00ad`。关联 [实际修复版本](evidence/bugfix-local-version.json)、[Bugfix 定向复验](evidence/bugfix-retest.json)、[Bugfix 报告](bugfix.md) 及 [Plan T001](../../plans/order-bugfix.md#t001-恢复取消保护和服务付款入口并验证)。本轮未改产品或测试代码、未重跑已充分证明的用例；沿用正式分发且匹配快照的证据，完整集成 Test Gate 由原测试阶段单独交付。

## 2. 检查项与后续

| 规则或共享指导 | 适用性及依据 | 检查项 |
| --- | --- | --- |
| CR-001；模块边界与依赖、状态权威 | 适用，ARC-1 明确 UI／服务／storage 职责，包含实际工程骨架 | CHK-001 |
| CR-002；状态权威与持久化 | 适用，ARC-2 文件持久化与完成判据 | CHK-002 |
| CR-002；接口与交互语义 | 适用，数据库异常传播及已有业务契约；业务失败单列，不扩张架构规则 | CHK-003～005 |
| CR-003；正式实现与测试实现隔离 | 适用，ARC-3 及实际 imports／装配 | CHK-006 |
| CR-004；环境边界与运行装配 | 适用，ARC-4 与本地运行配置 | CHK-007 |
| 测试隔离与可控验证 | 适用，ARC-3 与 quickstart 已明确数据和清理 | CHK-008 |
| 业务与运行保障分工 | 无后台任务、重试、部署或运行保障机制；无新增幂等要求 | CHK-009，不适用 |
| 观测数据与日志契约、观测影响与故障隔离 | Blueprint 明确无产品观测；验收 JSON 是测试输出 | CHK-010，不适用 |

通用验收安排：Main 提供修复快照、原 Issue／Task 与局部证据后，由原审查者沿下列编号复核；原集成执行者承担文件 SQLite 用户入口行为验收。复核保留初审事实，记录实际新源码哈希；修复实现方案归原 Task。当前未分派纯架构整改。规则映射无过期或缺失阻塞；测试生命周期按已确认 quickstart 核查，不据共享指导新增架构决定。

### CHK-001: 状态写入职责

- 依据／对象：CR-001、ARC-1；ui → order_service → SQL／commit，storage 仅连接建表。
- 初审：**FAIL**。`src/ui.py:4-6` 直接 UPDATE／commit，绕过 `src/order_service.py:18-21` 已有 set_status。工程目录存在不能代替职责符合；storage:5-9 符合连接建表职责。
- 整改目标／范围：UI 通过现有服务入口持久化 paid，UI 不执行状态 SQL。Main 已确认可在缺失订单行为缺陷修复中使用 set_status 同时恢复 ARC-1；未授权单独技术整改。
- 复核步骤／通过条件：扫描 src 全部 INSERT／UPDATE／commit，追踪 mark_paid → set_status → UPDATE／commit；确认 UI 无状态 SQL、无反向依赖；现存 paid 持久化、缺失订单及数据库异常均保持契约。
- Task：待 Main 提供。状态：Unfixed，FAIL。
- 第二批次复核：**PASS，Closed after recheck**。ui:3,6-7 仅调用服务 set_status；服务:18-21 承担读取、UPDATE、commit。src 全部订单 INSERT／UPDATE 仅位于服务:7,20；storage 仍仅连接建表，无反向依赖。[定向证据](evidence/bugfix-retest.json) paid 返回 None、重开 paid、缺失对象 ValueError；[局部回归](evidence/bugfix-local-regression.json) O-19 数据库异常传播。关联 ORDER-002／Plan T001；初审偏差关闭。

### CHK-002: 文件持久化与完成判据

- 依据／对象：CR-002、ARC-2；order_service 写入及 storage 文件连接、第二连接／重开读取。
- 初审：最初 **UNVERIFIED**，随后 Main 分发同源快照证据后补为 **PASS**（仅持久化与完成判据）。静态 `order_service.py:7-8,20-21,28-31` 写入后 commit，submit 在 commit 后返回 true；`storage.py:5-9` 使用调用者路径。`checks/acceptance.py:23-37` 使用临时文件关闭重开；`tests/test_order.py:22-28` 用第二连接检查 paid。实测 [initial-acceptance](evidence/initial-acceptance.json) AC-1 PASS、[initial-regression](evidence/initial-regression.json) O-01、O-06～09 PASS，分别证明创建、取消及 paid 文件持久化；[initial-unittest](evidence/initial-unittest.json) 第二连接 paid 通过。[initial-version](evidence/initial-version.json) 和 [initial-runtime-after](evidence/initial-runtime-after.json) 关联前后相同产品源码。AC-2 状态规则错误另归 CHK-004，不伪称其业务符合。
- 恢复／复核：Main 分发同快照实际文件 SQLite 验收证据，或在修复快照重跑创建、取消、提交、paid 的文件持久化检查；须核对源哈希，不以内存数据库探针代替。成功后返回且第二连接／重开见到约定状态为通过。
- 整改／Task：无独立整改派单。状态：Conforming，PASS；修改后仍须按原判据复核。
- 第二批次复核：**PASS，Conforming**。服务:7-8,20-21 写入后 commit，:31-32 完成后返回 true。[AC-1](evidence/bugfix-local-ac1.json) true/submitted、[AC-2](evidence/bugfix-local-ac2.json) false/cancelled，均文件数据库关闭重开；[局部回归](evidence/bugfix-local-regression.json) O-07～09 重开 paid、[单测](evidence/bugfix-local-unittest.json) 第二连接 paid 通过。创建和取消未变路径沿用同源初审证据，受影响提交／付款使用修复快照证据。

### CHK-003: 数据库异常不伪装成功

- 依据：CR-002、契约异常条款；所有写入口。
- 初审：**PASS**。源码无异常吞掉路径，正常返回在 commit 后；专业审查者以模拟连接让 commit 抛 sqlite3.OperationalError，create、set_status、cancel、submit、mark_paid 均传播异常，无成功返回。此证据限异常传播，不证明磁盘故障恢复。
- 复核：检查改后全部异常路径并对变化入口重复 commit 故障探针；异常必须传播。行为验收的实际持久化由 CHK-002 单独判定。
- Main 正式分发的 [initial-regression](evidence/initial-regression.json) O-15～19 还证明真实文件 SQLite query_only 失败传播；O-20 证明实际 commit 被读锁阻塞时抛 OperationalError，调用者回滚后状态 pending。失败时连接仍有事务，自动回滚并非本项目已确认保证，不据此新设违规。
- 整改／Task：不适用。状态：Conforming，PASS。
- 第二批次复核：**PASS，Conforming**。新 UI 与服务均无异常捕获；[局部回归](evidence/bugfix-local-regression.json) O-15～19 真实 query_only 失败传播，O-20 真实 commit 读锁失败传播，调用者 rollback 后重开 pending；保留失败后事务仍存在的事实，不新增产品自动回滚保证。

### CHK-004: 取消后提交契约

- 依据：契约 submit_order、AC-2；属于业务缺陷交接，不计为新增架构门禁。
- 初审：**FAIL（业务）**。`order_service.py:28-31` 忽略读到的状态，无条件改 submitted。专业审查者内存 SQLite create → cancel → submit 得 true/submitted，应为 false/cancelled。
- 复核／行为保持：在实际修复快照执行正式 AC-1／AC-2 文件 SQLite 入口并重开检查，cancelled 提交不得发生写入；保留 AC-1 true/submitted。必要时 SQL trace 核对无 UPDATE。
- 整改／Task：交 Main 的 Bugfix 链，[ORDER-001](../../issues/ORDER-001.md)；[initial-acceptance](evidence/initial-acceptance.json) 文件 SQLite 同样 true/submitted，正式确认缺陷。Task 待修复回执，初审未修复。
- 第二批次复核：**PASS，Closed after recheck（业务）**。service:29-30 cancelled 直接 false，不到写入及 commit；[定向证据](evidence/bugfix-retest.json) AC-2 false/cancelled，SQL trace 仅 SELECT、无 UPDATE／COMMIT；修复快照 AC-1 仍 true/submitted。关联 ORDER-001／Plan T001。

### CHK-005: 不存在订单异常契约

- 依据：契约规定不存在订单抛 ValueError；关联 CHK-001。
- 初审：**FAIL（业务）**。`order_service.py:11-15` 有存在性校验，set_status／cancel／submit 通过该路径；ui:4-6 无校验，专业审查者内存 SQLite 调 mark_paid(MISSING) 返回 None，未抛异常。
- 整改目标：缺失订单抛 ValueError；现存订单仍 paid。建议通过已有服务入口修复，接口和已确认职责均无需新决策。Main 已认可此恢复方向，实施由 Bugfix 调度。
- 复核：核对 set_status／cancel／submit／mark_paid 缺失订单均 ValueError，paid 文件持久化和异常传播保持。[initial-regression](evidence/initial-regression.json) O-14 正式文件 SQLite 证据同样失败，关联 [ORDER-002](../../issues/ORDER-002.md)。Task 待 Main 提供；初审未修复。
- 第二批次复核：**PASS，Closed after recheck（业务）**。ui:7 → service:19 → :11-15 缺失订单 ValueError；[局部回归](evidence/bugfix-local-regression.json) O-11～14 均抛 ValueError，既有行和重开数据保持；O-07～09 paid 持久化、O-19 错误传播保持。关联 ORDER-002／Plan T001。

### CHK-006: 正式依赖与测试隔离

- 依据：CR-003、ARC-3。
- 初审：**PASS**。src/__init__.py 仅文档字符串；order_service／ui 无测试依赖，storage:2 仅 sqlite3。checks/acceptance.py:8-10 与 tests/test_order.py:6 从验证资产调用 src；runtime 配置由 checks 读取，无测试身份路由、动态加载或夹具开关。
- 复核：扫描全部正式 imports、动态加载、配置读取及实际入口；正式模块不得加载验证资产。无需整改，Conforming。
- 第二批次复核：**PASS，Conforming**。唯一新增正式依赖为 ui:3 对 src 服务模块；无 tests／checks／runtime 配置依赖、动态加载或测试身份分支；新回归资产:15 调用 src，未倒置依赖。

### CHK-007: 本地装配与无外部调用

- 依据：CR-004、ARC-4、runtime。
- 初审：**PASS**（仅本地架构）。runtime 为隔离临时文件 SQLite、空端点、未授权、禁网络；src 无网络路径；checks/acceptance.py:14-22 明确返回 BLOCKED，不伪造真实外部回执。23-37 为本地临时 SQLite 装配。
- 复核：变化配置／调用链无网络，外部 AC-3 继续保留 BLOCKED。其恢复须有权人员提供端点、调用授权和可访问环境，不通过改写本地逻辑制造证据。无需整改。
- 第二批次复核：**PASS，Conforming（本地架构）**。runtime 及 checks 哈希未变，源码无新网络行为；外部 AC-3 保留阻塞。此项不表示真实外部服务验收通过。

### CHK-008: 测试生命周期与可控验证

- 依据：ARC-3、quickstart、共享测试隔离指导。
- 初审：**PASS（结构核查）**。acceptance:23-37 每场景独立临时目录，finally 关闭连接；tests:10-16 cleanup 按 LIFO 先关连接再删目录。断言对应 AC-1／AC-2／paid，acceptance:39-55 保留场景、实际／期望和退出码。
- 限制／复核：初始单测缺取消、缺失订单、数据库故障覆盖，单测通过不能表示全功能通过；实际运行清理和最终版本关联由集成报告补齐。复核变化测试的依赖边界、清理及契约断言；不要求增加与实现镜像的测试。
- 第二批次复核：**PASS（结构及已分发执行覆盖）**。新回归资产:23-38 逐场景临时文件并 finally 关连接，:58-60 关闭重开，:153-174 读锁由调用者 rollback 及释放锁，:210-236 比较实际／期望并保留异常和非零失败退出码；版本记录与命令 stdout／stderr／exit 可追溯。[局部回归](evidence/bugfix-local-regression.json) O-07～20 14 项 PASS，未将定向范围冒称全量集成，也未推断未记录的独立文件系统清理观测。

### CHK-009: 运行保障与后台恢复

**Not applicable**。Blueprint 和契约明确同步函数，无后台任务、重试、恢复、部署机制；没有已确认的并发、重复提交或恢复幂等新保证。不得将单次 commit 扩张为跨调用事务承诺。若范围变化，由 Main 取得设计决定后恢复检查。

第二批次复核保持不适用：cancelled 短路未引入任何上述机制或新保证。

### CHK-010: 产品观测与故障隔离

**Not applicable**。Blueprint 与契约明确无产品日志、采集、导出或保留机制，源码一致；checks 的 JSON 为测试输出。无需引入观测模块。若产品机制变化，由 Main 取得已确认策略后恢复检查。

第二批次复核保持不适用：测试 JSON 与 SQL trace 仍仅为验证证据，未引入产品观测系统。

## 3. Gate 与待续事项

- 初审 **Review Gate FAIL**：CR-001／CHK-001 明确偏差；CHK-002 已通过 Main 分发的同快照运行证据补查为 PASS。CHK-004／005 独立交业务缺陷链，不能用业务失败扩大架构规则。
- 第二批次／当前 **Review Gate PASS**：上述修复快照适用架构检查 CHK-001～003、006～008 全部 PASS，009／010 不适用；CHK-004／005 行为缺陷按原判据复核通过。规则映射继续有效，无新增架构偏差、待决设计或 Review 阻塞项。实现统一关联 Plan T001，原初审失败事实保留。
- 集成准备：修复快照在本地文件 SQLite 已具备集成条件，受影响行为保持证据通过；原测试 Agent 仍负责完整冻结快照复验及 Test Gate，本文不代替该结论。AC-3 缺外部条件，继续阻塞且不访问网络；恢复需有权人员提供真实端点、调用权限、允许网络的环境和协议／回执判据。
- 文档检查：初审与本次更新均对本文件执行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/current-review.md` 并语义读回；结果交 Main 回执。索引由 Main 统一链接本记录。
