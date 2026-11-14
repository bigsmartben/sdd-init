两个阶段均已完成。

- 付款适配已改为调用既有 `set_status`，公开行为保持，局部验证 4/4 通过；架构检查 CHK-001～004 全部通过。
- **Review Gate：UNVERIFIED**，仍有三项项目规则映射待补。详见[审查记录](docs/test-reports/order/mark-paid-review.md)和[Plan／Task](specs/order/refactor-plan.md)。
- 全产品集成共 13 场景：**11 通过、1 失败、1 阻塞；Test Gate：FAIL**。详见[集成报告](docs/test-reports/order/integration-20261115.md)与[复跑指南](specs/order/quickstart.md)。

剩余条件：按 [ISSUE-001](docs/issues/ISSUE-001.md)另行修复取消后仍可提交的 AC-2 缺陷；AC-3 待授权外部端点和调用权限。本轮未修改付款范围外代码，未执行外部调用、部署或 Git 写操作。