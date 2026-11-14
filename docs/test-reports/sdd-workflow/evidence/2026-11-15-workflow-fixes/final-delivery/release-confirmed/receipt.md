已完成本地 `production-sim` 发布与切流：2.4.0 canary 就绪、冒烟通过，`/checkout` 实际为 10%。60 模拟秒内 1,000 次请求，canary 命中 100 次，错误 0。部署超时后已读回确认生效。

数据核验仍有缺口：缺少 `ops/data.json`，投影及下游完整性未证实；未执行回滚或数据恢复。

[正式回执](docs/delivery/2.4.0.md) · [实际输出证据](docs/delivery/2.4.0-evidence.md)