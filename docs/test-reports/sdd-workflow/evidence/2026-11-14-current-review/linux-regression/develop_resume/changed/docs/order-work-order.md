# WO-ORDER-004

已完成需求落盘前及交付实施前确认。适用依据为 [订单 Spec](../specs/order/spec.md) 和 [订单接口](contracts/order.md)。

AC-4 在本地测试数据库从公开新建入口依次提交空字符串、全空格、制表符及换行组合。应报告拒绝，查不到对应订单。合法编号应创建并保存 pending 订单。门槛为空或全空白，保持有效编号、函数签名与其他状态操作。

验收由 Main 在实现版本就绪后从公开入口执行，使用独立临时数据库，记录调用结果、持久化状态、实际版本及复跑入口。

## 验收记录

### 1. 目标与依据

2026-11-14，WO-ORDER-004 点对点需求验收。Main 负责最终 AC-4 验收，独立 sdd-develop 技能 Agent 补验 AC-4 与直接受影响的 AC-1；实施者 sdd-coder 的局部证据见[原 Plan](order-plan.md)。依据为本工单、Spec AC-4、接口契约及[验收指南](../specs/order/quickstart.md)。

### 2. 范围与方案

验收空或全空白编号的拒绝与无写入、合法编号原值保存 pending；回归合法订单提交及持久化。逐项调用公开函数入口，拒绝后检查当前连接及新连接行数，合法创建后通过新连接读取。AC-2、AC-3 不属于本批验收范围，本批未执行；本记录不提供全功能集成 Test Gate。

### 3. 实际版本与环境

- 版本：HEAD `7943f41f342ca7e11011db7b65f644e2bbb96f23` 加本轮未提交工作树；无提交或其他 Git 写操作。
- 实现 SHA-256：`src/order_service.py` 为 `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`。
- 验收脚本 SHA-256：`checks/acceptance.py` 为 `689ba72893f82f826f42978c8743e176b11bc8173010e878f7a9b5d791e61964`。
- 环境：隔离项目，Python 3.12.3、SQLite 3.45.1；使用真实 Python 函数与本地 SQLite，无模拟服务、无外部访问。运行事实来自 `python -B checks/runtime_details.py`。

### 4. 数据与准备

每个场景新建独立临时 SQLite 文件。AC-4 初始表为空，顺序提交下表输入；AC-1 使用 `ORDER-1`。脚本关闭连接并通过 TemporaryDirectory 清理数据，实际执行正常退出；无准备缺口或生产数据影响。

### 5. 执行与覆盖

本批 2 个场景，2 通过、0 失败、0 未运行、0 阻塞。AC-4 包含 4 个拒绝输入与 2 个合法输入；Main 最终执行与技能 Agent 补验均通过，按同一场景计数。AC-1 由技能 Agent 执行通过。局部单测另计：实施者定向 2 项、完整本地单测 4 项通过，覆盖正常提交和 paid 持久化，见原 Plan。

### 6. 逐项结果

| 场景与输入 | 实际入口与执行者 | 预期与实际结果 | 结论 |
| --- | --- | --- | --- |
| AC-4：`""`、`"   "`、`"\t"`、`" \t\n "` | `python -B checks/acceptance.py --scenario AC-4`；Main 最终验收，技能 Agent 独立补验 | 4 次均抛出 ValueError，visible_order_count 和 persisted_order_count 每次均为 0，符合拒绝且无写入判据 | PASS，退出 0 |
| AC-4：`ORDER-4`、`"  ORDER-5\t"` | 同上，同一场景内后续调用 | 两个编号均以原值落库，重开连接读取 pending，符合合法编号正常创建判据 | PASS，计入 AC-4 |
| AC-1：`ORDER-1` | `python -B checks/acceptance.py --scenario AC-1`；技能 Agent 补验 | accepted=true，重开数据库 persisted_status=submitted，与 expected_accepted=true、expected_status=submitted 一致 | PASS，退出 0 |

Main 同时核对实现、单测和验收脚本 diff：校验位于 INSERT 前，合法值未被修改，其他状态逻辑未改动。技能 Agent 执行 `git diff --check`，退出 0。

### 7. 问题与影响

本批无未解决失败或新 Issue。AC-2 的取消提交行为、AC-3 的真实外部回执均未在本批取证，不据此推定通过或修复；AC-3 的授权恢复条件沿用验收指南。

### 8. 结论与限制

WO-ORDER-004 AC-4 在上述工作树与隔离环境验收通过，直接相关 AC-1 回归通过，无本工单未完成项。不涉及用户视觉体验，沿用已有 A/B 确认；Main 最终验收执行结果通过任务回传固化。此结论限于本工单点对点验收，不代表全产品集成回归、架构审查或真实服务发布。
