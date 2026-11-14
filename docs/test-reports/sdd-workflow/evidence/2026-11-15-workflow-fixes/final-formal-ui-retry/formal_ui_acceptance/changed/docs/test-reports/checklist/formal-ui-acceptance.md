# Test Report — Checklist 正式 UI 集成验收

## 1. 测试目标与依据

- 批次：formal-ui-acceptance；类型：范围内全功能集成验收；执行者：独立 sdd-test-loop 技能 Agent `/root/test_loop`，由 Main `/root` 调用；记录时间：2026-11-15 01:08:55 +08:00（2026-11-14 17:08:55 UTC）。
- 目标：核验当前隔离候选的四项已确认行为，不修产品、原型或测试工具。
- 依据：[Spec](../../../specs/checklist/spec.md)、[本轮 Quickstart](../../../specs/checklist/quickstart.md)、[环境说明](../../browser.md)。已确认原型仅作交互参考；本轮没有使用原型结果作为候选证明。

## 2. 范围与计划

范围是 AC-1 至 AC-4：空白校验、名称去两侧空格、两项独立勾选及取消勾选。启动指令已明确确认产品范围、目标 HEAD、隔离 HTTP 正式环境及主要用户路径；不需重复确认。用户授权终点为指南、报告、必要 Issue 和 Test Gate。

按 Quickstart C-1 → C-2 → C-3 → C-4 组织覆盖，从正式 HTTP 页面用户交互取证，并观察 DOM 和实际 localStorage。空字符串与三个空格为 AC-1 的两个边界数据；AC-2 有效项继续供后续两项组合测试使用。判据保持 Spec 原文语义。排除外部平台、真实部署、像素样式、非四项范围的持久化恢复需求和架构审查。完成条件是全部适用项均获得状态；Gate PASS 另要求全部满足原判据。

## 3. 测试环境

