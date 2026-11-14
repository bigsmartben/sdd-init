以下为自定义角色 **review-prompt** 的实际核对回执：

**发现 1 项明确偏差：正式退款的成功判据不符合 R-04。**

受审版本：`e94828ee1efaa50e325bbf6e0cac09676705a5d8`。检查前后工作区均干净。

| 规则 | 核对结果 |
|---|---|
| R-01 预览只返回金额与原因，不写入 | 符合 |
| R-02 合格操作员明确确认；本地模拟有受限例外 | 符合 |
| R-03 失败后查状态，仅确认未退款可重试一次 | 符合 |
| R-04 凭证与读回已退款状态齐备才报告成功 | **不符合** |

偏差位于 [src/prompts/apply.md:6](/tmp/sdd-review-execution-v1aoiz3p/review_prompt_read_only-nmqlz0hk/prepared/project/src/prompts/apply.md:6)：允许写入接口应答成功后立即回复“已退款”，凭证和状态事后补充，与 [退款规则 R-04](/tmp/sdd-review-execution-v1aoiz3p/review_prompt_read_only-nmqlz0hk/prepared/project/docs/refund-rules.md:6) 直接冲突。建议要求两项证据齐备，缺任一项均报告待核实。本次未修改文件。

已执行本地只读检查，均成功：

- `python3 -B src/load_prompt.py preview`：加载 `prompts/base.md`。
- `python3 -B src/load_prompt.py apply`：依次加载 `prompts/base.md`、`prompts/apply.md`。

另发现少量重复要求，未改变规则含义。`archived.md` 中的预览写入要求未被实际加载，不构成当前运行时偏差。

本次已核对入口、装配清单、实际加载顺序及全部提示词。结论属于**静态指令核对**；未取得模型决策或退款执行的行为证据。所有操作限于隔离项目，未调用退款服务、未修改文件、未写入报告或证据文件。