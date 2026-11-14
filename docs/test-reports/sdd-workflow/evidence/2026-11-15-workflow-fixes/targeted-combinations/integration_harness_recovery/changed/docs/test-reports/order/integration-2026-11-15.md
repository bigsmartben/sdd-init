# Test Report — 订单完整集成 / integration-2026-11-15

## 1. 测试目标与依据

- 类型：完整集成回归；批次 `integration-2026-11-15`。
- 实测时间：`2026-11-14T16:24:12.445920+00:00`；独立技能执行者 `/root/integration`，测试工具由其调度的 `/root/integration/harness`（sdd-coder）维护。后者的自验不替代本报告中的独立正式执行。
- 目标：验证已集成提交、取消、付款和外部回执的全部已确认行为，以及 CI 入口可复跑。
- 依据：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[本轮 Quickstart](../../../specs/order/quickstart.md)和 [用户启动任务](../../../TASK.txt)。启动任务已明确范围、当前工作树、隔离本地环境及主要路径；沿用 Main 传达的已有确认，未变更业务判据。

## 2. 范围与计划

范围含 Spec AC-1/2/3，以及契约中的新建 pending、取消持久化、现存订单付款 paid、不存在订单 ValueError、编号合法性和数据库异常传播。本地正常、异常、边界、组合、恢复及跨模块行为从原判据推导，共 25 个稳定场景；无新业务规则。每项独立临时文件 SQLite；真实公开调用经 storage、order_service、ui 观察持久状态，关闭并重开确认 commit。AC-3 仅核验环境前置条件，真实外部调用未执行。

执行顺序：保留基线工具失败及原验收结果 → 按测试资产授权修复入口并补覆盖 → 技能 Agent 从正式 CI 入口实测 → 全量再跑、直接 acceptance 对照和 25 项单场景复跑 → 版本、覆盖及文档核验。产品代码、运行配置冻结；无外部平台、服务、部署、凭据、Git 提交或暂存操作。架构符合性不作为本轮业务判据。

完成条件：25 项全部具有明确状态，指南可复跑；只有全体适用判据满足且证据齐备时 Test Gate 才能 PASS。失败和阻塞保留完整原因也可结束本轮执行。

## 3. 实测环境和版本

- 产品 HEAD：`1c6b8ab84d68d21144d549aa4eb717903896a828`；开始工作树 clean（基线 `git status --porcelain=v1` 输出为空）。
- 最终未提交改动仅为 checks 测试工具、工具测试及本轮文档/原始证据；`git diff -- src runtime.json` 输出为空，src 全部 SHA-256 前后逐文件相同。
- 运行环境：Python 3.12.3、SQLite 3.45.1、`isolated-local-fixture`；真实文件 SQLite，不是内存数据库。数据库连接、产品模块均实际调用，不以 mock 替代业务结果。
- 配置：`external_endpoint=null`，`external_call_authorized=false`，`network_access_in_this_run=false`。
- 正式入口：`python -B checks/integration_runner.py`；测试资产 SHA-256、实际环境、命令 stdout/stderr/退出码见 [final.json](evidence/final.json)。工具语义单测包含 mock，独立于产品场景证据；socket guard 仅覆盖常见 TCP/DNS Python 调用入口，不是操作系统网络审计。

## 4. 准备与数据

标准库可用，无需安装依赖或服务。每场景新建临时目录与 SQLite 文件，常规订单 `ORDER-1`；缺失订单 `MISSING`，写锁创建的目标 `ORDER-2`，编号边界 `""`、None、整数、单字符及 Unicode。数据来自契约规定的非空字符串与已存在订单条件。锁用第二真实 SQLite 连接 `BEGIN IMMEDIATE` 构造，busy_timeout=0，验证异常及锁释放后的状态。

连接在 finally 中关闭、写锁回滚释放、TemporaryDirectory 上下文完成后清理；两次全量及所有独立场景无数据复用依赖。本轮无需人工清理或产品数据恢复。外部回执前置条件缺失影响 AC-3，恢复见第 8 节。

