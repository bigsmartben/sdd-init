# Test Report — 订单隔离候选全功能集成批次 INT-001

## 1. 测试目标与依据

执行类型为公开入口全功能集成回归；执行者为独立 `order_integration` sdd-test-loop 技能 Agent，2026-11-14，末次取证时间 15:20 UTC。目标为验证第一阶段付款重构复核后的实际隔离候选，不修改实现。

依据：[订单 Spec](../../../specs/order/spec.md)、[订单契约](../../contracts/order.md)、[本轮 Quickstart](../../../specs/order/quickstart.md)。[付款 Review](payment-review.md)的 CHK-001 架构复核与行为保持 PASS、总 Review Gate UNVERIFIED 是独立架构结论；本轮未将局部单测或架构结论代替集成实测。

## 2. 范围与安排

启动交接沿用用户明确确认：范围为新建、取消、提交、公开付款和 AC-3；目标为第一阶段复核后的实际候选；环境为当前隔离本地 Python／文件 SQLite；主要路径和公开判据已确认，无需重复确认。按指南先核实版本与运行条件，执行既有 AC-1/2/3，再以公开库入口补齐正常、异常、边界、组合和调用者恢复。

新建、取消、提交、付款均使用真实 `src` 组件；不修改产品、测试、runtime、Review、Plan 或共享工作流，不访问原仓、外部平台或真实部署。AC-3 在范围内但授权环境未就绪，记录阻塞。完成条件为覆盖范围中所有适用功能满足原 Spec／契约且证据齐全；发现确定失败继续完成其余就绪项，失败与阻塞完整记录后可结束本批执行。

## 3. 实际环境与版本

- Git HEAD：`7a90ae57739b7ae93b554e0bd409259ab949a51e`；含第一阶段未提交 `src/ui.py` 与 `tests/test_order.py` 修改及文档。源码指纹与第一阶段 Review 一致，本批执行过程中未改代码。
- Python：`3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`；SQLite：`3.45.1`。无第三方运行依赖。
- 实际装配：`storage.connect` 建立临时文件 SQLite；`order_service` 负责真实 SQL／commit；公开 `ui.mark_paid` 调用现有服务。调用者负责关闭连接，独立重开确认持久化。
- runtime：`environment=isolated-local-fixture`，`database=per-scenario temporary SQLite file`，`external_endpoint=null`，`external_call_authorized=false`，`network_access_in_this_run=false`。无网络调用。

`python -B checks/runtime_details.py` 输出的源码 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| src/__init__.py | 10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded |
| src/order_service.py | 96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de |
| src/storage.py | 6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9 |
| src/ui.py | 54fab9bf063ba862facd10ccb97ba0550e524db1ddf716c8f932e96e51a7c6c8 |

IT-12 仅注入 commit 抛错点，execute、文件库、rollback 和重开均真实。它证明异常传播与调用者恢复，不证明真实磁盘故障发生机制。IT-11 是真实 SQLite query_only 写失败。无真实外部回执或模拟替代证明。

## 4. 准备、数据与复位

按已确认契约推导常规数据：每案例独立新临时文件，ORDER-1／EXISTS 为现存订单，MISSING 为不存在订单，A/B 验证隔离，空串／None／123 检查非空字符串边界。付款分别以前置公开操作建立 pending/submitted/cancelled/paid，不通过内部 SQL 伪造业务路径。重复 ID 仅验证真实 SQLite 异常上传与恢复，不新增重复订单业务处理要求。

每次读取持久化状态均关闭原连接再重开，或在故障恢复前用独立连接读取；未将同连接事务内值误作持久化。异常后调用者 rollback，再撤除 query_only 或 commit 包装并重试。所有原始连接最终由调用者关闭，TemporaryDirectory 自动删除，实际 `temporary_directory_removed=true`。无外部账户、凭据或准备操作。准备缺口仅 AC-3 端点及权限。

## 5. 执行与覆盖汇总

15 案例，PASS 13、FAIL 1、Not run 0、BLOCKED 1，合计 15；通过率 13/15，本地可执行案例 13/14。既有 acceptance 与指南脚本的重复执行作为同一案例的复跑证据，不重复计数。全部本地就绪场景已执行，无临时扩围或版本变更。

| 功能与判据 | 覆盖案例 | 覆盖结论 |
| --- | --- | --- |
| 新建／非空字符串／持久化 | IT-01、09、11～14 | 正常、边界、数据库异常与恢复均通过 |
| 提交／AC-1 | IT-02、10～12、14 | pending 提交和跨订单协同通过 |
| 取消与取消后提交／AC-2 | IT-03、04、10～12、14 | 取消、重复取消通过；取消后提交失败 |
| 公开付款／契约 | IT-05～08、10～14 | 四原状态、缺失订单、异常、调用者恢复均通过 |
| 真实外部回执／AC-3 | IT-15 | 阻塞，未形成真实回执证据 |

