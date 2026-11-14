# Architecture Review Record — 标记付款发布前对齐

## 1. 范围与基线

目标为按已确认 [Blueprint](../../blueprint.md)、[契约](../../contracts/order.md) 和 [CR-001](../../code-review-rules.md) 对齐公开 `ui.mark_paid` 的状态写入职责，保留业务行为。用户授权仅付款适配及直接相关局部测试；不修取消提交、不执行全产品集成、不写 Git 或操作外部服务。Main `/root` 调度技能 `/root/refactor`，专业初审与复核为 `/root/refactor/architect`。

初审版本 HEAD `76e8f410e7adeb3cb702dc1f89bb5129bf381c60`，初始工作树干净。环境为本地隔离项目、Python 3.12.3、SQLite 3.45.1；每场景独立临时文件库，无网络。确认来源为 Main 交接的用户授权；需求和依据无需重新确认。工程骨架仅核对受影响 src 依赖与现有装配，不新增模块、包或生成模板。

整改前基线（2026-11-15，技能 Agent 实测）：`python -B -m unittest discover -s tests -p test_order.py -k mark_paid -v`，1 项 PASS。另以 `storage.connect` 创建临时文件库，`create_order` → `ui.mark_paid` 返回 None；关闭重开后 paid；缺失编号抛 ValueError `order not found`；以 SQLite `mode=ro` 连接调用抛 OperationalError `attempt to write a readonly database`。这些是公开付款行为与契约判据；commit 失败仍须补验。

影响参考：`python -B checks/acceptance.py --scenario AC-2` 初始版本 FAIL（退出码 1），实际 accepted=true、persisted_status=submitted，期望 false/cancelled。这是范围外原有业务缺陷，不是保持目标，已交 Main，代码不改。AC-1 与完整集成由下一阶段执行。

## 2. 检查项、工单与验收方案

| 规则/指导 | 适用性及项目映射 | 检查项 |
|---|---|---|
| 模块边界与依赖、状态写入权威 | 适用，CR-001 对应 ARC-1 | CHK-001 |
| 状态持久化、接口与交互语义 | 适用，ARC-2 与契约已有确认，commit/异常语义缺项目规则映射 | CHK-002、MAP-001 |
| 测试隔离与可控验证 | 适用，ARC-3、quickstart 已确认，项目映射缺失 | CHK-003、MAP-002 |
| 环境边界与运行装配 | 适用，ARC-4、runtime 已确认，项目映射缺失 | CHK-004、MAP-003 |
| 业务与运行保障分工 | 不适用：没有后台任务、重试、保活、恢复机制 | 不计通过数 |
| 观测数据与日志、观测故障隔离 | 不适用：蓝图明确无产品观测机制，验收 JSON 仅为测试输出 | 不计通过数 |

### CHK-001：付款状态写入职责

