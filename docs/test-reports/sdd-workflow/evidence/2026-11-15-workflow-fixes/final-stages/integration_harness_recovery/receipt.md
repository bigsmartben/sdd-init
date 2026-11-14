已完成本轮集成测试，**Test Gate：FAIL**。

CI 入口 `python -B checks/integration_runner.py` 已修复并连续复跑两次，结果一致：**19 通过、8 失败、1 阻塞**，退出码均为 1，表示验收未通过。

失败归入 3 个产品缺陷：取消状态被提交覆盖、支付参数校验缺失、整数 ID 误操作字符串订单。外部回执因缺少端点、调用授权及网络许可而阻塞。

- [复跑指南](specs/order/quickstart.md)
- [完整报告与 Test Gate](docs/test-reports/order/2026-11-15-integration.md)
- [两次运行原始证据](docs/test-reports/order/evidence/ci-reruns.json)

仅修改测试工具和文档；产品实现及环境配置未改，未联网、未提交。