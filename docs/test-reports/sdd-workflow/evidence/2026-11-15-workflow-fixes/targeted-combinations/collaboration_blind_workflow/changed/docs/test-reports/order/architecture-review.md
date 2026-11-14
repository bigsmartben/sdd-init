# Architecture Review — 订单修复候选 R1

## 范围、依据与权限

本轮只取证修复后候选相关架构，保留公开函数、文件 SQLite、AC-1/AC-2 与现存订单 paid 行为；不重构、不改 UI、不更新蓝图、契约或项目规则。依据为 [索引](../../index.md)、[Blueprint ARC-1～4](../../blueprint.md)、[订单契约](../../contracts/order.md)、[项目 CR-001～004](../../code-review-rules.md)、[Spec](../../../specs/order/spec.md) 和[共享架构规范](../../../.agents/skills/sdd-workflow/sdd/references/architecture-rules.md)。

调用链：Main `/root` → 独立技能 `/root/review` → 专业审查者 `/root/review/architecture_evidence`（sdd-architect）；后者只读取证，无文件修改。技能组织最终候选动态核验及报告写入。专业角色实际继承工作区写权限，工单限制不写；没有将其描述成物理只读文档一致性会话。未启动 sdd-doc-consistency：当前启动接口不能取得独立只读权限会话；本技能自行核对本报告链接与依据，存在争议时交 Main。审查者独立于 BUG-001 实施者。仅本报告、原始证据及 Main 后续明确授权的 `tests/architecture_probe.py` 归本阶段；不执行 Git、网络、真实部署或外部平台操作。

