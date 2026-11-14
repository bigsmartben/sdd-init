# Architecture Review Record — 本地订单修复候选

## 1. 范围与依据

本轮仅审查当前隔离订单项目的正式模块、验证依赖和本地运行装配；不修改产品、测试、配置或项目规则，不执行 Git、外部平台或真实部署操作。依据 [Spec](../../specs/order/spec.md)、[Blueprint](../blueprint.md) ARC-1～4、[订单契约](../contracts/order.md) 和 [Code Review Rules](../code-review-rules.md) CR-001～004。paid 持久化及既有接口必须保持。修复取消后提交的实施和独立定向复验归 [BUG-001](../issues/BUG-001.md)。

审查执行链为 Main `/root` → 技能 Agent `/root/review` → 专业审查者 `/root/review/architect_check`。专业审查者未参与实施；运行环境为隔离本地 Python 与每场景临时文件 SQLite。初审环境及源码快照见 [基线环境](../test-reports/order-cancel/baseline-environment.json)。最终候选由 Main 转交后已用 `sha256sum src/*.py runtime.json` 独立核验。`src/order_service.py` SHA256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，storage、ui、初始化模块及 runtime 未变；全量目标文件及测试哈希见 [候选环境](../test-reports/order-cancel/candidate-environment.json)。本轮不用 Git 定位版本。取证时间为 2026-11-14 UTC（本地 2026-11-15），Python 3.12.3、SQLite 3.45.1。

四条现有项目规则可承接本轮已确认设计，无需生成或更新规则。共享规范映射如下。

| 规范指导 | 适用性与检查项 |
| --- | --- |
| 模块边界与依赖；工程骨架 | 适用 CHK-001、003：src 的 UI、服务、存储职责及验证目录单向依赖；无生成模板、package 或部署单元变更 |
| 状态权威与持久化 | 适用 CHK-001、002：服务唯一业务写入口、文件 SQLite、commit 和异常 |
| 接口与交互语义 | 适用 CHK-001、002：同步取消、不写入、成功与异常；蓝图明确无并发任务或后台恢复 |
| 业务与运行保障分工 | 无后台、保活、重试或运行恢复机制，不适用；不计 PASS |
| 观测数据与日志契约；观测影响与故障隔离 | 蓝图明确无产品观测管道，验收 JSON 为测试原始输出，不适用；不计 PASS |
| 环境边界与运行装配 | 适用 CHK-004 及 CHK-002 的真实文件 SQLite |
| 测试隔离与可控验证 | 适用 CHK-003：正式依赖链、测试数据和临时目录隔离 |

## 2. 检查项与证据

| 规则 | 适用条件与依据 | 检查项 |
| --- | --- | --- |
| CR-001 | 状态写入/UI 与服务调用；ARC-1 | CHK-001 |
| CR-002 | 提交持久化及异常；ARC-2、取消契约 | CHK-002 |
| CR-003 | 正式和验证模块依赖；ARC-3 | CHK-003 |
| CR-004 | 本地环境装配、外部路径；ARC-4 | CHK-004 |

### CHK-001: 状态写入权威

初审 FAIL：`src/ui.py:4-6` 直接执行 UPDATE 和 commit，绕过 `order_service.set_status`，违反 ARC-1、CR-001 和 mark_paid 契约。`order_service.py` 的 create/set_status 写入属于服务，storage 只建表。此为既有结构偏差；保持 paid 结果不能证明职责符合。静态提示的缺失订单异常已由集成 CT-10 证实：mark_paid(MISSING) 正常返回而非 ValueError，见 [集成契约原始输出](../test-reports/order-integration/contracts.stdout.txt)。该业务缺陷的状态与后续修复由独立 [BUG-002](../issues/BUG-002.md) 承载，本检查只记录其与旁路服务的关系。

整改本轮未获授权，跟踪 [ARCH-001](../issues/ARCH-001.md)。将来恢复条件为 Main 取得用户整改授权，再按本检查项经现有服务入口保持 paid，复核全部状态写入位置、现存订单第二连接读取 paid 及数据库异常传播；涉及缺失订单行为时引用 [BUG-002](../issues/BUG-002.md) 的验收判据，不在 ARCH-001 重复维护业务修复。无实施 Task；当前不修复、不关闭。最终候选 ui 哈希与初审相同，复核直接 SQL 仍在，当前结论 FAIL。

### CHK-002: 取消不变量、持久化与异常

初审 FAIL：基线 `submit_order` 读取后无条件写 submitted；[SQL 基线轨迹](../test-reports/order-cancel/baseline-causal-trace.json) 显示 cancelled 已持久化但被后续提交覆盖。不得将该缺陷当成需要保持的行为。行为判据沿 BUG-001：AC-1 返回 true/重开为 submitted；AC-2 返回 false/提交阶段无写入/重开为 cancelled；paid 重开为 paid；不存在订单与真实 SQLite 故障向上传播。

