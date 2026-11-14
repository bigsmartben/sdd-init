# Test Report — 订单付款整改后全产品集成

## 1. 目标与依据

- 批次：ORDER-INTEGRATION-001；类型：独立全功能集成回归；执行者：由 `/root` Main 调度的独立 `sdd-test-loop` 技能 Agent。
- 执行时间：2026-11-14 16:28 UTC 起（本地 Asia/Shanghai 为 2026-11-15）；仅当前隔离项目。
- 依据：[Spec](../../../specs/order/spec.md)、[接口契约](../../contracts/order.md)、[原位更新的复跑指南](../../../specs/order/quickstart.md)、[runtime.json](../../../runtime.json)。
- 目标：检查付款整改候选的新建、取消、提交、公开付款、持久化及异常协同；保留 AC-2 原判据，AC-3 仅以真实授权外部回执验收。

## 2. 范围与安排

Main 启动指令沿用用户已确认的验收范围、实际整改候选、本地 Python/文件 SQLite 环境、公开判据和主要路径，授权本轮实测，无新增常规确认事项。先核候选，再执行已有 AC 入口、指南内联扩展场景及现有局部单测。

正常、边界、组合、恢复与异常数据从 Spec 和契约推导。空字符串和非字符串不满足输入前提，不作为本轮通过判据；准备时曾观察其 ValueError，但不计入覆盖或 Gate。未定义的 submitted/paid 再提交规则不新增判断。IT-07 编号保留空缺，其他稳定编号不变。

不修改产品、测试、架构记录、规则、蓝图或契约；不运行网络、外部平台或部署。无吞吐、延迟或人工视觉指标。完成条件为全部已确认适用功能通过、真实外部回执证据齐备；完整失败/阻塞记录可结束本批次执行，但不使 Gate 通过。

## 3. 实际版本与环境

独立执行 `git rev-parse HEAD`、`git status --short`、`git diff -- src/ui.py tests/test_order.py`、`python -B checks/runtime_details.py` 核对：

- HEAD：`4f5329a6d36b7d7d1fb4b4685b2c8dbf9d8a67df`。
- 相关未提交改动：`src/ui.py` 的公开 `mark_paid` 委托服务 `set_status`；`tests/test_order.py` 的付款持久化及异常局部测试。不是仅以 HEAD 推定实测版本。
- Python `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`；SQLite `3.45.1`；环境 `isolated-local-fixture`。
- 外部端点 `null`，外部调用授权 `false`，本轮网络访问 `false`。
- 真实组件：`src.storage.connect`、`src.order_service`、`src.ui.mark_paid` 和临时文件 SQLite，无本地内存数据库替代，无外部服务模拟。

| 文件 | 实测 SHA-256 |
|---|---|
| src/__init__.py | 10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded |
| src/order_service.py | 96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de |
| src/storage.py | 6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9 |
| src/ui.py | 1b43c863d5f9dd8100d3c5a9f0dade6cde3e020502d780bf933cb489a122c63c |
| tests/test_order.py | 24f31eae7e6ae3f5c15430f9afa1b8d4e045f8c093f9f25f95f3718df7ecc87e |
| checks/acceptance.py | 3068c25ce6dee0b604c70f97e48b7ac9dc703ee44a2190c561972e4f65625eb9 |
| checks/runtime_details.py | 28fd81e51f8a07c30ae728f0faafd766965181b6b8178f3933871cdd87ef388d |
| runtime.json | e25bd6e9530e59c71dc6cd82b01722c85c24f609e0e7f16f398afe3a4e97ea85 |

[第一阶段架构记录](payment-alignment-review.md)的付款复核/行为保持通过，完整 Review Gate 因共享适用条款映射缺口为 UNVERIFIED。这不是本轮功能失败判据或全体开测阻塞，本轮所有可运行场景均实际执行；本报告不改判 Review Gate。

## 4. 准备与数据

每个 AC 和扩展案例使用独立 `TemporaryDirectory` 里的 `orders.sqlite`；公开连接入口创建真实表。AC-1/2 关闭原连接重开；扩展案例在写入后通过第二文件连接观察已提交状态，同时保留中间态。扩展连接在 finally 关闭，临时目录自动清理，全部正常完成，不修改长期数据。

