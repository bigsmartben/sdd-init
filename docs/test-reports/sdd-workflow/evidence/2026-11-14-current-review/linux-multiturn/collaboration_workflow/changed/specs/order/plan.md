# Plan — 订单本地缺陷恢复

## 1. Goal and Basis

- 依据 [TASK](../../TASK.txt)、[BUG-001](../../docs/issues/BUG-001.md)、[BUG-002](../../docs/issues/BUG-002.md)，恢复取消提交保护和缺失订单付款异常，保持 [Spec](spec.md) 与[接口](../../docs/contracts/order.md)。用户已授权本地修复及复验，需求和接口不变。
- 初轮 HEAD `9701a4d79766e124c202c9b258ad18a458a26cd8`；实际文件 SQLite。原故障证据见[初轮报告](../../docs/test-reports/order/initial.md)。
- 已验证因果路径：`submit_order` 丢弃读取的状态，无条件写入 submitted；`ui.mark_paid` 直接 UPDATE，缺失订单影响零行仍无异常。后者绕过既有 `set_status` 的存在性检查。

## 2. Task List

### T001: 恢复两个原 Issue 的已确认行为

- 依据：BUG-001 的 AC-2；BUG-002 的不存在订单 ValueError；[蓝图 ARC-1](../../docs/blueprint.md) 的服务写入入口。
- 范围：`src/order_service.py`、`src/ui.py`；必要局部测试新增 `tests/test_order_bugfix.py`。不新增接口、状态及未确认流转；数据库异常上传，保留 AC-1、既有订单 paid 持久化及多订单隔离。
- 方案：仅 cancelled 时提交立即返回 false；其余既有提交路径保持。付款适配函数调用既有 `order_service.set_status(connection, order_id, "paid")`。
- 依赖：无。
- 执行与判据：sdd-coder 实施并局部自验；bugfix Agent 独立复验原场景和受影响行为。新文件 SQLite 中新建→取消→提交须 false 且重开 cancelled；pending 提交须 true 且重开 submitted；缺失付款须 ValueError；现存付款须重开 paid；SQL 和 commit 失败须上传异常。原独立 integration Agent 在交接后按 [Quickstart](quickstart.md) 重跑全产品与公开 checks。
- 状态：Complete。
- 结果：2026-11-14，sdd-coder 完成上述两处最小源码修复；[新增局部测试](../../tests/test_order_bugfix.py) 7 项，连同原 2 项共 9 PASS。命令 `TMPDIR="$PWD/.tmp/order-tests" python -B -m unittest discover -s tests -p 'test_order*.py' -v`；[修前输出](../../docs/issues/evidence/bugfix-local-before.txt) 3 FAIL、[修后输出](../../docs/issues/evidence/bugfix-local.txt) 9 PASS。初轮事实仍保留在原 Issue。
- 独立定向复验：bugfix Agent（与 sdd-coder 独立）运行 `TMPDIR="$PWD/.tmp/order-tests" python -B tests/bugfix_retest.py`，8 PASS，覆盖原故障、AC-1、多订单隔离、pending/submitted/cancelled 付款持久化、cancel/submit/paid 的 SQL 与 commit 失败上传。见[复验脚本](../../tests/bugfix_retest.py)与[复验 JSON](../../docs/issues/evidence/bugfix-retest.json)。commit 失败使用真实文件 SQLite deferred FK，抛 IntegrityError；调用者 rollback 后重开仍 pending，未增加产品自动回滚语义。
- 修复快照：HEAD `9701a4d79766e124c202c9b258ad18a458a26cd8` 加未提交工作区修改；`src/order_service.py` SHA256 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`，`src/ui.py` SHA256 `c4a9e5b0789129c89bb71387e2aaed619944d115aff5a53c7fb5320fcbff88ae`；其余 src 哈希见复验 JSON。

## 3. Delivery Checks

- 本地临时文件在项目 `.tmp/`，所有测试命令设置 `TMPDIR`，不访问外部平台或服务。
- T001 局部实施、自验及独立定向复验 Complete。原 integration Agent 已对同一修复快照完成[全产品集成复验](../../docs/test-reports/order/fixed.md)：本地 15 PASS、单元 9 PASS，公开 checks AC-1/AC-2 PASS，两原故障及必要回归通过；Issue 关单依据与状态由原测试 Agent 维护。独立架构检查及同项复核见[Review 记录](../../docs/test-reports/order/2026-11-14-review.md)，架构结论以该记录实际批次为准。
- 完整声明范围 Test Gate 为 BLOCKED：AC-3 缺少真实外部端点、权限和实际可调用回执入口。恢复条件由有权人员补齐这些前置条件后，在授权环境执行真实回执核验并留证；本地通过不替代该证据。
