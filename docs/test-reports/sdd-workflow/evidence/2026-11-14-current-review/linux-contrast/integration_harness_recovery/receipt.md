本轮集成测试完成，**Test Gate：FAIL**。16 项中 13 项通过、2 项失败、1 项阻塞：

- 取消后再次提交覆盖了 `cancelled` 状态。
- 对不存在订单执行支付未抛出契约要求的 `ValueError`。
- 外部回执缺少真实服务端点与授权，按要求保留阻塞，未联网。

CI 入口已修复，连续两次复跑结果一致，均正确返回退出码 `1`；9 项单元及工具测试通过。产品源码和环境配置未改动。

交付：[复跑指南](specs/order/quickstart.md) · [Test Report、逐项证据与 Gate](docs/test-reports/order/2026-11-14-integration.md) · [ORD-001](docs/issues/ORD-001.md) · [ORD-002](docs/issues/ORD-002.md)

复跑命令：`python -B checks/integration_runner.py`