数据包含普通订单编号、Unicode、单空格（均为非空字符串）、不存在编号、四种已定义状态及多订单。真实故障通过 `PRAGMA query_only=ON` 制造，所有异常验证仍调用公开入口。无外部账号或凭据。唯一环境缺口是 AC-3 无端点、权限及真实验收入口。

## 5. 执行与覆盖摘要

计划及实际均为 13 个功能场景：**11 PASS、1 FAIL、0 Not run、1 BLOCKED**，合计 13；通过率 11/13。范围内全部功能均有明确覆盖状态，不将 BLOCKED 当作通过。另有现有局部单测 5/5 通过，仅作辅助证据，不重复计数。

| 功能 | 场景映射 | 覆盖结论 |
|---|---|---|
| 新建、非空字符串及初始持久化 | IT-01、AC-1/2、IT-11 | PASS |
| 取消及重复取消 | IT-02、IT-11 | PASS |
| pending 提交及关闭重开 | AC-1 | PASS |
| 取消后提交保护 | AC-2 | FAIL |
| 公开付款、四种合法前态、重复付款 | IT-03/04/05/06 | PASS |
| 缺单异常、失败不污染其他订单 | IT-08 | PASS |
| 真实文件库写异常传播与无虚假成功 | IT-09 | PASS |
| 合法状态写入持久化 | IT-10 | PASS |
| 多订单跨操作隔离 | IT-11 | PASS |
| 真实外部提交回执 | AC-3 | BLOCKED |

本轮全部本地项针对同一实际候选重新执行，没有把第一阶段结果或历史 AC-2 直接用作本批次实测替代。仅复用已确认判据、公开入口和局部测试资产。

## 6. 逐项结果与证据

以下各行均在第 3 节同一候选/环境运行，执行入口为指南主路径或同名内联函数。实际观察列保留 JSON 输出的关键业务字段；临时数据清理后仍可按指南逐项复跑。

| Case / 依据 | 数据与操作 | 预期 | 实际观察 | 结果 | 问题 |
|---|---|---|---|---|---|
| AC-1 / Spec | ORDER-1 create→submit→关闭重开 | true / submitted | accepted=true；persisted_status=submitted | PASS | 无 |
| AC-2 / Spec | ORDER-1 create→cancel→submit→关闭重开 | false / cancelled | accepted=true；persisted_status=submitted | FAIL | [ISSUE-001](../../issues/ISSUE-001.md) |
| AC-3 / Spec | 读取运行配置、检查真实服务就绪 | 获授权真实回执；缺条件则阻塞 | endpoint_configured=false；authorized=false；未发出外部请求 | BLOCKED | 无产品缺陷归因 |
| IT-01 / 创建契约 | create 函数创建 ORDER-1、订单-2、单空格，第二连接读取 | 三个非空字符串订单均 pending | 三项均 pending | PASS | 无 |
| IT-02 / 取消契约 | cancel 函数 create→cancel→读→cancel→读 | 两次读取均 cancelled | first=cancelled；repeat=cancelled | PASS | 无 |
| IT-03 / 付款契约 | payment 函数 pending→公开付款→第二连接 | None / paid | before=pending；returned=null；reopened=paid | PASS | 无 |
| IT-04 / 付款契约 | create→submit→公开付款→第二连接 | 提交 true；付款 None / paid | before=submitted；returned=null；reopened=paid | PASS | 无 |
| IT-05 / 付款契约 | create→cancel→公开付款→第二连接 | None / paid | before=cancelled；returned=null；reopened=paid | PASS | 无 |
| IT-06 / 付款契约 | create→付款→再次付款→第二连接 | None / paid | before=paid；returned=null；reopened=paid | PASS | 无 |
| IT-08 / 缺单契约 | missing 函数对缺单 read/cancel/submit/set/paid，保留 KEEP | 五项均 ValueError；KEEP pending | 五项均 ValueError；reopened={KEEP:pending} | PASS | 无 |
| IT-09 / 数据库异常契约 | database_failure 函数打开 query_only，对 create/cancel/submit/set/paid 调用 | 五项 OperationalError；不得返回成功或污染库 | 五项均 OperationalError；reopened={KEEP:pending}，无 NEW | PASS | 无 |
| IT-10 / set_status 契约 | legal_status 函数依次写四种合法状态，逐次第二连接读取 | 每次读到指定状态 | pending→submitted→cancelled→paid 均持久化 | PASS | 无 |
| IT-11 / 操作对象隔离 | isolation 函数新建四单，分别 submit/cancel/paid/保留 | 互不覆盖 | {SUBMIT:submitted,CANCEL:cancelled,PAY:paid,KEEP:pending} | PASS | 无 |

