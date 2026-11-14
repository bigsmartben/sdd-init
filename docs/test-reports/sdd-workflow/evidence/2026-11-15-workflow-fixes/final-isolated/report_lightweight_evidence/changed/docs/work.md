# T001 解析器局部自验

两条判据：空输入返回空列表；`one,two` 返回两个元素。运行 `python -B -m unittest discover -s tests -v`。记录实际版本、环境和两个用例，后续独立验收不在本轮。

## 局部自验证据

- 状态：Complete（已有局部实现及本工单局部自验完成；独立验收待执行）。
- 实现：`src/parser.py` 的 `parse` 在空输入时返回 `[]`，否则按逗号拆分；本轮未修改实现或测试。
- 执行时间：2026-11-14T16:41:49Z（UTC）。
- 实际版本：分支 `main`，HEAD `49635969dd435824814df0c1821757f0d0551eb4`；执行前工作区干净，实现与测试无未提交差异。
- 文件 Git blob：`src/parser.py` 为 `b57197cae8f72351669075797a46dedb6732c6d3`；`tests/test_parser.py` 为 `740ca354677b92f9d5b258c66eb967450e4b3b3c`。
- 环境：当前隔离项目根目录；Python 3.12.3，GCC 13.3.0；Linux 6.6.114.1-microsoft-standard-WSL2，x86_64，glibc 2.39。
- 命令：`python -B -m unittest discover -s tests -v`。

| 用例 | 判据与断言 | 局部自验结果 |
| --- | --- | --- |
| `test_parser.ParserTest.test_empty` | `parse('') == []` | PASS |
| `test_parser.ParserTest.test_split` | `parse('one,two') == ['one', 'two']` | PASS |

实际测试输出：

```text
test_empty (test_parser.ParserTest.test_empty) ... ok
test_split (test_parser.ParserTest.test_split) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

测试进程退出码为 0。证据仅证明上述两个用例的局部自验，不构成独立验收、架构复核或集成 Test Gate。后续独立验收仍待执行；接续时核对候选版本与本次证据的适用性，按原两条判据取证。当前进度见 [Status](status.md)。
