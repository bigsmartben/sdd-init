集成测试已完成，**Test Gate：FAIL**。25 个场景：22 通过、2 失败、1 阻塞。

- 失败：取消后提交覆盖了 `cancelled` 状态；不存在订单的支付操作未抛出 `ValueError`。
- 阻塞：外部回执缺少端点和授权，本轮未联网。
- CI 入口拼写错误已修复；`python -B checks/integration_runner.py` 已验证可重复运行，当前退出码 `1` 如实反映产品失败。

已交付[复跑指南](specs/order/quickstart.md)和[测试报告及证据](docs/test-reports/order/integration-2026-11-15.md)。产品源码未修改，未执行 Git 写操作或部署。