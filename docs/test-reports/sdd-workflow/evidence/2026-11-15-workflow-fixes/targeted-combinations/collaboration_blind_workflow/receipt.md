已修复取消后仍提交：现在返回 false，文件 SQLite 保持 cancelled；AC-1、AC-2 均通过，BUG-001 已关闭。

同一修复候选的检查结果：

- **集成 Test Gate：FAIL**。9 场景中 7 通过、1 失败、1 阻塞。另发现 BUG-002：mark_paid 对不存在订单未抛 ValueError，仅登记。
- **架构 Review Gate：FAIL**。UI 直接写数据库违反服务边界，仅取证。
- **AC-3：BLOCKED**。缺少获授权端点、权限、网络及真实验证入口。

报告、复跑指南和恢复条件见 [本轮状态](docs/status.md)。未执行 Git 操作、外部调用或部署。