# Test Report — Checklist 正式 Web 集成验收 2026-11-15

## 1. Test Goals and Basis

- **Batch, verification type, executor, and time** — `checklist-2026-11-15-formal`；完整范围集成验收；独立 sdd-test-loop Agent `/root/acceptance`（调用者及回执接收方 Main `/root`）；2026-11-15 01:07 CST（时钟核对值 2026-11-14 17:07:18 UTC）。精确到秒的各浏览器调用时间未由工具返回。
- **Subject and goal** — 对当前隔离仓库的正式 Web 客户端验证全部已确认功能点，取得真实 HTTP Chromium 证据并判定 Test Gate。
- **Basis** — [Checklist Spec](../../../specs/checklist/spec.md) 的 AC-1 至 AC-4、固定原型及 [本轮 Quickstart](../../../specs/checklist/quickstart.md)。指南归纳本轮所用操作和复跑条件；实际执行记录在本报告。不存在前次正式批次或可复用修复证据。

## 2. Test Scope and Plan

- **Scope and exclusions** — 空串/空格校验、去除首尾空格后展示及存储、两项独立勾选、取消勾选；四项全覆盖。排除纯视觉、像素比对、架构 Review、跨浏览器、发布部署和未确认的新功能。
- **Test arrangement** — 由独立技能执行者直接执行正式浏览器，依据四项 AC 推导空串、三空格、带空格的名称、两条独立条目及中间状态；顺序为 C-1 → C-2 → C-3 → C-4。工具提供用户入口及结果；只读源码和原型用于辅助，不替代正式业务结果。
- **Completion criteria** — 全部适用 AC 在指定正式版本及环境取得满足判据的证据，必要人工反馈齐备方可 PASS；失败和阻塞完整记录可结束本轮执行，但不满足通过条件。
- **Integration scope confirmation** — Main 启动工单明确用户已确认范围、目标 HEAD、隔离本地 HTTP 环境及主要路径；沿用该确认。执行中未变更范围、版本、环境或判据。

## 3. Test Environment

- **Version under test** — `eb0012894f193ac27f20548f016bdfdbc49985c7`。首次执行前及两次正式运行后 `git rev-parse HEAD` 一致，`git status --short` 均为空。后续仅新增本指南、报告、Issue 文档；产品、原型和工具未改。
- **Environment and entry point** — 隔离 `local_browser_fixture` HTTP 正式入口 `http://127.0.0.1:45881/src/index.html`，Chromium `149.0.7827.55`。入口来源为 [浏览器说明](../../browser.md)，实际值由工具回执取得。没有安装依赖或改动运行配置。
- **Artifact witness** — 正式工具返回 HTML SHA-256 `c76eb274a5c05ef5a149191c065b82caa2d67d511d63e667062c8a891cfdb5bb`，两次一致；本地 `sha256sum src/index.html` 完全一致，关联到上述 HEAD 的正式文件。
- **Real and simulated components** — 正式页使用真实浏览器 DOM 与本地存储，工具在真实 HTTP 入口运行。原型入口为 `http://127.0.0.1:45881/tests/prototypes/checklist/personal/index.html`，仅浏览器内存模拟；其结果单列，不能证明正式存储或正式 AC 通过。项目未要求外部服务或后端。

## 4. Test Setup and Data

- **Setup** — 使用已就绪隔离 fixture 与各自分离的正式/原型浏览器状态，不访问个人浏览器数据；无需账户或凭证。工具返回入口、浏览器、摘要及逐项 checks，未返回内部清理实现或控制台日志，不声称已检查这些内容。
- **Data** — AC-1 的 `""`、`"   "`，AC-2 的 `"  Pack bag  "`；C-3/4 为两个条目的状态组合。正式 AC-2/3/4 工具只返回错误，不能据此宣称实际名称、存储值或成功完成的中间动作。指南为手工复跑提供第二项常规数据 `Read book`。
- **Data recovery** — 只在隔离测试上下文执行；工具未返回运行后存储快照、上下文清理结果或状态复位回执，因此这些未独立验证。手工复跑按指南仅清空测试入口的 `checklist` 键后刷新。
- **Setup gaps** — 正式 C-2/3/4 在等待 checkbox 时超时，未获得必要业务结果。辅助 shell HTTP 请求被沙箱拒绝（`URLError <urlopen error [Errno 1] Operation not permitted>`）；本地 Python `playwright` 不可用。未绕过限制、未安装工具。既有浏览器工具仍可运行，故继续完成其可执行覆盖。

## 5. Execution and Coverage Summary

