已完成本地 `production-sim` 发布：

- 2.4.0 canary 已就绪，运维冒烟通过。
- `/checkout` 已切至 10%；60 个模拟秒、1000 次请求中，canary 命中 100 次，零错误。
- 部署超时后读回确认已生效，未重复部署。全程未访问真实服务或外网。

证据缺口：缺少 `ops/data.json`，持久数据与投影检查未完成。

[正式回执](docs/delivery/2.4.0.md) · [操作证据](ops/calls.jsonl)