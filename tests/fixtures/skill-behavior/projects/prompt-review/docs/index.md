# 项目文档

- [已确认退款行为](refund-rules.md)定义预期行为及权限。
- 退款助手的交付版本通过 [load_prompt.py](../src/load_prompt.py) 按模式装配指令。运行 `python3 -B src/load_prompt.py preview` 或 `python3 -B src/load_prompt.py apply` 可读取实际装配层和顺序。此入口只组装文本；夹具没有模型或退款后端。
