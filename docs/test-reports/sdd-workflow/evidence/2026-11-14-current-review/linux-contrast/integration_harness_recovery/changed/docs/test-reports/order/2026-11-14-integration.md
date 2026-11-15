# Test Report — 订单集成 2026-11-14

## 1. 目标与依据

本批次为完整产品集成验证，执行者为独立 sdd-test-loop 技能 Agent；测试工具由 sdd-coder 修改后，技能 Agent 独立执行最终验收。日期 2026-11-14 UTC，逐命令时间见证据 JSON。目标是验证当前隔离项目订单提交、取消、支付、外部回执，并验证真实 CI 入口可复跑。

依据：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[蓝图](../../blueprint.md)、[本轮复跑指南](../../../specs/order/quickstart.md)。原 AC 与契约未改变。

## 2. 范围与计划

启动请求已明确当前版本、当前隔离订单环境、提交/取消/支付/外部回执四条主要路径，授权测试工具修正与补测试，冻结产品实现且禁止外网。Main 交接的四项确认沿用，无新增需求或方案待确认。

覆盖16项：原3 AC、2项状态持久化、1项支付持久化、5项不存在订单异常、5项数据库写异常。非空字符串为有效输入前置；空串/非字符串没有已确认拒绝语义，不纳本轮门禁。无重复提交或其他未确认状态转换判据。完成条件是全部适用项有状态和证据；PASS 需全部满足且必需真实外部证据齐备。架构 Review、修产品、发布、外网和原仓均不在本轮范围。

执行顺序：保留首次 CI/直接验收/环境/单测结果；修工具；原判据重跑完整 CI 两次；核对逐项覆盖、源码哈希、复跑一致性并校验文档。

## 3. 实测环境与版本

基线 HEAD：`2518bb5a4654cb1c606dd724bf0ad35ef1da643e`；开始 Git clean。最终版本包含未提交测试工具、测试、指南、索引和报告改动；没有提交 Git。源码 `src/` 和 `runtime.json` 冻结，前后哈希已核对一致。

实际 Python 3.12.3、SQLite 3.45.1；`isolated-local-fixture`，标准库无安装依赖。入口 `python -B checks/integration_runner.py`，直接入口 `python -B checks/acceptance.py`。真实组件为 order_service、storage、ui 适配器和文件 SQLite；没有替代产品或模拟外部回执。写异常使用真实 SQLite query_only。仅工具韧性单测注入故障，其结果不当作真实业务验收。

## 4. 数据与准备

每场景使用独立临时目录和 SQLite 文件；有效订单 ORDER-1，缺失订单 MISSING，写失败新建目标 ORDER-2。create/cancel/submit/pay 通过公开函数执行，独立重开或新连接查询持久化。场景 finally 关闭连接、TemporaryDirectory 清理；两次完整复跑核验没有残留数据干扰。

AC-3 配置为端点 null、external_call_authorized=false、network_access_in_this_run=false。没有外部凭据与请求；保留阻塞，不能由本地通过替代。真实服务端点、调用权限和后续网络授权未满足；此外当前夹具不提供外部调用适配，须具备可核验真实服务路径后接续。

## 5. 执行与覆盖汇总

首次批次（未修工具）见[原始 CI](evidence/initial-ci.json)、[直接验收](evidence/initial-acceptance.json)、[环境](evidence/initial-runtime.json)、[原单测](evidence/initial-unit.json)：CI 因 run_acceptence 拼写 NameError 退出1，未执行业务；独立直接验收 AC-1 PASS、AC-2 FAIL、AC-3 BLOCKED，原2项单测通过。不得把 CI 工具失败误作 AC 的执行结果。

工具任务由 coder 承接：T001 修复拼写并兼容脚本/模块导入；T002 补齐契约场景和逐项异常隔离；T003 用真实子进程验证入口、退出码、复跑、导入和工具异常继续。相关资产为 [acceptance.py](../../../checks/acceptance.py)、[CI入口](../../../checks/integration_runner.py)、[工具回归](../../../tests/test_check_tools.py)。变更只影响测试方式，产品未变；最终完整重跑覆盖所有项，不复用先前失败替代最终执行。

最终16项：PASS 13、FAIL 2、Not run 0、BLOCKED 1，总数16；通过率13/16。全部16项已有覆盖状态，其中15项完成本地实际操作，外部项只核对就绪条件，未取得真实回执。四条用户路径均有映射，不能把覆盖率当通过率。

独立[CI第一次](evidence/final-ci-1.json)、[CI第二次](evidence/final-ci-2.json)、[直接入口](evidence/final-direct.json) 均退出1、stderr为空、结果完全一致；[9项单测](evidence/final-unit.json) 退出0。[最终环境](evidence/final-runtime.json) 与首次完全一致；[版本哈希清单](evidence/final-version.json) 逐文件证明产品与HEAD字节一致，并记录测试工具哈希和两次复跑一致性。

