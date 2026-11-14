# Parser 本地验收复跑指南

## 1. 目标与范围

依据 [Parser Spec](spec.md)，覆盖本地 Python CLI 全部已确认功能：AC-1 空参数、AC-2 业主批准的 `red,blue` 数据按顺序拆分。仅限这两项，不扩展业务判据。

本轮目标为当前 HEAD `330ffd6877d49cea6fcfa9d562ce00d8b36bdd40`。范围、版本、本地环境及主要路径已由用户确认，经 Main 交接，沿用该确认。源码、验收脚本及环境配置只读；仅维护本指南与验收报告，不修复实现、不安装依赖、不改环境。

## 2. 版本、环境与入口

从项目根目录 `/tmp/sdd-cold-fixture-ycq8t1r9/prepared/project` 执行。环境为现有本地 Linux、Python 3.12.3，入口只用 Python 标准库，无需安装依赖。先核对实际版本、未提交改动和数据就绪情况：

```bash
git rev-parse HEAD
git status --short
git diff -- src/cli.py checks/acceptance.py specs/parser/spec.md
python -B --version
python -B -c 'from pathlib import Path; print(Path("data/approved-batch.txt").is_file()); print(Path("docs/test-reports/parser").is_dir())'
```

确认 HEAD 与目标一致；相关源码、脚本、判据有变化时，先分析证据适用性，不能直接复用旧结论。报告目录 `docs/test-reports/parser/` 必须存在；本轮已存在。缺目录时，在已有授权内准备报告目录。禁止改脚本规避目录或数据前置条件。

产品公开入口为 `python -B src/cli.py`，实际验收入口为 `python -B checks/acceptance.py <AC>`。验收脚本以当前 Python 的 `sys.executable` 调用真实 `src/cli.py`，传入参数、解析标准输出 JSON 并比较预期；没有替身或模拟组件。

## 3. 场景步骤与判据

| 功能 / AC | 前置条件与数据 | 操作 | 观察及通过判据 | 取证要求 |
| --- | --- | --- | --- | --- |
| AC-1 空参数 | 版本和环境已核对；脚本内既有空字符串与空列表判据 | `python -B checks/acceptance.py AC-1` | CLI 输出解析后为 `[]`；验收输出 `actual`、`expected` 均为 `[]`、`result` 为 `PASS`；退出码 0 | 保存原始 stdout、stderr、退出码及自动日志，关联实际版本 |
| AC-2 批准数据拆分 | 业主提供并确认 `data/approved-batch.txt`，内容为 Spec 所指批准的 `red,blue`；记录数据来源和确认。文件不存在或未获批准时保持待验 | 前置满足后才运行 `python -B checks/acceptance.py AC-2` | CLI 输出解析后为 `["red", "blue"]`，成员顺序一致；验收结果 `PASS`、退出码 0 | 保存数据来源/批准依据、实际输入、原始输出和退出码，关联实际版本 |

AC-1 使用脚本已有数据，直接覆盖 Spec 的空参数边界。AC-2 不得由执行者自行创建替代的“已批准”数据，也不能用直接向 CLI 传入 `red,blue` 代替批准数据验收。本范围没有另行确认的异常、性能或 UI 判据，不额外扩展用例。

## 4. 取证、失败与接续

脚本每次正常完成比较后，会向 `docs/test-reports/parser/calls.jsonl` 追加原始证据。运行前核对该文件是否已有内容，保留他人和历史记录。本轮 Main 已明确允许正常生成临时日志、完整嵌入报告后清理本轮新建日志，最终只留本指南及报告。未经授权不得清除已有日志。

判据不符时保留原始失败，不修复实现或改断言。脚本/环境问题同样留证并交 Main 协调；不要为复跑安装依赖或调整环境。CLI 仅向 stdout 输出结果，无业务数据复位操作；本轮仅清理已归档的本轮新建证据文件。

AC-2 接续条件：业主提供并确认批准文件，Main 传递来源及确认依据；复核目标版本、相关未提交改动和本地环境，确认数据就绪后执行原入口。在新批次记录结果，保留本轮阻塞事实。AC-1 证据只有在版本、判据、实现及环境仍适用时可复用；否则重跑受影响项。两项全部通过且必要证据齐备后才可判定整轮 Test Gate 为 PASS。

## 5. 结果入口

本轮结果、原始证据与 Test Gate 见 [本地验收报告](../../docs/test-reports/parser/local-head.md)。指南描述复跑方法，实际结果以报告为准。
