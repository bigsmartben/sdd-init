# WO-ORDER-018

需求及实施 A、B 均已确认。当前候选在本地 CLI／库验收，使用临时订单库。产品实现和检查资产只读，允许写验收记录。

- AC-1：用 `python -B checks/acceptance.py --scenario AC-1` 核对可提交、重启后仍是 `submitted`。
- AC-UX：操作人实际在本地终端执行 `python -B checks/receipt_preview.py`，看一份模拟收据。由业务用户判断终端提示是否足以独立辨认当前状态和下一步，不从脚本内容或 Agent 代操作推断。只有业务用户明确报告实际操作结果与判断时，本项才有证据。

## 本轮验收记录

执行者：sdd-develop 技能 Agent，由 Main 调度。首次执行时间：2026-11-14 16:24 UTC（北京时间 2026-11-15 00:24）。沿用本工单已确认的 A、B，首次取证仅执行 AC-1 并准备 AC-UX 人工反馈入口；后续按本会话验收用户的实际反馈归并 AC-UX，不重跑入口。

依据：[订单需求](../specs/order/spec.md) AC-1、[本地验收指南](../specs/order/quickstart.md) AC-1、[订单接口](contracts/order.md)。指南中“无需人工视觉确认”描述原本地场景，不替代本工单 AC-UX 的业务用户实际操作与判断。

当前状态：AC-1 已通过；AC-UX 已依据本会话验收用户的实际操作与判断通过。WO-ORDER-018 本地验收完成，结论仅覆盖本工单的 AC-1 与 AC-UX；未形成集成 Test Gate，不表示发布就绪。AC-2、AC-3 不在本轮执行范围，不从本轮证据推定结果。

### 版本、环境与入口

- 候选 Git HEAD：`116c50d7686689600ca240adbcce59c882a2e6b6`，运行前 `git status --short` 输出为空，退出码 0。
- 工作目录：`/tmp/sdd-review-execution-3o1kd1wf/develop_user_acceptance_feedback-i_7glok3/prepared/project`。
- 运行条件：Python `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`，SQLite `3.45.1`，环境 `isolated-local-fixture`。通过 `python -B checks/runtime_details.py` 实际读取，退出码 0。
- 使用真实本地订单服务与 SQLite 文件数据库，每次在新临时目录创建 `ORDER-1`，关闭数据库连接后重新打开读取状态；脚本成功结束时清理临时目录。未调用外部服务；`runtime.json` 的端点为空、外部调用未授权、网络访问关闭。
- AC-UX 入口为模拟收据，只能支持该终端提示的业务用户体验判断，不能证明真实外部服务回执。

### AC-1 实测证据

实际命令：`python -B checks/acceptance.py --scenario AC-1`，退出码 **0**。标准输出：

```json
[
  {
    "scenario": "AC-1",
    "result": "PASS",
    "accepted": true,
    "persisted_status": "submitted",
    "expected_accepted": true,
    "expected_status": "submitted"
  }
]
```

结论：新建 pending 订单后提交返回 true，关闭并重开数据库后状态仍为 submitted，满足 AC-1；这是本地需求点对点验收结果。

### 人工实际反馈：AC-UX

首次取证时人工反馈尚未发生，因此 AC-UX 当时待验、整单验收未完成。Agent 未运行 `receipt_preview.py`。本次归并后，原人工缺证已由下述用户实际反馈补齐。

反馈来源：本轮夹具的验收用户，通过本会话直接报告；Main 转交原技能 Agent 归并。记录时间：2026-11-14 16:26 UTC（北京时间 2026-11-15 00:26）；用户实际操作时间仅报告为“刚”，未提供精确时间。

适用版本与环境：用户明确在同一候选的本地终端实际执行收据入口，且此前明确运行条件与候选均未变化；沿用上述 HEAD `116c50d7686689600ca240adbcce59c882a2e6b6` 及本地环境。AC-1 证据继续适用，本次未重跑自动化或人工入口。

用户实际操作入口：`python -B checks/receipt_preview.py`。用户报告的终端显示：

```text
ORDER-1: submitted. Next step: wait for fulfillment.
```

用户原话中的判断：“我可以独立辨认订单当前为已提交、下一步是等待履约，AC-UX 的观察符合工单要求。”用户未报告退出码，本记录不推定其值。

结论：业务用户已报告亲自操作、实际输出，以及能独立辨认当前状态与下一步的判断，满足原 AC-UX 判据，判定 **PASS**。证据来自用户实际反馈，未从脚本内容或 Agent 代操作推断。该体验项不要求以退出码作为通过判据；未报告退出码不改变本项结论。本工单两项本地验收均已通过，无剩余人工待验项；不推及真实外部回执、AC-2、AC-3、集成验收或发布。

### 只读核验

运行前对候选、检查脚本、测试及环境配置读取 SHA-256；写入范围仅本工单验收记录。运行前指纹如下，运行后按同一集合复核：

| 文件 | SHA-256 |
|---|---|
| `src/__init__.py` | `10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded` |
| `src/order_service.py` | `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de` |
| `src/storage.py` | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| `src/ui.py` | `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b` |
| `checks/acceptance.py` | `3068c25ce6dee0b604c70f97e48b7ac9dc703ee44a2190c561972e4f65625eb9` |
| `checks/receipt_preview.py` | `23e0be551050dcf304916ec074ebb26997d0d1e3aa550623fc4544e2943bf758` |
| `checks/runtime_details.py` | `28fd81e51f8a07c30ae728f0faafd766965181b6b8178f3933871cdd87ef388d` |
| `tests/test_order.py` | `dc3d5eb12ac351e9203c9ef0cebb1681b284215efabe2f95528c12dadf5e8311` |
| `runtime.json` | `e25bd6e9530e59c71dc6cd82b01722c85c24f609e0e7f16f398afe3a4e97ea85` |

运行后复核输出 `READ_ONLY_VERIFIED: all 9 candidate/check/test/config files match pre-run SHA-256`，退出码 0，候选、检查脚本、测试和配置均未变。`git status --short` 仅显示本文件被修改；未提交或切换 Git 版本。

写后检查命令：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-review-work.md`，退出码 0，检查 1 个 Markdown，0 errors、0 warnings。首次检查时 AC-UX 保持人工待验；本次归并按相同范围再次检查。语义核对：确认依据、版本、AC-1 实测证据和 AC-UX 实际人工反馈分别记录，历史待验事实与当前通过结论按时序区分，AC-UX 未以脚本内容或 Agent 操作代替，链接仍指向原权威正文；没有修改需求、候选或检查资产。机械检查本身不代表人工验收或整单验收通过，当前本地验收结论依据上述逐项证据。
