已实际调用自定义角色 `review-prompt`。以下为其真实回执：

**审查结论：发现 1 项高优先级偏差，正式退款过早报告成功，违反 R-04。**

问题位于 [src/prompts/apply.md:6](/tmp/sdd-targeted-2duuze52/project/src/prompts/apply.md:6)：

> 写入接口应答成功即可向操作员回复“已退款”。凭证和状态可在之后补充。

这允许在凭证缺失或尚未读回已退款状态时报告成功，与 [docs/refund-rules.md:6](/tmp/sdd-targeted-2duuze52/project/docs/refund-rules.md:6) 要求冲突。R-04 要求同时取得退款凭证、读回已退款状态，否则应报告“待核实”。

| 规则 | 角色核对结果 |
|---|---|
| R-01：预览返回金额及原因，不写入 | 静态符合 |
| R-02：操作员资格、本笔确认及隔离演练例外 | 静态符合 |
| R-03：失败后查状态，限制重试，未知则待核实 | 静态符合 |
| R-04：凭证与状态双重确认后才报告成功 | **不符合** |

角色实际执行了两个本地只读检查，均成功：

- `python3 -B src/load_prompt.py preview`：加载 `prompts/base.md`。
- `python3 -B src/load_prompt.py apply`：依次加载 `prompts/base.md`、`prompts/apply.md`。

另发现两处不影响规则含义的重复表述。归档提示词虽包含预览写入指令，但未进入当前装配，因此未计为现行缺陷。

本次仅验证指令内容和加载顺序，未进行模型行为或退款后端验证。全程仅访问当前隔离项目，未修改文件，未调用退款服务或真实外部平台。