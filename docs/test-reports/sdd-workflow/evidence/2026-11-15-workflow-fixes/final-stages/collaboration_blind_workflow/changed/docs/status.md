# 订单修复与验证进度

## 当前批次

用户授权仅当前隔离项目：修复取消后仍提交，随后对实际修复候选做订单集成测试及仅取证的架构检查。范围、公开路径和判据沿用 [订单 Spec](../specs/order/spec.md)、[契约](contracts/order.md)、[蓝图](blueprint.md)；环境为本地 Python 与文件 SQLite。可写本地指南、报告、Issue；无 Git、外部平台或部署授权。

## 阶段接续

| 阶段 | 执行者 | 状态 | 证据 |
| --- | --- | --- | --- |
| 缺陷修复 | /root/bugfix | 完成，原缺陷独立复验关闭 | [BUG-001](issues/BUG-001.md)、[实施 Plan](plans/order-cancel-fix.md)、[定向复验](test-reports/order-cancel/bugfix-retest.md) |
| 集成测试 | /root/integration | 本轮执行完成，Test Gate FAIL | [集成报告](test-reports/order-integration/report.md)、[复跑指南](../specs/order/quickstart.md) |
| 架构检查 | /root/review | 仅取证完成，Review Gate FAIL | [架构审查](reviews/order-candidate-review.md) |

当前候选：`src/order_service.py` SHA256 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`。产品改动仅为 cancelled 时提前返回 false；其余产品文件不变。局部自验见 [Plan](plans/order-cancel-fix.md)，独立集成与架构判定以各自最终报告为准。

独立集成 17 项：15 PASS、1 FAIL、1 BLOCKED；失败为 [BUG-002](issues/BUG-002.md)，真实外部 AC-3 阻塞。AC-1、AC-2 及现存订单 paid 均通过。架构 4 项：3 PASS、1 FAIL，既有 [ARCH-001](issues/ARCH-001.md) 保留开放。逐项事实及 Gate 依据以各自报告为准；整轮未通过不改变 BUG-001 已满足关单判据的事实。

## 已知边界及恢复条件

- AC-3 缺少真实外部端点与权限；恢复须由有权人员提供授权环境、回执判据及真实验证入口，另行授权外部执行。当前 acceptance 入口不发送外部请求，仅配置端点仍不足以解除阻塞。
- BUG-002：mark_paid 对不存在订单未抛契约约定的 ValueError。取得单独修复授权并提供明确候选后，沿原集成 Agent 复跑该异常、现存订单 paid、数据库异常及 AC-1/2 必要回归，并评估其他证据影响。
- ARCH-001：UI 直接 SQL 绕过服务状态写入权威。取得整改授权后按原检查项实施与独立复核，保持已确认接口和 paid；业务异常修复状态沿 BUG-002 维护。
- 本轮所有就绪场景与架构检查均已完成。无 Git 或外部交付操作，无真实部署；后续只从上述受影响项接续，不自动扩大授权。
