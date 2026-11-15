`review-prompt` 实际执行回执：已完成修订，所有工作留在隔离项目，仅修改授权文件：

- [base.md](src/prompts/base.md)：合并重复的预览要求。
- [apply.md](src/prompts/apply.md)：合并重复确认要求；成功判据改为“取得退款凭证且读回已退款状态”，缺任一项报告“待核实”。

已按 `docs/refund-rules.md` 复核，保留演练例外和失败后一次重试限制。

修改前后均运行本地 `preview`、`apply` 装配，全部通过；`git diff --check` 通过，工作区仅上述两份文件发生变化。

验证局限：项目没有模型及退款后端，本次证明了提示词加载内容和顺序，未验证实际退款行为。