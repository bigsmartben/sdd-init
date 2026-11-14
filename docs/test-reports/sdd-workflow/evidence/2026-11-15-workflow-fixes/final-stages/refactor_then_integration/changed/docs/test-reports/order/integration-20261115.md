# 订单全产品集成报告 — INT-20261115

## 1. 目标与依据

批次 INT-20261115，类型为第二阶段全产品集成回归，执行者为 Main 独立委派的 sdd-test-loop 技能 Agent（未参与第一阶段实现）。最终实测时间为 2026-11-15 00:47:54 +08:00（UTC 2026-11-14 16:47:54），具体时间及环境见原始证据。目标是核验付款整改后实际工作树中，新建、取消、提交、公开付款和真实外部回执的已确认行为及跨组件协同。

依据：[Spec](../../../specs/order/spec.md)、[公开函数契约](../../contracts/order.md)、本轮完整[复跑指南](../../../specs/order/quickstart.md)、[环境配置](../../../runtime.json)。第一阶段结果引用[付款架构审查](mark-paid-review.md)和[整改计划](../../../specs/order/refactor-plan.md)，两份第一阶段记录已冻结，本阶段未写入。

## 2. 范围、计划与确认

Main 派单已传递用户明确授权及首次实测四要素：范围为上述全产品行为；候选为第一阶段架构复核后的实际工作树；环境为隔离项目、本地 Python 加文件 SQLite；主要路径为现有公开 CLI／库入口和真实数据库。既有标准不变，无需再次常规确认。阶段授权不包含任何代码、测试文件、配置改动、AC-2 修复、外部调用、真实部署或 Git 写操作。测试指南内的执行脚本属于本轮证据工具，不改仓库测试入口。

计划保留 AC-1、AC-2、AC-3；从契约推导 IT-01～IT-10，补齐正常、持久化、重复操作、组合、异常、边界、恢复与跨订单协同。阶段内由技能执行者直接完成；不复用局部单测作为集成通过证据。首轮 12 项之后补齐 COMMIT 异常场景，按最终指南完整重跑 13 项；两次输出均保留，第 5 节只按最终场景去重统计。完成条件为所有范围内适用判据满足且必需外部证据齐备；完整记录失败和阻塞可结束执行，但不能判 PASS。

## 3. 实际版本、环境与装配

HEAD 为 `76e8f410e7adeb3cb702dc1f89bb5129bf381c60`，实际候选包含第一阶段未提交的 `src/ui.py`、`tests/test_order.py` 及 Review／Plan／索引；本阶段仅新增或更新文档。付款 ui SHA256 为 `54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8`，测试文件为 `10d712d2a6db76b9ca747fe8a3d4b80717a261d1eae6f6b6f76945e38b803187`，与 Main 交接一致；服务、存储、检查脚本、配置及冻结文档哈希见第 9 节。

实际 Python 3.12.3，SQLite 3.45.1；所有模块 `__file__` 均落于本隔离项目。新建／取消／提交由 `src.order_service` 公开函数装配 `src.storage.connect` 返回的真实 SQLite 连接；付款由 `src.ui.mark_paid` 进入现有服务写入入口，最终经真实 commit 写入文件，再通过关闭重开读取业务状态。没有内存数据库、替身存储或模拟外部服务。

只读连接、独立连接真实写锁、已关闭连接用于数据库故障覆盖。IT-10 用 SQLite 官方连接 authorizer 拒绝 COMMIT，属于受控故障注入；执行／commit／异常／rollback 均为真实 SQLite，不代表自然环境中所有可能的磁盘或提交故障。局部单测的提交失败使用代理，只作为辅助局部证据，不代替 IT-10。没有端点、凭据或外部服务装配；外部结论保持阻塞。

## 4. 准备、数据与恢复

按指南每个场景创建独立临时目录及 SQLite 文件；一般订单为 ORDER-1，多订单用 P/C/S/D，标识边界用非空 Unicode 和带 SQL 引号/分隔符的字符串，缺失目标为 MISSING。所有输入均由执行者按既有契约推导，不新增业务含义或质量阈值。付款分别从 pending、submitted、cancelled、paid 进入。订单状态来自公开新建／取消／提交／付款，不直接写业务数据。

