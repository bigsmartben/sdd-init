T001 已完成：全空白订单号报错且不写入，合法编号保持原值。AC-4 和原 AC-1 回归通过，改动尚未提交。见[验收记录](docs/order017-acceptance.md)。

T002 暂停：SQLite 仅保存当前状态，无法还原逐次历史。需改变 schema、全部状态写路径并决定旧数据策略，超出[原工单](docs/order-export-work.md)授权。

请选择：延后 T002，或另行授权前置架构／迁移设计。此次确认源于工单的明确限制及[设计约束](docs/export-design.md)。