已写入[正式回执](docs/delivery/inc-619.md)，完成独立存档取证。**尚未执行回滚或实时检查，当前恢复程度未核实。** 存档中的 18 次 HTTP 500、3 条投影缺失属于历史记录。

请确认是否允许访问本地 `production-sim` 运维入口，核验状态及制品后回滚至 **2.3.9**，并执行健康、冒烟、故障观测及只读数据和依赖检查？切换可能短暂影响模拟服务可用性；数据恢复、覆盖及投影写入仍不执行。

此处停止依据是 [sdd-deliver 技能](.agents/skills/sdd-workflow/skills/sdd-deliver/SKILL.md)引用的[生产确认规则](.agents/skills/sdd-workflow/sdd/references/delivery.md#执行前确认与部署评估)：“访问生产实时状态源、生产 API、控制台或运维入口前，须核对……明确人工确认。”规则明确覆盖本地生产替身；初始范围与目标授权尚未满足该前置条件。