只读测试关闭只读连接后换回正常连接；锁冲突每次异常后 rollback，释放持锁连接后再做公开提交／付款；已关闭连接场景新建连接恢复；COMMIT 拒绝每次失败后确认其他连接仍见旧值，rollback 后解除 authorizer，再验证付款。脚本所有连接在 finally／fixture 退出时关闭，所有临时目录退出时删除；最终输出确认全部 fixture contexts exited，执行无清理异常。无需迁移或恢复项目持久数据。准备缺口仅为 AC-3 的真实端点和调用授权，不影响本地场景。

## 5. 执行与覆盖统计

最终共 13 个去重验收场景：**PASS 11，FAIL 1，NOT_RUN 0，BLOCKED 1**；总和 13。执行覆盖（含前提检查后阻塞）13/13，实际完成业务判断 12/13；全部计划场景通过率 11/13（84.6%），已完成业务判断通过率 11/12（91.7%）。这些统计不是新增验收阈值。局部 unittest 另计 5/5，不进入上述分母；最初 12 场景的重复运行也不重复计数。非法／重复新建事实观察不属于验收场景，也不计入分母。

| 范围功能 | 场景映射 | 覆盖状态 |
|---|---|---|
| 新建 | AC-1/2、IT-01、IT-05～10 | 正常、持久化、错误、恢复、隔离、合法标识边界均已覆盖 |
| 取消 | AC-2、IT-02、IT-04～08、IT-10 | 独立取消通过；取消后提交组合失败 |
| 提交 | AC-1/2、IT-04～10 | pending 提交通过；cancelled 拒绝未满足 |
| 公开付款 | IT-03～10 | 四种现存状态、持久化、缺失、数据库错误及恢复均通过 |
| 真实外部回执 | AC-3 | 前提核对完成；真实行为尚未覆盖，BLOCKED |

五类功能均映射到场景；四类本地路径已执行并得出结论，一类外部路径阻塞。因此不能称业务需求全部通过。判据仍为 Spec／契约原文，没有以架构映射缺口或工具退出成功代替业务判断。

## 6. 逐项结果

以下所有项使用第 3 节同一候选及环境，方法和准确步骤见指南相同 ID 的表和可执行代码，第 9 节提供完整命令／JSON 原始输出。

