# Plan — ORDER-001 / ORDER-002 行为恢复

## 目标与依据

实际调用者、回执接收方 Main `/root`；执行者 Bugfix `/root/bugfix`。用户已授权修复本地现行缺陷，恢复 [ORDER-001](../issues/ORDER-001.md)、[ORDER-002](../issues/ORDER-002.md)；保持 [Spec](../../specs/order/spec.md)、[契约](../contracts/order.md) 和 [Blueprint](../blueprint.md) ARC-1～4。仅修改 src、必要 tests、原 Issue、此 Plan 与 bugfix 专属证据；不修改 checks、架构规则、外部配置，不执行 Git 写入或外部调用。

## 已验证归因

[修复前复现及实际源哈希](../test-reports/order/bugfix-diagnosis.json) 确认 AC-2 true/submitted、mark_paid 缺失对象无异常。直接路径证据：submit_order 已读取状态但丢弃结果，无条件 set_status(submitted)，因此取消被覆盖；ui.mark_paid 直接 UPDATE 并 commit，SQLite 对不存在记录 UPDATE 不抛异常，且绕过现有 read_status 存在检查。不存在对象的其他服务入口均 ValueError，排除数据库不存在表或共用服务存在检查失效。守卫取消状态、复用服务写入口可分别恢复预期；不涉及新的业务或架构决定。

## T001：恢复两项既定行为并定向复验

- 依据：原 Issue 验收计划及方案，Spec AC-1/AC-2、订单契约不存在对象与数据库异常要求。
- 修改范围：src/order_service.py、src/ui.py、tests/test_order.py。
- 实施：submit 在 read_status 为 cancelled 时直接返回 False，不 UPDATE、不 commit；其他现有路径保持。ui.mark_paid 调用现有 order_service.set_status(..., paid)，保留 paid 持久化并恢复 ValueError 和服务写入边界。
- 依赖：无。归因已验证，授权已具备。由具备实施能力的 Bugfix 承接此小批次，独立集成验收交 Main 接续原测试 Agent。
- 完成判据：公开 submit 的原 AC-2 返回 False、关闭重开仍 cancelled、SQLite trace 无写入且 commit 调用数为零；AC-1 保持 True/submitted。公开 mark_paid 对不存在对象 ValueError，pending/cancelled/submitted/paid 均持久化 paid。新建、取消、set_status、缺失对象及写入/commit 异常传播回归通过。
- 验证安排：修复后本执行者运行原 checks 对应局部场景及 unittest；新增真实文件 SQLite/trace 和 commit 故障连接检查。所有断言从公开入口观察；修复版本及原始结果留 bugfix 证据。全产品集成和架构复核由 Main 独立安排。
- 状态：Complete。
- 结果与证据：[定向报告](../test-reports/order/bugfix-verification.md)、[原始结果](../test-reports/order/bugfix-results.json)、[实际快照及 diff](../test-reports/order/bugfix-snapshot.json)。11 个本地定向场景和 6 个 unittest 全通过，原 Issue 的原场景及必要回归齐备。commit 代理仅证明异常传播机制；不是实际 SQLite commit 故障实测。

## 交付检查

本阶段终点是两项行为恢复及定向复验；整轮 Test Gate、AC-3 与独立架构审查不在本阶段判定。无新增待用户决定事项。
