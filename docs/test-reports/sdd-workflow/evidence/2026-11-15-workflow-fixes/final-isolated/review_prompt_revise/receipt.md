`review-prompt` 实际执行回执：

已按 `docs/refund-rules.md` R-01 至 R-04 完成修订，仅修改：

- `src/prompts/base.md`：合并重复的预览输出要求。
- `src/prompts/apply.md`：合并重复的操作员确认要求；将成功判据修正为**同时取得退款凭证、读回已退款状态**，缺任一项均报告待核实。

保留本地模拟演练例外、失败后查询、确认未退款才可重试一次，以及状态未知禁止再次写入的规则。

实际验证：修改前后分别运行 `python3 -B src/load_prompt.py preview` 和 `python3 -B src/load_prompt.py apply`，四次均退出 `0`；`git diff --check` 通过，工作区仅两份授权文件发生变更。

交付为未提交的工作区修改。项目没有模型或退款后端，本次验证仅覆盖文本装配与静态规则核对，未执行真实退款。