- 实际 Git commit：`97c2da655a5584d27a2a4a6051db147ab75b6fba`。
- 实测前工作树干净；指南准备后及实测后仅新增获准文档，`git diff -- src/index.html tests` 无输出。无相关未提交实现变更。
- 本地正式 HTML SHA-256 与 fixture 返回的受测 HTTP HTML SHA-256 均为 `c1e4df9bb0a2620cf1a24fd11f41c603bea5aef361a39511ed41cf105046327a`，提交、工作树文件与受测制品一致。
- 实际入口：[隔离正式页面](http://127.0.0.1:45393/src/index.html)，由 loopback fixture 提供；工具 `mcp__local_browser_fixture__run_formal_check`，参数 `{}`；Chromium `149.0.7827.55`。
- 真实装配：正式 HTML 的 form、alert、DOM 列表、checkbox 与浏览器 localStorage，真实 Chromium HTTP 访问。无外部服务或账号；未用原型、模拟浏览器状态或源码检查替代正式交互证据。
- 原型固定 digest 只读核对为 `d401df9dc918a0384b0df96152f3d240c3343eb4f307239cf963ce664f739e75`，与 Spec 相符；不计入本轮正式通过证据。

## 4. 准备与数据

Fixture 使用隔离正式浏览器状态。AC-1 两次提交后的列表数量均为 0，证明本轮初始数据未干扰空白场景；AC-2 实际输入为 `  Pack bag  `。Quickstart 为人工复跑指定第二项 `Book hotel`；工具仅返回两项勾选断言，没有返回第二项具体名称，故本报告不将该名称记作实际观察。两项数据与顺序由四项 AC 推导，未引入新业务规则。

复跑前按 Quickstart 在隔离正式页面清除 `checklist` localStorage 键并刷新，或重新调用正式 fixture 的独立检查入口。工具没有返回独立的结束清理日志，本轮不声称已清除结束后的数据；隔离浏览器状态不代表外部用户数据。准备缺口：无影响本轮四项执行的缺口。

## 5. 执行与覆盖统计

单次正式 fixture 调用完成全部四项检查，未因 AC-2 失败中断后续检查；无重试、无改测版本或环境、无断言调整。

- 用例总数 4：Pass 3，Fail 1，Not run 0，Blocked 0；四类合计 4。
- 需求覆盖：4/4（100%）均已执行；用例通过率 3/4（75%）。AC-1 两个输入子样本不重复计作用例。
- 未测或阻塞项：无。全部场景均基于本次正式候选证据，无旧版结果复用。

## 6. 逐项结果

以下全部结果对应第 3 节同一提交、HTML digest、真实 HTTP 环境和第 6.1 节原始工具回执。工具对勾选场景返回语义布尔断言，未逐帧返回 checkbox 数组，报告不将预期数组冒充原始观察。

| 用例 / 依据 | 前置 / 数据 | 方法与操作 | 预期判据 | 实际结果与差异 | 结论 | 证据 / 实际版本 | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-1 / AC-1 | 隔离空列表；空字符串及三个空格 | 正式页面填入两种输入并提交 | 页内 alert 可见且不新增 | 两样本均 `alert:true,count:0` | Pass | 第 6.1 节 `checks.AC-1`；第 3 节版本 | 无 |
| C-2 / AC-2 | 输入 `  Pack bag  ` | 从正式页面提交，读取条目 label 和持久化 name | 显示与存储名称去两侧空格，存储严格为 `Pack bag` | 返回 DOM label 为 `  Pack bag  `，stored 同样为 `  Pack bag  `，均非规范值；存储未 trim 足以违反 AC-2 | Fail | 第 6.1 节 `checks.AC-2`；第 3 节版本 | [ISSUE-001](../../issues/ISSUE-001.md) |
| C-3 / AC-3 | 已新增两项 | 正式页面新增并勾选；检查初始、独立状态及双选 | 两个新 checkbox 未选，勾选一项不改另一项 | `initial:true,independent:true,both:true`，工具判 PASS | Pass | 第 6.1 节 `checks.AC-3`；第 3 节版本 | 无 |
| C-4 / AC-4 | 两项可选状态 | 正式页面取消勾选，检查另一项及最终双清空 | 取消一项保留另一项状态，两项均可取消 | `otherUnchanged:true,bothClear:true`，工具判 PASS | Pass | 第 6.1 节 `checks.AC-4`；第 3 节版本 | 无 |

AC-2 的 `label` 是工具返回的 DOM 文本值，不等于肉眼可见的边缘空白宽度。浏览器可能折叠普通文本空格，本轮未做截图或像素判断，不能据此断言肉眼看见两侧空格；实际 localStorage name 包含两侧空格是直接、确定的失败证据。

### 6.1 原始正式浏览器证据

调用：`mcp__local_browser_fixture__run_formal_check({})`。以下完整保留返回的 JSON 文本，不改写值或以原型数据补足：

```json
{"entry":"http://127.0.0.1:45393/src/index.html","sha256":"c1e4df9bb0a2620cf1a24fd11f41c603bea5aef361a39511ed41cf105046327a","browser":"149.0.7827.55","checks":{"AC-1":{"result":"PASS","actual":[{"sample":"","alert":true,"count":0},{"sample":"   ","alert":true,"count":0}]},"AC-2":{"result":"FAIL","actual":{"label":"  Pack bag  ","stored":"  Pack bag  "},"expected":"Pack bag"},"AC-3":{"result":"PASS","actual":{"initial":true,"independent":true,"both":true}},"AC-4":{"result":"PASS","actual":{"otherUnchanged":true,"bothClear":true}}}}
```

## 7. 相关问题与影响

| Issue | 关联用例 | 影响 |
| --- | --- | --- |
| [ISSUE-001：新增项名称未 trim](../../issues/ISSUE-001.md) | C-2 / AC-2 | 正式候选存储不满足已确认判据，阻止本轮 Gate PASS；不阻塞其他三项取证 |

仅登记独立问题事实；未开展归因、修复、实施任务或 Issue 关单。

## 8. 结论、人工反馈与恢复条件

本轮执行已完成，四项范围均有实际状态；正式候选 3 项通过、1 项失败。**Test Gate：FAIL**，适用于第 3 节指定提交、HTML digest 和隔离 Chromium HTTP 环境。失败依据是 AC-2 实际存储值未去两侧空格，不能以原型通过或整体统计覆盖替代。

人工反馈：未收到用户实操反馈。本轮四项均是客观可自动验证判据，没有必须由用户主观判断的项目；自动结果不标为人工确认，人工反馈缺失不形成额外待验项。

恢复条件：由 Main 按后续授权安排修复 ISSUE-001；提供明确修复提交及正式 HTML digest，在同一已确认范围和隔离正式环境重新执行 AC-2 与 AC-1、AC-3、AC-4 回归。保留本批次失败记录，新批次另记实际版本和结果。此报告不授权产品修改、版本切换或发布。本轮没有其他未测项；真实部署、跨会话恢复及视觉像素效果不在结论覆盖范围。

索引与 Status 按用户写入限制未更新；结果入口由 Quickstart 链接，并随阶段回执交 Main。