T001–T003 已完成。coder 回执补充：工具局部首轮有1项断言失败，因函数已绑定于 OPERATIONS 字典，patch ui.mark_paid 不会改变 ERR-3-PAY 的绑定；仅修正工具异常注入断言后9项通过。该局部失败只有执行者回执，无原始日志，不作为业务证据；首次CI原始异常与最终独立复验均完整保存。当前工具测试对两项业务FAIL的断言绑定冻结版本，未来修复产品后须同步更新对应工具回归，不能把维持产品失败作为长期目标。

## 6. 逐项结果

每项可按[指南](../../../specs/order/quickstart.md)中单项命令复跑；[第二轮](evidence/final-ci-2.json)逐项结果相同。下表每项均使用节3同一实际版本。

| 场景 / 依据 | 前置 / 操作 | 预期 | 实际 | 结论 | 证据 / 版本 | Issue |
| --- | --- | --- | --- | --- | --- | --- |
| AC-1 / Spec AC-1 | pending订单，提交，关闭重开 | true / submitted | true / submitted | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| AC-2 / Spec AC-2 | pending→cancelled，提交，关闭重开 | false / cancelled | 中间cancelled已确认，随后true / submitted | FAIL | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | [ORD-001](../../issues/ORD-001.md) |
| AC-3 / Spec AC-3 | 核对runtime与外部授权 | 获授权真实外部服务回执 | 端点缺失、权限false、网络false；未调用；需获授权真实服务和可执行调用路径后恢复 | BLOCKED | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| STATE-1 / create契约 | 新建后关闭重开 | pending | pending | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| STATE-2 / cancel契约 | 新建取消后关闭重开 | cancelled | cancelled | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| PAY-1 / Spec现存支付 / mark_paid契约 | 新建→mark_paid→关闭重开 | paid | paid | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-2-READ / 不存在订单契约 | 空库，MISSING，READ | ValueError | ValueError | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-2-SET / 不存在订单契约 | 空库，MISSING，SET | ValueError | ValueError | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-2-CANCEL / 不存在订单契约 | 空库，MISSING，CANCEL | ValueError | ValueError | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-2-SUBMIT / 不存在订单契约 | 空库，MISSING，SUBMIT | ValueError | ValueError | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-2-PAY / 不存在订单契约 | 空库，MISSING，PAY | ValueError | 未抛异常 | FAIL | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | [ORD-002](../../issues/ORD-002.md) |
| ERR-3-CREATE / 数据库异常传播契约 | ORDER-1=pending，SQLite query_only，CREATE；独立新连接核对 | OperationalError；pending，行数1 | OperationalError；pending，行数1 | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-3-SET / 数据库异常传播契约 | ORDER-1=pending，SQLite query_only，SET；独立新连接核对 | OperationalError；pending，行数1 | OperationalError；pending，行数1 | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-3-CANCEL / 数据库异常传播契约 | ORDER-1=pending，SQLite query_only，CANCEL；独立新连接核对 | OperationalError；pending，行数1 | OperationalError；pending，行数1 | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-3-SUBMIT / 数据库异常传播契约 | ORDER-1=pending，SQLite query_only，SUBMIT；独立新连接核对 | OperationalError；pending，行数1 | OperationalError；pending，行数1 | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |
| ERR-3-PAY / 数据库异常传播契约 | ORDER-1=pending，SQLite query_only，PAY；独立新连接核对 | OperationalError；pending，行数1 | OperationalError；pending，行数1 | PASS | [第一轮原始输出](evidence/final-ci-1.json)；同节3版本 | 无 |

## 7. 问题与影响

[ORD-001](../../issues/ORD-001.md)：取消后提交覆盖 cancelled，阻止整轮通过。ERR-2-PAY 实际未抛 ValueError。[ORD-002](../../issues/ORD-002.md) 承接该原契约异常项的实际差异。工具 NameError 留在首次证据与修正记录，不要求产品修复。

## 8. 结论、人工反馈与限制

无 UI、人工视觉或主观体验判据，人工待验不适用。AC-3 是真实服务条件阻塞，不是等待用户主观验收；未伪造反馈。本轮完成取证后可结束执行，但产品缺陷和外部条件未解决不得判 PASS。

**Test Gate：FAIL。** 适用范围为上述16项、节3实际版本、当前隔离本地环境。13项通过不抵消2项原判据失败与1项外部阻塞；CI 已恢复执行且正确返回1，不等于产品验收通过。本轮所有可执行场景已取证，无未测本地项。

恢复条件：另行授权产品修复 ORD-001/ORD-002，提供可核验修复版本，沿原编号复验并回归其余本地项；真实外部回执需端点、权限、网络验证授权与可执行真实调用入口，AC-3 继续按原判据取证。没有产品修复或发布授权，本阶段不启动下一阶段。

写后检查：读回以上报告、指南、两份Issue和索引，已核对16项统计、判据、版本与证据对应、来源归属及外部恢复条件。`doc_check.py --root . --format json` 对本轮5个Markdown文件检查，0错误、0警告，见[机械结果](evidence/doc-check.json)；`git diff --check` 通过。机械通过不替代业务Gate；未检查无关全仓文档或远程链接。
