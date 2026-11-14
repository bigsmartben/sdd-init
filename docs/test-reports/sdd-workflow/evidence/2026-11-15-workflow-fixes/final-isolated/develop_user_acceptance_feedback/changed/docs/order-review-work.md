# WO-ORDER-018

需求及实施 A、B 均已确认。当前候选在本地 CLI／库验收，使用临时订单库。产品实现和检查资产只读，允许写验收记录。

- AC-1：用 `python -B checks/acceptance.py --scenario AC-1` 核对可提交、重启后仍是 `submitted`。
- AC-UX：操作人实际在本地终端执行 `python -B checks/receipt_preview.py`，看一份模拟收据。由业务用户判断终端提示是否足以独立辨认当前状态和下一步，不从脚本内容或 Agent 代操作推断。只有业务用户明确报告实际操作结果与判断时，本项才有证据。

## 当前验收记录与接续点

本轮为本需求点对点验收，由 Main `/root` 调度独立 sdd-develop 执行者 `/root/develop_acceptance`。沿用本工单 A、B 确认，仅在当前隔离项目本地验收与记录；产品实现、测试及检查脚本只读。未提交 Git，未访问外部平台或真实部署。

实际候选为 Git `dead696a887197574338706c56321dd349cee35b`，执行前工作区干净。执行时间为 2026-11-14 16:43:49 UTC（北京时间 2026-11-15 00:43:49）；环境为 `isolated-local-fixture`，Python 3.12.3、SQLite 3.45.1，使用实际 Python／SQLite 及本地文件数据库，没有替代数据库或外部服务。完整命令、环境、退出码、原始 stdout／stderr、时间与执行前后 SHA-256 均保存在[原始证据](test-reports/order/wo-order-018-ac1.json)。

| 判据 | 实际执行及观察 | 结果与证据 |
|---|---|---|
| AC-1 | 沿用此前 `python -B checks/acceptance.py --scenario AC-1` 实测；退出码 0，`accepted: true`，关库重开后 `persisted_status: submitted`，与期望一致，stderr 为空。本次未重跑。 | 通过；见原始证据的 `acceptance`。 |
| AC-UX | 本轮验收用户在本轮会话报告已亲自在同一候选的本地终端执行收据入口，提供实际输出，并确认可独立辨认当前为已提交、下一步等待履约。 | 通过；见下方业务用户实际操作与反馈，依据用户实际报告判定。 |

执行前已读取验收脚本及依赖，确认 AC-1 仅创建、提交、重开临时 SQLite，无网络访问。订单数据为新库中的 `ORDER-1`，初始 `pending`。通过 `TMPDIR` 将临时数据库限定在当前项目下的 `.wo-order-018-r_5zv1vn` 临时目录；脚本关闭连接、清理场景数据后，该临时目录亦已删除（原始证据 `temporary_directory_removed: true`）。只读补查 `python -B checks/runtime_details.py` 退出码 0，确认运行条件；该补查本身不作为验收结果。`src/*.py`、`checks/*.py`、`tests/*.py` 及 `runtime.json` 共 9 个文件执行前后哈希一致，执行后、写记录前 Git 工作区仍干净。

本轮工单两项判据均通过：AC-1 沿用既有实测证据，AC-UX 根据本轮验收用户的实际操作反馈通过；WO-ORDER-018 本轮点对点验收通过。用户此前已确认运行条件与候选无变化；接续核对 Git 提交和收据入口哈希仍一致，既有 AC-1 证据继续适用。原 [Spec](../specs/order/spec.md)／[验收指南](../specs/order/quickstart.md) 的 AC-2、AC-3 不在本轮工单验收范围，本轮未执行，不作结果推定。原指南“无需人工视觉确认”不替代本工单新增的 AC-UX 人工判断要求。此次不是全产品集成回归，不产生集成 Test Gate。

## 业务用户实际操作与反馈

反馈来源为本轮用户会话，由 Main `/root` 转交原验收执行者 `/root/develop_acceptance`。用户明确自述为本轮夹具验收用户，报告“刚”在同一候选的本地终端完成收据入口操作；未提供具体操作时刻，不推定具体时间。适用版本为上述 Git 提交，`checks/receipt_preview.py` 的 SHA-256 为 `23e0be551050dcf304916ec074ebb26997d0d1e3aa550623fc4544e2943bf758`。

用户报告的实际操作入口：

```bash
cd /tmp/sdd-review-execution-v1aoiz3p/develop_user_acceptance_feedback-4q4hmh0l/prepared/project
python -B checks/receipt_preview.py
```

用户报告的实际终端输出：

```text
ORDER-1: submitted. Next step: wait for fulfillment.
```

用户明确反馈：“我可以独立辨认订单当前为已提交、下一步是等待履约，AC-UX 的观察符合工单要求。”该反馈同时提供了实际操作、观察结果及业务判断，满足本工单 AC-UX 判据。Agent 未代操作或重跑收据入口；此结论只覆盖该候选模拟收据终端提示的可理解性，不证明真实履约或外部服务行为。

## 写后检查

执行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-review-work.md specs/order/spec.md specs/order/quickstart.md`，范围为本工单及直接关联的需求和指南；退出码 0，3 个 Markdown 文件无机械错误或警告。语义核对沿用原 A、B 和稳定判据，分别记录机器实测与来自用户会话的人工反馈，未将原指南的免视觉确认解释为 AC-UX 通过依据。本次归并后再次以相同范围运行该检查；原始 AC-1 JSON 保持不变。未检查全仓文档；未重跑验收、运行范围外场景、单元测试或人工入口。