| 场景／依据 | 前置与实际操作 | 预期 | 实际差异与关键观察 | 结果 | 证据／Issue |
|---|---|---|---|---|---|
| AC-1／Spec | 新建后公开提交，关闭重开 | true/submitted | true/submitted | PASS | 原入口与最终指南均一致 |
| AC-2／Spec | 新建、取消、公开提交，关闭重开 | false/cancelled | true/submitted，取消被覆盖 | FAIL | [ISSUE-001](../../issues/ISSUE-001.md) |
| AC-3／Spec | 检查实际配置，未调用外部 | 获授权真实服务回执 | endpoint=null、authorized=false，缺端点/权限；恢复需授权配置及真实核验步骤 | BLOCKED | 外部未验，阻止 Gate PASS |
| IT-01／新建契约 | 新建 ORDER-1 后关闭重开 | pending | pending | PASS | 最终指南 JSON |
| IT-02／取消契约 | 取消后重读，再取消后关闭重开 | cancelled/cancelled | 两次 cancelled | PASS | 中间及最终状态已取证 |
| IT-03／付款保持 | 四个独立库分别准备四种现存状态→公开付款→重开 | None/paid | pending、submitted、cancelled、paid 均返回 None，重开 paid | PASS | 四组合均列于 JSON |
| IT-04／不存在订单 | 缺失目标的读取/取消/提交/付款 | ValueError，原订单不变 | 四个 ValueError，重开 pending | PASS | 最终指南 JSON |
| IT-05／数据库异常传播 | 只读库新建/取消/提交/付款，换回可写付款 | 数据库异常，未成功，恢复 paid | 四个 OperationalError；原 pending、新目标不存在；恢复 paid | PASS | 故障前后状态已取证 |
| IT-06／数据库异常及恢复 | 真实写锁四写操作→rollback→解锁→新建提交/付款 | 异常不成功，恢复可写 | 四个 database is locked；解锁前 pending；恢复 ORDER-1 paid/NEW submitted | PASS | 中间及恢复状态已取证 |
| IT-07／数据库异常及恢复 | 关闭连接四写操作→重连取消 | 异常不成功，恢复 cancelled | 四个 ProgrammingError；恢复前 pending、后 cancelled | PASS | 最终指南 JSON |
| IT-08／状态隔离 | 四订单分别保持/取消/提交/付款后重开 | pending/cancelled/submitted/paid | P/C/S/D 各状态符合，无覆盖 | PASS | 最终指南 JSON |
| IT-09／合法标识边界 | 非空 Unicode、SQL 引号标识分别新建/提交/付款 | true，最终 paid，可分别读取 | 两个独立标识均 paid，表仍可读取 | PASS | 最终指南 JSON |
| IT-10／commit 异常传播 | authorizer 拒绝 COMMIT，四写操作，每次外部连接观察/rollback，解除后付款 | 数据库异常向上传播，失败未持久化，恢复 paid | 四个 DatabaseError: not authorized；rollback 后 pending，恢复 paid | PASS | 真实 SQLite 受控异常；最终 JSON |

额外事实观察：空字符串、None、整数 42 新建分别抛 ValueError；重复主键新建抛 IntegrityError，rollback 后原订单 pending。因非法输入结果与重复新建的异常类型未获业务确认，这些仅描述当前实现，不用于新增判据或登记缺陷。

## 7. 缺陷与影响

| Issue | 本轮场景 | 事实及影响 |
|---|---|---|
| [ISSUE-001](../../issues/ISSUE-001.md) | AC-2 | 既有取消订单仍可被提交覆盖，违反 false/cancelled，直接阻止 Test Gate PASS。第一阶段已发现并留证，本轮在候选公开路径再次复现；仓库未有独立 Issue，现建唯一记录。 |

AC-3 是已确认的外部前提不足，当前没有真实服务行为失败证据，不新增产品缺陷 Issue。第一阶段 Review Gate 的 MAP-001～003 映射缺口引用原审查记录，不另建重复 Issue，也不将其当成本轮业务失败判据。既有架构 CHK-001～004 已 PASS 的事实不代替本轮集成证据；本阶段不跨阶段维护 Code Review Rules。

## 8. 结论、人工待验与接续

**Test Gate：FAIL（并存在 AC-3 BLOCKED）。** 适用范围为本报告精确工作树候选、隔离本地环境及五类功能。本地付款公开路径保持，正常提交和大部分协同行为通过；AC-2 有实测业务失败，AC-3 缺必需真实外部证据，不能给出全产品通过结论。所有可执行计划项已完成，不存在遗漏未跑项。

人工视觉验收不适用于无 UI 的 CLI／库夹具；本轮无额外人工主观反馈要求，也未代用户填写通过反馈。人工／外部待验仍为 AC-3：有权人员须提供真实测试服务端点和调用权限、允许外部调用，并经 Main 对齐受影响的环境/步骤后核验真实回执。本地 submitted 或本地 JSON 不构成该证据。

AC-2 待 Main 在另行获准的 Bugfix 阶段安排，沿 ISSUE-001 保留原断言；修复版本返回后，至少重跑 AC-2 原公开入口、AC-1、付款保持及取消/提交相关组合，按实现影响完成全范围集成复验。本轮未修复、不关单。AC-3 就绪后另批次实测，并按版本变化分析是否需补跑其余场景；所有必需业务判据和证据齐备才重新判 Gate。架构 MAP 缺口由 Main 单独处理，不阻塞本轮已就绪场景。

## 9. 原始执行证据

