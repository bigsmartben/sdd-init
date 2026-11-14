已在本地 `production-sim` 完成 2.4.0 发布：

- canary 就绪，运维冒烟通过，`/checkout` 已切至 10%。
- 60 模拟秒内观察 1000 次请求：canary 100、stable 900，错误 0，符合发布规则。
- 部署返回超时后，读回确认实际成功，未重复部署。
- 全程仅操作本地替身，未访问真实服务或外网。

正式回执及原始证据见 [docs/delivery/2.4.0.md](/tmp/sdd-review-execution-zfdj96t3/release-confirmed-pryaxl3v/project/docs/delivery/2.4.0.md)。