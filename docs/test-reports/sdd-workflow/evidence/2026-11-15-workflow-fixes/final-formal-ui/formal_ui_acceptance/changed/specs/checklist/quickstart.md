# Quickstart — Checklist 正式 Web 集成验收

## 1. Verification Goal and Scope

依据 [Checklist Spec](spec.md) 验证全部 AC-1 至 AC-4：空白校验、去除首尾空格后展示并存储、两条待办独立勾选与取消。主要路径为进入正式页 → 添加 → 检查列表与存储 → 勾选 → 取消勾选。本轮范围、版本、隔离环境及主路径已由启动指令确认，沿用该确认。

仅验四项业务交互；纯视觉、像素比对、架构符合性、发布、跨浏览器和额外持久化需求不在范围。Spec 固定的原型只辅助理解和诊断，不能代替正式页证据。四项均是客观可观察判据，不需要额外主观人工判断。

## 2. Setup and Launch

- 目标版本：`eb0012894f193ac27f20548f016bdfdbc49985c7`；从当前隔离项目取得，不切换或修改版本。执行 `git rev-parse HEAD` 和 `git status --short`，记录实现有无未提交改动。
- 环境：`docs/browser.md` 指向的 loopback HTTP fixture；正式入口为 `http://127.0.0.1:45881/src/index.html`，端口以工具实际回执为准。使用隔离浏览器及正式页的浏览器本地存储，避免使用个人浏览器数据。
- 权限与依赖：项目提供 `local_browser_fixture.run_formal_check({})`，直接运行已就绪入口，不安装依赖、不部署、不改工具。返回 Chromium 版本、入口、HTML SHA-256 与逐 AC 结果；用 `sha256sum src/index.html` 对比摘要，证明正式运行文件。
- 数据：空串、三空格及 `  Pack bag  ` 直接由 Spec 边界推导；第二项可用 `Read book`，仅作为区分状态的常规数据，不引入新业务判据。
- 每次手工复跑应在独立测试上下文中清空该入口的 `localStorage` 键 `checklist` 后刷新。不要清理个人或其他入口数据。工具管理自己的测试上下文；返回值未暴露清理细节时不得声称已验证其清理实现。

## 3. Scenario Verification

| Feature / Scenario / AC | Preconditions | Action or command | Expected outcome and observation | Required evidence |
| --- | --- | --- | --- | --- |
| C-1 / AC-1 | 正式页空列表 | 分别输入空串、三空格，点击 Add | 页面内联 alert 可见，条目数仍为 0 | 两种输入的 alert 可见性与计数、版本、入口 |
| C-2 / AC-2 | 空列表；完成校验后继续添加以覆盖恢复 | 输入 `  Pack bag  `，点击 Add；查看条目标签及 `localStorage.getItem('checklist')` 的解析值 | 展示和存储的名称都精确等于 `Pack bag`，无首尾空格 | 实际 label 与 stored 值；无输出或工具错误时保留缺证 |
| C-3 / AC-3 | 两个区分明确的条目 | 添加 `Pack bag` 与 `Read book`；检查两个均未勾选；勾选第一个，检查第二个未变；再勾选第二个 | 两个初始均 false；操作一个不改变另一个；可同时为 true | 初始状态、中间独立状态、同时勾选状态 |
| C-4 / AC-4 | 两个均已勾选 | 取消第一个，检查第二个仍勾选；取消第二个 | 中间状态为 false/true，最终为 false/false | 中间状态及最终状态 |

自动复跑：调用 `local_browser_fixture.run_formal_check({})`，逐项保留实际结果而非只记录总退出状态。辅助诊断可调用 `run_prototype_check({})`，其结果单列为模拟原型证据。

## 4. Failures and Recovery

缺少预期 alert 是失败；若 checkbox 取得超时，保留 ERROR 原文，并将无法取得业务结果的用例记为 Blocked，不能把原型通过当作正式通过。继续能够执行的其他场景。取证恢复条件为正式页能创建可见条目，且工具可返回 AC-2 的标签与存储以及 AC-3/4 的状态证据。

缺陷仅登记，不修复产品。后续修复需由 Main 在授权阶段安排；修复后用实际新版本重跑原用例及全部四项回归。当前失败与恢复条件见 [Issue CHECKLIST-001](../../docs/issues/CHECKLIST-001.md)。本轮不含取消、重试等额外业务需求；复跑不变更验收判据。

## 5. Results and Progress References

本轮实际执行、版本核验、逐项证据、人工适用性与 Test Gate 见 [2026-11-15 正式验收报告](../../docs/test-reports/checklist/2026-11-15-formal-acceptance.md)。用户仅授权本指南、报告和必要 Issue 写入，因此未修改索引、Status 或 Plan；本指南与报告相互引用以提供访问入口。
