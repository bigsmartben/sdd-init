# 订单协作评测夹具

本目录是故意保留初始缺陷的测试代码资产，用于在隔离副本中验证 Agent 协作；不属于产品实现，不连接真实外部服务。实际依据和运行入口见 [项目索引](docs/index.md)。

使用 Python 标准库，工作目录为本夹具生成的项目根目录：

```powershell
python -B -m unittest discover -s tests -v
python -B checks/acceptance.py
python -B checks/runtime_details.py
```

验收命令返回 0 表示所选场景通过，1 表示存在失败，3 表示存在阻塞。结果来自本次真实执行，不预存通过回执。
