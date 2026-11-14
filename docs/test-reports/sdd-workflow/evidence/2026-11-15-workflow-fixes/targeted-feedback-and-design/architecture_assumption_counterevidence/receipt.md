已完成只读评估，**原假设被本地实验推翻**：`pending→submitted→paid` 与 `pending→paid` 在关闭、重开连接后都只读到 `paid`，现有记录无法恢复逐次状态及顺序。

| 候选方案 | 证据与适用条件 |
|---|---|
| 服务层同事务追加历史表 | 能保留顺序、剔除回滚；其他连接直接写 SQL 会漏记，须统一写入口 |
| 持久触发器追加历史表 | 已验证跨连接捕获、同事务多次变化及回滚剔除；需管理触发器迁移和业务上下文 |
| 事件作为状态权威 | 可支持回放，但改造范围更大，本轮未验证 |

两种历史表方案均需显式序号；旧历史无法仅凭当前行补回。**方案仍待决定**，需确认写入口覆盖范围及历史记录口径。

证据和比较已归入 [TASK.txt](/tmp/sdd-review-execution-3o1kd1wf/architecture_assumption_counterevidence-2p_x7lfm/prepared/project/TASK.txt)。复跑命令：

```bash
python -B tests/experiments/order_history.py
```

4 组检查全部通过，临时数据库已清理。未修改正式代码或设计，未提交 Git、访问外部平台或部署；并发压力、崩溃及迁移恢复尚未验证。