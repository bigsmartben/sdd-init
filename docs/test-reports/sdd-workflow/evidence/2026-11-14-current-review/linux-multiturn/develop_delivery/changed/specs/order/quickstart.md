# 订单验收指南

依据：[Spec](spec.md)。AC-1、AC-2、AC-3 操作如下，AC-4、AC-5 见[本轮订单号校验验收](#本轮订单号校验验收)。执行者在生成的隔离项目目录操作，使用 Python 3.11+ 与标准库 SQLite；无需安装依赖。运行前将 `TMPDIR` 设置为项目内可写临时目录或获授权 scratch 路径。本轮使用 `/tmp/sdd-review-execution-ykzxy2w_/develop_delivery-zwof9g4j/scratch`。现有每个本地场景使用新临时目录中的 SQLite 文件和订单 `ORDER-1`，执行后关闭连接并删除该临时目录。无需人工视觉确认。

| 场景 | 操作 | 判断点 |
|---|---|---|
| AC-1 | `python -B checks/acceptance.py --scenario AC-1` | 提交返回 true，重开数据库后状态 submitted。 |
| AC-2 | `python -B checks/acceptance.py --scenario AC-2` | 取消后提交返回 false，重开数据库后状态 cancelled。 |
| AC-3 | `python -B checks/acceptance.py --scenario AC-3` | 检查 runtime.json 的端点和授权；未就绪时返回 BLOCKED，不访问网络。 |

`python -B checks/acceptance.py` 执行全部场景并逐项输出 JSON。退出码为 0（全部通过）、1（存在失败）或 3（无失败但存在阻塞）。局部单元测试入口为 `python -B -m unittest discover -s tests -v`，不能替代上表验收。

运行条件证据可以使用 `python -B checks/runtime_details.py` 只读补查。该入口输出实际 Python、SQLite 版本、配置事实与源文件哈希，不推定未运行场景的结果。AC-3 恢复条件是由有权人员提供已授权测试服务端点和调用权限；本轮不得自行配置外部服务或获取凭据。

## 本轮订单号校验验收

范围为 [Spec](spec.md) AC-4、AC-5，以及直接受影响的 AC-1 和既有 mark_paid 行为。B 已确认，实施执行者已补充检查入口并局部自验，由本轮 sdd-develop 技能 Agent 逐项验收。实际版本、结果与原始证据见[本轮验收报告](../../docs/test-reports/order/validation.md)。

前提沿用上文 Python 与 SQLite 条件。每个输入使用独立临时目录中的文件数据库，通过 `storage.connect` 建库；先由公开服务创建基准订单 `BASELINE`，保存其状态和数据库全部行。通过 `order_service.create_order` 调用被验入口，观察异常或返回及数据库行；关闭并重开同一数据库后再比较持久化结果，最后关闭连接并清理临时目录。合法订单分支在第一次关闭前检查 pending，重开后再次检查。每个分支都必须有独立断言，不捕获异常后无条件判成功。

| 场景 | 输入与操作 | 通过判据 |
|---|---|---|
| AC-4 | 分别新建 `""`、`" "`、`"   "`、`"\t"`、`"\n"`、`" \t\r\n "`、`"\u3000"`、`"\u00a0"` | 每次均为 ValueError，消息 `order_id is required`；当前连接及重开后全部数据库行均与基准完全相同。 |
| AC-5 合法 | 分别新建 `"ORDER-1"`、`" ORDER-1 "`、`"\tORDER-1\n"` | 使用传入原值可读取 pending，当前连接及重开后恰好多出该原值的 pending 行，基准行未变；对于首尾含空白的输入，不存在裁剪后的替代行。 |
| AC-5 类型保持 | 分别传入 `None`、`0`、`False`、`[]`、`{}` | 同 AC-4 的异常和数据库不变判据。 |
| 直接回归 | 按原 AC-1 操作，另运行现有 mark_paid 单测 | AC-1 提交返回 true 且重开后 submitted；mark_paid 重开后 paid。 |

运行入口为 `python -B checks/acceptance.py --scenario AC-4` 和 `--scenario AC-5`，输出逐输入结果，任一检查不满足返回失败；全部场景默认入口包含新增编号，原 AC-1 至 AC-3 行为与退出码约定保持。点对点验收分别运行 AC-4、AC-5、AC-1；局部回归运行 `python -B -m unittest discover -s tests -v`。记录实际版本、命令、环境、逐输入结果与证据，并由同一[计划](plan.md)引用回执与验收报告。

AC-2 保留既有判据，实施角色运行默认入口时复现取消后提交的历史偏差，结果见本轮报告；不将其修复列为本轮完成条件。AC-3 的外部阻塞和恢复条件保持，当前不调用外部服务。本轮为需求点对点验收，不产出全产品集成 Test Gate。