## 5. 执行及覆盖汇总

- 计划及实际均为 25 项：PASS 22、FAIL 2、BLOCKED 1、Not run 0（合计 25）。AC-3 的前置检查执行，但真实外部业务调用未执行，计 BLOCKED。
- 场景通过率 22/25（88%）；本地执行 24 项全部已覆盖状态，其中 22 PASS/2 FAIL。范围和判据未缩减。
- 25 项逐项登记覆盖状态；真实业务证据不完整的是外部回执，故不能将“已登记”称为全部业务验收通过。

| 功能点 / 已确认依据 | 场景映射 | 覆盖结论 |
| --- | --- | --- |
| 提交及文件持久化 / AC-1 | AC-1、LOCAL-create、PAID-submitted | PASS |
| 取消及禁止提交覆盖 / AC-2 | AC-2、LOCAL-cancel | 取消持久化 PASS；取消后提交 FAIL |
| 真实外部回执 / AC-3 | AC-3 | BLOCKED，未验证真实服务 |
| 既存订单付款保持 / Spec、mark_paid 契约 | PAID-pending、PAID-submitted、PAID-cancelled | 三个前态均 paid 且重开持久化 PASS |
| 缺失订单异常 / 契约 | 五个 MISSING-* | 服务四项 PASS，付款 FAIL |
| 编号合法性 / Spec、create 契约 | 三个 INVALID-*、两个 VALID-* | PASS |
| 数据库异常传播 / 契约 | 五个 LOCK-*、CLOSED-read_status | PASS，未返回成功且写锁后数据未变 |
| 本地操作无网络 / Spec、契约 | LOCAL-no-network；全部本地场景 guard | PASS；guard 捕获尝试 0，限常见 Python TCP/DNS 入口 |

两次正式全量 JSON 完全一致；直接 `acceptance.py` 与 CI 全量一致；25 个单场景 JSON 均与全量对应项相同，且退出码符合各自结果。复跑作为重试证据，不重复计入场景统计。全部单场景与命令证据保留在 final.json，适用于相同产品哈希、测试资产和环境。

## 6. 逐项实测结果

每行操作均可用 `python -B checks/integration_runner.py --scenario <ID>` 复跑，数据与方法见 Quickstart。表内 JSON 为主要判断字段；完整预期、实际、取消等中间状态、异常消息和网络尝试数见 [正式原始证据](evidence/final.json)。所有行产品版本均为第 3 节所列，未修改产品。

