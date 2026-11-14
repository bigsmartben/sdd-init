# Issue — ISSUE-001 新增条目存储名称未去两侧空格

## 1. 问题事实

- ID：ISSUE-001；类型：实现行为缺陷（正式浏览器已观察到判据不符，尚未做修复归因）。
- 依据：[Checklist Spec AC-2](../../specs/checklist/spec.md)，提交 `  Pack bag  ` 后显示与存储均应为 `Pack bag`。
- 首次发现：2026-11-15 01:08 +08:00，独立 sdd-test-loop 执行者 `/root/test_loop`；提交 `97c2da655a5584d27a2a4a6051db147ab75b6fba`；Chromium `149.0.7827.55`；[发现报告 C-2](../test-reports/checklist/formal-ui-acceptance.md#6-逐项结果)。
- 环境入口：`http://127.0.0.1:45393/src/index.html`，隔离 loopback HTTP 正式页面。正式 HTML SHA-256：`c1e4df9bb0a2620cf1a24fd11f41c603bea5aef361a39511ed41cf105046327a`。
- 复现：在隔离正式页面空列表输入 `  Pack bag  `，点击 Add；读取新增 DOM label 文本及 localStorage 的条目 name。预期 name 为 `Pack bag`，实际工具返回 `label:"  Pack bag  "`、`stored:"  Pack bag  "`。DOM 文本保留空格不等于肉眼必然能看到边缘空白；存储未 trim 已直接违反判据。
- 影响：带两侧空格的有效名称持久化不规范，AC-2 失败，当前候选 Test Gate FAIL。AC-1、AC-3、AC-4 在同批次通过；不推断其他业务影响或根因。

## 2. 当前状态与接续条件

- 负责人：Unassigned，由 Main 承接后续阶段安排。
- Fix Task：尚无；本轮仅验收与登记，不授权修复。
- 状态：Pending。
- 恢复条件：后续授权修复并交付明确版本、正式 HTTP 入口与 HTML digest 后，在正式页面复验原输入及全部四项回归。没有已完成修复或关单依据。
- 点对点验收步骤沿用 [Quickstart C-2](../../specs/checklist/quickstart.md#3-场景验收)；须证明 DOM 的规范名称与 localStorage name 都为 `Pack bag`，并保留 AC-1 空白拦截、AC-3/AC-4 状态独立。当前四项无需必需人工主观反馈，后续自动与人工结果仍应分列。

## 3. 处理与复验历史

| 时间 / 执行者 | 操作与结果 | 修复版本 / Task / 局部证据 | 复验报告或用例与版本 | 状态变化与依据 |
| --- | --- | --- | --- | --- |
| 2026-11-15 01:08 +08:00 / `/root/test_loop` | 正式 HTTP Chromium 检查发现存储未 trim；继续其余三项并均通过；登记问题 | 无修复；未创建实施 Task | [原始浏览器证据](../test-reports/checklist/formal-ui-acceptance.md#61-原始正式浏览器证据)，原始版本同第 1 节 | 新建 Pending；C-2 Fail，无关单证据 |

## 4. 相关引用

- [正式验收报告与 Gate](../test-reports/checklist/formal-ui-acceptance.md)
- [可复跑指南](../../specs/checklist/quickstart.md)
- [确认判据](../../specs/checklist/spec.md)

无外部平台 Issue；未修改索引、Status、实现或测试资产。