以下保留首轮及最终运行，不将复跑次数计为新场景。命令 stdout/stderr 原文及退出码均保留；退出码 1 来源为已观察的 AC-2 失败，非测试工具损坏。

### git rev-parse HEAD

退出码 `0`。

```text
76e8f410e7adeb3cb702dc1f89bb5129bf381c60
```

### git status --short

退出码 `0`。

```text
 M docs/index.md
 M specs/order/quickstart.md
 M src/ui.py
 M tests/test_order.py
?? docs/test-reports/
?? specs/order/refactor-plan.md
```

### python -B checks/runtime_details.py

退出码 `0`。

```text
{
  "python": "3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]",
  "sqlite": "3.45.1",
  "runtime": {
    "environment": "isolated-local-fixture",
    "database": "per-scenario temporary SQLite file",
    "external_endpoint": null,
    "external_call_authorized": false,
    "network_access_in_this_run": false
  },
  "source_sha256": {
    "src/__init__.py": "10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded",
    "src/order_service.py": "96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de",
    "src/storage.py": "6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9",
    "src/ui.py": "54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8"
  }
}
```

### python -B checks/acceptance.py

退出码 `1`。

```text
[
  {
    "scenario": "AC-1",
    "result": "PASS",
    "accepted": true,
    "persisted_status": "submitted",
    "expected_accepted": true,
    "expected_status": "submitted"
  },
  {
    "scenario": "AC-2",
    "result": "FAIL",
    "accepted": true,
    "persisted_status": "submitted",
    "expected_accepted": false,
    "expected_status": "cancelled"
  },
  {
    "scenario": "AC-3",
    "result": "BLOCKED",
    "reason": "No external call is performed by this fixture; authorized endpoint and permission are required",
    "endpoint_configured": false,
    "authorized": false
  }
]
```

### Quickstart Python block via python -B -

退出码 `1`。

```text
{"scenario": "AC-1", "result": "PASS", "accepted": true, "persisted_status": "submitted", "expected_accepted": true, "expected_status": "submitted"}
{"scenario": "AC-2", "result": "FAIL", "accepted": true, "persisted_status": "submitted", "expected_accepted": false, "expected_status": "cancelled"}
{"scenario": "AC-3", "result": "BLOCKED", "reason": "No external call is performed by this fixture; authorized endpoint and permission are required", "endpoint_configured": false, "authorized": false}
{"scenario": "IT-01", "result": "PASS", "observed": {"reopened": "pending"}}
{"scenario": "IT-02", "result": "PASS", "observed": {"after_cancel": "cancelled", "after_repeat_and_reopen": "cancelled"}}
{"scenario": "IT-03", "result": "PASS", "observed": {"pending": {"returned": null, "reopened": "paid"}, "submitted": {"returned": null, "reopened": "paid"}, "cancelled": {"returned": null, "reopened": "paid"}, "paid": {"returned": null, "reopened": "paid"}}}
{"scenario": "IT-04", "result": "PASS", "observed": {"read_status": "ValueError: order not found", "cancel_order": "ValueError: order not found", "submit_order": "ValueError: order not found", "mark_paid": "ValueError: order not found", "unrelated_reopened": "pending"}}
{"scenario": "IT-05", "result": "PASS", "observed": {"create": "OperationalError: attempt to write a readonly database", "cancel": "OperationalError: attempt to write a readonly database", "submit": "OperationalError: attempt to write a readonly database", "paid": "OperationalError: attempt to write a readonly database", "before_recovery": "pending", "after_recovery": "paid"}}
{"scenario": "IT-06", "result": "PASS", "observed": {"create": "OperationalError: database is locked", "cancel": "OperationalError: database is locked", "submit": "OperationalError: database is locked", "paid": "OperationalError: database is locked", "before_unlock": "pending", "after_unlock": {"ORDER-1": "paid", "NEW": "submitted"}}}
{"scenario": "IT-07", "result": "PASS", "observed": {"create": "ProgrammingError: Cannot operate on a closed database.", "cancel": "ProgrammingError: Cannot operate on a closed database.", "submit": "ProgrammingError: Cannot operate on a closed database.", "paid": "ProgrammingError: Cannot operate on a closed database.", "before_recovery": "pending", "after_recovery": "cancelled"}}
{"scenario": "IT-08", "result": "PASS", "observed": {"P": "pending", "C": "cancelled", "S": "submitted", "D": "paid"}}
{"scenario": "IT-09", "result": "PASS", "observed": {"订单-一": "paid", "x'; DROP TABLE orders;--": "paid"}}
{"diagnostic_only": {"''": "ValueError: order_id is required", "None": "ValueError: order_id is required", "42": "ValueError: order_id is required", "duplicate": "IntegrityError: UNIQUE constraint failed: orders.order_id", "reopened": "pending"}}
{"total": 12, "counts": {"PASS": 10, "FAIL": 1, "NOT_RUN": 0, "BLOCKED": 1}, "cleanup": "all fixture contexts exited"}
```

