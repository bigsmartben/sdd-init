# 订单号校验隔离验收

## 1. 目标与依据

2026-11-14，由本轮 sdd-develop 技能 Agent 执行需求点对点验收，与实施角色分离。依据 [Spec](../../../specs/order/spec.md) AC-4、AC-5、用户 A/B 确认及[验收方案](../../../specs/order/quickstart.md#本轮订单号校验验收)。用户已明确授权实施并完成本轮隔离验收。

## 2. 范围与计划

验证全空白拒绝且不写订单、合法原值创建、非字符串保持，直接回归 AC-1 和 mark_paid。按方案从正式服务公开函数调用，检查当前连接及重开文件后的数据。取消提交、外部服务及架构 Review 不属于本轮验收；不产出集成 Test Gate。

## 3. 实际版本与环境

基线 Git HEAD `83a8ad12ca4c60ba9bcaf37ec891db0e6a35c046` 加本轮未提交工作区变更，未创建提交。`src/order_service.py` SHA256 为 `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`。Python 3.12.3、SQLite 3.45.1；真实 Python 服务模块和文件 SQLite，无模拟数据库或网络调用。配置及正式源文件哈希见[环境原始输出](evidence/runtime.json)。

## 4. 准备与数据

命令设置 `TMPDIR=/tmp/sdd-review-execution-ykzxy2w_/develop_delivery-zwof9g4j/scratch`。每个输入在独立临时文件数据库预建 `BASELINE`，按指南比较全部行，关闭并重开后复查；临时目录由上下文退出清理，命令均正常结束。8 个空/空白、3 个合法及 5 个非字符串样本逐项见下列 JSON；无准备缺口。

## 5. 执行与覆盖汇总

AC-4、AC-5、AC-1 和单元测试各命令退出码均为 0，[命令及回执](evidence/commands.json)。按不同输入或独立直接回归计 18 个验收案例，18 通过、0 失败、0 未执行、0 阻塞；5 个单元测试作为补充回归单独统计，不重复计入这 18 个案例。覆盖本轮全部 AC 及指定直接回归；未扩大为全产品回归。

## 6. 逐项结果

命令均在隔离项目根目录运行，使用上文 TMPDIR 和版本。

| 案例 / 依据 | 实际入口与数据 | 实际结果与判据 | 结论 | 原始证据 |
|---|---|---|---|---|
| AC-4 的 8 个输入 | `python -B checks/acceptance.py --scenario AC-4`；空串、单/多空格、tab、换行、混合空白、U+3000、U+00A0 | 全部 ValueError，消息均为 order_id is required；当前及重开后均只有未变的 BASELINE 行 | 8/8 PASS | [逐输入 JSON](evidence/AC-4.json) |
| AC-5 的 3 个合法输入 | `python -B checks/acceptance.py --scenario AC-5`；普通编号、首尾空格、首尾 tab/换行 | 当前及重开后新增原值 pending 行；基准未变；有空白的编号没有裁剪替代行 | 3/3 PASS | [逐输入 JSON](evidence/AC-5.json) |
| AC-5 的 5 个类型输入 | 同上；None、0、False、空列表、空字典 | 全部为相同 ValueError；当前及重开后全部行与基准完全相同 | 5/5 PASS | [逐输入 JSON](evidence/AC-5.json) |
| AC-1 | `python -B checks/acceptance.py --scenario AC-1` | 返回 true；重开后 submitted | PASS | [原始 JSON](evidence/AC-1.json) |
| mark_paid | `python -B -m unittest discover -s tests -v` 中既有持久化测试 | 重新连接读取 paid；整套 5 个测试通过 | PASS | [单测输出](evidence/unit.txt) |

## 7. 相关问题与影响

无本轮新增失败。实施前静态调查发现既有取消后提交覆盖 cancelled、UI 直接写 SQL，已交 Main；没有为本轮修改这些路径。复用实施角色在相同代码哈希和环境下的[默认入口原始输出](evidence/coder-all.json)：`python -B checks/acceptance.py` 退出 1，AC-1/4/5 PASS、AC-2 FAIL（实际 true/submitted，预期 false/cancelled）、AC-3 BLOCKED。这是额外入口核验，不计入上述 18 个本轮案例，也不是全产品集成验收。AC-2 未判通过；AC-3 无端点及外部权限，未发起外部调用，恢复条件仍为有权人员提供端点和授权。上述事项不改变本轮 AC-4、AC-5 的通过结论，不声明其修复或全产品可交付。

## 8. 结论与限制

本轮隔离验收通过：全空白按空字符串拒绝且无订单新增或已有行变更，合法原值、类型校验及指定直接回归保持。结论适用于上述工作区版本和实际环境。无需人工视觉判断；用户 A/B 确认只证明需求和实施授权，不替代执行证据。集成 Test Gate、架构符合性及外部服务结果均不适用本批次。后续集成入口与局部实施回执见[同一计划](../../../specs/order/plan.md)。