- **Planned and actual execution** — 正式 `run_formal_check({})` 执行两轮，结果一致；辅助 `run_prototype_check({})` 一轮。额外轮次用于排除一次性现象，不增加用例计数。所有四个 AC 均有明确状态；AC-2/3/4 已尝试但阻塞，并非遗漏。当前可用正式浏览器工具只有这一整组执行入口，四项均已尝试；在不改产品/工具、不突破环境限制的已授权条件下，没有剩余可执行却未覆盖的场景。
- **Case counts** — 共 4 项：Pass 0、Fail 1、Not run 0、Blocked 3，总和 4。正式已取得完整可判定业务证据 1/4；正式通过率 0/4。需求到场景映射覆盖 4/4（100%）不表示四项已通过或都已取得完整实测证据。
- **Requirements coverage** — C-1 ↔ AC-1，C-2 ↔ AC-2，C-3 ↔ AC-3，C-4 ↔ AC-4。空白两种边界均实际观察；空白后恢复添加、展示/存储及勾选组合受阻。辅助原型四项 PASS 另计，不合并进正式通过率。不复用其他版本证据。

## 6. Test Details

| Case / Requirement basis | Preconditions / Data | Method and actual steps | Expected outcome and criteria | Actual outcome and differences | Verdict | Evidence / Actual version | Issue reference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-1 / AC-1 | 正式入口，空串与三空格 | 正式工具分别提交两种输入，读取 alert 与 count；原版本重跑一次 | 两种输入均显示内联 alert，且条目数 0 | 两轮两种输入均 alert=false、count=0；无新增通过，但提示要求失败 | Fail | E1、E2；`eb0012894f193ac27f20548f016bdfdbc49985c7`，正式摘要匹配 | [CHECKLIST-001](../../issues/CHECKLIST-001.md) |
| C-2 / AC-2 | 计划添加 `  Pack bag  ` | 正式工具进入该项，等待首个 checkbox 以读取标签 | 展示及存储名称均为 `Pack bag` | 两轮均 locator.evaluate 等待首个 checkbox 3500 ms 超时；没有 label 或 stored 直接证据 | Blocked | E1、E2，同版本；恢复需正式页可创建条目并返回标签与存储 | [CHECKLIST-001](../../issues/CHECKLIST-001.md)（关联影响，不推定同一根因） |
| C-3 / AC-3 | 计划两个初始未选条目 | 正式工具进入该项读取初始状态及独立勾选 | 初始均未选，勾选一个不影响另一个 | 两轮均 locator.isChecked 等待首个 checkbox 3500 ms 超时；未取得 initial/independent/both | Blocked | E1、E2，同版本；恢复需两个真实可操作条目及状态证据 | [CHECKLIST-001](../../issues/CHECKLIST-001.md)（关联影响） |
| C-4 / AC-4 | 计划两个已选条目 | 正式工具进入该项取消勾选并观察另一项 | 取消一个不影响另一个，最终均未选 | 两轮均 locator.uncheck 等待首个 checkbox 3500 ms 超时；未取得 otherUnchanged/bothClear | Blocked | E1、E2，同版本；恢复需前置条目可用及中间/最终状态证据 | [CHECKLIST-001](../../issues/CHECKLIST-001.md)（关联影响） |

### E1 — 正式首次浏览器原始回执

调用：`local_browser_fixture.run_formal_check({})`。原始文本 JSON 如下，未将 ERROR 改写为业务失败或通过：

```json
{"entry":"http://127.0.0.1:45881/src/index.html","sha256":"c76eb274a5c05ef5a149191c065b82caa2d67d511d63e667062c8a891cfdb5bb","browser":"149.0.7827.55","checks":{"AC-1":{"result":"FAIL","actual":[{"sample":"","alert":false,"count":0},{"sample":"   ","alert":false,"count":0}]},"AC-2":{"result":"ERROR","error":"locator.evaluate: Timeout 3500ms exceeded.\nCall log:\n  - waiting for getByRole('checkbox').first()\n"},"AC-3":{"result":"ERROR","error":"locator.isChecked: Timeout 3500ms exceeded.\nCall log:\n  - waiting for getByRole('checkbox').first()\n"},"AC-4":{"result":"ERROR","error":"locator.uncheck: Timeout 3500ms exceeded.\nCall log:\n  - waiting for getByRole('checkbox').first()\n"}}}
```

### E2 — 正式复跑

在未修改任何产品、原型或工具的情况下，再次调用 `run_formal_check({})`。入口、浏览器、SHA-256 及完整 checks JSON 与 E1 相同：AC-1 两种样本仍 alert=false/count=0；AC-2 仍 evaluate、AC-3 仍 isChecked、AC-4 仍 uncheck 的 3500 ms 等待超时。没有取得任何 label、stored 或 checkbox 状态快照。复跑保留初轮结果，无修复版本。

### E3 — 辅助原型回执

调用：`local_browser_fixture.run_prototype_check({})`。本地原型 SHA 与 Spec 固定值、工具值完全一致，辅助确认同一浏览器通路能执行原型交互：

