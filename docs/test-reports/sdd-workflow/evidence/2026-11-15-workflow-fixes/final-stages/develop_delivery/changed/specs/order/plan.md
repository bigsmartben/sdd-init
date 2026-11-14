# 订单号校验 Plan／当前任务

当前已取得 A 与 B 确认，T001 实施、局部自验及本轮隔离点对点验收完成。实际调用者与回执接收方为 Main `/root`；本阶段 Agent 为 `/root/order_develop`。

## 目标与依据

- 原始目标保留于项目根目录 [TASK.txt](../../TASK.txt)，已确认需求及 A 确认来源见 [Spec](spec.md#本轮确认与接续)。
- 交付目标为拒绝空串及全空白订单号，保持合法订单号原样创建和其他订单操作行为。范围为 Spec AC-4、AC-5、AC-6，保持行为核验 AC-1 及 paid 持久化；适用[订单契约](../../docs/contracts/order.md)与[蓝图](../../docs/blueprint.md) ARC-1～ARC-4。
- 调查时 `src/order_service.py:create_order` 仅排除非字符串和空串；合法输入直接 INSERT 并 commit。无需数据迁移、额外依赖或接口变化。
- 2026-11-15，实施执行者 `/root/order_develop/order_plan`（sdd-coder）完成只读调查并提出方案。随后用户经 Main 明确 B：「确认 B。按刚才的范围、用户流程和已确认的就绪条件开始实施，并完成本轮隔离验收。」原执行者接续 T001，授权范围不含 Git 写操作、外部平台及部署。

## 验收计划与方案

验收项、环境、数据、复位、公开调用入口、操作和判据见[点对点验收指南](quickstart.md#订单号校验点对点验收)。B 确认且实现就绪后，实施者先完成局部自验，sdd-develop 技能 Agent 接收实现回执后逐 AC 验收，可复用适用于实际版本的证据并补验公开入口及持久化缺项。无人工操作判据；不进行外部核验或全产品集成回归。

## Task

### T001: 拒绝全空白订单号并保持合法编号原值

- **依据**：Spec AC-4、AC-5、AC-6，及上述保持行为与验收方案。
- **改动范围**：产品仅 `src/order_service.py` 的 `create_order`；测试仅 `tests/test_order.py`；实际回执和证据原位更新本 Plan。`checks/acceptance.py`、其他订单操作及运行配置无需改动。
- **实际实现**：保留 `not isinstance(order_id, str)` 的短路判断，将空值判断改为 `not order_id.strip()`。`strip()` 只用于判定，SQL 继续使用原始 `order_id`；在 INSERT／commit 前抛出原有 `ValueError("order_id is required")`，不新增订单或修改既有订单。
- **测试安排**：在现有测试文件增加定向覆盖。非法输入为 `''`、`' '`、`'\t'`、`'\n'`、`'\u3000'`、`' \t\n\u3000 '`，以及原有类型边界 `None`、`0`、`False`、`[]`；核对异常类型／消息、调用前后及重开后的订单集合。合法编号为 `ORDER-2`、` ORDER-3 `、`\tORDER-4\n`、`\u3000订单-5\u3000`；核对成功返回 None、pending、原值存储及重开可读。沿用普通提交和 paid 持久化测试及 AC-1 入口。
- **依赖**：无前置 Task。用户已确认方案并明确 B 交付实施授权，执行条件已满足。
- **完成条件与局部自验**：定向单测、既有单测、AC-1 及验收指南公开入口全部满足相应判据。记录实际版本或工作区源文件哈希、执行命令、原始输出与逐 AC 结果；不存在合法订单号被自动修剪的变化。
- **状态**：完成；实施、局部自验及 sdd-develop 技能 Agent 逐项验收通过。
- **结果与证据**：2026-11-15，执行者 `/root/order_develop/order_plan` 在当前隔离项目完成产品一行变更及两个定向测试；仅修改 `create_order` 校验和本 Task 指定测试。验证使用临时文件 SQLite，无新增依赖、外部访问或 Git 写操作。覆盖 AC-4、AC-5、AC-6，及 AC-1、paid 持久化保持行为；技能 Agent 的逐项验收见下文交付核对。
- **失败与复验**：先补测试，`python -B -m unittest discover -s tests -v` 首次退出 1（9 个失败，含同一测试数据库中错误接受全空白后导致后续断言连带失败）；把每个输入的基线快照移至对应 subTest 后重跑，退出 1，精确得到 5 个 `ValueError not raised`，分别为 `' '`、`'\t'`、`'\n'`、`'\u3000'`、`' \t\n\u3000 '`。其余测试通过。实施后同一命令退出 0，原始结果为：

```text
test_invalid_order_ids_leave_orders_unchanged (test_order.OrderTests.test_invalid_order_ids_leave_orders_unchanged) ... ok
test_mark_paid_is_persisted (test_order.OrderTests.test_mark_paid_is_persisted) ... ok
test_normal_submit (test_order.OrderTests.test_normal_submit) ... ok
test_valid_order_ids_are_persisted_without_trimming (test_order.OrderTests.test_valid_order_ids_are_persisted_without_trimming) ... ok

Ran 4 tests in 0.071s

OK
```

- **公开入口局部验证**：从已固化 quickstart 的订单号校验章节提取并原样执行 Python 验收代码（`python -B -`，通过标准库 subprocess 启动同一命令，退出 0）；每个输入独立临时文件数据库，原连接关闭后重开。完整输出：

```text
PASS invalid ''
PASS invalid ' '
PASS invalid '\t'
PASS invalid '\n'
PASS invalid '\u3000'
PASS invalid ' \t\n\u3000 '
PASS invalid None
PASS invalid 0
PASS invalid False
PASS invalid []
PASS valid 'ORDER-2'
PASS valid ' ORDER-3 '
PASS valid '\tORDER-4\n'
PASS valid '\u3000订单-5\u3000'
```

- **保持行为**：`python -B checks/acceptance.py --scenario AC-1` 退出 0，原始结果：

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

- **实际版本 SHA256**：`sha256sum src/*.py tests/test_order.py checks/acceptance.py` 输出：

```text
10a2558aaa2b9e1e596848196950162b8ea998f80f6d1b7086f8c6166fd8eded  src/__init__.py
22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b  src/order_service.py
6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9  src/storage.py
89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b  src/ui.py
6c9fc343234e191dd329ece02d1bf4c006e9b95517a2079b4c391452f8c78f6d  tests/test_order.py
3068c25ce6dee0b604c70f97e48b7ac9dc703ee44a2190c561972e4f65625eb9  checks/acceptance.py
```

## 交付核对与接续

2026-11-15，技能 Agent `/root/order_develop` 接收实施回执后，在当前隔离工作区执行[指南](quickstart.md#订单号校验点对点验收)全部 bash 代码块：用 `python -B -` 读取 Markdown 提取该块，经 `subprocess.run(['bash', '-e', '-c', block])` 原样运行。实际 Python 3.12.3、SQLite 3.45.1；全部命令退出 0。重新计算上述产品源文件、测试和验收入口 SHA256，与实施者版本一致。

| 验收项 | 实际结果与证据 | 结论 |
|---|---|---|
| AC-4 | 空串抛出原 ValueError 消息，调用前后及关闭重开后的订单集合一致；原始输出同上 `PASS invalid ''`。 | PASS |
| AC-5 | 五类全空白数据均拒绝，异常和无写入断言通过；原始输出与上列五项完全一致。 | PASS |
| AC-6 | 四类合法编号返回 None，原始编号及 pending 重开后保持；四项非字符串仍拒绝；原始 PASS 输出同上。 | PASS |
| AC-1 保持 | `python -B checks/acceptance.py --scenario AC-1` 输出与上列 JSON 一致，accepted 为 true，重开后 submitted。 | PASS |
| paid 与普通提交保持 | `python -B -m unittest discover -s tests -v` 四项测试全部 ok，`Ran 4 tests in 0.080s`，`OK`。 | PASS |

本轮已确认需求、约定实现、实际改动与逐项验收一致，T001 无待验项。集成入口为当前工作区的正式 `src` 模块和上述测试／验收命令；未创建提交或发布制品，不形成全产品 Test Gate 或架构 Review 结论。原始输出复用本记录上列相同内容，保留了本次命令、执行者、环境与版本对应关系。

文档机械检查：以给定共享 `sdd/scripts/doc_check.py --root .` 检查 `specs/order/spec.md`、`specs/order/quickstart.md`、本 Plan、`docs/contracts/order.md`、`docs/index.md`，结果为 5 files、0 errors、0 warnings。语义核对确认旧 AC 保留、A/B 授权与实际范围一致，无未解决的本轮需求或引用冲突。

已知范围外事项：静态读取发现 `submit_order` 无条件写入 submitted，与原 AC-2 的取消保护要求存在既有偏差；本轮未实测 AC-2，不修复、不改变其要求。AC-3 保留外部测试端点和调用权限缺口，本轮不运行外部核验。上述事项均不计为本轮通过，也不阻止已限定的订单号校验方案就绪。
