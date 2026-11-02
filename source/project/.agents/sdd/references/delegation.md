# 执行与协作

用户选择讨论模型和推理强度。分发七个独立角色到项目 .codex/agents/；角色仅定义 name、description、developer_instructions，不固定 model 或 model_reasoning_effort，不改写 .codex/config.toml 或用户级配置。

## 按场景选择角色

| 角色 | 场景与产出 | 执行边界 |
| --- | --- | --- |
| sdd-requirements | 新需求、验收反馈／缺陷、需求变更；目标、规则、范围、验收条件和待决项 | 只读分析，不自动写 Issue 或修代码 |
| sdd-architect | 架构设计／变更、重构要求；职责、接口、状态归属、依赖和取舍 | 只读分析，不自动改架构正文或实施整改 |
| sdd-planner | 实施 Plan；修改范围、步骤、依赖、验证和风险 | 返回计划，不编码、不创建 plan.md 或写 PR |
| sdd-documenter | 用 sdd-doc 固化确认内容与制作隔离原型 | 只写授权文档或原型，不改产品代码 |
| sdd-implementer | 用 sdd-imp 实现、修复、重构及局部自验 | 不擅自改需求或架构，不自动部署 |
| sdd-acceptor | 用 sdd-accept 准备指定版本、环境及操作文档 | 不修产品代码，不代替人工判定验收通过 |
| sdd-delivery | 用 sdd-commit 达成授权 Git 交付终点 | 不扩大提交范围或默认合并、关闭 Issue |

重构由架构角色主导分析，业务行为变化交主会话协调需求讨论；明确后按需规划、固化和实施。主会话负责理解意图、分配范围和汇总结果，不再新增总控角色。

## 模型建议（调用时选择）

| 角色 | 建议模型 | 选择理由 |
| --- | --- | --- |
| sdd-requirements | gpt-6-astra | 需求歧义、多条件规则与反馈归因的判断 |
| sdd-architect | gpt-6-astra | 职责边界、状态归属及复杂方案取舍 |
| sdd-planner | gpt-6-astra | 跨模块依赖、实施顺序和风险分析 |
| sdd-documenter | gpt-6.1-terra | 确认内容归并、清晰表达及原型视觉理解 |
| sdd-implementer | gpt-6.1-sol | 持续编码、修复及局部验证 |
| sdd-acceptor | gpt-6.1-sol | 拉取、部署、环境诊断与可执行验收步骤 |
| sdd-delivery | gpt-6.1-terra | 范围明确的 Git 操作、PR 文字和回执整理 |

以上为 2026-11-02 根据[官方模型定位](https://learn.chatgpt.com/docs/models#recommended-models)与角色工作作出的建议，不是强制绑定或实测优劣排名。简单需求或计划可用 Sol，复杂交付冲突可选 Sol 或 Astra；用户明确选择优先。推理强度按实际任务与模型支持选择，不设统一值。调用支持选择模型时可使用建议；不支持或模型不可用时说明限制，沿用用户允许的选择，不虚称切换，也不以建议触发强制委派。

项目角色使用[官方独立 TOML 格式](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)。未固定模型和强度时，实际值按调用、现有运行配置与父会话解析；安装不会把建议写成运行默认值。角色继承父会话权限，职责说明不是额外授权或强制权限隔离。

## 执行与交接

当前执行者在任务范围内完成工作。仅在用户或运行环境允许且独立分工有实际收益时委派，不因 Skill 名、文件数量或流程阶段自动创建子 Agent 或聊天。

实际委派时说明目标、必要来源、写入边界与完成依据，协调共享文件并保留他人改动。执行者返回实际差异、验证证据与未决事项；当前执行者汇总，证据缺口、失败或版本变化时复验相关部分。自查不称为独立审查，不能虚称模型已切换或人工验收已通过。