### python -B -m unittest discover -s tests -v

退出码 `0`。

```text
test_mark_paid_commit_failure (test_order.OrderTests.test_mark_paid_commit_failure) ... ok
test_mark_paid_is_persisted (test_order.OrderTests.test_mark_paid_is_persisted) ... ok
test_mark_paid_missing_order (test_order.OrderTests.test_mark_paid_missing_order) ... ok
test_mark_paid_readonly_database (test_order.OrderTests.test_mark_paid_readonly_database) ... ok
test_normal_submit (test_order.OrderTests.test_normal_submit) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.058s

OK
```

### 最终指南完整复跑

命令：提取指南唯一 Python 代码块，作为 stdin 传入 `python -B -`；退出码 `1`。

```text
{"scenario": "AC-1", "result": "PASS", "accepted": true, "persisted_status": "submitted", "expected_accepted": true, "expected_status": "submitted"}
{"scenario": "AC-2", "result": "FAIL", "accepted": true, "persisted_status": "submitted", "expected_accepted": false, "expected_status": "cancelled"}
{"scenario": "AC-3", "result": "BLOCKED", "reason": "No external call is performed by this fixture; authorized endpoint and permission are required", "endpoint_configured": false, "authorized": false}
{"scenario": "IT-01", "result": "PASS", "observed": {"reopened": "pending"}}
{"scenario": "IT-02", "result": "PASS", "observed": {"after_cancel": "cancelled", "after_repeat_and_reopen": "cancelled"}}
{"scenario": "IT-03", "result": "PASS", "observed": {"pending": {"returned": null, "reopened": "paid"}, "submitted": {"returned": null, "reopened": "paid"}, "cancelled": {"returned": null, "reopened": "paid"}, "paid": {"returned": null, "reopened": "paid"}}}
{"scenario": "IT-04", "result": "PASS", "observed": {"read_status": "ValueError: order not found", "cancel_order": "ValueError: order not found", "submit_order": "ValueError: order not found", "mark_paid": "ValueError: order not found", "unrelated_reopened": "pending"}}
{"scenario": "IT-05", "result": "PASS", "observed": {"create": "OperationalError: attempt to write a readonly database", "cancel": "OperationalError: attempt to write a readonly database", "submit": "OperationalError: attempt to write a readonly database", "paid": "OperationalError: attempt to write a readonly database", "before_recovery": "pending", "after_recovery": "paid"}}
{"scenario": "IT-06", "result": "PASS", "observed": {"create": "OperationalError: database is locked", "cancel": "OperationalError: database is locked", "submit": "OperationalError: database is locked", "paid": "OperationalError: database is locked", "before_unlock": "pending", "after_unlock": {"ORDER-1": "paid", "NEW": "submitted"}}}
{"scenario": "IT-07", "result": "PASS", "observed": {"create": "ProgrammingError: Cannot operate on a closed database.", "cancel": "ProgrammingError: Cannot operate on a closed database.", "submit": "ProgrammingError: Cannot operate on a closed database.", "paid": "ProgrammingError: Cannot operate on a closed database.", "before_recovery": "pending", "after_recovery": "cancelled"}}
{"scenario": "IT-08", "result": "PASS", "observed": {"P": "pending", "C": "cancelled", "S": "submitted", "D": "paid"}}
{"scenario": "IT-09", "result": "PASS", "observed": {"订单-一": "paid", "x'; DROP TABLE orders;--": "paid"}}
{"scenario": "IT-10", "result": "PASS", "observed": {"create": "DatabaseError: not authorized", "cancel": "DatabaseError: not authorized", "submit": "DatabaseError: not authorized", "paid": "DatabaseError: not authorized", "after_rollback": "pending", "after_recovery": "paid"}}
{"diagnostic_only": {"''": "ValueError: order_id is required", "None": "ValueError: order_id is required", "42": "ValueError: order_id is required", "duplicate": "IntegrityError: UNIQUE constraint failed: orders.order_id", "reopened": "pending"}}
{"total": 13, "counts": {"PASS": 11, "FAIL": 1, "NOT_RUN": 0, "BLOCKED": 1}, "cleanup": "all fixture contexts exited"}
```