主验收命令 `python -B checks/acceptance.py` 退出码 **1**，输出：

```json
[
  {"scenario":"AC-1","result":"PASS","accepted":true,"persisted_status":"submitted","expected_accepted":true,"expected_status":"submitted"},
  {"scenario":"AC-2","result":"FAIL","accepted":true,"persisted_status":"submitted","expected_accepted":false,"expected_status":"cancelled"},
  {"scenario":"AC-3","result":"BLOCKED","reason":"No external call is performed by this fixture; authorized endpoint and permission are required","endpoint_configured":false,"authorized":false}
]
```

指南内联命令直接抽取执行，退出码 **0**，IT-01/02/03/04/05/06/08/09/10/11 全部 PASS；准备时 IT-07 的越界输入观察不纳入此统计。`python -B -m unittest discover -s tests -v` 实际运行 5 项并输出 `OK`，覆盖 normal_submit、付款文件持久化、付款缺单、真实写异常，以及 mock commit 失败传播/rollback。commit 注入使用 mock，只证明该局部异常路径，不能充当 AC-3 或真实数据库 commit 故障的端到端证据。

## 7. Issue 与影响

[ISSUE-001](../../issues/ISSUE-001.md)：取消后提交返回 true，覆盖 cancelled 为 submitted，违反 AC-2。状态 Pending，本轮仅记录、未修复。其余本地路径通过不能抵消此失败。

AC-3 是环境/授权缺失的阻塞，未观察到真实外部调用或故障，不据此另登记产品缺陷。

## 8. 结论、限制与 Test Gate

**Test Gate：FAIL（另有 AC-3 BLOCKED）**。适用第 3 节候选、本地 Python 3.12.3/SQLite 3.45.1 文件库及第 5 节完整范围；本轮已完成所有可测场景，未满足整轮通过条件。

- AC-2 仍失败。恢复条件：另获修复授权并由 Main 调度修复；对实际修复候选重跑原 AC-2、AC-1、取消持久化、付款及相关异常/隔离回归。现有 Issue 保持 Pending，不能关闭。
- AC-3 待验/BLOCKED。恢复条件：有权人员提供获授权真实外部测试端点、权限及合法操作方法，并安排真实调用取证。当前 acceptance.py 仅报告条件，配置到位本身不证明 AC-3 通过；本地结果不得替代真实回执。
- 无 UI 或人工体验判断要求，无额外人工视觉验收；本轮已有用户范围/版本/环境确认由 Main 启动指令承接，未虚构用户实际操作反馈。AC-3 的授权/回执仍缺失并影响 Gate。
- 架构 Review Gate 仍按原记录 UNVERIFIED；其恢复由 Main 另行协调，与本报告功能缺陷分别保留。

写后核对：从最终指南逐字抽取内联 Python 命令重跑，10 个扩展案例全部 PASS、退出 0；单独重跑 AC-2 仍为 true/submitted、FAIL、退出 1。上述复跑保留为同批次重复证据，不增加案例数。结束时重新计算 8 个源代码/测试/验收入口/运行配置哈希，与第 3 节全部一致。

文档检查：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/quickstart.md docs/test-reports/order/payment-integration.md docs/issues/ISSUE-001.md docs/index.md`，4 个 Markdown 文件，0 errors、0 warnings。语义核对确认保留原 AC-2 预期、AC-3 外部前提、全部覆盖及其差异；机械检查不代替功能 Gate 或架构 Review。未检查远程链接或外部服务。
