# Plan — BUG-001 空输入解析修复

## 1. 目标与依据

- 目标与范围：恢复空字符串返回空列表的已确认契约，保留非空字符串按逗号拆分的行为。
- 上游工单：[BUG-001](BUG-001.md) 的问题事实、归因及第 2 节验收计划与方案；原始要求见 [TASK.txt](../../TASK.txt)。
- 修复前实现：[src/parser.py](../../src/parser.py) 的 `parse` 空值分支显式返回 `None`；上游真实调用已复现，与代码路径一致。

## 2. Task 清单

### T001: 恢复空输入返回列表并保持拆分行为

- 依据：[BUG-001](BUG-001.md) 第 1 节归因证据与第 2 节四项通过判据。
- 改动范围：`src/parser.py`；新增本 Plan，其他文件由调度方负责。
- 实施方案：仅将空值分支的 `return None` 改为 `return []`，保持现有 `split(',')` 路径。无需新增持久测试资产。
- 依赖：无。
- 完成条件与局部自验：通过公开入口 `src.parser.parse` 真实调用，断言 `parse('')` 等于 `[]` 且为 `list`；`parse('a,b')`、`parse('item')`、`parse(',a,,')` 分别等于上游规定的拆分结果。记录命令、输出、版本；对本 Plan 执行文档机械检查并读回核对。
- 状态：Complete。
- 结果与证据：2026-11-14，sdd-coder 在当前隔离项目、Python 3.12.3 中完成以下局部自验，退出码 0；四项判据全部通过。修复版本为 HEAD `2d9fd8ecd137d6c5c4a0d1092aa33dec6fa5096c` 加本次未提交变更；`src/parser.py` SHA256 为 `3e0d14ca1979f8a546363180e6b36e5c2264897a6cac66e72ab75fbf0c9f49f9`。源代码差异仅为空值分支返回值修改。工作区另有调度方维护的 Issue 与索引修改，均未撤销。

局部自验命令（项目根目录）：

```bash
python -B - <<'PY'
from src.parser import parse

cases = [('', []), ('a,b', ['a', 'b']), ('item', ['item']), (',a,,', ['', 'a', '', ''])]
for value, expected in cases:
    actual = parse(value)
    assert actual == expected, (value, actual, expected)
    if value == '':
        assert isinstance(actual, list), type(actual)
    print(f'PASS parse({value!r}) == {actual!r}; type={type(actual).__name__}')
print('4/4 passed')
PY
```

实际输出：

```text
PASS parse('') == []; type=list
PASS parse('a,b') == ['a', 'b']; type=list
PASS parse('item') == ['item']; type=list
PASS parse(',a,,') == ['', 'a', '', '']; type=list
4/4 passed
```

## 3. 交付核对

- 目标覆盖：T001 覆盖本工单全部四项判据。
- 阻塞：无。
- 文档核对：读回本 Plan，对照上游四项判据、源代码差异及实际输出核对，编号、链接、范围和证据归属一致。机械检查命令为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/issues/BUG-001-plan.md`，输出 `Checked 1 Markdown files: 0 errors, 0 warnings (mechanical only)`，退出码 0。检查范围仅为本 Plan。
- 后续验收：调度方依据 [BUG-001](BUG-001.md) 第 2 节在同一修复工作区独立复验并维护原 Issue 状态。
