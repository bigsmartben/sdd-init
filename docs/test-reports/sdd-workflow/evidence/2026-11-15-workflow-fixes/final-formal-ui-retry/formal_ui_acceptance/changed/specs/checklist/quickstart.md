# Quickstart — Checklist 正式页面集成验收

## 1. 验收目标与范围

依据 [Spec](spec.md) 的 AC-1 至 AC-4，验证空输入反馈、名称 trim、两项独立勾选和取消勾选。范围、目标版本、隔离环境和主要用户路径沿用本轮启动指令的明确确认。

仅验收正式页面；[已确认原型](../../tests/prototypes/checklist/personal/index.html) 是交互参考，不替代正式候选证据。无像素比对或新增性能判据。

## 2. 环境与启动

- 目标提交：`97c2da655a5584d27a2a4a6051db147ab75b6fba`。在当前隔离项目执行 `git rev-parse HEAD`、`git status --short` 和 `sha256sum src/index.html`，核对实际版本及未提交实现变化。
- 正式文件：`src/index.html`，本轮准备时 SHA-256 为 `c1e4df9bb0a2620cf1a24fd11f41c603bea5aef361a39511ed41cf105046327a`。
- 环境入口由 [浏览器说明](../../docs/browser.md) 的隔离 fixture 提供：loopback HTTP `/src/index.html`，Chromium，正式页面以 localStorage 保存条目；不需要账号或外部服务。
- 自动复跑入口：调用 `mcp__local_browser_fixture__run_formal_check`，参数 `{}`，保留完整回执中的真实 URL、浏览器信息、HTML digest、逐项观察和存储结果。将 HTTP HTML digest 与本地正式文件 SHA-256 对比。
- 人工复跑时访问该回执给出的正式 HTTP URL。仅在隔离浏览器中清除 `checklist` localStorage 键后刷新，确认列表为空。不要清除其他环境的数据。
- 常规数据从 Spec 推导：空字符串、三个空格、`  Pack bag  `、`Book hotel`。两个有效输入构成同一组合场景，不因某条断言失败而跳过其余可执行场景。

## 3. 场景验收

| 场景 / 判据 | 前置条件 | 操作 | 预期和观察点 | 所需证据 |
| --- | --- | --- | --- | --- |
| C-1 / AC-1 | 空列表 | 保持输入为空，点击 Add；再输入三个空格，点击 Add | 两次均显示页内 alert，列表始终为零项 | 两次 alert 可见性、文本、项数 |
| C-2 / AC-2 | C-1 后 | 输入 `  Pack bag  `，点击 Add | 行文本严格等于 `Pack bag`；localStorage 中 name 严格等于 `Pack bag` | DOM 原始文本及 localStorage JSON，不能仅凭视觉空白判断 |
| C-3 / AC-3 | 已有第一项 | 输入 `Book hotel`，点击 Add；观察两项，再勾选第一项 | 新增后 `[false,false]`；勾选后 `[true,false]` | 两次 checkbox 状态及条目数 |
| C-4 / AC-4 | 两项且第一项已勾选 | 勾选第二项；取消第一项；取消第二项 | 依次 `[true,true]`、`[false,true]`、`[false,false]`；取消操作不影响另一项 | 每个中间状态及最终状态 |

以上均为可客观自动观察的交互与存储判据，没有必须由用户主观判断的项目。人工执行可按相同步骤反馈，人工反馈与自动结果分开记录。

## 4. 失败与复位

失败保留预期与实际差异，继续其余就绪场景，不改变产品实现或测试工具。复跑前再次核对提交及 HTML digest，并在隔离正式页面清除 `checklist` 键、刷新回到空列表。失败后的修复和版本切换不在本轮授权内；修复后应在明确版本重跑原失败及全部四项回归。

## 5. 结果入口

实际执行结果与 Test Gate 记录于 [本轮正式集成报告](../../docs/test-reports/checklist/formal-ui-acceptance.md)。索引与 Status 依用户写入限制保持不变。
