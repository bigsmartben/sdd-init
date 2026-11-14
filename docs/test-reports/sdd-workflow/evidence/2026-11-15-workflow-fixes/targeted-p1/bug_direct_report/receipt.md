已修复：[src/parser.py](src/parser.py) 的空输入分支原先显式返回 `None`，现改为 `[]`。

实际验证 4/4 通过：空字符串返回空列表；`a,b`、`one`、`a,,b` 保持原有拆分行为。

修复证据已记入 [BUG-001](docs/issues/BUG-001.md)。仅操作当前隔离项目，未提交或推送。