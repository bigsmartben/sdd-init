# 订单验收指南

依据：[Spec](spec.md) AC-1、AC-2、AC-3、AC-4。执行者在生成的隔离项目目录操作，使用 Python 3.11+ 与标准库 SQLite；无需安装依赖。每个本地场景使用新临时目录中的 SQLite 文件；AC-1、AC-2 使用订单 `ORDER-1`，AC-4 数据见下表。执行后关闭连接并删除该临时目录。无需人工视觉确认。

| 场景 | 操作 | 判断点 |
|---|---|---|
| AC-1 | `python -B checks/acceptance.py --scenario AC-1` | 提交返回 true，重开数据库后状态 submitted。 |
| AC-2 | `python -B checks/acceptance.py --scenario AC-2` | 取消后提交返回 false，重开数据库后状态 cancelled。 |
| AC-3 | `python -B checks/acceptance.py --scenario AC-3` | 检查 runtime.json 的端点和授权；未就绪时返回 BLOCKED，不访问网络。 |
| AC-4 | `python -B checks/acceptance.py --scenario AC-4` | 依次提交空串、全空格、制表符及制表符/换行混合空白；均抛出 ValueError，当前及重开连接无订单。随后提交普通合法编号与两端含空白的合法编号，重开连接后编号原样保存且状态 pending。 |

`python -B checks/acceptance.py` 执行全部场景并逐项输出 JSON。退出码为 0（全部通过）、1（存在失败）或 3（无失败但存在阻塞）。局部单元测试入口为 `python -B -m unittest discover -s tests -v`，不能替代上表验收。

运行条件证据可以使用 `python -B checks/runtime_details.py` 只读补查。该入口输出实际 Python、SQLite 版本、配置事实与源文件哈希，不推定未运行场景的结果。AC-3 恢复条件是由有权人员提供已授权测试服务端点和调用权限；本轮不得自行配置外部服务或获取凭据。
