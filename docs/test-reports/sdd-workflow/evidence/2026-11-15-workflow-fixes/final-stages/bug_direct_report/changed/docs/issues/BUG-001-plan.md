# Plan — BUG-001 空输入返回空列表

已恢复空输入返回 `[]`，保留非空字符串按逗号拆分行为。真实函数五项局部断言全部通过；其后 Bugfix 技能 Agent 对同一源码版本完成[定向复验](BUG-001.md#修复版本定向复验)，五项全部通过。

## 1. Goal and Basis

- **Goal and scope** — 仅修复 [解析函数](../../src/parser.py) 空值分支的返回值，不改变拆分分支，不提交、推送或部署。
- **Upstream work** — [BUG-001](BUG-001.md) 的已确认行为、已验证归因及[验收计划与方案](BUG-001.md#验收计划与方案)。
- **Current implementation** — 基线 `d8c2ef4c0289c55bf0d6673b61aa9f6b86e713d5`；`parse` 在 `if not value` 分支返回 `None`，其余输入执行 `value.split(',')`；归因与基线输出见原 Issue。

## 2. Task List

### T001: 恢复空输入并保持非空拆分

- **Basis** — [BUG-001 事实和诊断证据](BUG-001.md#1-issue-facts)，及原 Issue 三类通过判据。
- **Change scope** — 修改 `src/parser.py`；新建本 Plan。Issue 和索引由调度方维护。
- **Implementation** — 将空值分支 `return None` 改为 `return []`，保留原条件与 `split` 分支。
- **Dependencies** — 无。
- **Completion criteria and local verification** — 在项目根目录用 Python 直接导入真实函数，对 `''`、`'alpha,beta'`、`'alpha'`、`'alpha,,beta'`、`','` 分别断言原 Issue 规定的结果，额外断言空输入结果类型为 `list`。局部检查覆盖原 Issue 全部判据；调度方随后按原计划完成[定向复验](BUG-001.md#修复版本定向复验)。
- **Status** — Complete。
- **Results and evidence** — 2026-11-15，在 Python 3.12.3 下运行以下命令，退出码 0，五项结果与预期一致，空输入类型检查通过。修复版本为基线 `d8c2ef4c0289c55bf0d6673b61aa9f6b86e713d5` 加未提交的单行修复；`src/parser.py` SHA-256 为 `3e0d14ca1979f8a546363180e6b36e5c2264897a6cac66e72ab75fbf0c9f49f9`。覆盖原 Issue 空输入恢复、非空拆分保持及直接影响边界保持全部判据，无局部失败。原失败证据保留于 Issue。

从项目根目录运行：

```bash
python -B - <<'PY'
import hashlib
from pathlib import Path
from src.parser import parse
cases = [('', []), ('alpha,beta', ['alpha', 'beta']), ('alpha', ['alpha']), ('alpha,,beta', ['alpha', '', 'beta']), (',', ['', ''])]
for value, expected in cases:
    actual = parse(value)
    assert actual == expected, (value, expected, actual)
    if value == '':
        assert type(actual) is list, type(actual)
    print(f'PASS {value!r} -> {actual!r}')
print('5/5 passed; empty input type is list')
print('src/parser.py SHA-256:', hashlib.sha256(Path('src/parser.py').read_bytes()).hexdigest())
PY
```

实测输出：

```text
PASS '' -> []
PASS 'alpha,beta' -> ['alpha', 'beta']
PASS 'alpha' -> ['alpha']
PASS 'alpha,,beta' -> ['alpha', '', 'beta']
PASS ',' -> ['', '']
5/5 passed; empty input type is list
src/parser.py SHA-256: 3e0d14ca1979f8a546363180e6b36e5c2264897a6cac66e72ab75fbf0c9f49f9
```

## 3. Delivery Checks

- **Goal coverage and completion** — T001 完成，diff 核对仅将空值分支返回值改为 `[]`。本 Plan 语义核对确认上游链接、范围、判据、代码改动及实测结果一致。文档机械检查命令为 `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/issues/BUG-001-plan.md`，退出码 0，检查 1 个 Markdown 文件，0 errors、0 warnings；机械检查不替代上述语义核对。
- **Blockers and next actions** — 无；局部自验及调度方定向复验均已完成。
- **Coverage gaps and applicable follow-up** — 无待验判据。Bugfix 技能 Agent 按[原验收计划与方案](BUG-001.md#验收计划与方案)对相同源码 SHA-256 独立完成[定向复验](BUG-001.md#修复版本定向复验)，五项结果及每项 `list` 类型断言均通过；复验证据及 Issue 状态由调度方维护。
