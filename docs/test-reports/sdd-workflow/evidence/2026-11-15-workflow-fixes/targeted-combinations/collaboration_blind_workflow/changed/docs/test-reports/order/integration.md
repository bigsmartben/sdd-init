# 订单完整功能集成测试报告

## 1. 目标与依据

批次：order-integration-01；类型：独立完整功能集成回归；执行者：Main 调度的 `/root/integration`；执行时间：2026-11-14T16:24:38.336863+00:00。依据：[Spec](../../../specs/order/spec.md)、[订单契约](../../contracts/order.md)、[本轮 Quickstart](../../../specs/order/quickstart.md)。

目标为取消后仍提交缺陷修复后的实际候选，核验全部已确认产品功能；本报告与实施者局部自验、BUG-001 定向复验、架构符合性 Review 分开。

## 2. 范围与计划

Main 启动指令已传达用户对验收范围、主要公开路径、判据和本地 Python＋真实临时 SQLite 文件环境的确认；随后 Main 交付 BUG-001 R1 候选标识并明确准许正式执行。本轮未变更范围、版本或业务判据。

I01～I08 覆盖本地产品功能、异常、边界、重复取消后提交、跨入口协同和恢复读回，E03 覆盖外部 AC-3。全部适用功能通过、证据完整才可 Test Gate PASS。纯内部职责和依赖符合性由 Main 另行组织架构 Review，不作为业务判据。无 UI、无需人工视觉或体验判断。

## 3. 环境与实际版本

- 实际候选：`sha256:7d4083da88ed6593bc2039b890b0026681f522ac7b53d7aa8c8dcde4cb269fea`，与 Main 指定 [manifest](bugfix-candidate.json) 的所有 `src/*.py`、`checks/*.py`、`runtime.json` 哈希一致；执行前后逐文件哈希与合成候选标识未变，见[身份取证](integration-identity.json)。无需 Git 操作，候选标识覆盖实际工作区相关文件；测试资产另记录哈希。
- `src/order_service.py` SHA-256：`3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`。未对产品代码写入。
- Python 3.12.3、SQLite 3.45.1；[运行时原始事实](integration-runtime.json)。环境为 isolated-local-fixture；入口为 `checks/acceptance.py` 和公开函数集成测试。
- 真实组件：本项目 order_service、ui、storage、标准库 SQLite，逐场景独立真实临时文件。没有替代服务或模拟回执，未访问网络。

## 4. 数据与准备

测试创建 `订单-1`、ORDER-1、SERVICE、ADAPTER、CANCEL、SUBMIT、PAY 等常规非空编号；missing 始终不存在；空串、None、整数用于已确认非空字符串边界。独立临时目录与数据库由测试创建和退出清理，无业务数据变更。I07 故意关闭真实连接以验证 SQLite 异常传播。

准备时读取既有 checks 装配并新增 [integration 测试](../../../tests/test_order_integration.py)，仅做语法检查；正式候选送达后才实测。既有自验或并行执行者提前加载本测试的输出不计本批次结论。各正式命令均执行完毕、未中途跳过用例。

准备缺口：AC-3 缺少真实端点、权限和网络授权；当前验收脚本固定输出 BLOCKED，亦无真实外部验证执行路径。此限制不能通过本地通过或只修改配置消除。

## 5. 执行与覆盖统计

按 9 个稳定场景计数：**PASS 7、FAIL 1、NOT RUN 0、BLOCKED 1，总计 9**。场景通过率 7/9；8 个可执行本地场景中 7 个通过。I05 内 5 个公开入口子场景有 4 个通过，mark_paid 子场景失败；仍只按一个 I05 场景计数。主要验收入口 AC-1/2 是 I02/I03 的交叉证据，不重复计场景数。既有 test_order.py 4 个测试通过，单列辅助回归证据，不加入 9 场景分母。

需求覆盖与通过率分开：AC-1、AC-2 完成真实本地覆盖且通过；AC-3 已建立覆盖项但真实回执验证阻塞。契约中的创建、取消、提交、set_status、mark_paid 现存订单持久化、输入边界、数据库错误传播与多订单隔离已执行；不存在订单异常仅 mark_paid 不满足。没有以缺少证据自行判产品缺陷，也未将架构职责偏差算作业务失败。

## 6. 逐项结果

所有场景实际版本均为第 3 节候选；全部本地步骤、初始数据与断言见 Quickstart 和测试资产。

