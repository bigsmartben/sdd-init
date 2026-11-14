# BUG-7 空输入解析

已确认行为：parse('') 返回 []，非空字符串按逗号拆分。修复前空输入返回 None。已核对直接因果：修复前解析器空输入分支返回 None，复现入口为调用 parse('')。影响依赖列表结果的调用方。修复边界为返回值，不改非空解析。验收计划：修复版本就绪后由验收执行者复验原场景和非空回归，本轮只实施和局部自验。验收方案：从公开入口调用 parse('') 与 parse('red,blue')，分别观察返回 [] 和 ['red', 'blue']。

## 实施计划

### T001：修复空输入返回值并补定向测试

- 依据：本 Issue 已确认行为、归因和验收计划；沿用 [实施授权](../../TASK.txt)。
- 目标与范围：修改 [解析器](../../src/parser.py)，新增 [定向单元测试](../../tests/test_parser.py)；空字符串返回空列表，保持非空逗号拆分。
- 方法：保留现有分支与非空解析路径，将空输入分支返回值改为 `[]`；使用标准库 `unittest` 覆盖空字符串、非空逗号拆分、无逗号字符串及连续/首尾逗号。
- 依赖：无。无需外部服务或新增依赖。
- 完成判据与局部检查入口：在项目根目录运行 `python -B -m unittest discover -s tests -p 'test_parser.py' -v`；全部断言通过，确认 `parse('') == []` 且非空拆分保持原行为。此检查为实施者局部单测，原场景正式复验另行安排。
- 状态：完成。
- 结果与证据：仅将空输入分支返回值改为 `[]`，非空路径未变；[局部自验](#局部自验证据)通过。基线为 `552c0dc7c4d4c64ed96406af6ec99f2bd9f6fef9`，接单时工作区干净。

## 局部自验证据

- 批次类型、执行者与日期：实施者局部单测，`sdd-coder /root/bug7_implementation`，2026-11-15（Asia/Shanghai）。实际调用者与回执接收方为 Main `/root`。
- 环境：Linux `6.6.114.1-microsoft-standard-WSL2` x86_64，Python 3.12.3；从项目根目录运行标准库 `unittest`，直接调用真实解析器，无模拟、外部依赖或外部状态，无需数据复位。
- 修复前版本：HEAD `552c0dc7c4d4c64ed96406af6ec99f2bd9f6fef9`，解析器未修改，未提交路径为 `docs/issues/BUG-7.md`、`tests/test_parser.py`。
- 修复后实际版本：同一 HEAD，加未提交修改 `src/parser.py`、`docs/issues/BUG-7.md` 与新增 `tests/test_parser.py`；未创建提交。
- 两次执行使用相同入口：`python -B -m unittest discover -s tests -p 'test_parser.py' -v`。
- 修复前结果：退出码 1，2 个测试方法中 1 失败、1 通过；空字符串断言在 `tests/test_parser.py:8` 报 `AssertionError: None != []`。非空参数组通过，支持已记录归因。
- 修复后结果：退出码 0，`Ran 2 tests in 0.000s`、`OK`；2 个方法全部通过，包含以下 4 组输入。此次通过仅满足 T001 局部完成判据。

| 输入 | 预期输出 | 修复前局部结果 | 修复后局部结果 |
| --- | --- | --- | --- |
| `''` | `[]` | 失败：`None` | 通过 |
| `'red,blue'` | `['red', 'blue']` | 通过 | 通过 |
| `'red'` | `['red']` | 通过 | 通过 |
| `',red,,blue,'` | `['', 'red', '', 'blue', '']` | 通过 | 通过 |

- 代码与文档检查：`git diff --check` 通过。Markdown 机械检查范围为本文件，入口为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/issues/BUG-7.md`；退出码 0，检查 1 个 Markdown 文件，0 errors、0 warnings。机械检查不代替语义核对。
- 写后语义核对：原编号、归因、修复边界与验收计划保留；任务引用、实际未提交版本、前后结果及覆盖相符；本轮单测与后续正式复验分开记录。未运行正式复验、集成测试或架构审查。

## 当前状态与接续

- Issue 状态：待复验；本轮仅实施和局部自验，不关闭 Issue。
- T001 已完成，无实施阻塞；待验判据为原场景 `parse('')` 返回 `[]` 以及非空 `parse('red,blue')` 返回 `['red', 'blue']`。
- 接续：Main 向验收执行者交付上述修复后实际版本；验收执行者按上文验收计划与方案，从项目根目录通过 `src.parser.parse` 公开入口复验原场景和非空回归。只需 Python 环境及本轮工作树，无额外准备条件；正式复验证据仍待补充。
