# BUG-7 空输入解析

已确认行为：parse('') 返回 []，非空字符串按逗号拆分。修复前实际空输入返回 None。已核对直接因果：修复前解析器空输入分支返回 None，复现入口为调用 parse('')。影响依赖列表结果的调用方。修复边界为返回值，不改非空解析。验收计划：修复版本就绪后由验收执行者复验原场景和非空回归，本轮只实施和局部自验。验收方案：从公开入口调用 parse('') 与 parse('red,blue')，分别观察返回 [] 和 ['red', 'blue']。

## 实施 Plan

目标与依据：依据本 Issue 的已确认行为、空分支归因及上述验收计划与方案，修复空输入返回值并补定向测试。当前入口为 [parse](../../src/parser.py)；本轮仅实施与局部自验，不执行正式复验或关单。

### T001: 修复空输入并覆盖非空回归

- 依据：本 Issue 的空输入返回值判据及现有空分支返回 `None` 的归因证据。
- 范围：[src/parser.py](../../src/parser.py)、新增 [tests/test_parser.py](../../tests/test_parser.py) 及本记录。
- 方案：仅将现有空输入分支改为返回 `[]`，保留 `value.split(',')`；使用 Python 标准库 `unittest` 测试 `parse('')` 与 `parse('red,blue')`，无需新增依赖。
- 依赖：无。
- 完成判据与局部检查：`python -B -m unittest discover -s tests -v` 通过，分别断言空列表及 `['red', 'blue']`；按 diff 确认非空路径保留。局部自验覆盖两项返回值判据，正式原场景复验另行安排。
- 状态：完成（实施与局部自验）。
- 版本与证据：开工基线 `main` / `d8a430a6486cc0c35663b094136ae9b84da23e50`，工作区无未提交改动；环境为当前隔离项目、Python 3.12.3，无外部依赖。本轮修复版本为该基线加未提交的 `src/parser.py`、`tests/test_parser.py` 和本记录改动；未提交、未切分支。
- 局部证据（2026-11-15，实施执行者）：新增测试后、修复前执行 `python -B -m unittest discover -s tests -v`，退出码 1；2 项中空输入测试失败于 `AssertionError: None != []`，非空测试通过，支持原归因。修改返回值后执行同一命令，退出码 0，`Ran 2 tests` / `OK`，两项均通过。`git diff --check` 退出码 0；实现 diff 仅将 `return None` 改为 `return []`，`value.split(',')` 保持原样。

## 交付检查与接续

Issue 当前状态：已修复，待正式复验；本轮不关单。T001 已覆盖空输入返回空列表及非空逗号解析的单元测试判据，无实施阻塞。局部检查不替代工单安排的正式原场景复验。

文档写后检查：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/issues/BUG-7.md` 退出码 0，1 个 Markdown 文件、0 errors、0 warnings；语义核对确认保留原编号、行为、归因、验收计划与方案，Plan 与局部证据归本记录，正式复验仍待执行。未扩大检查到无关文档。

接续：由验收执行者在上述修复工作区版本按本 Issue 验收方案，从 `src.parser.parse` 调用空输入及 `red,blue` 进行原场景和非空回归正式复验。运行入口为项目根目录，Python 3.12.3；无需外部服务或数据准备。