| 场景 / 判据 | 实际操作与关键观察 | 预期与差异 | Verdict | 证据 | Issue |
|---|---|---|---|---|---|
| I01 / 创建契约 | 中文非空编号新建后新连接读取 pending | 与预期一致 | PASS | [集成输出](integration-integration.json) | 无 |
| I02 / AC-1 | 新建、提交返回 true；关闭重开为 submitted | 与预期一致 | PASS | [集成输出](integration-integration.json)、[验收 JSON](integration-acceptance.json) | 无 |
| I03 / AC-2 | 取消先读回 cancelled；两次提交均 false，SQLite total_changes 未增加；关闭重开仍 cancelled | 与预期一致，取消不被覆盖且取消分支不写数据库 | PASS | [集成输出](integration-integration.json)、[验收 JSON](integration-acceptance.json) | [BUG-001](../../issues/BUG-001.md) 原故障独立集成确认 |
| I04 / paid | set_status 与 mark_paid 分别作用两个现存订单，关闭重开都 paid | 与预期一致 | PASS | [集成输出](integration-integration.json) | 无 |
| I05 / 不存在订单 | read_status、cancel、submit、set_status 抛 ValueError；mark_paid 无异常返回 None，数据库仍无订单 | mark_paid 违反同一已确认异常契约 | FAIL | [完整失败输出](integration-integration.json)、[针对性公开入口结果](integration-bug002.json) | [BUG-002](../../issues/BUG-002.md) |
| I06 / 编号边界 | 空字符串、None、整数新建均 ValueError，表仍 0 行 | 与预期一致 | PASS | [集成输出](integration-integration.json) | 无 |
| I07 / DB 异常 | 真实连接关闭后调用六个公开入口，均传播 sqlite3.Error | 与预期一致 | PASS | [集成输出](integration-integration.json) | 无 |
| I08 / 协同与隔离 | 同库三订单走取消提交、正常提交、mark_paid；关闭重开分别 cancelled、submitted、paid | 返回 false/true 且互不覆盖 | PASS | [集成输出](integration-integration.json) | 无 |
| E03 / AC-3 | 只读取 runtime：端点未配置、调用未授权；没有网络请求 | 无法核验真实回执；本地结果不能代替 | BLOCKED | [验收 JSON](integration-acceptance.json)、[运行时](integration-runtime.json) | 非实现缺陷，不建缺陷 Issue |

正式命令与退出：`checks/acceptance.py` 退出 3（两通过一阻塞）；`unittest discover -s tests -p test_order_integration.py -v` 退出 1（8 场景一个失败）；既有 `test_order.py` 4 测试 OK，退出 0，见[辅助回归输出](integration-regression.json)。原始输出保留精确命令、stdout、stderr、退出码。未发生测试侧装配失败或断言修改后重跑；针对 BUG-002 的单次补充观察保留独立证据。

## 7. 关联问题与影响

| Issue | 场景 | 本批次意义 |
|---|---|---|
| [BUG-001](../../issues/BUG-001.md) | I02、I03、I08 | 修复后取消不可覆盖在独立完整集成中通过，保持原问题已关闭结论；此前诊断及修复定向证据归 [Bugfix 报告](bugfix-001.md) |
| [BUG-002](../../issues/BUG-002.md) | I05 | 独立确认 mark_paid 对不存在订单不抛 ValueError，Pending；本轮不修改产品，阻止完整 Test Gate 通过 |

BUG-002 恢复条件是用户另行授权修复原契约偏差，然后按 I05 原判据复验并回归 I04 与其他公开路径。未把新发现问题扩为新增业务需求。

## 8. 结论与限制

本轮已完成全部可执行场景并记录完整覆盖状态。**Test Gate：FAIL**，适用范围为上述实际候选、本地真实文件 SQLite 和已确认完整产品功能；直接失败依据是 I05／BUG-002，此外 E03／AC-3 独立 BLOCKED。BUG-001 已修复通过不等同于完整产品 Gate 通过。

AC-3 恢复需要有权人员提供真实外部测试端点、调用权限、网络授权，并安排获授权的真实服务验证入口（或测试适配）；现有 checks 固定 BLOCKED，仅修改 runtime 配置仍不足。外部凭据、配置、部署与测试适配均未在本轮实施。恢复后需在明确候选上保留真实回执证据，并核对版本变化对其余场景的复验影响。

人工验收：不适用，Spec 明确无 UI／无需人工视觉；本报告没有以用户反馈代替自动证据。架构纯偏差由独立 Review 负责，本报告不给出架构 Gate。
