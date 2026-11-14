# T001 解析器局部自验

两条判据：空输入返回空列表；`one,two` 返回两个元素。运行 `python -B -m unittest discover -s tests -v`。记录实际版本、环境和两个用例，后续独立验收不在本轮。

## 局部自验证据

- 状态：T001 局部实现及本轮局部自验完成；后续独立验收待执行。
- 执行者与时间：Main（本轮记录补记者）；2026-11-15T00:29:49+08:00。
- 实际版本：分支 `main`，提交 `e880e3e4883e649b5834429ef20235a2f90a335f`；测试前工作树干净，实现及测试无未提交变更。
- 环境与入口：当前隔离项目根目录，Python 3.12.3，Linux 6.6.114.1-microsoft-standard-WSL2 x86_64；已有 [解析器实现](../src/parser.py) 与 [定向测试](../tests/test_parser.py)，无需外部服务。
- 命令：`python -B -m unittest discover -s tests -v`；退出码 `0`。

| 用例 | 工单判据／输入 | 实际结果 | 局部自验结论 |
| --- | --- | --- | --- |
| `ParserTest.test_empty` | 空字符串返回空列表 | 断言 `parse('') == []` 通过 | PASS |
| `ParserTest.test_split` | `one,two` 返回两个元素 | 断言 `parse('one,two') == ['one', 'two']` 通过 | PASS |

实测输出：

```text
test_empty (test_parser.ParserTest.test_empty) ... ok
test_split (test_parser.ParserTest.test_split) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

覆盖：2 项计划用例，2 项通过，0 项失败、未运行或阻塞。上述证据仅证明工单两条判据的局部自动验证，不构成独立验收、架构复核或集成测试结论；本轮无人工反馈判据。后续独立验收须在另行授权后核对候选版本及证据适用性。
