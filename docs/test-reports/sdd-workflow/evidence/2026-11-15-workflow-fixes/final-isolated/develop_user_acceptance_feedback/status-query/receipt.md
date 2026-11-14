按已有记录，WO-ORDER-018 当前状态是：

- **通过：AC-1。** 提交返回 `true`，关闭并重开数据库后仍为 `submitted`，命令退出码 `0`。
- **待验：AC-UX。** 你尚未提供亲自操作后的观察与判断，整体验收仍待验。
- **未执行：AC-2、AC-3。** 两项不在本轮工单验收范围。

本轮候选和运行条件未变化，沿用已有 AC-1 证据，无需重跑。

下一步，请在当前隔离项目终端执行：

```bash
python -B checks/receipt_preview.py
```

反馈实际输出、操作时间，以及：你理解的当前状态和下一步是什么，提示是否足以独立判断，有哪些不清楚的地方。收到后按原 AC-UX 判据记录结论。

详见[工单验收记录](docs/order-review-work.md)与[原始证据](docs/test-reports/order/wo-order-018-ac1.json)。