# 文档写入规则

实际写入者（含直接写入的 Main）依据已确认结论或真实执行证据，在授权内原位更新正文并完成写后检查。

1. **取证**：读取目标正文、同义条款、直接引用及写入范围内适用的项目资料与共享条款，以已确认结论或用户指定来源为依据。沿用已定位的权威实体；需要定位时查[文档与产物落点](sdd-repository-governance.md#文档与产物落点)。内容层级难以判断时查[场景提示](scenarios.md)，按问题核对需求与架构各自的权威依据。
2. **归并**：沿用已有记录，不自动迁移历史。原位保留唯一正文，其他位置引用，删除已替代、失效或重复表述，不追加变更说明。保留稳定编号、追溯关系及不同对象、前提、条件、例外、禁止项和验收含义；下位不得改变上位要求。
3. **同步与核对**：更新受影响条款；入口新增、移动或替代时同步索引与直接引用。读回文件并对照来源、diff 和下表核对完整性、归属及可执行前提，迁移同样逐项核对承接。检查术语、结构、编号、表格、链接、锚点、编码；模板链接按产物实际目录重定位。
4. **机械检查**：按[文档 CLI 用法](doc-check.md#使用)对修改及直接受影响的 Markdown 执行校验，不默认全仓扫描；失败后修复并复查，无关存量问题不扩大范围。CLI 不替代语义、条件例外或证据充分性的判断。
5. **处理缺口**：来源不清、未确认或冲突的内容保留为待决。在回执中记录新取舍、不可执行的要求、跨归属写入和无法消歧的问题，附位置、影响与待决项。

完成时报告落点、关键归并、检查命令与范围、诊断、语义结论及未检查／未解决项。设计写入影响已初始化矩阵时，按[矩阵维护契约](sdd-repository-governance.md#目标仓库的-code-review-rules)向 Main 交接变化与受影响项，由重构技能同步并展示确认。其余关联 Code Review Rules 可能过时的情况简短提醒用户决定维护时机，不扩为全量检查。

## 按对象读取与语义核对

按对象与语义影响选用下表，已有结构内的修改同样适用；不加载无关资源或机械填满模板。模板只规定结构、字段及填写约束，不授予设计或执行权限。

| 对象 | 读取依据与结构参考 | 写后判断点 |
|---|---|---|
| Spec | 项目索引、权威实体、[Spec](../assets/spec_template.md) | 承接适用高位用例与验收维度，或引用足以明确本次行为与判据的已确认工单或其他权威依据；详细行为、条件、异常及 AC 完整；不复制蓝图同层级正文，不把实现缺陷写成需求变化 |
| Blueprint | [Blueprint](../assets/blueprint_template.md#architecture-modeling-and-assessment) | 保持产品与架构的高位抽象，承接已确认设计并核对内部一致性及引用。由重构技能初始化后保留规范和独立矩阵的固定链接，不复制矩阵正文；设计写入本身不加载 checklist 或执行实现符合性检查，影响既有矩阵时按维护契约交接 |
| Technical Research and Selection Report | [Technical Research and Selection Report](../assets/research_template.md)、适用的需求与设计约束、实际调研材料及证据 | 按需归并调研问题、比较标准、候选方案、依据和取舍，核对证据适用条件及确认来源；建议待确认时标明待决问题，已确认的架构决定归 Blueprint 或项目已有 ADR，实测结果引用对应报告 |
| Interface Contract | Architecture Modeling and Assessment、适用 Blueprint／ARC、[Interface Contract](../assets/contract_template.md) | I/O、调用双方、状态与副作用归属、受理／完成及异常语义承接确认内容 |
| Scenario Sequence | Architecture Modeling and Assessment、需求与契约、[Scenario Sequence](../assets/sequence_template.md) | 参与者、请求／回执、先后／并发、取消／迟到、未知／恢复承接契约；箭头不暗示未确认成功或同步等待；结果和进度引用报告及 Status／任务 |
| Prototype Reference | [原型规则](prototype.md)、[Prototype Reference](../assets/prototype_reference_template.md) | 核对入口、固定版本、模拟边界及确认来源，按适用规则保留历史版本 |
| Test Report | [Test Report](../assets/test_report_template.md)、实际执行证据。需核对验收边界时读[测试范围约束](sdd-repository-governance.md#测试范围约束) | 核对适用字段、未执行项和批次归属；集成测试另核对完整报告结构和统计，简单工单可在原记录保留足够证据。Bug 归因、修复自验、定向复验、需求验收及集成回归分别引用对应版本的事实，集成 Test Gate 关联实际目标版本、环境、完整覆盖及未通过原因，人工待验与执行结果分别记录，反馈取自用户 |
| Issue | [Issue](../assets/issue_template.md)、原工单和实际执行证据 | 核对稳定编号、处理历史、验收计划与方案、修复及报告／Task 引用。按[Issue 关单](sdd-repository-governance.md#issue-关单)核对状态、授权及其依据。平台议题按授权单独处理 |
| Architecture Review Record | [Architecture Review Record](../assets/review_template.md)、原检查项和实际执行证据 | 在原检查项下维护工单与 Task 引用、验收计划与方案及历次结果。分别关联架构复核与业务行为保持验收的判据、整改版本和证据。Review Gate 依据适用架构检查，实施方案与局部自验归原 Task |
| Review Matrix | [Review Matrix](../assets/review-matrix_template.md)、已确认 Blueprint／契约、项目规则及适用 checklist | 由重构技能维护，按项目层级及协作边界映射规则、方法和判据；首次内容及受影响增删改先展示确认，再归并并维护蓝图链接；保留编号、适用条件及例外。批次任务、结果与证据归专用审查记录 |
| Delivery Record | 已授权的交付或运维终点、项目运行指南、实测回执及适用证据，首次建档用 [Delivery Record](../assets/delivery_record_template.md) | 核对实际版本、环境、目标对象、步骤回执、运行验证与恢复效果。未完成项保留影响及恢复条件，适用的架构或集成结论引用原证据 |
| Plan | [Plan](../assets/plan_template.md)、实施执行者的方案、任务与证据 | 保留同一计划及编号；按单项轻量、多文件／依赖完整、长程恢复点选择分档，核对上游验收计划与方案的引用、依赖、Task 完成条件、局部证据覆盖与仍待验的判据。Bug Task 引用原 Issue 和归因检查证据，方案、拆分与任务完成判断取自实施执行者。 |
| Quickstart | [测试范围约束](sdd-repository-governance.md#测试范围约束)、[Quickstart](../assets/quickstart_template.md) | 核对验收产品范围内已确认功能点与场景／AC 的覆盖关系，以及版本、环境、入口、数据、步骤、观察点、通过判据和必要复位。实际结果归 Test Report，报告引用本轮指南 |
| Status / Current Task | Test Report、执行者状态；新建时用[Status](../assets/status_template.md) | 按[运行状态与接续](sdd-repository-governance.md#运行状态与接续)更新进度；版本、覆盖及状态与证据对应，逐项结果、Gate 和人工反馈使用引用 |
| README / Project Index | 项目权威正文、工程资产规则 | 只定位导航，已有正文不继续指向模板；同步直接受影响入口 |

## Code Review Rules

重构初始化、矩阵同步或用户单独要求生成／更新规则时，按[规则与矩阵维护契约](sdd-repository-governance.md#目标仓库的-code-review-rules)定位正文。依据已确认 Blueprint、契约及实际路径选用[架构规范](architecture-rules.md)的 checklist，将适用项按 [Code Review Rules](../assets/code-review-rules_template.md)写成项目可检查规则，已有合格规范可直接引用。同义规则原位归并，保留稳定标识和有效例外；受影响增删改展示确认后归并。缺乏设计依据的归属或冲突列为待决。对象映射归独立矩阵，执行证据归本轮 Review。