候选复核由原专业审查者和技能 Agent 承接。候选 `order_service.py:29-30` 在 cancelled 时返回 false，`set_status:20-21` 仍由服务执行 UPDATE、commit，无异常捕获或成功转换。修复与局部测试归 [原 Plan](../plans/order-cancel-fix.md)，不是本轮架构整改。

复用条件已核对：[BUG-001 独立定向复验](../test-reports/order-cancel/bugfix-retest.md) 的目标源码哈希与本次一致；公开调用、临时文件 SQLite、取消及正常判据一致；[独立原始证据](../test-reports/order-cancel/independent-retest.json) 前后哈希未变。AC-1 true/重开 submitted，AC-2 false/SQL仅SELECT/变更量0/重开cancelled；paid 重开为 paid；不存在订单提交抛 ValueError；真实第二连接读锁造成 COMMIT OperationalError，读连接仍 pending，调用者 rollback 后重开 pending。以上为候选运行事实，不将锁异常当成功，也不暗示服务自动回滚。[6 项局部测试](../test-reports/order-cancel/candidate-tests.json) 另覆盖关闭连接的真实读取异常传播。静态确认 execute/commit 均不吞异常；本轮不声称穷尽所有数据库故障。CHK-002 架构与适用行为判据 PASS，取消偏差经复核关闭；没有把单测结果替代架构判断。

### CHK-003: 正式与验证资产隔离

初审静态 PASS：`storage.py:2` 仅导入 sqlite3，其余正式模块不导入测试资产，不读取 AC 身份或 runtime 夹具配置。`checks/acceptance.py` 和 `tests/test_order.py` 单向调用 src；临时文件和清理由验证资产负责。正式代码没有测试专用分支。候选复扫确认仍为同一依赖条件，新增测试仅在 tests 中，无 src 测试依赖。当前结论 PASS。测试实际隔离执行事实复用上述定向复验；未声明全套集成通过。

### CHK-004: 本地装配与外部边界

初审静态 PASS：src 无网络路径；storage 连接文件 SQLite；`runtime.json` 端点为空、外部调用与网络授权均 false。验收入口 AC-3 返回 BLOCKED，不冒充真实外部服务回执。本规则符合不能作为 AC-3 验收通过的证据。候选配置哈希未变，正式调用链复扫无外部调用；本地装配边界结论 PASS。AC-3 为独立环境/授权阻塞。

## 3. Gate 与接续

Review Gate：**FAIL**，绑定上述 `3148af…89bfbb` 服务候选及全量 src 快照。4 项适用检查：CHK-001 FAIL、CHK-002 PASS、CHK-003 PASS、CHK-004 PASS；不适用专项不计通过数。取消缺陷修复和行为保持证据已通过，既有 UI 写入权威偏差仍开放；本轮只有审查授权，不继续整改。

| 批次／执行者 | 范围与实际结果 | 状态 |
| --- | --- | --- |
| 初审／architect_check | 基线四规则取证：001、002 FAIL；003、004 静态符合 | 保留历史 |
| 候选复核／review 与原专业审查者 | 相同候选哈希、取消与持久化独立证据、依赖和装配复扫 | 001 未整改；002 复核通过；003、004 PASS |

待办：ARCH-001 等待用户决定是否授权整改；无规则维护缺口，未生成或修改项目规则。

本地 AC-1、AC-2 及现存订单 paid 的候选和运行条件已就绪，可通过既有公开入口和临时文件 SQLite 运行，CHK-001 无候选不可用或环境依赖证据，不能泛化为阻止这些场景。AC-3 真实阻塞为缺少授权端点、权限和可用真实测试入口；需 Main 取得对应授权及条件后恢复，不能用本地模拟替代。集成 Test Gate 归独立 test-loop；Main 已转交并已核读 [本轮独立集成报告](../test-reports/order-integration/report.md)，Test Gate 为 FAIL（17项：15 PASS、1 FAIL、1 BLOCKED），CT-10 业务异常及 AC-3 阻塞分别维护，不能将本地 AC-1/2 通过扩大为整轮通过。本轮未授权正式发布。

写后检查：显式文档 CLI 覆盖本记录和 ARCH-001，机械检查 0 errors、0 warnings；语义核对保留初审与候选事实、规则映射、版本边界、可测范围和未授权整改条件。专业审查者未重跑测试，复用哈希吻合的独立及局部实测；UPDATE execute 失败未独立故障注入，只由无捕获路径支持异常传播，不宣称已实测。
