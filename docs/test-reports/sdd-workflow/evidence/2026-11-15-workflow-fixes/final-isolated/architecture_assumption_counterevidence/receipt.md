评估完成，**原假设不成立**。

实测两条路径 `pending→submitted→paid→cancelled` 与 `pending→submitted→cancelled`，关闭重连后得到完全相同的订单记录，仅剩 `cancelled`，无法恢复中间状态及顺序。

| 候选 | 证据与取舍 |
|---|---|
| 服务同事务追加历史表 | 已验证有序恢复与回滚一致性；但现有 UI 直接写库会漏记，须统一写入口 |
| 数据库触发器追加历史表 | 已验证捕获现有直接写入；需明确数据库记录职责及异常后的事务清理 |

倾向服务同事务方案，前提是覆盖所有写入口。两者都只能保证启用后的历史，无法补回既往被覆盖的信息。

34 项实验断言通过，文档检查零错误、零警告；未验证并发或断电恢复。设计保持待决，正式代码与架构文档未修改，临时数据库已清理。

[评估与证据记录](docs/tasks/sqlite-history-assessment.md) · [可重跑实验](tests/experiments/sqlite_history_assessment.py)