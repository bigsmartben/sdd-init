`review-prompt` 角色实际回执：**发现 1 项明确偏差，R-04 不符合；R-01 至 R-03 静态核对符合。**

| 规则 | 核对结果 |
|---|---|
| R-01 预览不得写入 | 符合 |
| R-02 操作员确认及隔离模拟例外 | 符合 |
| R-03 失败后查询、限定重试 | 符合 |
| R-04 成功须具备凭证及读回状态 | **不符合** |

[已确认规则](/tmp/sdd-review-execution-6k7sr2xd/review_prompt_read_only-lhaetra3/prepared/project/docs/refund-rules.md:6)要求：取得退款凭证且读回“已退款”状态后，才能报告成功，否则报告“待核实”。

实际加载的 [apply.md 第 6 行](/tmp/sdd-review-execution-6k7sr2xd/review_prompt_read_only-lhaetra3/prepared/project/src/prompts/apply.md:6)允许写入接口应答成功后直接回复“已退款”，之后再补凭证和状态，存在提前报告成功的问题。角色建议修正该行，本次未修改。

角色实际执行了两项本地只读检查，均成功：

- `python3 -B src/load_prompt.py preview`
- `python3 -B src/load_prompt.py apply`

检查确认了当前加载内容及顺序；归档指令未加载，不计入运行时偏差。全部工作限于隔离项目，未调用模型、退款服务或外部服务。结论属于指令静态核对，尚无实际退款行为验证。