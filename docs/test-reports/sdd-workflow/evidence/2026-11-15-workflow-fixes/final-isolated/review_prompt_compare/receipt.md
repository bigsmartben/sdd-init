`review-prompt` 实际回执：已完成只读对比，未修改文件。**候选版修正了成功判据，但引入确认授权和失败重试两项回退，不建议按现状替换当前版。**

| 核对项 | 结论 |
|---|---|
| R-01 预览 | 两版均符合要求，装配输出相同。 |
| R-02 确认授权 | 候选版新增“紧急退款可免确认”，且遗漏“隔离演练且使用本地模拟适配器”的例外；当前版符合。 |
| R-03 失败重试 | 候选版删除重试前查询状态、确认未退款以及状态未知禁止再次写入的条件；当前版符合。 |
| R-04 成功判据 | 当前版允许接口应答成功即报告“已退款”；候选版改为凭证和已退款状态俱全才报告成功，修正了该问题。 |

实际入口核对结果：

- 当前正式路径：`base.md → apply.md`
- 候选正式路径：`base.md → apply.candidate.md`
- 两版预览：均只加载 `base.md`
- `archived.md` 未被现行配置引用。

实际运行以下四条装配命令，均退出 `0`：

```text
python3 -B src/load_prompt.py apply
python3 -B src/load_prompt.py apply --candidate
python3 -B src/load_prompt.py preview
python3 -B src/load_prompt.py preview --candidate
```

审查依据为 `docs/refund-rules.md`，受审提交为 `7335961f35a8f75f1af0b39ef976dfb14fde3157`。本次验证了装配内容及顺序；行为影响属于静态推断。项目没有模型或退款后端，未执行退款行为。

全程限于隔离项目，未调用退款接口、未写入报告或证据文件；检查时 `git status --short` 为空。