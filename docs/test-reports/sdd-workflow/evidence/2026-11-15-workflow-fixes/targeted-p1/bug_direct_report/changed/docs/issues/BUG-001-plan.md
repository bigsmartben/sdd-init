# Plan — BUG-001 空输入返回空列表

T001 已完成：空分支返回值改为 `[]`，四组公开函数调用均通过局部自验。Bugfix 技能 Agent 在同一修复版本的独立复验 4/4 通过，见 [Issue 复验历史](BUG-001.md#3-处理与复验历史)。

## 1. 目标与依据

- 目标：恢复空字符串输入返回空列表，保留非空字符串按逗号拆分的行为。
- 上游：[BUG-001 的归因与验收方案](BUG-001.md)、[用户工单](../../TASK.txt)。调用者为 Bugfix 技能 Agent `/root/bugfix`；沿用已授权的单项修复范围，不提交或推送。
- 修复前实现：[parse](../../src/parser.py) 的空值分支显式 `return None`；原故障与初始取证见 Issue 第 1 节。只需替换该返回值，无需改变拆分路径。

## 2. Task 清单

### T001: 恢复空输入返回值并局部复验

- **依据**：BUG-001 第 1 节的已验证原因、第 2 节的验收计划与方案。
- **改动范围**：`src/parser.py`；新增本 Plan 记录方案与局部证据。
- **实施方案**：将空值分支改为 `return []`；保持 `value.split(',')` 路径。无影响本方案的未知项。
- **依赖**：无。
- **完成判据与局部验证**：通过真实公开入口断言 `parse('') == []` 且类型为 `list`；对 `a,b`、`one`、`a,,b` 断言拆分结果与 Issue 一致。项目根目录使用 Python 3 执行，无外部依赖。
- **状态**：完成。
- **结果与证据**：2026-11-15，sdd-coder 在项目根目录、Python 3.12.3 执行下列局部复验，退出码 0。实际版本为 HEAD `eb59588acc9c3e152904c2ecb96c29983c726f3a` 加未提交单行修复；`sha256sum src/parser.py` 得到 `3e0d14ca1979f8a546363180e6b36e5c2264897a6cac66e72ab75fbf0c9f49f9`。全部 Issue 判据在局部自验覆盖，无失败或阻塞；未创建持久测试文件。

局部复验命令：

```bash
python -B - <<'PY'
from src.parser import parse
cases = [('', []), ('a,b', ['a', 'b']), ('one', ['one']), ('a,,b', ['a', '', 'b'])]
for value, expected in cases:
    actual = parse(value)
    assert actual == expected, (value, actual, expected)
    assert isinstance(actual, list), (value, type(actual))
    print(f'PASS parse({value!r}) = {actual!r}; type={type(actual).__name__}')
print('4/4 cases passed')
PY
```

实际输出：

```text
PASS parse('') = []; type=list
PASS parse('a,b') = ['a', 'b']; type=list
PASS parse('one') = ['one']; type=list
PASS parse('a,,b') = ['a', '', 'b']; type=list
4/4 cases passed
```

## 3. 交付检查

- 目标覆盖：T001 已完成，实际 diff 仅替换空值分支返回值，四项实测覆盖原故障及必要非空回归。
- 阻塞：无。
- 待验：无。Bugfix 技能 Agent 已按 Issue 第 2 节在同一 SHA256 版本独立复验，四项判据均通过；执行证据及关闭依据归 [Issue](BUG-001.md#3-处理与复验历史)。
- 写后核对：语义核对本 Plan 与上游 Issue 的目标、原因和四项判据一致；保持 T001 唯一编号，任务无依赖环，引用可定位。机械检查命令为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/issues/BUG-001-plan.md docs/issues/BUG-001.md`，退出码 0，输出 `Checked 2 Markdown files: 0 errors, 0 warnings (mechanical only)`。机械结果不替代语义核对。
