# 订单修复、集成与架构取证状态

## 当前授权与进展

用户已明确范围、公开路径和判据沿用 [订单 Spec](../specs/order/spec.md) 与 [契约](contracts/order.md)。仅在当前隔离项目使用本地 Python 和文件 SQLite；产品修改限取消后仍提交缺陷。允许本地指南、报告和 Issue 写入，无 Git、外部平台或真实部署授权。

| 阶段 | 实际调用链 | 状态与证据 |
| --- | --- | --- |
| 指定缺陷修复 | Main → /root/bugfix | [BUG-001](issues/BUG-001.md) 已修复并经独立定向复验关闭；[Plan](issues/BUG-001-plan.md)、[证据](test-reports/order/bugfix-001.md) |
| 修复候选集成 | Main → /root/integration | 已实测；AC-1/2 PASS，I05 FAIL，AC-3 BLOCKED；[报告](test-reports/order/integration.md)、[复跑指南](../specs/order/quickstart.md) |
| 相关架构检查 | Main → /root/review | 仅取证；UI 绕过服务写入偏差保留；[Review](test-reports/order/architecture-review.md) |

实际候选为 `sha256:7d4083da88ed6593bc2039b890b0026681f522ac7b53d7aa8c8dcde4cb269fea`，覆盖 src、checks 和 runtime.json，见 [manifest](test-reports/order/bugfix-candidate.json)。集成与架构检查均核验该候选及执行前后文件一致性；没有 Git 操作，版本由文件哈希识别。

## 决定与恢复条件

- 外部端点及权限缺失：AC-3 保留阻塞；恢复需提供获授权真实外部测试服务端点、必要凭据、明确调用及网络授权，并具备真实外部验证执行入口。现有 AC-3 脚本固定返回 BLOCKED，仅补配置无法恢复；不能以本地结果代替。
- [BUG-002](issues/BUG-002.md)：mark_paid 对不存在订单不抛约定 ValueError，保留 Pending；恢复需另行授权此独立契约缺陷修复，再按 I05 复验及回归现存订单 paid 行为。
- Review CHK-001：UI 直接 SQL 绕过服务状态入口，保留未整改；恢复需另行授权架构整改并完成职责与行为复核。
- Review CHK-005/006：项目规则对取消语义、测试初始化及清理的映射待查；恢复需用户决定是否及何时维护规则、明确维护范围，再复核原检查项。未修改项目规则。
- 本轮无新增需求或架构决定；既有确认沿用。阶段新增实质待决内容由 Main 集中回报。

## 门禁

- Test Gate：FAIL；独立契约缺陷 I05，另有 AC-3 BLOCKED。逐项证据见集成报告。
- Review Gate：FAIL；CHK-001 服务边界偏差，另有规则映射待查。逐项证据见 Review。

本轮授权内可执行项目已完成，独立缺陷、架构偏差及外部缺口按上述条件接续。人工视觉和体验反馈不适用；没有执行外部调用、真实部署或修改共享工作流。逐项事实保留在原 Issue 和专用报告。

Main 已核对三阶段最终回执、候选标识、判据及恢复条件；对本轮 9 份修改及直接受影响 Markdown 执行文档 CLI 检查，0 errors、0 warnings。机械检查只证明链接、编号和结构等受支持项，功能及门禁结论来自对应执行证据。