这表示本轮范围全部有覆盖状态，本地全部已执行；不表示所有需求通过。无需人工视觉或主观反馈。AC-3 缺失的是端点、调用权限及真实服务证据。

## 6. 逐项结果与执行证据

各项方法为 [Quickstart 场景表与精确内联命令](../../../specs/order/quickstart.md#3-场景验证)，版本统一为第 3 节候选。正常场景均逐项重开；异常及恢复证据见下方命令原始输出（仅折叠 JSON 排版，字段和值保留）。

| 案例／依据 | 前置数据与实际操作 | 原预期 | 实际差异与关键结果 | 结果 | 证据／Issue |
| --- | --- | --- | --- | --- | --- |
| IT-01／新建 | 空库 create ORDER-1，关闭重开 | pending 持久化 | None/pending | PASS | 下方脚本输出 |
| IT-02／AC-1 | pending submit，关闭重开 | true/submitted | true/submitted | PASS | 两入口同结果 |
| IT-03／取消 | create 后连续 cancel 两次，重开 | cancelled 不变 | 两次 cancelled | PASS | 中间与重开一致 |
| IT-04／AC-2 | create/cancel，独立读，再 submit，重开 | false/cancelled | 提交前 cancelled，实际 true/submitted | FAIL | [BUG-001](../../issues/BUG-001.md) |
| IT-05／付款 | pending mark_paid | None/paid，调用者连接可用 | None，连接内与重开均 paid | PASS | 下方脚本输出 |
| IT-06／付款组合 | submitted mark_paid | 同上 | 同上 | PASS | 下方脚本输出 |
| IT-07／付款组合 | cancelled mark_paid | 同上 | 同上，不新增限制 | PASS | 下方脚本输出 |
| IT-08／付款重复 | paid mark_paid | 同上 | 同上 | PASS | 下方脚本输出 |
| IT-09／输入边界 | 空串、None、123 后合法 create | 拒绝无效输入、不创建行，合法调用恢复 | 三次 ValueError，0 行，RECOVER 重开 pending | PASS | 下方脚本输出 |
| IT-10／不存在对象 | read/cancel/submit/paid missing；后付 EXISTS | ValueError，其他订单不受影响，连接可用 | 四次 ValueError；EXISTS pending → paid 持久化 | PASS | 下方脚本输出 |
| IT-11／数据库异常 | 四写入口 query_only；rollback/恢复可写/重试 | 异常上传、原数据不变、重试可持久化 | 四次真实 OperationalError；独立 pending；重试各目标状态 | PASS | 下方脚本输出 |
| IT-12／commit 与恢复 | 四写入口 commit 注入故障；独立读/rollback/重试 | 同一异常上传、调用者可恢复、重试持久化 | 四次同一异常；独立 pending；rollback 恢复 true；重试成功 | PASS | 注入范围限 commit |
| IT-13／数据库边界 | 重复 create 后 rollback 再 paid | 数据库异常上传，原订单可恢复 | IntegrityError；pending → paid 持久化 | PASS | 下方脚本输出 |
| IT-14／跨订单 | cancel A、submit/paid B，关闭重开 | A cancelled、B paid、B 提交 true | 全部一致 | PASS | 下方脚本输出 |
| IT-15／AC-3 | 读取 runtime／执行公开 acceptance AC-3 | 已授权真实服务回执；缺前提则 BLOCKED | endpoint=null、authorized=false，无网络与真实回执 | BLOCKED | 影响 AC-3；提供端点和权限及操作授权后接续 |

`python -B checks/acceptance.py` 实际输出与退出码：

```json
[
  {"scenario":"AC-1","result":"PASS","accepted":true,"persisted_status":"submitted","expected_accepted":true,"expected_status":"submitted"},
  {"scenario":"AC-2","result":"FAIL","accepted":true,"persisted_status":"submitted","expected_accepted":false,"expected_status":"cancelled"},
  {"scenario":"AC-3","result":"BLOCKED","reason":"No external call is performed by this fixture; authorized endpoint and permission are required","endpoint_configured":false,"authorized":false}
]
```

退出 1。既有运行器不会接触外部服务；即使未来 runtime 就绪，也需有权执行者接入真实回执验证，不能把其固定 BLOCKED 的本地结果改写成成功。

精确指南脚本从 Markdown 的第二个 bash 围栏提取后实际运行，和首次内联扩展检查结果一致。其 stdout 原始字段和值如下；指南子命令退出 1，无 stderr。提取脚本外层返回 0 仅表示成功捕获结果，不能当验收通过。

```json
{
  "cases": [
    {"case":"IT-01","result":"PASS","actual":[null,"pending"]},
    {"case":"IT-02","result":"PASS","actual":[true,"submitted"]},
    {"case":"IT-03","result":"PASS","actual":["cancelled","cancelled"]},
    {"case":"IT-04","result":"FAIL","actual":["cancelled",true,"submitted"]},
    {"case":"IT-05","result":"PASS","actual":["pending",null,"paid","paid"]},
    {"case":"IT-06","result":"PASS","actual":["submitted",null,"paid","paid"]},
    {"case":"IT-07","result":"PASS","actual":["cancelled",null,"paid","paid"]},
    {"case":"IT-08","result":"PASS","actual":["paid",null,"paid","paid"]},
    {"case":"IT-09","result":"PASS","actual":[["order_id is required","order_id is required","order_id is required"],0,"pending"]},
    {"case":"IT-10","result":"PASS","actual":[["order not found","order not found","order not found","order not found"],"pending","paid"]},
    {"case":"IT-11","result":"PASS","actual":[
      ["create","OperationalError","attempt to write a readonly database","pending","pending"],
      ["cancel","OperationalError","attempt to write a readonly database","pending","cancelled"],
      ["submit","OperationalError","attempt to write a readonly database","pending","submitted"],
      ["paid","OperationalError","attempt to write a readonly database","pending","paid"]]},
    {"case":"IT-12","result":"PASS","actual":[
      ["create","injected commit failure",true,"pending",true,"pending"],
      ["cancel","injected commit failure",true,"pending",true,"cancelled"],
      ["submit","injected commit failure",true,"pending",true,"submitted"],
      ["paid","injected commit failure",true,"pending",true,"paid"]]},
    {"case":"IT-13","result":"PASS","actual":["IntegrityError","UNIQUE constraint failed: orders.order_id","pending","paid"]},
    {"case":"IT-14","result":"PASS","actual":[true,"cancelled","paid"]}
  ],
  "temporary_directory_removed":true
}
```

IT-12 数组顺序为操作、异常消息、同一异常对象、独立连接旧状态、rollback 恢复成立、重试重开状态。IT-11 数组顺序为操作、异常类型、消息、恢复前独立读取、重试重开状态。首次独立内联检查另确认 IT-09 三个错误类型均 ValueError、IT-10 四个错误均 `ValueError: order not found`，上述复跑断言仍检查类型，输出精简为消息。

## 7. 问题与影响

| Issue | 案例 | 影响 |
| --- | --- | --- |
| [BUG-001：取消后提交覆盖取消](../../issues/BUG-001.md) | IT-04／AC-2 | OPEN；既有业务缺陷仍不满足原 false/cancelled 判据，阻止 Test Gate 通过。本轮未修复 |

AC-3 端点和权限缺失是已知前置阻塞，无证据表明产品缺陷，不另造产品 Bug。Review CHK-002～005 项目规则映射缺失独立保留，不改本轮业务预期。

## 8. 结论、限制与恢复

**Test Gate：FAIL。** 适用范围为本批第 2 节已确认订单功能、指定 HEAD 加指纹所示未提交候选、当前隔离本地 Python／文件 SQLite。13 PASS、1 FAIL、1 BLOCKED 不能判为 PASS；批次取证已完成且无可执行遗漏。

AC-2 必须经 Main 获得缺陷处理授权后另阶段修复，再回到实际修复候选复验原 IT-04 与必要回归，保持原判据及历史失败证据。此处 Issue 登记不启动 bugfix。AC-3 由有权人员提供真实外部测试服务端点、权限及操作授权后续验真实回执；本地测试不能替代。必需人工视觉反馈不适用，未请求主观反馈。

[Review Gate](payment-review.md) 仍为 UNVERIFIED，其规则维护恢复条件保持原记录；本轮 Test Gate 与其分别判定，不作为发布通过证据。后续候选或环境变化需重新核对指纹和覆盖影响。

文档写后核对：已读回本报告、Quickstart、Issue 与索引，核对原 Spec／契约、案例总数与逐项计数、真实／注入边界、失败保留、恢复条件和引用。机械检查命令 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/order/quickstart.md docs/test-reports/order/integration.md docs/issues/BUG-001.md docs/index.md`，结果 4 files、0 errors、0 warnings、退出 0；`git diff --check` 退出 0。机械检查不证明业务通过，语义结论为完整本地取证但 AC-2 失败、AC-3 阻塞，未解决项如上。
