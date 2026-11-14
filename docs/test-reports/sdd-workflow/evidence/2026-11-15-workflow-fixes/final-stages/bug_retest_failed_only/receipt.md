ISS-001 已完成实际复验：

- **取消后提交：失败**。返回 `true`，重开数据库为 `submitted`；原判据要求 `false`、`cancelled`。
- **正常提交：通过**。返回 `true`，重开数据库为 `submitted`。

结果及证据已记录到 [ISS-001](docs/issues/ISS-001.md)，缺陷保持未关闭。本轮仅在隔离项目操作，未修改实现或测试，未访问外部服务。