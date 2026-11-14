# 工作流 Review 报告 · 2026-11-15 修复与最终回归

## 范围与版本

用户明确启动 `$sdd-workflow-review`，随后确认修复 F01–F11，并要求完成全部逐项 Review、修复和定向复验后，再运行最终隔离回归。授权覆盖仓库工作流源码、相应测试夹具和报告。沿用白皮书既定设计、Spec 产品承诺、RW 编号和判据。真实生产、外部平台、主机的已安装工作流和真人业务验收不在本次执行范围。初审事实及证据保留在原批次。[初审报告归档](evidence/2026-11-15-workflow-fixes/initial-review-references.zip) · [受审白皮书归档](evidence/2026-11-15-workflow-fixes/before-sources.zip) · [Spec](../../../specs/platform-independent-sdd/spec.md) · [受审 RW 判据归档](evidence/2026-11-15-workflow-fixes/before-sources.zip)

- 基线 HEAD `f059378784e9833f7f4fd3363fa76516a35dc15c`。归档原始及补录清单共 135 个受审输入的原字节，包括当时的未提交、未跟踪资源。5 个已跟踪缺失路径仍缺失。两个压缩包分别保存原字节和修改后 21 个输入的字节，可按清单核对 SHA-256。[修复前清单](evidence/2026-11-15-workflow-fixes/before-manifest.json) · [原字节](evidence/2026-11-15-workflow-fixes/before-sources.zip) · [修改后的字节](evidence/2026-11-15-workflow-fixes/fixed-sources.zip)
- 最终候选 `final-v2` 固定 158 个输入。源码清单 SHA-256 `207b6815958537fca02ecae96449d90c301dc9cb650ab6da881fee36598c7aec`；分发清单 SHA-256 `4df59f14ac34ab2b8e9eb16ce10593ed24706070949396e3ca135b5bcd80d727`。相对原受审快照有 21 个改动项；新增到清单的构建、夹具与文档校验输入另列。首个最终启动未进入模型：包构建在冻结树产生了 `egg-info`，且审核所需的历史引用目标未复制。`final-v2` 将包构建移到一次性副本，补齐引用目标，并排除生成的打包元数据。两版分发清单一致。[冻结输入](evidence/2026-11-15-workflow-fixes/final-v2-manifest.json) · [分发清单](evidence/2026-11-15-workflow-fixes/final-v2-build-manifest.json) · [修复差异](evidence/2026-11-15-workflow-fixes/source-fixes.diff) · [第一次文档检查](evidence/2026-11-15-workflow-fixes/final-v1-mechanical/doc-check.log)
- 2026-11-15，Asia/Shanghai。Windows 运行机械检查和临时 wheel 安装；Ubuntu WSL2 运行 Codex CLI `0.169.0`、Python `3.12.3`、本地文件 SQLite、Chromium 和文件型运维替身。行为用例以 `gpt-6.1-sol`／`medium` 发起，注册角色配置和实际模型见会话。独立用户配置只信任夹具，shell 禁网、审批设为 `never`，评估者输入和主工作区位于夹具权限范围外。原生 Windows MXC 的恢复证据沿用初审；本批可执行行为从 WSL 重新取证。[隔离执行器与审计脚本](evidence/2026-11-15-workflow-fixes/isolation-harness.zip) · [上批 MXC 证据归档](evidence/2026-11-15-workflow-fixes/initial-review-references.zip)

- 本地提交按归档差异提取 F01–F11 的修复，纳入新增回归用例所需的入口、注册和直接引用。逐对象和逐 RW 的隔离证据对应完整的 `final-v2` 冻结候选。修复前归档按仓库相对路径保存白皮书、评审 Skill、RW 判据、成本规则和 review-prompt 角色。初审引用归档保存原报告和 Windows 探针回执。

## 综合结论

F01–F11 已按原判据完成修复和定向复验。`final-v2` 执行 48 个隔离用例，覆盖 15 个对象与 36 个 RW 子项。F05 在原组合实际执行 Bugfix → Main → 原测试 Agent 的版本交接。该组合 32 次可归属调用中，无同层或越级直传，19 项本地场景通过，外部 AC-3 仍阻塞。F08 的四个未确认场景无运行入口调用和活动数据直读，只确认查询的场景未改变运行状态。动态状态查询和冷接续也取得证据。最终回归保留 53 次用例尝试，夹具预设故障按业务 Gate 判定，真实外部和扩展路径的证据缺口另列。[逐例判定](evidence/2026-11-15-workflow-fixes/final-behavior-index.json)

## 逐对象覆盖