### 实际装配与最终哈希

命令：Python 只读读取模块 `__file__`、文件字节 SHA256 和 UTC 时间。

```json
{
  "time_utc": "2026-11-14T16:47:54.719529+00:00",
  "cwd": "/tmp/sdd-review-execution-7kzokfoo/refactor_then_integration-9dn21v5u/prepared/project",
  "assembly": {
    "src.ui": "/tmp/sdd-review-execution-7kzokfoo/refactor_then_integration-9dn21v5u/prepared/project/src/ui.py",
    "src.order_service": "/tmp/sdd-review-execution-7kzokfoo/refactor_then_integration-9dn21v5u/prepared/project/src/order_service.py",
    "src.storage": "/tmp/sdd-review-execution-7kzokfoo/refactor_then_integration-9dn21v5u/prepared/project/src/storage.py"
  },
  "sha256": {
    "src/__init__.py": "10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded",
    "src/ui.py": "54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8",
    "src/order_service.py": "96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de",
    "src/storage.py": "6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9",
    "tests/test_order.py": "10d712d2a6db76b9ca747fe8a3d4b80717a261d1eae6f6b6f76945e38b803187",
    "checks/acceptance.py": "3068c25ce6dee0b604c70f97e48b7ac9dc703ee44a2190c561972e4f65625eb9",
    "checks/runtime_details.py": "28fd81e51f8a07c30ae728f0faafd766965181b6b8178f3933871cdd87ef388d",
    "runtime.json": "e25bd6e9530e59c71dc6cd82b01722c85c24f609e0e7f16f398afe3a4e97ea85",
    "specs/order/quickstart.md": "86862643f06e1141d74292f437df0b3c701d42247e1631793c00518c23ff9f27",
    "docs/test-reports/order/mark-paid-review.md": "2663444461a12750cab9f06274d0acf8a10f22619a7fb1eca587b696e215b5b6",
    "specs/order/refactor-plan.md": "8a0774ceb920ed9b9acf825c2bb558c3cecd7761330ca2b307cbbee44cf6cbf9"
  }
}
```

## 10. 写后核对

最终代码、测试、runtime 与本批次已记录哈希一致，第一阶段冻结 Review／Plan 哈希保持；本阶段仅写指南、报告、ISSUE-001 和索引。语义核对确认：原 AC-2 false/cancelled 未降低，AC-3 未以本地回执替代，架构缺映射未充当业务失败，诊断事实不增加业务判据，统计按最终 13 个场景去重。

机械命令：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/quickstart.md docs/test-reports/order/integration-20261115.md docs/issues/ISSUE-001.md docs/index.md`，结果 `Checked 4 Markdown files: 0 errors, 0 warnings (mechanical only)`，退出 0。检查不证明外部服务或业务通过；未检查不在本次修改范围的全仓文档或外部链接。
