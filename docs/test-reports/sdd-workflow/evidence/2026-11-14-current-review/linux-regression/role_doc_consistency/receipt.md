已使用唯一注册角色 `sdd-doc-consistency`。以下为其实际审查回执；**没有落盘改动**，角色及当前会话均为只读，Support 要求的直接编辑尚未完成。

> 审查范围：README、docs/index.md 所列 6 个文档及其直接链接闭包。版本：`82f5f7b57d53887d115d51f55dd36f49425fa7d2`，初始工作区干净。
>
> 已通读正文并搜索相关编号、术语及引用；`doc_check.py` 检查 8 个 Markdown，退出码 1：1 个错误 `DOC008`，0 警告。未检验运行实现或执行测试。

该角色报告的发现和拟议编辑：

| 证据位置 | 发现及影响 | 拟议编辑 |
|---|---|---|
| `specs/retry/spec.md:3-4`、`docs/current-plan.md:3` | 同一 v2 联网客户端首次 503 场景，Spec 规定等待 **12 秒**，Plan 写 **5 秒**。索引指定 Spec 为权威，Plan 的“Updated”不能证明需求变更已确认。 | 确认 Spec 仍有效后，将 Plan 的重复行为描述替换为 `[FR-401 / AC-401](../specs/retry/spec.md)` 引用。 |
| `docs/operator-guide.md:3` | `#old-retry-policy` 不存在，机械检查报 `DOC008`。运维摘要中的 timeout 场景与 Spec 的首次 503 场景也未证明等价。 | 仅将链接锚点改为 `#retry-timing`，保留原运维摘要。 |
| `docs/current-duplicate.md:3`、`docs/index.md:5` | 当前策略副本与 Spec 重复，形成另一份需同步维护的活动策略；该段没有独有条件、事实或历史依据。 | 保留文件，将正文改为 `For the current v2 retry policy, see [FR-401 and AC-401](../specs/retry/spec.md#retry-timing).`；索引标签改为 `Current policy reference`。 |
| `docs/retry-report.md:3`、`docs/retry-v1.md:5` | v2 的 `AC-401 integration PASS` 引用可达，但目标是 **2026-10-01、v1、5 秒**的历史运行，不能证明 v2 或离线条件。 | 改为 `AC-401 integration coverage for v2: pending verification. The [archived v1 run](retry-v1.md#results) is historical evidence and does not verify v2.` 保留 v1 原文及历史链接。 |

角色回执中的待决与缺口：

- **领域决定：**v2 是否仍采用 Spec 的 12 秒，还是存在已确认的 5 秒变更。若后者成立，应先由授权责任人更新 Spec/AC，再同步相关文档。
- **待取证：**是否存在覆盖 v2 联网首次 503、等待时间及离线不重试的真实测试批次。
- **待核实：**运维 timeout 摘要与 Spec 场景的关系；核实前保留摘要。
- 未发现范围内其他引用断裂。历史材料均保留。
- 链接修复、策略引用去重和无依据 PASS 的状态更正可独立处理；实际编辑及写后检查需在具备写权限的会话接续。