| 对象／版本／入口 | 适用 RW 子项 | 静态结论与证据 ID | 行为结论与证据 ID | 交付闭环结论 | 发现 ID／未验与理由 |
| --- | --- | --- | --- | --- | --- |
| [Main](../../../source/project/.agents/sdd/references/sdd-repository-governance.md#职责与交接) | 01.1–02.3、04.1、07.2、08.2–08.3、09.1–09.3、10.1、12.3 | 符合，S01、S02。三类入口、授权终点和状态接续明确。 | T01、T02、T04、T05；R01、R07、R09、R12、R16、R18。 | 按原调用链接续及回报用户，原执行者不可用时用原证据交新执行者。 | F01、F02、F03、F05、F06、F11。 |
| [共享治理与模板](../../../source/project/.agents/sdd/references/document-writing.md) | 05.1–05.3、06.1–06.3、07.1–07.3、08.1、10.2、11.1–12.3 | 符合，S01–S06。权威归属、合格依据、轻量记录及历史引用。 | T03–T06；R06、R08、R10、R11。 | 规则、产物及实测证据可追溯。 | F03、F04、F06–F11；长期成本未测。 |
| [sdd-develop](../../../source/project/.agents/skills/sdd-develop/SKILL.md) | 01.1–02.3、03.1、03.3、04.3、06.1–06.3 | 符合，S01、S03、S04；两次确认和异常授权保持同一边界。 | T01、T03–T05；R07、R09–R12。 | 分别取证讨论、只规格、实施、逐 AC 验收及独立前置。 | F01、F04、F06、F11；R17 为正式候选集成入口的合成对照。 |
| [sdd-architecture](../../../source/project/.agents/skills/sdd-architecture/SKILL.md) | 01.1、01.3、02.2–02.3、05.2、08.1 | 符合，S07。证据推翻关键假设时回到方案比较，正式写入需确认。 | T04；R05、R12。 | 已确认设计归并及反证后待决定各有证据。 | 真实架构迁移、恢复未验。 |
| [sdd-refactor](../../../source/project/.agents/skills/sdd-refactor/SKILL.md) | 03.2–03.3、04.2–04.3、06.1–06.3、07.1 | 符合，S05。复核、保持、可开测条件与 Gate 独立。 | T05、T06；R02、R06、R12。 | 原检查项回溯整改及保持证据；历史失败保留。 | F09、F11；真人反馈未验。 |
| [sdd-bugfix](../../../source/project/.agents/skills/sdd-bugfix/SKILL.md) | 01.3、04.2–04.3、06.1–06.2、07.1–07.2 | 符合，S02。角色先交实际调用者，原 Issue 按证据处理。 | T01、T02；R01、R03。 | 原缺陷关闭、只复验失败与范围外缺陷登记各有样本。 | F03、F05；需外部证据的关单待验。 |
| [sdd-test-loop](../../../source/project/.agents/skills/sdd-test-loop/SKILL.md) | 01.2、04.2、06.1–06.3、07.2–07.3、11.3 | 符合，S05。阶段内测试资产恢复与用户验收各有正文。 | T02、T06；R01、R02、R04、R17、R18。 | 重跑原断言、实测候选、冷接续和 Gate 交付有证。 | F07、F09；无外部端点时保留阻塞。 |
| [sdd-deliver](../../../source/project/.agents/skills/sdd-deliver/SKILL.md) | 01.2–01.3、04.1–04.3、06.1、06.3、07.3 | 符合，S02、S06。告知、确认、证据和操作边界可定位。 | T07、T08；R13–R15。 | 按最终候选证据停点，覆盖确认后复验和部分恢复。 | F03、F08；真实生产未验。 |
| [sdd-product-manager](../../../source/project/.codex/agents/sdd-product-manager.toml) | 01.1、01.3、05.2、06.3、12.2 | 符合，S03。实质变化回实际调用者，原型关联实际版本。 | T03；R05。单独注册及 Chromium 四检查。 | 交本地候选和模拟证据，确认保持待验。 | F01、F04；真实体验未验。 |
| [sdd-architect](../../../source/project/.codex/agents/sdd-architect.toml) | 02.2–02.3、05.2、06.1、10.3 | 符合，S02、S07。核对设计与复核职责。 | R02、R05、R06。 | 保留原检查项，归并已确认架构。 | 真正迁移和外部装配未验。 |
| [sdd-coder](../../../source/project/.codex/agents/sdd-coder.toml) | 03.1、03.3、04.2、06.1–06.2、07.1、11.2 | 符合，S02、S07。工单输入、同一 Plan、局部自验和待验。 | T04；R03、R05、R07。 | 实际调用、相称自验与独立下一步可定位。 | F02、F06；独立接受另有执行者。 |
| [sdd-devops](../../../source/project/.codex/agents/sdd-devops.toml) | 04.3、06.1、06.3、07.3、11.3、12.2 | 符合，S02、S06。操作和回执遵循实际调度。 | T08；R05、R13–R15。 | 保护无关暂存，读回操作结果并保留恢复缺口。 | F03、F08；真实生产未验。 |
| [sdd-doc-consistency](../../../source/project/.codex/agents/sdd-doc-consistency.toml) | 05.1–05.3、07.3、10.3、12.1–12.2 | 符合，S02、S07。保留只读工单及提示词专项边界。 | R05、R08。 | 实际接单、四类发现、零写入。 | 保留点是测试数据中的故意冲突。 |
| [review-prompt](evidence/2026-11-15-workflow-fixes/before-sources.zip) | 04.3、05.1–05.3、06.1–06.3、10.3、12.1–12.2 | 符合，S07。专项观察、对比和授权写入终点明确。 | R08。三类实际提示词工单和评审中的专项回执。 | 专项交调用方，结论按装配或实际运行范围。 | 真实退款不可测。 |
| [sdd-workflow-review](evidence/2026-11-15-workflow-fixes/before-sources.zip) | 04.3、06.1–06.3、08.1、10.1、11.1、12.1 | 符合，S07。触发、固定证据与修复授权可追溯。 | R08；M01。 | 实际专项调用、36 子项、报告写入边界和读回。 | 合成待办助手业务行为未运行。 |

## 逐 RW 子项覆盖

下列「符合」限于已运行样本。行为证据不足时分别说明静态条款、已测范围和缺口。

| RW 子项 | 设计条款／Spec | 对象及场景 | 静态结论／证据 ID | 行为结论／证据 ID | 本项结论／发现 ID／缺口 |
| --- | --- | --- | --- | --- | --- |
| RW-01.1 | S1／FR-025 | Main、需求、产品的异常决定 | S01、S03；实质业务变化需决定。 | R09；自动取消候选停在确认。 | 符合；F01。 |
| RW-01.2 | S1／FR-025 | A/B 及发布授权复用 | S01、S03、S06；适用确认可复用。 | R09、R15；已确认的执行继续。 | 符合。 |
| RW-01.3 | S1／FR-025 | 新异常、设计反证、生产影响 | S01、S03、S06、S07；重新对齐实质变化。 | R09、R12、R14；范围外结果提请决定。 | 符合；F01。 |
| RW-02.1 | S2／FR-029 | Main 派单与开发前置 | S01、S02；范围、排除、判据与终点。 | R07、R09、R12；可核对工单及范围。 | 符合；F06。 |
| RW-02.2 | S2／FR-029 | 技术调查、架构假设 | S01、S07；授权内实验可执行。 | R04、R12；实际工具取证及临时 SQLite 验证。 | 符合。 |
| RW-02.3 | S2／FR-029 | 设计反证、依赖调查 | S01、S03；新约束核对原决定。 | R12；当前数据无法重建历史。 | 符合；F06。 |
| RW-03.1 | S3／FR-020、029 | 局部实施及无 Blueprint 规格 | S01、S04；合格工单能作为依据。 | R07、R10；局部工单在原范围交付。 | 符合；F04。 |
| RW-03.2 | S3／FR-020、029 | 付款结构和业务保持 | S05；架构与保持分开验。 | R02、R06；局部对齐、已知业务缺陷保留。 | 符合。 |
| RW-03.3 | S3／FR-020、029 | 历史导出前置 | S01、S03；阻塞只沿实际依赖。 | R12；T001 继续，T002 有条件暂停。 | 符合；F06。 |
| RW-04.1 | S4／FR-005、031 | 已授权阶段和独立备份 | S01、S02、S06；达前置后接续。 | R01、R02、R09、R15。 | 符合。 |
| RW-04.2 | S4／FR-005、031 | 缺陷复验、测试资产故障、重构交接 | S01、S05；原判据重跑与局部阻塞。 | R01–R04、R15；夹具保留预设失败和后续。 | 符合；F09。 |
| RW-04.3 | S4／FR-005、031 | 只讨论、只审、场景限权、生产停点 | S01、S02、S06；按实际授权终点。 | R03、R06、R08–R10、R13–R15。 | 符合；F08。 |
| RW-05.1 | S5／FR-001、006 | 测试工具归属、文档冲突、模板轻量化 | S02、S04、S05；唯一正文及替代及时引用。 | R04、R08、R10–R11；历史兼容。 | 符合；F04、F07、F10。 |
| RW-05.2 | S5／FR-001、006 | 按工单归并、索引与模板 | S03、S04、S07；同步直接入口和权威引用。 | R05、R08、R10–R11；M01。 | 符合；F04、F10。 |
| RW-05.3 | S5／FR-001、006 | 保留历史和有效例外 | S04、S07。 | R08、R11；资产差异及角色回执。 | 符合所测。 |
| RW-06.1 | S6／FR-008、009、010、026 | 局部、集成、架构、上线和显示证据 | S03–S06；阶段不互替。 | R02、R05–R08、R11、R15、R17。 | 符合已测；F04、F09。正式 UI 仅有合成产品证据。 |
| RW-06.2 | S6／FR-008、009、010、026 | 需求、重构、集成及缺陷复验 | S01、S03、S05；缺证与失败留档。 | R01、R03、R04、R12；合成反馈有实际观察。 | 符合合成路径；F11。真人行为待验。 |
| RW-06.3 | S6／FR-008、009、010、026 | 原型、有效证据、实际候选 | S03–S06；证据限版本环境与覆盖。 | R01、R04、R05、R08、R14–R15、R17。 | 符合所测。 |
| RW-07.1 | S7／FR-005、009、031 | Main、工单、持续状态和恢复 | S01、S02、S04；保存关键时点。 | R01、R04、R09、R12；状态及原证据实际读取。 | 符合已测状态；F11。 |
| RW-07.2 | S7／FR-005、009、031 | 原测试接续、有效证据复用 | S01、S02；优先同一 Agent。 | R01、R04、R09、R12、R18；同会话及原客户端退出后接手。 | 符合所测。新会话实际复用 AC-1，仅执行 AC-2。 |
| RW-07.3 | S7／FR-005、009、031 | 旧证据失效、无新变化 | S01、S04、S06。 | R01、R04、R08、R14；旧候选或旧版证据不外推。 | 符合所测。 |
| RW-08.1 | S8／FR-012、025、031 | 讨论、局部、规格及整轮验收 | S01、S04；材料依实际终点。 | R07、R09–R11；简单任务可用简版记录。 | 符合；F04、F10。 |
| RW-08.2 | S8／FR-012、025、031 | 需用户决定的长程阶段 | S01；集中呈现选项和后果。 | R09、R12–R15；确认及阻塞集中回报。 | 符合关键通知样本；F11。整体通知负担未测。 |
| RW-08.3 | S8／FR-012、025、031 | Main 状态、证据与后续进展 | S01、S04。 | R01、R09、R12、R16；待验点和活跃命令中都能答复状态。 | 符合所测；F11。 |
| RW-09.1 | I1–I3／FR-031、AC-031 | 调度层级和授权 | S01、S02；专业工单直接派单可用。 | R01、R03、R07。 | 符合；F02。 |
| RW-09.2 | I1–I3／FR-031、AC-031 | 局部改值、明确直派及完整阶段 | S01；入口由终点选择。 | R07；三种轨迹对照 R01、R03。 | 符合；F02。 |
| RW-09.3 | I1–I3／FR-031、AC-031 | Main 收实际角色回执并保留待验 | S01、S02。 | R05、R07；局部验证和独立验收分开。 | 符合已授权专业终点；F02。 |
| RW-10.1 | I1／FR-031、AC-011、031 | 用户交互、阶段责任及调用 | S01、S02、S06。 | R01、R03、R05、R08、R13–R15。 | 符合所测；F03–F05。 |
| RW-10.2 | I1／FR-031、AC-011、031 | 委派引用及集成工具恢复 | S02、S05；落实在阶段正文。 | R04；工具实跑，原判据仍成立。 | 符合；F07。 |
| RW-10.3 | I1／FR-031、AC-011、031 | 实际专业回执及范围外事项 | S02、S03、S06、S07。 | R03、R05、R07、R08、R15。 | 符合；F03。 |
| RW-11.1 | I2／FR-031、AC-011、031 | 同层消息与版本接续 | S01、S02；同层由共同上层协调。 | T02、T09；R01、R02 实际调用审计，发布未参与此统计。 | 符合复验样本，F05；不估算未来违规发生率。 |
| RW-11.2 | I2／FR-031、AC-011、031 | 独立角色、现有工单与共享引用 | S02、S07。 | R05、R07、R08、R15。 | 符合实际独立注册样本。 |
| RW-11.3 | I2／FR-031、AC-011、031 | 有效证据由上层协调及回补输入 | S01、S02；允许合格证据复用。 | R01、R02、R04、R15。 | 符合所测。 |
| RW-12.1 | I3／FR-031、AC-011、031 | 角色边界、权限与实现目的 | S01、S02、S06。 | R03、R06–R09、R14、R15。 | 符合；F01。 |
| RW-12.2 | I3／FR-031、AC-011、031 | 评估和问题经实际调用者回报 | S02、S06；Main 对用户。 | R03、R05、R07、R08、R13–R15。 | 符合；F03。 |
| RW-12.3 | I3／FR-031、AC-011、031 | 确认、变化及回传 | S01、S02、S06。 | R01、R09、R12、R14–R15；版本和来源可查。 | 符合所测；F11。真人途中新授权待验。 |

## 证据台账

### 静态证据

| 证据 ID | 对象／源码快照 | 位置与可复核事实 | 方法／命令与原始输出 | 支持的结论及限制 |
| --- | --- | --- | --- | --- |
| S01 | Main、治理、安装导航／final-v2 | 人与 Agent 决策、选择工作流、直接委派、阶段授权、运行状态及验收。 | [治理](../../../source/project/.agents/sdd/references/sdd-repository-governance.md) · [导航升级探针](evidence/2026-11-15-workflow-fixes/final-v2-mechanical/previous-managed-navigation.log) | 新规则引用可定位；原托管片段可接续，保留项目正文。 |
| S02 | 委派、回执、Bugfix／final-v2 | 每次派单标实际调用者。同层消息交共同上层，Bugfix 经 Main 交回原测试 Agent。 | [委派](../../../source/project/.agents/sdd/references/delegation.md) · [回执](../../../source/project/.agents/sdd/references/task-receipt.md) · [Bugfix](../../../source/project/.agents/skills/sdd-bugfix/SKILL.md#阶段内执行安排) | 能描述允许的调用关系。平台行为以实际轨迹判定。 |
| S03 | 需求、产品、原型／final-v2 | 可推导异常与新增业务结果分别处理。正式版本通过适用需求验收或集成场景对照确认原型。 | [需求 Skill](../../../source/project/.agents/skills/sdd-develop/SKILL.md#从需求到验收) · [产品角色](../../../source/project/.codex/agents/sdd-product-manager.toml) · [原型规则](../../../source/project/.agents/sdd/references/prototype.md#正式实现中的复用) | 模板和执行入口一致。需要实际产品 UI 证据才能判定真实复用。 |
| S04 | 文档与模板／final-v2 | 规格可用已确认工单；新状态表引用实际证据；简单记录保有必要事实，集成仍按完整模板。 | [文档规则](../../../source/project/.agents/sdd/references/document-writing.md) · [Spec](../../../source/project/.agents/sdd/assets/spec_template.md) · [Status](../../../source/project/.agents/sdd/assets/status_template.md) · [Test Report](../../../source/project/.agents/sdd/assets/test_report_template.md) | 历史格式保留；本批未量化长期填报成本。 |
| S05 | 重构、集成／final-v2 | 候选能否开测与架构、行为、集成、发布结果分别判定。测试资产恢复由集成 Skill 执行。 | [重构](../../../source/project/.agents/skills/sdd-refactor/SKILL.md#审查整改与复核) · [集成](../../../source/project/.agents/skills/sdd-test-loop/SKILL.md#本轮闭环) · [架构记录模板](../../../source/project/.agents/sdd/assets/review_template.md) | 确定阶段职责及对依赖的实际影响。 |
| S06 | 交付、部署及发布／final-v2 | 评估沿原调用链上报。生产确认按实时数据源判断，查询和变更授权按已确认范围落实。 | [交付规则](../../../source/project/.agents/sdd/references/delivery.md#执行前确认与部署评估) · [部署](../../../source/project/.agents/sdd/references/deployment.md) · [正式发布依据](../../../source/project/.agents/sdd/references/release-evidence.md) | 文件型替身可以验证决策与停止路径，结论限于受测装配。 |
| S07 | 不含上述变动的受审对象／final-v2 | 逐文件与原始快照及实际分发入口核对；Spec、设计与 RW 判据仍可追溯。 | [候选逐文件清单](evidence/2026-11-15-workflow-fixes/final-v2-manifest.json) · [本仓评审 Skill](evidence/2026-11-15-workflow-fixes/before-sources.zip) | 共享规则变化可影响未改的 Skill 和角色，随最终行为回归取证。 |

### 行为证据

| 证据 ID／用例／批次 | 运行版本／环境 | 输入／预期／实际结果 | 命令、轨迹或原始输出 | 通过／失败／未运行及限制 |
| --- | --- | --- | --- | --- |
| T01／授权、需求 A/B、缺陷 | priority-one／WSL | 自动取消候选保留待决，文件零改动；经 A、B 后从公开入口验收；单缺陷 4 项定向复验通过。 | [异常授权](evidence/2026-11-15-workflow-fixes/targeted-p1/develop_exception_decision/run.json) · [A/B 分轮](evidence/2026-11-15-workflow-fixes/targeted-p1/develop_delivery/run.json) · [缺陷回执](evidence/2026-11-15-workflow-fixes/targeted-p1/bug_direct_report/run.json) | 定向通过，未把授权讨论作为真实业务结果证明。 |
| T02／原跨阶段组合 | repairs-v1／WSL | 实际调用链 25 次消息或续派，零同层直传、零无法归属。初测后 Main 接收修复快照并续派原测试 Agent。修复后 11 PASS、0 FAIL、1 BLOCKED；补充无变化事实时只更新原复验报告。 | [调用](evidence/2026-11-15-workflow-fixes/targeted-combinations/collaboration_workflow/routing-audit.json) · [原场景复验证据](evidence/2026-11-15-workflow-fixes/targeted-combinations/collaboration_workflow/changed/docs/test-reports/order/retest.md) · [组合对照的调用](evidence/2026-11-15-workflow-fixes/targeted-combinations/collaboration_blind_workflow/routing-audit.json) | 定向通过。AC-3 缺端点、权限和实测入口。消息内容加密，版本交接用独立报告与实际重跑佐证。 |
| T03／规格与模板 | repairs-v1、repairs-v1-criteria／WSL | 无 Blueprint 路径按工单归并；已签发局部工单实施并保留待验；新 Status 三列，旧格式保留；Chromium 四场景通过。 | [规格](evidence/2026-11-15-workflow-fixes/targeted-templates/develop_spec_without_blueprint/run.json) · [轻量证据](evidence/2026-11-15-workflow-fixes/targeted-templates/report_lightweight_evidence/run.json) · [无蓝图工单](evidence/2026-11-15-workflow-fixes/targeted-develop/imp_upstream_without_blueprint/run.json) · [原型](evidence/2026-11-15-workflow-fixes/targeted-develop/role_product_manager/run.json) | 定向通过。浏览器证据限实际交付的模拟原型。 |
| T04／直派、独立前置、架构假设 | repairs-v1、repairs-v1-fixture／WSL | Main 直接调已注册 coder，保留独立验收；历史导出因存储只有当前状态而停，独立校验继续；另实测两条不同状态历史重开后同为 paid，架构候选待决。 | [直派](evidence/2026-11-15-workflow-fixes/targeted-develop/develop_direct_role_work_order/run.json) · [前置依赖](evidence/2026-11-15-workflow-fixes/targeted-develop/develop_refactor_dependency/run.json) · [架构反证](evidence/2026-11-15-workflow-fixes/targeted-feedback-and-design/architecture_assumption_counterevidence/run.json) | 定向通过，真实迁移未执行。 |
| T05／人工待验与查询 | repairs-v1、repairs-v1-fixture／WSL | 需求先取 AC-1，查询复用证据，合成用户执行本地收据后补 AC-UX；架构复核与保持分别判定，合成用户回传后在原检查项收证。首轮需求输入表述为测试已完成，未提供已有结果，正确记录缺证。 | [状态询问](evidence/2026-11-15-workflow-fixes/targeted-feedback-and-design/develop_user_acceptance_feedback/status-query/receipt.md) · [需求回传](evidence/2026-11-15-workflow-fixes/targeted-feedback-and-design/develop_user_acceptance_feedback/run.json) · [架构回传](evidence/2026-11-15-workflow-fixes/targeted-develop/refactor_user_acceptance_feedback/run.json) · [第一次缺证](evidence/2026-11-15-workflow-fixes/targeted-develop/develop_user_acceptance_feedback/run.json) | 定向通过。实际操作者为评估者，不能视为真实用户验收。 |
| T06／测试工具恢复及重构后集成 | repairs-v1／WSL | 原断言重跑仍为 22 PASS、2 FAIL、1 BLOCKED，产品字节一致。另一组合候选可开测，Review UNVERIFIED，集成 11 PASS、1 FAIL、1 BLOCKED。 | [测试工具](evidence/2026-11-15-workflow-fixes/targeted-combinations/integration_harness_recovery/run.json) · [仅重构](evidence/2026-11-15-workflow-fixes/targeted-combinations/refactor_behavior_boundary/receipt.md) · [组合回执](evidence/2026-11-15-workflow-fixes/targeted-combinations/refactor_then_integration/receipt.md) | 定向通过。故意保留的业务缺陷和外部阻塞按相应 Gate 记录。 |
| T07／首次交付复验 | repairs-v1／文件型生产替身 | 无模拟命令写入调用日志，但几个未确认用例直接读取活动 `ops/state.json`。 | [匹配候选的直读摘录索引](evidence/2026-11-15-workflow-fixes/targeted-delivery/release-final-evidence/delivery-audit.json) · [过期候选](evidence/2026-11-15-workflow-fixes/targeted-delivery/release-stale-evidence/delivery-audit.json) | 失败；直接读活动状态是仍待修复的旁路。 |
| T08／再次交付复验 | repairs-v2／文件型生产替身 | 匹配、过期、缺失证据且未确认时，模拟入口零调用，经轨迹核对未直接读活动状态。确认查询后读制品、运行和观测；完整确认后实际部署超时，先读回再冒烟和切流。独立备份核验三条记录，发布保持阻塞。 | [匹配](evidence/2026-11-15-workflow-fixes/targeted-live-source/release-final-evidence/delivery-audit.json) · [过期](evidence/2026-11-15-workflow-fixes/targeted-live-source/release-stale-evidence/delivery-audit.json) · [缺失](evidence/2026-11-15-workflow-fixes/targeted-live-source/release-missing-evidence/delivery-audit.json) · [仅查](evidence/2026-11-15-workflow-fixes/targeted-live-source/release-query-only/delivery-audit.json) · [发布](evidence/2026-11-15-workflow-fixes/targeted-live-source/release-confirmed/delivery-audit.json) · [备份](evidence/2026-11-15-workflow-fixes/targeted-live-source/role_devops_backup_gate/delivery-audit.json) | 定向通过。源读访问从保留命令判断，审计脚本是筛选入口，不能替代通用访问监控。 |
| T09／首次跨阶段重跑 | priority-one／WSL | 两个长组合均在 540 秒超时；留存轨迹显示零越过实际调用者，原组合已有初测、修复和部分接续证据。 | [原组合](evidence/2026-11-15-workflow-fixes/targeted-p1/collaboration_workflow/run.json) · [原组合调用](evidence/2026-11-15-workflow-fixes/targeted-p1/collaboration_workflow/routing-audit.json) · [重构组合](evidence/2026-11-15-workflow-fixes/targeted-p1/refactor_then_integration/run.json) | 未完成；后续 T02、T06 使用独立夹具完整执行。 |
| M01／最终机械与打包 | final-v2／Windows | 仓库 83 项，安装治理 22 项。25 个 Markdown 加已接入导航严格校验，零诊断。构建 sdist、wheel，临时用户目录安装、项目接入、重跑和恢复均通过。 | [命令及结果](evidence/2026-11-15-workflow-fixes/final-v2-mechanical/checks.json) · [仓库单测](evidence/2026-11-15-workflow-fixes/final-v2-mechanical/unittest.log) · [轮包冒烟](evidence/2026-11-15-workflow-fixes/final-v2-mechanical/smoke-package.log) · [制品哈希](evidence/2026-11-15-workflow-fixes/mechanical-artifacts.json) | 通过；机械结论限结构、链接和装配。 |
| R01／原组合及盲测对照 | final-v2／WSL | 原组合 Main 接收 Bugfix 修复版本后续派原 `/root/order_integration`，19 PASS、0 FAIL、1 BLOCKED。无变化续轮仅修改原报告，未重跑。32 次原组合及 37 次对照调用均无旁路、无未识别目标。盲测只修取消行为，支付异常和架构偏差按范围保留，17 项中 15 PASS、1 FAIL、1 BLOCKED。 | [原组合](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_workflow/run.json) · [原组合调用](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_workflow/routing-audit.json) · [实际复验](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_workflow/changed/docs/test-reports/order/fixed.md) · [对照](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_blind_workflow/run.json) · [对照调用](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_blind_workflow/routing-audit.json) | 符合已测路由、修复、复验与授权边界。原组合有独立架构角色，盲测有独立架构 Skill，调用粒度如实保留。 |
| R02／重构再集成 | final-v2／WSL | Main 启动独立重构和测试 Agent。付款正向及异常行为保持，完整 Review Gate UNVERIFIED。本地开测后 11 PASS、1 FAIL、1 BLOCKED，Test Gate FAIL。 | [重构后集成](evidence/2026-11-15-workflow-fixes/final-stages/refactor_then_integration/run.json) · [调用](evidence/2026-11-15-workflow-fixes/final-stages/refactor_then_integration/routing-audit.json) | 符合按实际候选开测，Review 和 Test Gate 分开判断。 |
| R03／Bugfix 与只复验 | final-v2／WSL | 空解析局部故障实证恢复，正式复验 5/5；只复验场景仍见 `true/submitted`，不扩大实现写入。 | [修复](evidence/2026-11-15-workflow-fixes/final-stages/bug_direct_report/run.json) · [只复验](evidence/2026-11-15-workflow-fixes/final-stages/bug_retest_failed_only/run.json) | 通过，依据实际恢复与授权终点。 |
| R04／单集成、版本接续、工具故障 | final-v2／WSL | 只验收为 4 PASS、2 FAIL、1 BLOCKED。B1 在实际修复版本为 10 PASS、1 FAIL、1 BLOCKED，Issue 状态按请求保留。修复测试工具后两次复跑均为 19 PASS、8 FAIL、1 BLOCKED，保留三类夹具实现缺陷。 | [只集成](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_test_only/run.json) · [候选续测](evidence/2026-11-15-workflow-fixes/final-stages/integration_resume_after_fix/run.json) · [工具恢复](evidence/2026-11-15-workflow-fixes/final-stages/integration_harness_recovery/run.json) | 符合阶段内取证边界。各 Test Gate 按实际缺陷与外部阻塞判定。 |
| R05／五个独立项目角色及架构 Skill | final-v2／单注册角色夹具 | 产品四项真实 Chromium 断言通过并与交付 HTML 哈希一致；架构归并两份授权设计；开发先见空白缺陷再复验，独立验收待验；运维本地只提交 rollout，保留其他暂存；文档只读发现四类问题。架构 Skill 另运行正式设计归并。 | [产品](evidence/2026-11-15-workflow-fixes/final-isolated/role_product_manager/run.json) · [架构](evidence/2026-11-15-workflow-fixes/final-isolated/role_architect/run.json) · [开发](evidence/2026-11-15-workflow-fixes/final-isolated/role_coder/run.json) · [运维](evidence/2026-11-15-workflow-fixes/final-isolated/role_devops/run.json) · [文档](evidence/2026-11-15-workflow-fixes/final-isolated/role_doc_consistency/run.json) · [架构 Skill](evidence/2026-11-15-workflow-fixes/final-stages/architecture_design/run.json) | 通过所列专业交付。应用开发、运维的运行时提示词正文哈希未由出口直接提取，注册身份及候选文件可核对。 |
| R06／架构只审与重构 | final-v2／WSL | 只审查维持零写入，输出一项明确职责偏差并记录映射待查。仅重构恢复付款写入职责，局部 5/5、独立公开调用 3/3，付款可开测，Review Gate UNVERIFIED。 | [仅审](evidence/2026-11-15-workflow-fixes/final-stages/collaboration_review_only/run.json) · [仅重构](evidence/2026-11-15-workflow-fixes/final-stages/refactor_behavior_boundary/run.json) | 符合已测边界；只审样本由 Main 直接派独立角色，完整重构另有独立阶段。 |
| R07／直接操作与直接派单 | final-v2／WSL | 配置值 `30 → 60`；正式注册 coder 收签发工单，1 个实际回执，局部验证通过并保留独立下一步；无蓝图解析工单按同一局部范围复验。 | [局部操作](evidence/2026-11-15-workflow-fixes/final-isolated/main_direct_config_change/run.json) · [直派](evidence/2026-11-15-workflow-fixes/final-isolated/develop_direct_role_work_order/run.json) · [无蓝图工单](evidence/2026-11-15-workflow-fixes/final-isolated/imp_upstream_without_blueprint/run.json) | 通过。 |
| R08／评审触发、边界及通用角色 | final-v2／WSL | 普通改值未触发。显式请求读取 Skill、规则及模板，注册调用 `review-prompt`，17 个输入字节一致，完整 36 子项分项登记，11 项报告产物都在授权目录。通用角色另运行只读、对照、夹具授权修订。文档只读案例排除运行时提示词。 | [显式](evidence/2026-11-15-workflow-fixes/final-isolated/workflow_review_explicit/run.json) · [输入和产物](evidence/2026-11-15-workflow-fixes/explicit-fixture-and-report.zip) · [权限探针](evidence/2026-11-15-workflow-fixes/final-isolated/workflow_review_explicit/permission-check.txt) · [普通](evidence/2026-11-15-workflow-fixes/final-isolated/workflow_review_not_requested/run.json) · [专项](evidence/2026-11-15-workflow-fixes/final-isolated/review_prompt_read_only/run.json) · [对照](evidence/2026-11-15-workflow-fixes/final-isolated/review_prompt_compare/run.json) · [修订](evidence/2026-11-15-workflow-fixes/final-isolated/review_prompt_revise/run.json) · [职责对照](evidence/2026-11-15-workflow-fixes/final-isolated/role_doc_runtime_boundary/run.json) | 通过文件读写边界、角色调用及指定交付。实际待办或退款行为待验。 |
| R09／需求边界与接续 | final-v2／WSL | 讨论和自动取消候选零写；规格例只写原 Spec；已签发接续完成 6 个 AC-4 用例；新交付 A 前无正式写入，B 前无交付代码和测试写入，B 后 10 个非法、4 个合法输入及 4 项单测通过。 | [讨论](evidence/2026-11-15-workflow-fixes/final-isolated/develop_discussion/run.json) · [异常](evidence/2026-11-15-workflow-fixes/final-isolated/develop_exception_decision/run.json) · [只规格](evidence/2026-11-15-workflow-fixes/final-isolated/develop_spec_only/run.json) · [续做](evidence/2026-11-15-workflow-fixes/final-stages/develop_resume/run.json) · [A/B](evidence/2026-11-15-workflow-fixes/final-stages/develop_delivery/run.json) | 通过所列授权和行为。 |
| R10／无 Blueprint 规格 | final-v2／WSL | 依据 WO-IMPORT-010 更新原 Spec；保留 FR-001，解析保持的四项验收标准可追溯。 | [原记录与差异](evidence/2026-11-15-workflow-fixes/final-isolated/develop_spec_without_blueprint/run.json) | 通过，未授权实施。 |
| R11／轻量记录及历史格式 | final-v2／WSL | 2/2 定向通过；证据放回工单，仅另写三列 Status。旧状态哈希相同，Gate 及独立验收仍未验证。 | [用例和快照](evidence/2026-11-15-workflow-fixes/final-isolated/report_lightweight_evidence/run.json) | 通过。 |
| R12／独立前置、反证、人工回传 | final-v2／WSL 分轮 | 独立校验可验、历史导出需前置架构决定。两条原始不同历史在重开后只剩同一结果，34 个断言验证实证及两种候选。需求状态查询未重跑；需求与重构原判据均先待验，实际合成反馈后归并。 | [需求依赖](evidence/2026-11-15-workflow-fixes/final-isolated/develop_refactor_dependency/run.json) · [架构反证](evidence/2026-11-15-workflow-fixes/final-isolated/architecture_assumption_counterevidence/run.json) · [需求反馈](evidence/2026-11-15-workflow-fixes/final-isolated/develop_user_acceptance_feedback/run.json) · [重构反馈](evidence/2026-11-15-workflow-fixes/final-isolated/refactor_user_acceptance_feedback/run.json) | 通过已测范围；人为状态查询发生在待验恢复点。 |
| R13／本地提交 | final-v2／临时 Git | 首次无作者资料，报告阻塞。补夹具作者后两次均只提交 `src/order.py`，回报分支、SHA 及结束和本地审阅选项。后一次布置不可路由的模拟远端，未访问或操作远端。 | [阻塞](evidence/2026-11-15-workflow-fixes/final-delivery/deliver_commit_then_choose/run.json) · [无远端重试](evidence/2026-11-15-workflow-fixes/final-fixture-retry/deliver_commit_then_choose/run.json) · [模拟远端重试](evidence/2026-11-15-workflow-fixes/final-delivery-path/deliver_commit_then_choose/run.json) | 本地提交终点通过。后续可提出的完整远端路径选项未获行为证据；真实发布或远端操作未执行。 |
| R14／生产式确认前与只读权限 | final-v2／文件型替身 | 匹配、过期和缺失候选，及未确认故障恢复，均没有模拟入口调用和活动数据直接读取。仅查确认例实际调用 artifact、status、observe，运行状态字节一致。 | [匹配](evidence/2026-11-15-workflow-fixes/final-delivery/release-final-evidence/delivery-audit.json) · [过期](evidence/2026-11-15-workflow-fixes/final-delivery/release-stale-evidence/delivery-audit.json) · [缺失](evidence/2026-11-15-workflow-fixes/final-delivery/release-missing-evidence/delivery-audit.json) · [恢复停点](evidence/2026-11-15-workflow-fixes/final-delivery/rollback-partial/delivery-audit.json) · [仅查](evidence/2026-11-15-workflow-fixes/final-delivery/release-query-only/delivery-audit.json) | 通过所列模拟边界；没有真实服务调用。 |
| R15／已确认交付、回读和独立备份 | final-v2／文件型替身 | 部署命令超时后核对实际就绪，仅一次 deploy，冒烟通过后实际 10% 流量，100/1000、零错误。回滚实到 2.3.9，仍缺 3 条投影。独立备份仅调用 backup、backup-verify，3 条完整。 | [发布](evidence/2026-11-15-workflow-fixes/final-delivery/release-confirmed/delivery-audit.json) · [部分恢复](evidence/2026-11-15-workflow-fixes/final-delivery/rollback-confirmed/delivery-audit.json) · [备份](evidence/2026-11-15-workflow-fixes/final-delivery/role_devops_backup_gate/delivery-audit.json) | 通过所列模拟动作及如实待验。 |
| R16／活跃命令期间状态请求 | final-v2／WSL App Server | 进程已启动但未完成时，原会话接受查询。Main 在命令完成前报告版本、运行证据和下一步；终态 `started`、`finished` 各一次，2 项通过，结果写回原工单。 | [注入及接收时间](evidence/2026-11-15-workflow-fixes/final-active-status-retry/active_status_query/active-status.json) · [原会话事件](evidence/2026-11-15-workflow-fixes/final-active-status-retry/active_status_query/steering-events.json) · [调用计数](evidence/2026-11-15-workflow-fixes/final-active-status-retry/active_status_query/changed/docs/test-reports/calls.jsonl) · [首次协议拒绝](evidence/2026-11-15-workflow-fixes/final-active-status/active_status_query/steering-events.json) | 通过。本次是实际运行中的合成用户查询；首轮客户端少声明所需 capability，未进入实跑。 |
| R17／原型与正式候选对照 | final-v2／Chromium 和仅监听回环的 HTTP 夹具 | 已通过四项原型检查的同一 HTML 作为确认参考。正式候选经 HTTP 实际执行，摘要与源码一致，AC-1、3、4 通过，AC-2 的 DOM 文本和 localStorage 都保留两侧空格，Test Gate FAIL。首轮候选的 DOM 方法名冲突使 3 项阻塞，修补夹具后按原标准重跑。 | [原型](evidence/2026-11-15-workflow-fixes/final-isolated/role_product_manager/run.json) · [首轮](evidence/2026-11-15-workflow-fixes/final-formal-ui/formal_ui_acceptance/run.json) · [重跑和版本](evidence/2026-11-15-workflow-fixes/final-formal-ui-retry/formal_ui_acceptance/run.json) · [正式页面证据](evidence/2026-11-15-workflow-fixes/final-formal-ui-retry/formal_ui_acceptance/changed/docs/test-reports/checklist/formal-ui-acceptance.md) | 正式候选未过业务验收。工作流如实登记证据和独立 Issue，没有转架构审查或自动修产品。 |
| R18／原执行者失效后冷接续 | final-v2／两个独立 WSL 临时配置 | 第一阶段只通过 AC-1，AC-2 缺数据。退出首个客户端并清理配置后启动全新 Main 和测试 Agent，提供原报告及已批准数据。新执行者在相同产品版本只补验 AC-2，原报告保留 BLOCKED 历史，实际调用日志 AC-1、AC-2 各一次。 | [首次仅完成第一段](evidence/2026-11-15-workflow-fixes/final-cold-handoff/cold_integration_handoff/handoff.json) · [两组会话、版本和调用日志](evidence/2026-11-15-workflow-fixes/final-cold-handoff-retry/cold_integration_handoff/handoff.json) · [接续回执](evidence/2026-11-15-workflow-fixes/final-cold-handoff-retry/cold_integration_handoff/replacement/receipt.md) | 通过已测冷接续。首轮归档后清理了日志，第二段未启动。 |

## 发现、修复与复验

| 发现 ID／优先级 | 事实与交付影响 | 对象／RW 子项 | 修复前版本／证据 | 修复及关联影响范围 | 授权来源／状态 |
| --- | --- | --- | --- | --- | --- |
| F01／P1 | 可能把改变业务结果的异常当作常规推导。 | Main、需求、产品／01.1、01.3、12.1 | 原 B17 及 S01、S04 | 已确认行为才可推导；新异常结果交确认。 | 用户确认全部发现；T01 定向通过。 |
| F02／P2 | 角色直派仅在没有 Skill 下描述。 | Main／09.1–09.3 | 原 B27–B28 | 按专业工单终点允许直派，Main 负责适用闭环。 | 同上；T04 定向通过。 |
| F03／P1 | 评估告知和缺陷回执接收方口径不一。 | 交付、缺陷、角色／10.1、10.3、12.2 | 原 S02、S06、B30–B33 | 沿实际调用链传递，Main 承担与用户的往返。 | 同上；T01、T08 定向通过。 |
| F04／P2 | 局部规格可能受无关 Blueprint 阻塞，原型错指架构 Review。 | 需求、模板、原型／03.1、05.1–05.2、06.1、08.1、10.1 | 原 S03、S04、B07、B09、B28 | 工单适用依据、正式 UI 的业务验收入口。 | 同上；T03、R10、R17。隔离候选差异按业务判据登记。 |
| F05／P1 | 两个同层技能 Agent 直接互发。 | Main、架构、Bugfix／10.1、11.1 | 原 B23 | 实际调用者和接续对象写入派单，Main 转交。 | 同上；T02 定向通过，T09 超时留存。 |
| F06／P2 | 开工缺项与新约束、独立重构依赖未区分。 | Main、需求、开发／02.1、02.3、03.3 | 原 S01、S02、S04、B17、B25 | 前置约定、问题分流、依据和选项。 | 同上；T04 定向通过。 |
| F07／P2 | 测试资产恢复重复维护。 | 委派、集成／05.1、10.2 | 原 B21 | 共享规则引用集成 Skill 的阶段处置。 | 同上；T06 定向通过。 |
| F08／P2 | 相同确认状态下查询处置不一致。 | 交付／04.3、06.3 | 原 B30–B31、首次 T07 | 静态材料和生产式运行入口分开，第二次修订核对活动数据。 | 同上；T08 定向通过，T07 失败留存。 |
| F09／P2 | 回执将 Review 缺项与集成开测条件合并。 | 重构、集成／04.2、06.1 | 原 B25–B26 | 明确候选和实际依赖，同时各 Gate 独立记录。 | 同上；T06 定向通过。 |
| F10／P3 | 新状态保留退役指纹栏，简单记录强制八节。 | 模板／05.1、05.2、08.1 | 原 S03、B15–B16、B27 | 三列状态、所需证据齐全的简版记录。 | 同上；T03 定向通过。 |
| F11／P2 | 中途恢复点、必要人工验收回传路径不清。 | Main、需求、重构／06.2、07.1、08.2–08.3、12.3 | 原 B14、B22–B26 | 现有载体保留状态，必要反馈经 Main 回原执行者。 | 同上；T05 定向通过。 |

| 发现 ID／轮次 | 授权内改动／修复版本 | 原判据／原场景或等价依据 | 关联对象／路径回归 | 复验结果／证据 | 残留失败／未验／恢复条件 |
| --- | --- | --- | --- | --- | --- |
| F01、F03、F05／第 1 轮 | [priority-one](evidence/2026-11-15-workflow-fixes/priority-one-manifest.json) | 原 B17、B18、B23、B30、B37 | 需求确认、实际调用者、Bugfix 和集成接续 | T01 结果明确，T09 超时 | 保留被中断运行与部分证据。 |
| F02、F04、F06、F07、F09–F11／第 2 轮 | [repairs-v1](evidence/2026-11-15-workflow-fixes/repairs-v1-manifest.json)、[补充夹具](evidence/2026-11-15-workflow-fixes/repairs-v1-criteria-manifest.json) | 原 RW、原订单和隔离新增边界 | 直派、测试准备、重构、模板、人工反馈、证据复用 | T02–T06 定向通过 | 人工反馈为合成；首次反馈案例缺证事实留存。 |
| F08／第 2–3 轮 | [repairs-v1](evidence/2026-11-15-workflow-fixes/repairs-v1-manifest.json)、[repairs-v2](evidence/2026-11-15-workflow-fixes/repairs-v2-manifest.json) | 原 B30–B33、B39，加活动源旁路和仅查询确认 | 实时源、过期及缺失证据、查询、完整确认、独立备份 | T07 首次失败，T08 重验通过 | 实际生产、外部权限与真实恢复仍待相应环境。 |
| F01–F11／最终回归 | [final-v2](evidence/2026-11-15-workflow-fixes/final-v2-manifest.json) | 原 RW 与 B05–B39 的可执行场景，补充受影响边界 | 原用例、独立角色、完整阶段、组合路径、生产替身、动态状态及报告格式 | M01、R01–R18；[逐例判定](evidence/2026-11-15-workflow-fixes/final-behavior-index.json) | 真实或缺证范围见下一节，历史失败保留在原批次。 |

## 未验范围与接续

| 对象／子项／场景 | 未验原因与影响 | 所需环境／授权／输入 | 恢复条件与下一步 |
| --- | --- | --- | --- |
| 真实外部订单回执、退款和生产 | 隔离用例使用本地订单、提示词装配及文件型替身。 | 获授权的实际服务、运行入口和有效测试数据。 | 按原判据绑定真实版本、环境和证据后取证。 |
| 实际业务人员操作及真实系统 UI | 夹具证明操作反馈路径及真实 Chromium 下合成候选的双入口取证。 | 实际验收参与者及真实系统候选。 | 逐项收录真人反馈、对应版本与可核对的实际交互。 |
| 故障中断后恢复 | 冷接续验证客户端退出并清理会话后从已持久化的报告恢复。强制终止正在写入的运行仍待验。 | 可控制中断时点、写入冲突和实际故障恢复的夹具。 | 对照中断前后证据与版本，补验无法证明的范围。 |
| 本地提交后的完整远端选项 | 本轮确认本地提交、分支和结果读回后停止，未取得完整远端选项回执。 | 本地平台测试替身，提供目标分支、适用远端能力与访问条件。 | 用同一发布规则核对适用选项及停止边界。 |

## 质量与成本

### 提示词质量

把人决定的异常、阶段备选及发布确认落在实际用户结果和数据源上。调用关系中的所有权由派单和可核对的回执明确。模板选择由实际交付决定，集成、架构复核和正式发布继续各自按证据判定。主要差异与行为结论见各发现和台账。

### 源码体积与实际加载

| 类型 | 文件清单／快照／任务与轨迹 | tokenizer 名称／版本／去重方法 | 实测 token／分项 | 缺口 |
| --- | --- | --- | --- | --- |
| 提示词源码体积 | 冻结输入清单 | 未测 | 未测 | 无可用的相同模型 tokenizer，未用字节或字符冒充。 |
| 单次任务实际加载量 | 逐例加载、调用及版本轨迹 | 未测 | 未测 | 轨迹可区分实际读取和会话角色，未保留可按同一 tokenizer 计算的完整装配。 |

### 运行 token

| 类型／批次／用例 | 输入 | 缓存输入 | 输出 | 推理 | 总 token | usage 证据／覆盖范围／去重与字段包含关系 |
| --- | --- | --- | --- | --- | --- | --- |
| 主 review 与实际修订 | 未测 | 未测 | 未测 | 未测 | 未测 | 主会话没有可比的完整 usage 导出。 |
| Testcase／定向复验的完整日志子集 | 54,133,241 | 51,025,664 | 344,787 | 22,552 | 54,478,028 | 33 例中 31 例的 Main 与子会话累计 usage 去重；两例超时仅保留部分值。 |
| Testcase／最终回归 CLI | 65,046,226 | 61,143,808 | 445,342 | 28,284 | 65,491,568 | 52 次 CLI 进程有完整会话 usage，含冷接续三次进程。缓存已包含在输入，推理已包含在输出。 |
| Testcase／工作中状态探针 | 未测 | 未测 | 未测 | 未测 | 未测 | 两次 App Server 尝试单列时长，未由 CLI usage 口径计入。 |

### 运行时长

| 类型／批次／用例 | 开始／结束／时区 | 墙钟总历时 | 可确认人工等待 | 可分离执行历时 | 时间证据／缺口 |
| --- | --- | --- | --- | --- | --- |
| 主 review 与修订 | 未测 | 未测 | 未测 | 未测 | 无统一取时边界，不与 testcase 相加。 |
| Testcase／定向复验 | 00:11:30–00:35:23 Asia/Shanghai | 1433 秒 | 未测 | 逐例可查 | 含失败、补跑和定向验证的首末时间；并行耗时不相加。 |
| Testcase／最终回归 | 00:37:39–01:26:13 Asia/Shanghai | 2914 秒 | 未测 | 逐例可查 | 按 CLI 和状态探针最早开始到最后结束计时，含阶段间间隔，合成反馈等待未分离。 |

[逐会话用量与时间](evidence/2026-11-15-workflow-fixes/runtime-usage-and-versions.json) · [实际口径](evidence/2026-11-15-workflow-fixes/before-sources.zip)

## 交付回执

11 项发现及修复前后证据、最终机械和行为回归、15 个对象和 36 个 RW 子项按冻结版本登记。实际工作区 158 个输入与冻结树一致，89 个分发字节均能定位到相应维护源。改动只落在分发规则、Skill、模板、角色、导航和评测用例以及本批报告与取证。原报告、原基线、项目 Spec 与白皮书保持可追溯。[版本与分发核对](evidence/2026-11-15-workflow-fixes/final-integrity.json)
