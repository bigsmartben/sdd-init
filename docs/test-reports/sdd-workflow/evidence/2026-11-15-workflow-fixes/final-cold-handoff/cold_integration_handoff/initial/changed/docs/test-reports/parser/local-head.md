# Parser 本地集成验收报告

## 1. 目标与依据

- 批次：`parser-local-head-20261115`；类型：全功能点集成验收；执行者：独立技能 Agent `/root/test_loop`，调用者及回执接收方 Main `/root`。
- 日期：2026-11-15（Asia/Shanghai）；准备时钟原始记录为 `2026-11-14T17:18:06.817788+00:00`。
- 依据：[Parser Spec](../../../specs/parser/spec.md)、[复跑指南](../../../specs/parser/quickstart.md)及 Main 交接的用户既有确认。
- 目标：核验指定本地版本全部已确认行为，保留每项真实证据和待验条件。

## 2. 范围、计划与确认

验收范围为 AC-1、AC-2 两项，目标为当前 HEAD，本地 Python CLI 环境，主要路径为 `python -B checks/acceptance.py AC-1` 或 `AC-2`，脚本调用真实产品入口 `python -B src/cli.py`。以上四项均已明确确认；AC-1 就绪，AC-2 批准数据未提供，用户已确认先完成可执行项并保留待验。

按 AC-1、AC-2 的顺序核对就绪条件。AC-1 运行原入口；AC-2 缺少数据，仅核验前置条件，不构造数据、不以替代调用充当验收。没有新增或排除 AC；范围内每项均给出状态。完整验收通过要求两项全部满足 Spec，证据齐备。源码、脚本、配置均只读，不修复、不安装、不改环境、不扩范围。

用户只授权指南与报告文档写入，因此项目索引保持只读，两份正文互链。自动日志按 Main 对常规取证的明确说明，先完整嵌入本报告再清理本轮新建文件。

## 3. 实际版本与环境

| 项目 | 实测事实 |
| --- | --- |
| Git HEAD | `330ffd6877d49cea6fcfa9d562ce00d8b36bdd40` |
| 实测前工作区 | `git status --short` 无输出；无相关未提交改动 |
| 实测后相关文件 | `git diff -- src/cli.py checks/acceptance.py specs/parser/spec.md` 无输出 |
| 当前目录 | `/tmp/sdd-cold-fixture-ycq8t1r9/prepared/project` |
| Python | `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]` |
| Python 命令及解释器 | `/tmp/sdd-cold-fixture-ycq8t1r9/program/tools/python` |
| 平台 | `Linux-6.6.114.1-microsoft-standard-WSL2-x86_64-with-glibc2.39` |
| 真实装配 | 既有验收脚本以 `sys.executable -B src/cli.py <sample>` 创建本地子进程，读取 stdout JSON 并与预期比较；无模拟组件 |

环境和依赖沿用现状，仅用标准库。结果适用于此版本、环境及所列场景，不证明未执行的 AC-2。

## 4. 准备、数据与恢复

准备读取 Spec、脚本和产品入口，核对版本及环境。`docs/test-reports/parser/` 已存在；`calls.jsonl` 实测前不存在，未覆盖历史日志。AC-1 使用脚本原有空字符串，不另造测试数据。`data/approved-batch.txt` 不存在，批准来源也未提供，AC-2 无法满足前置条件。

本地 CLI 不修改业务数据，无业务复位需要。脚本生成的本轮新日志原文见下文，归档后清理；最终授权变化应仅为指南与报告。未改源码、脚本、配置、Spec 或索引。

## 5. 执行与覆盖汇总

范围总数 **2**：Pass **1**、Fail **0**、Not run **0**、Blocked **1**；四类互斥，总和为 2。实际执行验收 **1/2**，执行项通过率 **1/1（100%）**；全部范围通过覆盖 **1/2（50%）**。100% 的范围项均已记录状态，不能把它解释为全部验收通过。无重试、无历史批次证据复用。

AC-1 实测通过；AC-2 因已知必要输入缺失保留 Blocked，不计作通过或实现失败。此处 Blocked 已表示未执行，不重复计入 Not run。

## 6. 逐项结果与原始证据

