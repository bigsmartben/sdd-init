已修复取消后仍提交：现在返回 `False`、不写入数据库，重开后仍为 `cancelled`。6 项单测及独立复验通过，[BUG-001 已关闭](docs/issues/BUG-001.md)。

- [集成测试](docs/test-reports/order-integration/report.md)：17 项中 15 通过、1 失败、1 阻塞，Test Gate **FAIL**。新发现 `mark_paid` 对不存在订单未抛异常；外部回执缺端点和权限。
- [架构检查](docs/reviews/order-candidate-review.md)：3 项通过、1 项失败，Review Gate **FAIL**，原因是既有 UI 直接写库偏差。

其余问题仅登记，恢复条件已写入[进度记录](docs/status.md)。未执行 Git、外部平台操作或部署。