```json
{"entry":"http://127.0.0.1:45881/tests/prototypes/checklist/personal/index.html","sha256":"d401df9dc918a0384b0df96152f3d240c3343eb4f307239cf963ce664f739e75","browser":"149.0.7827.55","checks":{"AC-1":{"result":"PASS","actual":[{"sample":"","alert":true,"count":0},{"sample":"   ","alert":true,"count":0}]},"AC-2":{"result":"PASS","actual":{"label":"Pack bag","stored":null},"expected":"Pack bag"},"AC-3":{"result":"PASS","actual":{"initial":true,"independent":true,"both":true}},"AC-4":{"result":"PASS","actual":{"otherUnchanged":true,"bothClear":true}}}}
```

原型 AC-2 的 stored=null 与其内存模拟边界一致，不是正式存储通过证据。辅助通过不能排除正式页面或正式工具适配问题，不能据此确定运行故障根因。

### E4 — 文件与版本核验

两次正式执行期间读到 `git rev-parse HEAD` 均为 `eb0012894f193ac27f20548f016bdfdbc49985c7`，`git status --short` 均为空。`sha256sum src/index.html tests/prototypes/checklist/personal/index.html` 输出：

```text
c76eb274a5c05ef5a149191c065b82caa2d67d511d63e667062c8a891cfdb5bb  src/index.html
d401df9dc918a0384b0df96152f3d240c3343eb4f307239cf963ce664f739e75  tests/prototypes/checklist/personal/index.html
```

正式和原型均核对各自摘要；没有把原型摘要关联成正式制品。

## 7. Related Issues and Impact

| Issue reference | Related cases in this batch | Issue summary and impact on this batch's conclusion |
| --- | --- | --- |
| [CHECKLIST-001](../../issues/CHECKLIST-001.md) | C-1；关联 C-2/3/4 阻塞 | 正式页空白 alert 不出现，已确认行为差异；后续无 checkbox 的工具超时另列影响，根因未证实。阻止 Test Gate 通过，未修复、未关闭 |

## 8. Test Conclusion and Limitations

- **Overall conclusion** — 本轮已完成所有 AC 的执行尝试和状态覆盖；正式 C-1 失败，C-2/3/4 缺必要结果而阻塞。未满足验收通过条件。
- **Remaining risks and unverified items** — 尚不能判断正式 AC-2 展示/存储、AC-3/4 状态是否符合判据。只读源码可见新增对象使用原始 `raw` 名称而非裁剪值，提示 AC-2 风险，但不作为动态验收结果或已验证根因。工具未提供控制台、截图、逐动作轨迹、清理回执，因此只对回执实际覆盖内容下结论。环境/测试适配与产品故障的进一步区分需 Main 在后续授权内安排；不修改工具或被测实现。
- **Human confirmation** — 四项均为客观交互判据，本轮无必须由用户主观体验判断的 AC；现有范围确认来自启动工单，不冒充用户实际验收反馈。未收到用户操作反馈，也无独立的人工待验项。当前 Gate 的缺口来自正式失败及取证阻塞。
- **Gate** — **FAIL**。仅适用于 commit `eb0012894f193ac27f20548f016bdfdbc49985c7`、上述 Chromium/隔离 HTTP 正式入口、AC-1 至 AC-4 全范围。依据 E1/E2/E4；原型 E3 不提升 Gate。恢复条件：解决已记录故障或取证装配问题，在可核验实际版本上重跑全部四项，获得 AC-2 的展示和存储、AC-3/4 的完整中间与最终状态；保留本轮失败历史。无发布或修复授权。
- **Document boundary and checks** — 仅写入指南、报告及必要 Issue；按用户明确边界未同步索引、Status 或 Plan，不做 Git 写入。三个产物互链提供可访问入口。写后机械及语义检查结果见下方；机械通过不改变业务 FAIL。

### 文档写后检查

执行 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/checklist/quickstart.md docs/test-reports/checklist/2026-11-15-formal-acceptance.md docs/issues/CHECKLIST-001.md`：检查 3 个 Markdown，0 errors、0 warnings（mechanical only）；`git diff --check` 无诊断。读回三份正文，语义核对 AC 映射、合计 4 项、Fail 与 Blocked 区别、真实/模拟边界、相对链接、Issue 未修复状态及人工反馈适用性，均与当前来源和证据一致。

写后 `git status --short` 仅显示新增 `docs/issues/`、`docs/test-reports/`、`specs/checklist/quickstart.md`；最终 HEAD 和两份 HTML 摘要仍与 E4 一致，说明产品及原型未变。本轮未检查远程链接可达性、工具内部实现或未提供的浏览器截图/控制台；这不影响已确认 AC-1 失败，但限制 AC-2/3/4 的进一步判断。机械检查通过不等于业务通过；实际业务 Gate 保持 FAIL。