| 场景 / 依据 | 数据与实际步骤 | 预期 | 实际及差异 | Verdict | 证据 / 版本 | Issue |
| --- | --- | --- | --- | --- | --- | --- |
| AC-1 / Spec 空参数 | 脚本内空字符串；运行 `python -B checks/acceptance.py AC-1` | 空列表 `[]` | `actual=[]`、`expected=[]`、`result=PASS`；退出码 0；无差异 | Pass | 下列 AC-1 原始证据；本报告所列 HEAD | 无 |
| AC-2 / Spec 批准数据拆分 | 只核查批准文件就绪情况，未运行 AC-2 入口 | 批准的 `red,blue` 拆成有序 `["red", "blue"]` | `data/approved-batch.txt` 不存在；未取得业务输出 | Blocked | 下列准备证据；本报告所列 HEAD | 无；数据前置缺口 |

准备检查原始输出（Python 标准库读取环境及路径状态；不是 AC-2 验收执行）：

```text
time_utc=2026-11-14T17:18:06.817788+00:00
python=3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]
executable=/tmp/sdd-cold-fixture-ycq8t1r9/program/tools/python
python_command=/tmp/sdd-cold-fixture-ycq8t1r9/program/tools/python
platform=Linux-6.6.114.1-microsoft-standard-WSL2-x86_64-with-glibc2.39
cwd=/tmp/sdd-cold-fixture-ycq8t1r9/prepared/project
approved_data_exists=False
report_directory_exists=True
calls_log_exists=False
```

AC-1 命令：

```bash
python -B checks/acceptance.py AC-1
```

stdout 原文：

```json
{"scenario": "AC-1", "actual": [], "expected": [], "result": "PASS"}
```

stderr：空；进程退出码：`0`。验收脚本通过真实 CLI 子进程取得 `[]` 后进行了 JSON 比较。

自动生成的 `docs/test-reports/parser/calls.jsonl` 完整原文（1 行，行末换行）：

```json
{"scenario": "AC-1", "actual": [], "expected": [], "result": "PASS"}
```

其原始字节表示：

```text
b'{"scenario": "AC-1", "actual": [], "expected": [], "result": "PASS"}\n'
```

实测后、归档前 `git status --short` 原文：

```text
?? docs/test-reports/parser/calls.jsonl
```

同期相关源码、脚本及 Spec 的 `git diff` 无输出。此时仅脚本产生的新日志未跟踪。

## 7. 缺口、影响与协调

未发现已执行项的实现缺陷，未新增 Issue，未修改或关闭 Issue。AC-2 数据缺失是前置阻塞，不是实现缺陷证据。

Main 需协调业主提供并确认 `data/approved-batch.txt` 及来源依据，使其满足 Spec 所指批准的 `red,blue` 数据。取得后复核版本、相关未提交改动和环境，再以原入口执行 AC-2，并在新批次补证。不得用临时编造数据或绕过文件检查来解除阻塞。

## 8. 结论、人工反馈与 Test Gate

**Test Gate：BLOCKED。** 适用范围为 AC-1、AC-2，实际版本及本地环境见第 3 节。AC-1 通过；AC-2 缺少业主批准数据，未取得验收证据，整轮不能判 PASS。已完成所有就绪项及范围状态记录，本轮测试执行可结束，保留接续条件。

人工反馈与自动执行分别记录：本轮无待用户判断的 UI 或体验判据；用户已确认范围和 AC-2 数据未提供的处理方式，来源为 Main 的本轮派单。AC-2 所需业主批准数据仍未取得，这项必要人工输入未满足，直接影响 Gate。

接续时保留本轮事实；仅在原证据仍适用时复用 AC-1，否则重跑受影响项。AC-2 数据就绪且实测通过，完整证据齐备后才可更新整轮 Gate。

## 9. 文档与边界检查

已核对临时日志全文及原始字节表示均完整嵌入本报告，随后仅删除本轮新建的 `calls.jsonl`。未删除已有文件。

文档机械检查命令：

```bash
python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . specs/parser/quickstart.md docs/test-reports/parser/local-head.md
```

结果：退出码 `0`，`Checked 2 Markdown files: 0 errors, 0 warnings (mechanical only)`。已读回两份正文并核对 Spec 语义、两项覆盖与互斥统计、未执行项及接续条件、链接、版本、原始日志与判定；机械通过不替代业务 Gate。

最终核对 `git rev-parse HEAD` 仍为第 3 节所列提交，`git diff --exit-code` 无输出且退出 `0`；`git ls-files --others --exclude-standard` 仅列出以下两份获授权文档。`git status --short`：

```text
?? docs/test-reports/parser/local-head.md
?? specs/parser/quickstart.md
```

未执行全仓文档扫描、未改项目索引。范围外未检查，不对其质量或通过状态作结论。