| 场景 / 依据 | 前置和实际操作 | 预期主要结果 | 实际主要结果 | 状态 | 证据 / Issue |
| --- | --- | --- | --- | --- | --- |
| AC-1 / Spec | pending → submit → 关闭并重开 | `{"accepted": true, "persisted_status": "submitted"}` | `{"accepted": true, "persisted_status": "submitted"}` | PASS | [原始结果](evidence/final.json) |
| AC-2 / Spec | pending → cancel → submit → 关闭并重开 | `{"accepted": false, "persisted_status": "cancelled"}` | `{"accepted": true, "persisted_status": "submitted"}` | FAIL | [原始结果](evidence/final.json) / [ORD-001](../../issues/ORD-001.md) |
| AC-3 / Spec | 读取 runtime.json 的端点和调用授权 | `{"real_external_receipt_verified": true}` | `{"real_external_receipt_verified": false}` | BLOCKED | [原始结果](evidence/final.json) |
| LOCAL-create / 契约 | create → 关闭并重开 | `{"persisted_status": "pending"}` | `{"persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| LOCAL-cancel / 契约 | create → cancel → 关闭并重开 | `{"persisted_status": "cancelled"}` | `{"persisted_status": "cancelled"}` | PASS | [原始结果](evidence/final.json) |
| PAID-pending / 契约 | 创建 pending 前置状态 → ui.mark_paid → 关闭并重开 | `{"persisted_status": "paid"}` | `{"persisted_status": "paid"}` | PASS | [原始结果](evidence/final.json) |
| PAID-submitted / 契约 | 创建 submitted 前置状态 → ui.mark_paid → 关闭并重开 | `{"persisted_status": "paid", "setup_submit_returned": true}` | `{"setup_submit_returned": true, "persisted_status": "paid"}` | PASS | [原始结果](evidence/final.json) |
| PAID-cancelled / 契约 | 创建 cancelled 前置状态 → ui.mark_paid → 关闭并重开 | `{"persisted_status": "paid"}` | `{"persisted_status": "paid"}` | PASS | [原始结果](evidence/final.json) |
| MISSING-read_status / 契约 | 对不存在订单调用 read_status | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| MISSING-set_status / 契约 | 对不存在订单调用 set_status | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| MISSING-cancel_order / 契约 | 对不存在订单调用 cancel_order | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| MISSING-submit_order / 契约 | 对不存在订单调用 submit_order | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| MISSING-mark_paid / 契约 | 对不存在订单调用 mark_paid | `{"exception": "ValueError", "order_count": 0}` | `{"exception": null, "returned": null, "order_count": 0}` | FAIL | [原始结果](evidence/final.json) / [ORD-002](../../issues/ORD-002.md) |
| INVALID-empty / 契约 | create 的编号分别为空字符串、None、整数（按场景选择） | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| INVALID-none / 契约 | create 的编号分别为空字符串、None、整数（按场景选择） | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| INVALID-integer / 契约 | create 的编号分别为空字符串、None、整数（按场景选择） | `{"exception": "ValueError", "order_count": 0}` | `{"exception": "ValueError", "order_count": 0}` | PASS | [原始结果](evidence/final.json) |
| VALID-single / 契约 | create 合法单字符或 Unicode 编号 → 关闭并重开 | `{"persisted_status": "pending", "order_id": "x"}` | `{"order_id": "x", "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| VALID-unicode / 契约 | create 合法单字符或 Unicode 编号 → 关闭并重开 | `{"persisted_status": "pending", "order_id": "订单-一"}` | `{"order_id": "订单-一", "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| LOCK-create / 契约 | 独立 SQLite 连接持有写锁 → 调用 create → 释放锁并重开 | `{"exception": "OperationalError", "persisted_status": "pending", "locked": true, "order_count": 1}` | `{"locked": true, "exception": "OperationalError", "order_count": 1, "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| LOCK-cancel / 契约 | 独立 SQLite 连接持有写锁 → 调用 cancel → 释放锁并重开 | `{"exception": "OperationalError", "persisted_status": "pending", "locked": true, "order_count": 1}` | `{"locked": true, "exception": "OperationalError", "order_count": 1, "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| LOCK-submit / 契约 | 独立 SQLite 连接持有写锁 → 调用 submit → 释放锁并重开 | `{"exception": "OperationalError", "persisted_status": "pending", "locked": true, "order_count": 1}` | `{"locked": true, "exception": "OperationalError", "order_count": 1, "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| LOCK-set_status / 契约 | 独立 SQLite 连接持有写锁 → 调用 set_status → 释放锁并重开 | `{"exception": "OperationalError", "persisted_status": "pending", "locked": true, "order_count": 1}` | `{"locked": true, "exception": "OperationalError", "order_count": 1, "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| LOCK-paid / 契约 | 独立 SQLite 连接持有写锁 → 调用 paid → 释放锁并重开 | `{"exception": "OperationalError", "persisted_status": "pending", "locked": true, "order_count": 1}` | `{"locked": true, "exception": "OperationalError", "order_count": 1, "persisted_status": "pending"}` | PASS | [原始结果](evidence/final.json) |
| CLOSED-read_status / 契约 | 关闭连接后读取订单 | `{"exception": "ProgrammingError"}` | `{"exception": "ProgrammingError"}` | PASS | [原始结果](evidence/final.json) |
| LOCAL-no-network / 契约 | socket guard 中执行新建、提交、取消、set_status、付款及读取 | `{"persisted_status": "paid"}` | `{"persisted_status": "paid"}` | PASS | [原始结果](evidence/final.json) |

AC-3 BLOCKED 的具体影响：未能证明真实订单提交回执；缺少端点/调用授权且本轮禁止网络，不能用本地结果代替。其余已授权就绪场景均完成。

### 工具原始故障、恢复和辅助检查

[baseline.json](evidence/baseline.json)保留原入口退出码 1 与 `NameError: run_acceptence` traceback。原 `acceptance.py` 独立执行已给出 AC-1 PASS、AC-2 FAIL、AC-3 BLOCKED；原 2 项局部单测 PASS，没有覆盖完整产品范围。

本轮修正 runner 调用拼写，扩充 acceptance 的真实场景、逐项异常隔离及输出，新增 6 项工具语义测试。原预期不变；最终正式 CI 两次均退出 1，均输出 25 项完整 JSON，stderr 为空。该退出 1 来自产品 FAIL 聚合，已不再是工具 NameError。单独 AC-1 退出 0、AC-2 退出 1、AC-3 退出 3。工具可运行、可复跑已验证，不能将进程非零简单归为工具未恢复，也不能把工具恢复记为产品 Gate PASS。

`python -B -m unittest discover -s tests -v` 最终 8 项 PASS（原 2 项 + 工具 6 项），退出 0；仅证明局部及工具语义。产品故障由真实 CI 场景保留，工具测试不硬编码故障必须存在。环境信息入口退出 0，不替代业务验收。

## 7. 相关问题与影响

| Issue | 相关场景 | 实测事实和影响 |
| --- | --- | --- |
| [ORD-001](../../issues/ORD-001.md) | AC-2 | create → cancel 时为 cancelled；submit 返回 true 并写 submitted；关闭重开仍 submitted，取消被覆盖。保持 Pending，交 Main，未修产品。 |
| [ORD-002](../../issues/ORD-002.md) | MISSING-mark_paid | 不存在订单付款返回 None、无 ValueError；行数 0。保持 Pending，交 Main，未修产品。 |

AC-3 是已知前置条件阻塞，未伪造实现缺陷或发起外部操作。工具侧原故障已恢复，失败与恢复都在本报告和原始证据中保留。

## 8. 结论、人工反馈与 Test Gate

- **Test Gate：FAIL（同时存在 AC-3 BLOCKED）。** 适用于本轮 HEAD、未变的产品源哈希及当前隔离本地环境。22 项通过不能消除 2 项明确产品判据失败，外部回执也没有真实证据。
- 本轮测试执行已完成：全部适用项获得 PASS/FAIL/BLOCKED 状态、用户指南与原始证据齐备，CI 工具已恢复复跑。没有未登记的未测项。
- 人工待验：不适用。Spec 明确无 UI，本轮判据均为机器可观察行为；外部阻塞属于真实组件与授权缺口，不以人工主观确认代替。
- 恢复：Main 在另行授权的产品修复阶段处理 ORD-001/ORD-002，交回修复版本后沿原 ID 复验并回归全部适用本地场景；AC-3 由有权人员提供真实测试端点、调用权限和允许联网环境后实测。只有产品失败及外部真实证据缺口都消除才能重新判定全范围 PASS。
- 边界：未执行架构 Review、发布、部署、外部服务配置或网络调用，未执行 Git 写操作。报告不把这些非本轮证据推定为通过。

文档机械与语义核对证据见 [文档检查记录](evidence/document-check.json)，最终改动范围及只读 Git 核验见 [交付核验记录](evidence/delivery-check.json)。[Status](../../status.md)仅引用本报告及原 Issue。
