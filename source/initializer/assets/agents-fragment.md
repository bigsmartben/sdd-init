<!-- sdd-contract-governance:start -->
## 规则

- 日常开发必须由用户显式调用对应 SDD Skill；未调用时仅讨论、只读分析或提示入口，不自动实施。已启动流程内的状态维护沿用授权；纯讨论不落盘，文档完成不自动授权实施。
- AGENTS 负责入口、导航与沟通，Skill 负责执行流程，项目规范负责约束。先按索引定位相关需求、架构和状态，再遵循已调用 Skill；无需通读全部文档。
- 沿用唯一正文；当前实现与目标不一致时登记偏差，不以代码改写契约。
- 涉及测试用例、验证或验收内容时，遵循[测试范围约束](.agents/sdd/references/governance.md#测试范围约束)，排除视觉相关内容。

### 沟通

- **业务相关**：沿用现行需求、架构与契约的术语。需求讨论按“业务场景 → 预期行为 → 验收条件”；架构/方案讨论按“所属模块 → 能力与接口 → 交互关系”；验收反馈（含缺陷描述）按“业务场景 → 预期表现 → 实际表现 → 验证证据”。区分已确认约定、当前实现与建议变更，不混淆模块职责或完成状态。
- **仓库治理相关**：按“治理事项 → 现行规则 → 问题或调整建议 → 影响范围”描述，引用对应治理规范，不混入产品行为或架构设计。
- 简单问题只保留必要内容，不机械套用完整格式。

## 索引

### 研发入口

| 场景 | 显式调用 |
|---|---|
| 文档落盘 | [sdd-doc](.agents/skills/sdd-doc/SKILL.md) |
| 实施、测试与修复 | [sdd-imp](.agents/skills/sdd-imp/SKILL.md) |
| 独立架构审查 | [sdd-review-loop](.agents/skills/sdd-review-loop/SKILL.md) |
| 需求验收 | [sdd-test-loop](.agents/skills/sdd-test-loop/SKILL.md) |
| Git 交付 | [sdd-commit](.agents/skills/sdd-commit/SKILL.md) |

强制架构约束见[运维与可观测基线](.agents/sdd/references/observability-baseline.md)；设计、实施及审查须定位其项目映射，缺项不能免审。

实体职责与执行规则见[治理约定](.agents/sdd/references/governance.md)；需要分工时读[协作约定](.agents/sdd/references/delegation.md)。
### 关键文件职责

以下为默认路径，已有项目以其现行权威路径和项目索引为准；未创建的能力文件不视为已存在。

| 文件 / 入口 | 职责 |
|---|---|
| `architecture/blueprint.md` | 全局架构、模块边界与不变量 |
| `specs/<capability>/spec.md` | 单个能力的场景、需求与验收条件 |
| `specs/<capability>/status.md` | 当前迭代事实、证据、阻塞与续接入口 |
| 项目现行治理、环境及编码规范 | 文档协作、操作边界和工程约束；按任务定位读取 |

<!-- sdd-contract-governance:end -->