- 依据与对象：CR-001 / ARC-1，`src/ui.py` → `src/order_service.py:set_status` → 文件 SQLite。
- 初审：FAIL；原 `mark_paid` 查询后直接 UPDATE 和 commit，绕过服务写入入口。paid 结果正确不能证明职责符合。
- 整改工单：交 coder，仅改 `src/ui.py` 和直接付款局部测试；将写入交现有服务入口，保持 paid、None、缺失及数据库异常传播、文件持久化。实施方法归 [Plan T001](../../../specs/order/refactor-plan.md#t001付款适配职责对齐)。
- 架构复核：原架构审查者在整改后沿公开入口追踪调用、写入、commit 和 src 依赖；通过条件为 UI 只适配，服务承担状态写入，无测试依赖或网络。
- 行为保持验收：技能 Agent 在实际整改快照执行付款局部用例，并从公开入口以真实文件库检查关闭重开 paid、None、缺失 ValueError、写入与 commit 异常传播；不得仅凭 mock 服务调用证明业务结果。
- 实施：coder `/root/refactor/coder` 已完成 Plan T001，UI 仅调用既有 `set_status`，服务/存储未改。
- 行为保持结果：技能 `/root/refactor` 在实际整改快照独立执行付款局部入口，4 项 PASS，退出码 0（0.065s）。覆盖 None、关闭重开 paid、缺失 ValueError、真实只读库 OperationalError、commit 失败传播与新连接 pending。另按原基线步骤从公开函数复测，None/paid、ValueError `order not found`、OperationalError `attempt to write a readonly database` 均 PASS。commit 失败由测试侧连接代理注入，不代表真实外部服务或磁盘故障实验。
- 当前状态：原架构角色在同一哈希快照复核 PASS，结合行为保持 PASS 后关闭。初审 FAIL 的事实保留。

### CHK-002：付款持久化与异常语义

- 依据：ARC-2、订单契约；追踪存在性检查、UPDATE、commit 完成及异常传播。
- 初审：静态路径符合；初始 paid/None/缺失/只读失败实测 PASS，commit 失败待验。
- 整改与验收：关联 CHK-001 / Plan T001；技能在整改后按上项公开入口检查并补充 commit 失败。原架构角色复核无捕获转成功或重试扩权。
- 当前状态：原架构角色复核与技能行为验收均 PASS，关闭；规则映射缺口单列 MAP-001，不能由行为测试关闭。commit 故障证据不主张真实磁盘故障或自动回滚保证。

### CHK-003：正式依赖和测试隔离

- 依据：ARC-3、quickstart；初审静态 PASS，src 不导入 checks/tests。
- 复核：原架构角色检查所有 src 导入、付款实际路径和新增局部测试；正式模块无测试开关或测试身份，测试连接/临时目录有清理。
- 当前状态：原架构角色在整改快照核对全部 src 导入、测试侧代理及资源清理，PASS，关闭；映射缺口见 MAP-002。

### CHK-004：本地装配与外部边界

- 依据：ARC-4、runtime；初审静态 PASS，文件 SQLite、传入连接、无网络。
- 复核：原架构角色核对付款调用链、src 依赖与 runtime 未改变；技能付款验证使用临时文件库，不访问外部。
- 当前状态：原架构角色在整改快照复核 service、storage、runtime 未改且无网络路径，PASS，关闭；映射缺口见 MAP-003。

### MAP-001：持久化与交互规则映射待查

UNVERIFIED：共享“状态权威与持久化 / 接口与交互语义”适用，CR-001 仅覆盖写入职责，缺 ARC-2 / 契约的 commit 完成、异常传播项目规则。路径为 `ui.mark_paid` → `set_status` → SQLite。现有设计判据可继续核验，但不宣称规则映射完整。恢复需用户决定何时授权维护 Code Review Rules，完成映射后按原项复核。

### MAP-002：测试隔离规则映射待查

UNVERIFIED：共享“测试隔离与可控验证”适用，缺 ARC-3、临时文件库隔离/清理与可复跑入口映射；路径为 src 依赖及 `tests/test_order.py` 付款用例。恢复需用户授权维护规则并复核。不会阻止已具备条件的本地场景执行。

### MAP-003：环境装配规则映射待查

UNVERIFIED：共享“环境边界与运行装配”适用，缺 ARC-4、runtime 的文件库与外部授权边界映射；路径为 `storage.connect`、付款入口、runtime。恢复需用户授权维护规则并复核；外部端点缺失仅阻塞外部场景。

## 3. Gate 与集成准备

初审 Review Gate：FAIL（CHK-001）。最终 Review Gate：UNVERIFIED；CHK-001～004 复核 PASS，技术整改和付款行为保持已完成，MAP-001～003 仍缺项目规则映射。2026-11-15 原审查者 `/root/refactor/architect` 只读核对实际 diff、src 依赖和上述证据，确认其适用于下列快照；未重复执行测试。用户可决定何时授权维护规则，再沿原 MAP 项复核。本轮未扩写规则，不能报告完整重构门禁通过，也不把待查误报为已知代码偏差。

本地 Python/SQLite 与公开函数、`checks/acceptance.py` 均可用；已知 AC-2 失败应在下一阶段保留。AC-3 无端点、未授权，须有权人员提供授权测试服务端点与调用权限；不得用本地证据替代。Review Gate 与集成 Test Gate 分别判断；缺映射本身不使整个候选不可测试。

候选为 HEAD `76e8f410e7adeb3cb702dc1f89bb5129bf381c60` 加本轮工作树：`src/ui.py` 付款调用服务、`tests/test_order.py` 付款局部测试；新增本 Review 和 [Plan](../../../specs/order/refactor-plan.md)，索引仅补导航。未提交。候选代码/测试 SHA-256：

| 文件 | SHA-256 |
|---|---|
| src/ui.py | `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8` |
| tests/test_order.py | `10d712d2a6db76b9ca747fe8a3d4b80717a261d1eae6f6b6f76945e38b803187` |
| src/order_service.py（未改） | `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` |
| src/storage.py（未改） | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |

第二阶段本地新建、取消、提交可按 [quickstart](../../../specs/order/quickstart.md) 逐场景执行；公开付款可用 `ui.mark_paid` 与上列付款局部入口，数据为每场景新建临时文件库与现存订单 ORDER-1。标准库依赖已满足，无安装、进程或额外权限前置。AC-2 可执行但已知不符合确认判据；外部 AC-3 仅可记录配置缺口，真实回执待授权端点与实际调用能力恢复。Test Gate 由 Main 委派下一阶段判定，本记录不代替集成或正式发布依据。

写后检查：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/order/mark-paid-review.md specs/order/refactor-plan.md docs/index.md`，3 文件 0 errors / 0 warnings；`git diff --check` 通过。初稿检查曾因待创建 Plan 链接 DOC007，Plan 就绪后已消除。语义核对保持原检查项、历史事实、未确认规则维护边界与 Gate/本地准备区分，链接已随新增产物同步索引；未检查远端内容。
