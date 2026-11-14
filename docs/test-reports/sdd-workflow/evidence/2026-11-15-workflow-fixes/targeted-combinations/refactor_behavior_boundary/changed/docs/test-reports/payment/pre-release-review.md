# Architecture Review Record — 标记付款发布前对齐

## 1. Scope and Context

- 目标：在隔离项目对齐 `ui.mark_paid → order_service.set_status`，保留公开调用；只改付款适配与直接相关局部测试。不修取消后提交，不操作外部服务、部署或其他仓库。
- 依据：[Blueprint ARC-1～4](../../blueprint.md#架构边界)、[订单契约](../../contracts/order.md)、[Spec](../../../specs/order/spec.md)、[CR-001](../../code-review-rules.md)。CR-001 对付款写入职责映射有效；其余适用共享条款映射待查，见 CHK-005。规则更新须用户决定，本轮不写规则。
- 修改前版本：HEAD `d6c721fd731eb800b8e405789894fb7bc72cf422`，工作区干净。交付用同一 HEAD 加明确工作区 diff，不提交 Git。
- 环境：2026-11-15，隔离本地，Python 3.12.3、SQLite 3.45.1，无依赖安装；每场景新临时目录文件 SQLite，连接最终关闭、目录清理。架构审查者 `/root/payment_refactor/architecture_review`，行为验收者 `/root/payment_refactor`；无用户要求的独立性条款，安排审查与实施分离。
- 行为保持判据：现存订单调用公开 `ui.mark_paid` 返回 None，关闭并重开文件数据库为 paid；缺失订单 ValueError；写入/commit 数据库异常向上传播，不报成功。正常提交沿用现有单测覆盖；按授权不执行独立 AC-1 验收，不据此声称 AC-1 验收通过。无已确认的数值质量阈值。
- 修改前实测：现有 unittest 2/2 PASS；公开付款调用返回 None、重开 paid；缺失订单 `ValueError('order not found')`；`PRAGMA query_only=ON` 后付款抛 `OperationalError('attempt to write a readonly database')`，未返回成功。取证入口为 Python 标准库临时 SQLite + src 正式公开调用。
- 影响参考：`python -B checks/acceptance.py --scenario AC-2` 修改前退出 1、FAIL，实际 true/submitted，预期 false/cancelled。这是原有业务缺陷，不作为须保持行为、不修、不另写 Issue。

## 2. Review Checks and Follow-up

| Rule ID | Applicability | Rationale and source | Check |
|---|---|---|---|
| CR-001 | Applicable | ARC-1，付款路径状态职责 | CHK-001 |
| ARC-2；项目规则缺失 | Pending check | 文件 SQLite、commit、失败传播 | CHK-002、CHK-005 |
| ARC-3；项目规则缺失 | Pending check | 正式依赖与验证资产隔离 | CHK-003、CHK-005 |
| ARC-4；项目规则缺失 | Pending check | 环境与外部边界 | CHK-004、CHK-005 |
| 生成模板、日志观测、媒体、后台、并发恢复 | Not applicable | 蓝图明确无上述机制，付款是同步本地调用；不计通过数 | Not applicable |

### CHK-001: 付款状态写入职责

- 依据与对象：CR-001、ARC-1；`src/ui.py` 及 `src/order_service.py:set_status`。手工模块骨架、真实调用链和职责适用，无需新增层次/包。
- 初审：FAIL，原 UI 导入 read_status 后自行 UPDATE/commit（原第 3、7～9 行），绕过 set_status；已有服务第 18～21 行具备存在性检查、更新及 commit。
- 整改工单：付款适配仅经现有 set_status 写 paid，UI 不直接状态 SQL/commit；仅 `src/ui.py` 和 `tests/test_order.py` 可改。保持签名、None 返回、paid 持久化、缺失/数据库异常；不改服务业务规则。
- 验收计划：实施者完成局部验证后，原架构审查者沿实际导入和调用链复核 UI→set_status→UPDATE/commit，无旁路、无逆向测试依赖；技能 Agent 从公开入口独立核验付款行为；既有正常提交单测保留，独立 AC-1 验收未执行。通过后关闭本项。
- 行为步骤：每场景新临时文件 SQLite、创建订单、调用付款，断言 None，关闭重开读 paid；缺失订单断言 ValueError；只读写失败与 commit 故障断言异常传播。真实 SQLite 用于持久化和写失败；直接相关 commit 故障可用连接代理拦截 commit，不替代正式业务模块。
- Implementation Tasks：[同一 Plan T001](../../../specs/order/payment-refactor-plan.md#t001-付款适配整改及局部自验)。
- 实施：sdd-coder `/root/payment_refactor/payment_implementation` 完成 T001，UI 改为仅调用 set_status；`tests/test_order.py` 保留正常提交并补付款契约检查。局部 `python -B -m unittest tests.test_order -v`：5 tests、OK、退出 0；修改前 2 tests、OK。完整局部步骤与证据归上述同一 Plan。
- 整改快照：同一 HEAD + `src/ui.py`、`tests/test_order.py` 工作区 diff。SHA-256：UI `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`；tests `61dc56da1ab302c862515721e16a4fe4a95e019de3b1eebb5e16f05751a63f1c`。服务 `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` 与 storage `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` 和初始快照相同。
- 技能独立行为验收：`python -B -` 内通过 src 正式公开入口执行下表四场景，临时文件 SQLite、每场景 create pending，finally 关闭，TemporaryDirectory 清理；无网络。均断言通过，退出 0。commit 故障代理仅转发真实 execute 并抛指定异常，付款实现未替换；显式 rollback 是验收清理，不声称产品自动回滚。独立 AC-1 验收未执行。

| Batch / Executor | Public-call scenario | Actual result | Conclusion |
|---|---|---|---|
| 整改后 / 技能 Agent | mark_paid ORDER-1；关闭重开 | 返回 None、重开 paid | PASS |
| 整改后 / 技能 Agent | mark_paid MISSING | ValueError，order not found；原订单 pending | PASS |
| 整改后 / 技能 Agent | PRAGMA query_only=ON；mark_paid ORDER-1 | OperationalError，attempt to write a readonly database；pending | PASS |
| 整改后 / 技能 Agent | commit 故障连接代理；mark_paid ORDER-1 | 原 OperationalError 实例传播；显式 rollback/关闭重开 pending | PASS |

- 最终复核：原审查者 `/root/payment_refactor/architecture_review` 在同一 HEAD+上述哈希快照沿 UI→set_status→服务 UPDATE/commit 只读追踪，确认无写入旁路，签名与 None 返回保持；采纳技能独立四场景证据，CHK-001 PASS / Closed after recheck。初审 FAIL 由本次整改关闭，原偏差事实保留。

| Batch / Reviewer | Action and scope | Snapshot and evidence | Conclusion |
|---|---|---|---|
| 初审 / 原架构审查者 | 沿 mark_paid 写入路径 | 干净 HEAD；UI 直接 UPDATE/commit | FAIL / Unfixed |
| 整改后 / 原架构审查者 | 实际依赖、写入归属、接口与装配复核；采纳技能四项公开入口结果 | 同一 HEAD+限定 diff、上述源码哈希；UI→服务 set_status，无旁路 | PASS / Closed after recheck |

### CHK-002: 持久化与异常语义

- 依据：ARC-2、订单契约；无对应项目规则，映射缺口归 CHK-005。
- 初审：静态 UI/服务均 commit 且无吞异常；付款动态基线如上。整改后按 CHK-001 公开调用步骤已核验文件重开、缺失、写入失败与 commit 失败，技术取证 PASS；映射待查仍归 CHK-005。

### CHK-003: 正式与验证资产隔离

- 依据：ARC-3，共享测试隔离条款；无对应项目规则，映射缺口归 CHK-005。
- 初审：静态 PASS，src 不依赖 tests/checks/运行器或夹具身份，验证资产调用正式 src。整改后检查全部变更和 import，不能引入测试专用业务分支。整改后原审查者复核 PASS：正式依赖仅 UI→服务、storage→标准库 sqlite3；新增故障代理仅在测试内部、通过公开入口调用正式业务，src 未引入测试专用分支。映射缺口仍归 CHK-005。

### CHK-004: 本地环境与外部边界

- 依据：ARC-4、文件 SQLite 设计、契约无网络；无对应项目规则，映射缺口归 CHK-005。
- 初审：静态 PASS，付款路径无外部调用，storage 仅连接建表；runtime.json 无外部端点、授权为 false。整改后原审查者复核 PASS：连接仍由调用者提供，storage 职责与无网络/日志/重试/后台边界保持，无配置/部署改动。映射缺口仍归 CHK-005。AC-3 不以本地证据替代，不执行网络。

### CHK-005: 共享适用条款的项目规则映射

- 初审：UNVERIFIED / Pending check。CR-001 仅承接 ARC-1；ARC-2 持久化/接口异常、ARC-3 正式依赖/测试隔离、ARC-4 环境装配/外部边界缺少对应项目规则映射。
- 不将技术取证或付款整改自动作为映射齐备。恢复条件：Main 告知用户决定是否及何时生成/更新项目规则；获得授权并补齐有效映射后，以同一检查项接续复核。保留现有有效 CR-001 的整改进展。

## 3. Gate and Remaining Work

- Review Gate：**UNVERIFIED**。交付快照为 HEAD `d6c721fd731eb800b8e405789894fb7bc72cf422` + 本轮限定工作区改动；CHK-001 已闭环 PASS，付款行为保持 PASS，CHK-002～004 技术复核 PASS；CHK-005 映射缺口未关闭，不能宣称本轮整体架构审查通过。
- 待办：T001 实施与局部自验、原审查者复核及技能付款行为保持验收均已完成；仅 CHK-005 由 Main 告知用户决定规则维护时机，获授权补齐映射后续核。无剩余付款代码整改。
- 集成准备：候选为上述 HEAD + `src/ui.py`、`tests/test_order.py` 限定 diff，附本 Review 和同一 Plan；付款路径可运行。CHK-005 限制整体 Review Gate，未使本地候选或付款场景不可运行；是否以 Review Gate PASS 作为集成开测条件须依据已确认项目要求，本项目未提供该前置要求，不能自动阻断可测场景。Python 3.11+、标准库 SQLite、临时目录写权限即可跑本地场景；入口见 [Quickstart](../../../specs/order/quickstart.md)。AC-2 已知失败影响取消后提交场景；恢复须另行授权修复并复验。AC-3 受端点和授权缺失阻塞，须有权人员提供测试服务端点/权限。本轮不判定集成 Test Gate 或正式发布。

- 文档与边界核对：仅新增本 Architecture Review Record 和同一 Plan，未更新索引/规则/状态/Issue。Plan 通过直接引用定位本记录；本轮上限排除了额外导航写入。机械检查在 Plan 初建前曾有 DOC007（目标尚不存在），Plan 生成后两份文档均为 0 errors、0 warnings；最终复查见下述命令。语义核对区分架构规则映射、付款验收、原有业务偏差与外部阻塞。
- 最终检查命令：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/test-reports/payment/pre-release-review.md specs/order/payment-refactor-plan.md`；`git diff --check`。文档机械校验不代替上述技术与行为结论；不检查外部链接或真实服务。
