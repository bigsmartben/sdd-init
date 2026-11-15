# Issue — ORDER-001 取消订单被提交覆盖

## 1. 问题事实

- 编号与类型：ORDER-001；实测行为偏差（未开展修复归因）。
- 依据：[AC-2](../../specs/order/spec.md)；本轮 C02。
- 发现：2026-11-14，独立测试技能 Agent；版本 `6d5e6b6737cc61d38206817f58876c7f65473a21`，isolated-local-fixture。
- 复现：项目根目录运行 `python -B checks/acceptance.py --scenario AC-2`。新建 ORDER-1，取消，再提交并重开文件数据库。
- 预期：返回 false，重开状态仍 cancelled。
- 实际：返回 true，重开状态 submitted。
- 影响：取消不可被提交覆盖的业务规则失效，阻止本轮通过。
- 取证：[本轮报告](../test-reports/order/20261114.md)，[用户复跑指南](../../specs/order/quickstart.md)。

## 2. 当前状态

- 负责人：未分配。
- Fix Task：无；本轮只测试，不启动修复。
- 状态：Pending（待处理）。
- 接续条件：Main 获取后续修复授权与实际修复版本后，沿用原判据复验，并执行本地必要回归。当前不关闭 Issue。

## 3. 处理与复验历史

| 时间／执行者 | 动作与结果 | 修复版本／Task | 证据与状态 |
| --- | --- | --- | --- |
| 2026-11-14／测试技能 Agent | 实测发现并登记原始偏差 | 无 | [报告 C02](../test-reports/order/20261114.md)，Pending；未修复未复验 |

## 4. 相关引用

[Spec](../../specs/order/spec.md)、[契约](../contracts/order.md)、[报告](../test-reports/order/20261114.md)。未创建外部平台 Issue。