最终候选为 [manifest](bugfix-candidate.json) 的 `sha256:7d4083da88ed6593bc2039b890b0026681f522ac7b53d7aa8c8dcde4cb269fea`（src、checks、runtime）；service SHA-256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`。本阶段重新计算路径／内容 manifest，全部文件及候选标识匹配，见[候选核验与测试资产哈希](architecture-candidate-check.json)。没有执行 Git，不声称有新提交。环境实际为 Python 3.12.3、SQLite 3.45.1，逐场景真实临时文件数据库；日期为 2026-11-15（Asia/Shanghai）。[原始修复前快照](bugfix-initial-runtime.json) 和 [BUG-001 初始失败](bugfix-diagnosis.json) 只证明修复前事实：取消后提交曾返回 true 并持久化 submitted，不作为须保持行为。[BUG-001](../../issues/BUG-001.md) 与[原 Task](../../issues/BUG-001-plan.md) 承接唯一获授权产品修复。

最终动态命令为 `python -B tests/architecture_probe.py > docs/test-reports/order/architecture-probe.json`，退出 0；[原始 JSON](architecture-probe.json) 保留全部观察与执行前后哈希（完全一致）、候选匹配及临时目录清理结果。探针自身 SHA-256 为 `d3167d61d357abbca3d533d0600860cf568877439e123de54e4c7e1c1111a6a8`，位于[测试资产](../../../tests/architecture_probe.py)，不被正式源码依赖。该局部探针结果不替代整产品 Test Gate。

R1 最终静态复核沿用原审查者 `/root/review/architecture_evidence`：回读全部正式模块、配置、测试装配、manifest 与探针原始证据，独立重算 candidate_id 与探针哈希一致，逐项确认以下结论。动态执行由 `/root/review` 完成，未由产品实施者自证 Review。

## 规则适用性与有效性

四条项目规则均能映射当前设计，未发现过时或相互冲突；本轮没有自动维护规则。规则缺口只影响相应待查项，其他有效规则继续取证。

| 规则或共享条款 | 适用性、映射及依据 | 检查项 |
|---|---|---|
| CR-001／模块边界与依赖 | 适用：ARC-1 的服务唯一写入口；ARC-3 的 src 单向依赖。工程骨架为 src、checks、tests，按实际职责核查；无 package 生成器及模板，生成子项不适用。 | CHK-001、CHK-003 |
| CR-002／状态权威与持久化 | 适用：ARC-1/2，文件 SQLite 是权威存储，服务拥有业务状态裁决。无副本、缓存、多节点及后台恢复机制，相应子项不适用。 | CHK-001、CHK-002、CHK-005 |
| 业务与运行保障分工 | 有限适用：业务状态规则由 service 承担，见 ARC-1、契约。契约明确无重试／部署，蓝图无后台任务；限流、背压、熔断、唤醒、保活、重启、恢复策略不适用，不能据此声称已实现运行隔离。 | CHK-001、CHK-005 |
| 接口与交互语义 | 适用：同步调用、写入完成、异常、取消结果以契约为准；CR-002 覆盖持久化和异常，但没有完整表达取消不写入判据。无异步任务、并发调度、超时、迟到结果及重试装配，相应子项不适用。 | CHK-002、CHK-005（映射待查） |
| 观测数据与日志契约 | 不适用：Blueprint 明确无产品日志系统；验收 JSON 是测试原始输出，不是产品观测记录或业务状态权威。 | 不适用 |
| 观测影响与故障隔离 | 不适用产品观测机制：同上，没有采集、传输、导出、缓冲或媒体；不虚构日志失败、队列预算或降级能力。 | 不适用 |
| CR-004／环境边界与运行装配 | 适用：ARC-2/4、runtime.json、本地 Python+文件 SQLite；本地与真实外部验证必须区分。 | CHK-002、CHK-004 |
| CR-003／测试隔离与可控验证 | 适用：ARC-3、Spec 与 quickstart；正式模块不能依赖验证资产。CR-003 未完整映射测试初始化、清理及诊断，记录待查；无并行运行、时间随机依赖或重试，相关机制不适用。 | CHK-003、CHK-006（映射待查） |

CHK-005 与 CHK-006 的缺口是规则映射完整性，不能冒充实现违规。已确认契约与验收指南仍支持直接事实核验。请用户决定是否以及何时维护项目规则；恢复条件是取得维护范围及决定，由负责方补齐映射，再复核原检查项。本轮不擅自修改规则，也不将共享推荐策略直接设为新项目门禁。

## 稳定检查项

### CHK-001：状态写入职责

- 依据：ARC-1、CR-001；`src/ui.py:4-6`、`src/order_service.py:18-25`。通过条件是 ui 只调用现有服务入口，全部业务状态写入由服务承担。
- 初审：ui.mark_paid 直接执行 UPDATE 和 commit，绕过 order_service.set_status，**FAIL**。paid 可持久化不能证明职责符合。影响是适配层独立写状态并绕开服务统一校验；缺失订单语义由集成阶段负责 [BUG-002](../../issues/BUG-002.md)，本报告不重复登记。
- 复核方案：候选回读全部 SQL 写入位置、imports 和实际调用链；若以后获整改授权，独立复核调用委托及 paid 持久化、缺失订单 ValueError。此轮禁止修 UI，因此保持 Unfixed，无整改 Task。
- 最终候选事实：ui 哈希与修复前相同，仍为 `src/ui.py:4-6` 的直接 UPDATE／commit；探针第二连接读到 paid，仅证明须保持的现存订单结果。**FAIL／Unfixed**。未因 BUG-001 关闭而关闭本项。

### CHK-002：文件持久化与失败不返回成功

- 依据：ARC-2、CR-002、契约。检查 `create_order → commit`、`cancel_order → set_status → commit`、`submit_order → set_status → commit`，storage 只连接／建表。
- 初审：SQL／commit 后才正常返回；没有捕获数据库异常并转成功的分支。仅静态事实不足以证明持久化通过。
- 取证方案：独立文件数据库第二连接读取 submitted；只读 SQLite 执行真实写入失败须抛 OperationalError；受控连接代理在 commit 抛 OperationalError，公开调用不得返回成功。代理不是物理磁盘故障实验，不据此宣称断电恢复能力。关闭连接并清理临时目录。
- 最终候选事实与结论：第二连接读取 submitted，accepted=true；真实只读数据库写入抛 OperationalError；受控 commit 失败抛 OperationalError，均未转为成功。结合源码 commit 返回先于成功返回，**PASS**。创建、取消及正常提交的重开持久化另复用[同候选 Bugfix R1](bugfix-001.md)，不外推至未约定的磁盘断电恢复。

### CHK-003：正式模块与验证资产依赖隔离

- 依据：ARC-3、CR-003；全部 `src/*.py`、`checks/acceptance.py:8-10`、`tests/test_order.py`、`tests/architecture_probe.py`。检查导入、动态加载及配置读取。
- 初审：storage 仅导入标准库 sqlite3；其余正式模块无测试／夹具依赖，checks/tests 单向调用 src。源代码没有测试身份、测试路由或运行开关，静态符合。
- 最终候选复核：全部 src 回读和哈希绑定表明仅 service 增加取消分支；正式依赖仍只有 storage → sqlite3，无动态测试加载或 fixture 配置读取，验证资产单向 import src。**PASS**。测试运行事实与工程资产归属不替代业务权限。

### CHK-004：本地装配与真实外部证据边界

- 依据：ARC-4、CR-004；runtime.json、全部 src、`checks/acceptance.py:14-22`。
- 初审：正式函数无网络调用；端点为空、授权和网络均 false；AC-3 输出 BLOCKED，不以本地状态冒充真实服务回执。该本地边界符合。真实服务 AC-3 尚未执行。
- 恢复条件：有权人员提供授权测试端点、调用权限、网络访问，并安排获授权的真实服务执行路径。现有 AC-3 分支无条件返回 BLOCKED，仅补配置仍不能完成真实调用。本轮不配置服务、不取凭据、不新增本地模拟。
- 最终候选复核：runtime 与所有正式调用链绑定相同 manifest，仍无网络入口或本地模拟外部回执。**PASS（本地 CR-004 边界）**；真实服务 AC-3 **BLOCKED／未执行**，不混入本地 PASS。真实服务阻塞只影响 AC-3，不阻塞 CHK-001～003 或本地功能验收。

### CHK-005：取消交互不变量与项目规则映射

- 依据：Blueprint 同步交互约定、订单契约 submit_order、Spec AC-2；共享接口与交互语义。项目规则未显式列出取消不写入判据，映射状态 **UNVERIFIED／待查**，不擅自扩写 CR-002。
- 初审实现事实：旧 `submit_order` 忽略 read_status 返回值并无条件提交，见 BUG-001 初始失败；唯一获授权修复由原 BUG-001 Task 执行。
- 最终候选事实方案：创建、取消后追踪 submit SQL，必须返回 false、无 INSERT/UPDATE/DELETE/REPLACE；关闭重开后保持 cancelled。即使该事实通过，规则映射仍保留待查，待用户决定规则维护时机。
- 最终候选事实：`src/order_service.py:28-32` 新增 cancelled 判断，实际追踪只出现 SELECT，没有状态写 SQL；返回 false，关闭重开后仍 cancelled，**已确认契约事实 PASS**。项目规则取消映射仍 **UNVERIFIED／待查**；这不是修复失败，也不重新打开 BUG-001。

### CHK-006：测试数据隔离及可复跑证据映射

- 依据：ARC-3、Spec、quickstart；共享测试隔离与可控验证。CR-003 只覆盖 src 依赖，初始化／清理／诊断等映射未完整表达，**UNVERIFIED／待查**；不引入未确认的并行、重试或质量阈值要求。
- 初审：checks/acceptance 使用逐场景 TemporaryDirectory，finally 关闭连接，重新连接检查状态；单测 addCleanup 关闭连接并清目录。断言对应 AC，未以“没抛异常”替代业务结果。
- 最终候选方案：沿用原入口与最终候选定向证据，架构探针使用独立临时文件、关闭连接、检查临时目录已移除并保存原始 SQL／异常／前后哈希。探针置于 tests，src 不导入它。映射缺口须由用户决定维护时机，事实证据不能代替规则维护决定。
- 最终候选事实：探针 `temporary_data_cleaned=true`、前后快照一致；受控异常路径 finally rollback／close，临时目录最终移除。原验收及单测清理装配保持；没有覆盖所有可能失败分支的清理，也未做破坏性进程终止实验。取证事实符合本地指南；规则完整性仍 **UNVERIFIED／待查**。不把本次运行清理证据外推成所有失败或进程崩溃清理保证。

## Review Gate 与接续

**Review Gate：FAIL，绑定上述最终候选。** CHK-001 为明确未修复偏差；CHK-002/003/004 的已映射本地规则均 PASS；CHK-005/006 为规则映射 UNVERIFIED，已验证的取消及清理事实单独记录。观测、生成、后台运行等不适用项不计 PASS。本轮没有获授权架构整改，不能自行续派开发修复 UI。没有将真实外部权限缺口用于阻塞所有本地审查。

恢复与建议：CHK-001 如获后续整改授权，按原编号将 ui 委托既有 set_status 后复核调用链及 paid／缺失订单契约；BUG-002 的业务修复授权由 Main 单独协调。CHK-005/006 请用户决定规则维护时机，未获授权前不改权威规则。AC-3 仅在端点、权限、网络和真实服务执行路径齐备后恢复。

候选已具备本地库／CLI AC-1/AC-2 开测条件：Python 标准库、真实临时文件 SQLite、原公开入口，运行命令见 [quickstart](../../../specs/order/quickstart.md)。UI 写入口职责偏差不阻止这些本地场景开测；缺失订单业务偏差按 BUG-002 影响相应契约场景，不能因局部通过声称全产品通过。功能行为保持及整产品 Test Gate 由 [集成报告](integration.md) 独立判定；BUG-001 定向结论见 [Bugfix 报告](bugfix-001.md)。真实服务缺前置只阻塞 AC-3。正式发布另需授权与依据，本报告不授予发布许可。

## 写后检查

执行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . --format json docs/test-reports/order/architecture-review.md`，退出 0、0 errors、0 warnings，原始结果见[文档机械检查](architecture-doc-check.json)。本技能另核对稳定检查项、引用、实际候选关联、授权边界、模拟／真实证据区分及恢复条件；未改权威规则、产品代码、索引或 Status。机械检查不代表 Review 通过。
