# 工作流 Review 报告 · 2026-11-14 当前工作区

## 范围与版本

沿用用户显式启动的同一批次，先验证 Skill 触发、规则版本、角色调用及取证回执，再评价发现。未获授权修复受审源码。实现、提示词修订、提交和模拟运维均只发生在一次性夹具，按各自的合成工单取证。

- 基线提交 f059378784e9833f7f4fd3363fa76516a35dc15c，含未提交和未跟踪改动。原始快照记录 134 个文件的 SHA-256，清单摘要为 91f0ec7230763b286162880b58eb10def609bf8c3ae1f013f2418e157d2e9876。补充清单记录 5 个已跟踪缺失路径和续审补录依据。补录文件绑定续审时的字节。 [原快照](evidence/2026-11-14-current-review/snapshot.json) · [补充快照](evidence/2026-11-14-current-review/supplemental-snapshot.json)
- 判据为白皮书 S1–S8、I1–I3 和 Spec，按当前 Review 判据与模板交付。Skill 正文哈希 d7e2c20f2ac93415db526e33fccdf8f62d9bd9c7a8349c2d2e85ba396dc1458c。 [白皮书](../../sdd-workflow-whitepaper.md) · [Spec](../../../specs/platform-independent-sdd/spec.md) · [审查判据](../../../.agents/skills/sdd-workflow-review/references/review-criteria.md) · [版本核对](evidence/2026-11-14-current-review/skill-execution-audit.json)
- 实验日期 2026-11-14，Asia/Shanghai。Windows 原生 CLI 0.169.0-alpha.11.1，批量回归用 Ubuntu WSL2、CLI 0.169.0、Python 3.12.3、文件 SQLite 及 Chromium。主执行配置 gpt-6.1-sol、medium，项目角色的实际模型见轨迹。独立临时配置，模型的 shell 网络关闭，读写限制在夹具及必要工具目录。跨阶段夹具使用当前临时构建及初始化入口。构建清单的 89 个文件中，88 个匹配原始快照；release.py 为续审补录的安装辅助文件。 [构建版本](evidence/2026-11-14-current-review/regression-release-provenance.json)
- 历史证据只按对应版本使用，早期阻塞和测试中断均留档。真实用户验收、外部订单回执、真实退款、平台和生产行为不计入已验证范围。 [续审前报告](evidence/2026-11-14-current-review/review-before-sandbox-recovery.txt) · [首轮中断](evidence/2026-11-14-current-review/unittest.log) · [83 项机械测试](evidence/2026-11-14-current-review/unittest-resume.log)

## 执行策略定位与恢复

失败日志显示两个条件。临时项目未受信任时，项目角色注册没有生效。信任该临时项目后，子角色可以启动，读取命令仍被拒绝。原始 Windows 沙箱日志记录 MXC 可用但选择为 disabled。同一注册版客户端的最小探针在启动无害的 cmd.exe 时直接复现 “registered Core process has no package identity”。因此最小复现将阻塞定位到 Windows 注册版 Core 的沙箱启动和包身份检查。现有证据无法确定哪个安装或激活组件遗漏了身份。对照时点在 AppLocker 和 Code Integrity 中未查到相应事件。 [早期失败轨迹](evidence/2026-11-14-current-review/role-doc-trusted.jsonl) · [原始沙箱日志](evidence/2026-11-14-current-review/windows-original-sandbox.log) · [最小复现](evidence/2026-11-14-current-review/windows-sandbox-repro.txt)

同一原生客户端使用一次性参数 -c windows.sandbox=mxc 后可以启动命令。在只读模式下读取成功且哨兵写入受拒；工作区模式允许夹具内部写入。原生模型复验用同一文档夹具，PowerShell 读到了工单，注册子角色实际完成四类审查且零文件变化。批量回归沿用现有 WSL 客户端，采用受限目录配置、禁止网络和禁止提权。显式评审仅报告目录可写，评估者答案不在沙箱读范围。 [Windows 原生复验](evidence/2026-11-14-current-review/native-mxc-model/run.json) · [PowerShell 轨迹](evidence/2026-11-14-current-review/native-mxc-model/events.jsonl) · [WSL 权限探针](evidence/2026-11-14-current-review/linux-gate/workflow_review_explicit/permission-check.txt) · [官方 MXC 配置](https://learn.chatgpt.com/docs/windows/windows-sandbox#mxc-compatibility)

## Skill 执行验收

在评价工作流发现前，先对照 B05 和 B06。普通配置变更只改目标字段并读回，轨迹未见读取评审 Skill 正文、调用角色或生成报告。显式执行成功读取 Skill 正文、规则、成本口径和模板，内容与快照吻合。实际子会话为注册的 review-prompt，读取夹具依据并交回专项回执，由 Main 合并 RP-01 到夹具 F-01。报告列出 36 个 RW 编号的合成适用性，17 个原输入字节无变化，7 个新增文件全部在指定目录；夹具归档可检查报告相对链接。构建清单没有分发本仓评审 Skill。 [验收核对](evidence/2026-11-14-current-review/skill-execution-audit.json) · [夹具与报告归档](evidence/2026-11-14-current-review/linux-gate/workflow_review_explicit/fixture-and-outputs.zip) · [专项原始回执](evidence/2026-11-14-current-review/linux-gate/workflow_review_explicit/changed/docs/test-reports/sdd-workflow/2026-11-14-minimal-review/review-prompt-receipt.md)

夹具 F-01 属于合成待办助手。回读失败路径缺少待验原因和再次回读条件。审查报告将这项静态偏差与两条未实跑的助手行为分列，装配脚本退出 0。合成判据用于验收评审行为，真实工作流结论来自以下单独的回归。

## 综合结论

原生 MXC 和 WSL 均已恢复隔离取证。五个独立项目角色、通用提示词角色与六个分发阶段 Skill 均有实际执行轨迹。集成、缺陷、同阶段接续、重构后集成、版本门禁及模拟发布恢复均有可核查结果。83 项机械测试已通过。

**整版判定为存在偏差。** 集成组合中，架构审查与缺陷两个同层 Agent 双向直发消息，违反通过 Main 交接的规则。复验仍保留 AC-3 阻塞，另一重构组合按 Main 路径完成。需求／交付决策和验收中的静态歧义另列，未观测到的后果不推定发生。

## 逐对象覆盖

| 对象与当前入口 | 重点 RW | 静态核对 | 行为证据及闭环 |
| --- | --- | --- | --- |
| [Main](../../../source/project/.agents/sdd/references/sdd-repository-governance.md) | 01、02、04、07–10、12 | 阶段授权、已就绪直接操作、局部阻塞有规定。F02、F05、F06、F11。 | B23、B26–B28、B37–B38。按局部、直派、进入 Skill 三类实测。当前缺陷组合出现同层直接交接。 |
| [共享治理与模板](../../../source/project/.agents/sdd/references/document-writing.md) | 05–08、10–12 | 权威、版本、回执及模板用途已核对。F03–F07、F09–F11。 | B11–B12、B20–B26、B38。已验证记录和版本；未覆盖所有模板例外。 |
| [sdd-develop](../../../source/project/.agents/skills/sdd-develop/SKILL.md) | 01–04、06 | A／B、逐 AC 实测、缺证及结束范围明确。F01、F04、F06、F11。 | B14–B17、B37。讨论、只规格、接续及实测验收路径。 |
| [sdd-architecture](../../../source/project/.agents/skills/sdd-architecture/SKILL.md) | 01、02、05、08 | 关键取舍、反证反馈、文档权威和实施隔离。 | B13。确认设计归并通过；反证与真实演化待验。 |
| [sdd-refactor](../../../source/project/.agents/skills/sdd-refactor/SKILL.md) | 03、04、06、07 | 原检查项、行为基线、独立复核。集成交接见 F09。 | B23–B26。只审、仅重构和组合；实际 Review Gate 按证据保留。 |
| [sdd-bugfix](../../../source/project/.agents/skills/sdd-bugfix/SKILL.md) | 01、04、06、07 | 只复验、归因、原场景和关单证据。回报路径见 F03。 | B18–B19、B23。恢复、失败停点、接续。F05 列入行为偏差。 |
| [sdd-test-loop](../../../source/project/.agents/skills/sdd-test-loop/SKILL.md) | 01、04、06、07、11 | 实际版本、功能映射、待验及 Test Gate。F07 重复处置。 | B20–B23、B26、B38。失败、阻塞、续测、复用和测试资产恢复。 |
| [sdd-deliver](../../../source/project/.agents/skills/sdd-deliver/SKILL.md) | 01、04、06、07 | 按授权、确认、最终候选与运行读回。F03。 | B29–B33。候选、确认、超时、部分恢复；F08 记录查询口径差异。 |
| [sdd-product-manager](../../../source/project/.codex/agents/sdd-product-manager.toml) | 01、05、06、12 | 从已确认目标推导行为，原型与用户确认分列。 | B07。实际 Chromium 通过，真实用户反馈待验。 |
| [sdd-architect](../../../source/project/.codex/agents/sdd-architect.toml) | 02、05、06、10 | 设计取舍和实现遵循分别交付。 | B08、B24–B26。设计文档与独立复核有证，业务环境待验。 |
| [sdd-coder](../../../source/project/.codex/agents/sdd-coder.toml) | 03、04、06、07、11 | 原 Task、实际版本、局部证据及待验交回。 | B09、B14、B18、B23、B28。局部实施和多级委派轨迹可复核。 |
| [sdd-devops](../../../source/project/.codex/agents/sdd-devops.toml) | 04、06、07、11、12 | 按同工单复验实际版本、结果和依赖。 | B10、B32–B33、B39。独立提交、模拟运行及备份取证。 |
| [sdd-doc-consistency](../../../source/project/.codex/agents/sdd-doc-consistency.toml) | 05、07、10、12 | 按实际只读权限核对冲突、重复和错位引用。 | B03、B11–B12。原生和 WSL 真实角色回执，保护工作区与历史。 |
| [review-prompt](../../../source/initializer/assets/user-agents/review-prompt.toml) | 04–06、10、12 | 实际装配、授权终点、专项回报及未验证项。 | B05、B34–B36。只读、比较和合成授权修订均上交证据。 |
| [sdd-workflow-review](../../../.agents/skills/sdd-workflow-review/SKILL.md) | 04、06、08、10–12 | 只显式发起，定义依据、报告、范围和专项分工。 | B05–B06。符合合成执行对照。真实工作流另按实际证据判断。 |

## 逐 RW 子项覆盖

各项按当前白皮书与 Spec 追溯，所列符合限于用例范围。静态有歧义、实跑符合时分别记录。

| RW | 设计与 Spec | 核对对象与静态判断 | 行为证据 | 结论及缺口 |
| --- | --- | --- | --- | --- |
| RW-01.1 | S1／FR-025 | Main、sdd-develop／F01 的异常授权边界 | B13、B16–B17 有判断选项 | 存在偏差，B17 本次未发生越权 |
| RW-01.2 | S1／FR-025 | Main、sdd-develop／已有确认直接沿用 | B14–B15、B23、B32、B37 | 符合已测确认复用 |
| RW-01.3 | S1／FR-025 | 需求和交付／F01 实质异常变化裁决歧义 | B17、B30–B33 | 存在偏差，实际异常方案正确停在待决 |
| RW-02.1 | S2／FR-029 | Main、开发／F06 前置排除与待决未统一 | B07–B10、B23、B37 | 存在偏差，已就绪工单可执行 |
| RW-02.2 | S2／FR-029 | 需求、架构、开发／授权内调查有规定 | B09、B14、B21、B25 | 符合已运行的探索，架构反证未测 |
| RW-02.3 | S2／FR-029 | 架构反证规则存在，F06 通用前置区分不足 | B17 新业务变化交回，B21 取证后识别工具故障 | 存在偏差，关键假设反证分支未验 |
| RW-03.1 | S3／FR-020、029 | 需求、开发／F04 Spec 模板可能误设 Blueprint 前置 | B09、B28 不要求无关 Blueprint | 存在偏差，已签发局部工单可前进 |
| RW-03.2 | S3／FR-020、029 | 重构／结构复核与保持证据分开 | B25–B26 局部调整保留业务约束 | 符合已测付款范围 |
| RW-03.3 | S3／FR-020、029 | 需求、重构／F06 缺独立重构前置分流 | B25–B26 范围外缺陷留证，B28 局部改动 | 存在偏差，必须先重构的分支未验 |
| RW-04.1 | S4／FR-005、031 | Main、交付／已就绪时按授权接续 | B14、B23、B26、B32–B33 | 符合已测路径 |
| RW-04.2 | S4／FR-005、031 | 复验、测试资产及阻塞／F09 交接口径不一 | B19–B23、B25–B26、B33、B39 | 局部失败修正和独立事项推进有证，存在交接口径偏差 |
| RW-04.3 | S4／FR-005、031 | 各阶段、角色／有授权终点 | B05–B06、B10–B12、B15–B20、B22、B24、B29–B31、B34–B36 | 终点有实测，模拟查询的确认边界见 F08 |
| RW-05.1 | S5／FR-001、006 | 共享规则／F04、F07、F10 的依赖、模板及重复维护 | B11–B12、B34–B36 区分现行与历史 | 存在偏差 |
| RW-05.2 | S5／FR-001、006 | 归并、模板／F04、F10 引用与当前责任不完全一致 | B08、B11–B13、B15、B35 | 存在偏差，按权威归并及识别旧证据有证 |
| RW-05.3 | S5／FR-001、006 | 文档及提示词角色／保护历史与有效例外 | B11–B12、B23、B34–B36 | 符合所列取证、清理建议与改动边界 |
| RW-06.1 | S6／FR-008、009、010、026 | 集成、重构、发布／F04、F09 验收路径歧义 | B05、B07、B14、B20–B26、B30–B33 | 存在偏差，已执行的各 Gate 分别按证据 |
| RW-06.2 | S6／FR-008、009、010、026 | 验收转交／F11 需求及保持验收的必要人工观察路径 | B19–B23、B25–B26、B33 保留失败和待验 | 人工反馈仍待验，现行回传说明不完整 |
| RW-06.3 | S6／FR-008、009、010、026 | 原型、模拟、真实部件与版本适用性 | B05、B07、B22–B23、B31–B33、B38 | 符合已测版本和证据边界 |
| RW-07.1 | S7／FR-005、009、031 | 交接／有版本、证据及缺口字段，F11 运行中状态时机不明确 | B09、B14、B20、B22–B26 | 现有证据可定位，动态恢复点存在缺口 |
| RW-07.2 | S7／FR-005、009、031 | 原执行者接续及新执行者沿原记录 | B14、B22、B23、B38 | 覆盖已确认交接；强制旧会话丢失待验 |
| RW-07.3 | S7／FR-005、009、031 | 版本变化与旧证据判断 | B11–B12、B22、B31–B33、B38 | 符合已测版本和旧证据边界 |
| RW-08.1 | S8／FR-012、025、031 | 轻量与正式路径／F04、F10 额外流程歧义 | B05、B15–B16、B27–B28 | 存在偏差，局部与讨论对照通过 |
| RW-08.2 | S8／FR-012、025、031 | Main／F11 长程通知与集中待决时点未统一 | B23、B26 有过程通知，B30、B33 汇总待决 | 未验证整体通知负担 |
| RW-08.3 | S8／FR-012、025、031 | 状态与阻塞／终态和缺口已有字段，F11 中途状态恢复未统一 | B20–B23、B26、B29–B33 | 终态可核查，运行中查询待验 |
| RW-09.1 | I1–I3／FR-031、AC-031 | Main、Skill、角色／F02 直派条件偏窄 | B05、B18、B23、B26–B28 三类路由有轨迹 | 存在偏差，显式直派闭环有证 |
| RW-09.2 | I1–I3／FR-031、AC-031 | Main 局部直达、角色直派／F02 | B27 与 B28 实际尝试成功 | 存在偏差，实跑局部路径可用 |
| RW-09.3 | I1–I3／FR-031、AC-031 | 直派的局部自验及后续责任／F02 | B10、B27–B28 保留适用相称验收及待验 | 已测专业终点符合，完整阶段改走直派留待取证 |
| RW-10.1 | I1／FR-031、AC-011、031 | 回报用户、阶段组织、专业执行／F03–F05 | B05、B14、B23、B26、B30–B33 | 存在偏差，组合中有同层直传 |
| RW-10.2 | I1／FR-031、AC-011、031 | 共享交接与阶段处置／F07 重复维护 | B21 实证阶段内恢复可执行 | 存在偏差，长期漂移未测 |
| RW-10.3 | I1／FR-031、AC-011、031 | 专业角色产物及跨阶段事项／F03 | B07–B12、B28、B34–B36 | 存在回报路径歧义，独立产物有证 |
| RW-11.1 | I2／FR-031、AC-011、031 | 同层禁止交接／治理第 29 行、白皮书 I2 | B23 同层双向直传；B26 按 Main 路径 | 存在偏差 F05 |
| RW-11.2 | I2／FR-031、AC-011、031 | 五角色及通用角色／独立输入和禁止启动其他角色 | B07–B12、B34–B36、B39 | 所列工单符合，独立注册与实际角色身份可查 |
| RW-11.3 | I2／FR-031、AC-011、031 | 上层补输入和证据／允许合格复用 | B09、B22–B23、B28、B31、B38–B39 | 符合证据复用和缺项回报，F05 单独判断 |
| RW-12.1 | I3／FR-031、AC-011、031 | 下层权限／F01 的异常语义授权 | B05、B12、B17、B24–B25、B29、B34–B36 | 存在静态歧义，B17 未发生越权 |
| RW-12.2 | I3／FR-031、AC-011、031 | 实际调用者／F03 的部署通告和缺陷回报 | B05、B07–B12、B28、B30–B33 | 存在偏差，普通专业角色回执路径有证 |
| RW-12.3 | I3／FR-031、AC-011、031 | 确认来源与变更记录／F11 的动态状态缺口 | B14、B22–B23、B26、B30–B33、B37–B38 | 已测版本和确认可复核，长程变化待验 |

## 证据台账

### 静态证据

逐对象表链接到本批当前原始源码。下表列出发现的具体依据，位置与结论也可和保留的初查版本对读。

| 证据 | 文件与位置 | 核对依据 |
| --- | --- | --- |
| S01 | [治理](../../../source/project/.agents/sdd/references/sdd-repository-governance.md) 7–9、21–77、148–150、170–184 行，[项目入口](../../../source/initializer/assets/agents-fragment.md) 7–27 行 | 决策、直接路径、阶段授权、用户观察及证据复用。 |
| S02 | [委派](../../../source/project/.agents/sdd/references/delegation.md) 13–42、46–53、63–80 行 | 角色接单、只读权限、同层限制、实际调用者及接续。 |
| S03 | [Spec 模板](../../../source/project/.agents/sdd/assets/spec_template.md) 9、17 行，[原型引用模板](../../../source/project/.agents/sdd/assets/prototype_reference_template.md) 5 行，[Status](../../../source/project/.agents/sdd/assets/status_template.md) 11–19 行，[测试报告模板](../../../source/project/.agents/sdd/assets/test_report_template.md) 5–7 行 | 依据定位与模板负担。 |
| S04 | [需求 Skill](../../../source/project/.agents/skills/sdd-develop/SKILL.md#从需求到验收) 12–19、33–37 行，[实施规则](../../../source/project/.agents/sdd/references/implementation.md) 11–19 行 | A／B、异常及必要架构依赖、验收。 |
| S05 | [重构 Skill](../../../source/project/.agents/skills/sdd-refactor/SKILL.md#审查整改与复核) 18–24 行，[集成 Skill](../../../source/project/.agents/skills/sdd-test-loop/SKILL.md#本轮闭环) 20–26 行 | 初审、原判据、保持、集成准备、证据复用。 |
| S06 | [交付规则](../../../source/project/.agents/sdd/references/delivery.md#执行前确认与部署评估) 19–31 行，[部署指引](../../../source/project/.agents/sdd/references/deployment.md) 3 行，[Bugfix](../../../source/project/.agents/skills/sdd-bugfix/SKILL.md#从复现到关闭) 16–30 行 | 实际调用者、用户确认、生产查询和候选门禁。 |

### 行为证据

每例索引记录环境、源提交、前后哈希、角色身份、用时及轨迹位置。同目录保存实际工单、回执、调用事件和必要产物。原回执中的绝对路径是当时的临时环境路径，实证以索引及对应保存副本定位。

| 证据／用例 | 实际结果及适用边界 | 入口 |
| --- | --- | --- |
| B01／早期装配 | 脚本读取两层指导文本并退出 0。 | [输出](evidence/2026-11-14-current-review/fixture-load.log) |
| B02／仓库机械回归 | 83 项通过，用时 146.253 秒，验证工具与构建。 | [日志](evidence/2026-11-14-current-review/unittest-resume.log) |
| B03／Windows 探针 | 保留早期三次失败与信任修正，MXC 恢复后通过实际只读角色审查。 | [旧轨迹](evidence/2026-11-14-current-review/role-doc-trusted.jsonl) · [原生结果](evidence/2026-11-14-current-review/native-mxc-model/run.json) |
| B04／历史提示词专项 | 同角色源码哈希的历史只读取证。B34 有本轮实跑。 | [历史轨迹](evidence/2026-11-14-current-review/historical-prompt-session-tools.json) |
| B05／显式 Review | 读取锁定的 Skill、规则与模板，实际注册调用 review-prompt。17 个受审文件字节一致。7 个报告产物均在指定目录。合成助手两条行为未验。 | [索引](evidence/2026-11-14-current-review/linux-gate/workflow_review_explicit/run.json) · [回执](evidence/2026-11-14-current-review/linux-gate/workflow_review_explicit/receipt.md) |
| B06／普通维护 | 仅改配置 30 → 60 并读回，无评审正文读取或报告。 | [索引](evidence/2026-11-14-current-review/linux-gate/workflow_review_not_requested/run.json) · [回执](evidence/2026-11-14-current-review/linux-gate/workflow_review_not_requested/receipt.md) |
| B07／产品角色 | 实际 Chromium 四项 PASS，SHA-256 与存档 HTML 一致。Spec 标注原型待确认，无托管预览。 | [索引](evidence/2026-11-14-current-review/linux-regression/role_product_manager/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/role_product_manager/receipt.md) |
| B08／架构角色 | 原位归并 Blueprint 与时序，保留公开契约，文档检查零诊断。设计未部署。 | [索引](evidence/2026-11-14-current-review/linux-regression/role_architect/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/role_architect/receipt.md) |
| B09／开发角色 | 工单就绪后记录原 Plan 和预期基线失败，复验定向 3/3、单测 5/5。轨迹未见读取无关 Blueprint，独立验收留给 Main。 | [索引](evidence/2026-11-14-current-review/linux-regression/role_coder/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/role_coder/receipt.md) |
| B10／运维角色 | 本地提交仅含 ops/rollout.txt，保护 notes.txt 暂存。回执未提交，app.py 独立问题交调用方。 | [索引](evidence/2026-11-14-current-review/linux-regression/role_devops/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/role_devops/receipt.md) |
| B11／文档角色 | 实际只读，发现同版权威冲突、重复政策、断链及 v2 错引 v1，零变化。 | [索引](evidence/2026-11-14-current-review/linux-regression/role_doc_consistency/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/role_doc_consistency/receipt.md) |
| B12／文档职责对照 | 索引混入运行时指令仍返回四项文档发现，声明排除提示词，轨迹未见读取其正文。零变化。 | [索引](evidence/2026-11-14-current-review/linux-boundaries/role_doc_runtime_boundary/run.json) · [回执](evidence/2026-11-14-current-review/linux-boundaries/role_doc_runtime_boundary/receipt.md) |
| B13／架构 Skill | 独立阶段沿已确认决策归并 ARC-002 和 SCN-001，只改两份设计文档。反证实验未验。 | [索引](evidence/2026-11-14-current-review/linux-regression/architecture_design/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/architecture_design/receipt.md) |
| B14／需求成品接续 | 沿用有效 A／B、原 T002 和同一 Plan，AC-4、AC-1 实测通过。局部单测另计。 | [索引](evidence/2026-11-14-current-review/linux-regression/develop_resume/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/develop_resume/receipt.md) |
| B15／仅规格 | 仅修改原 Spec，实施、测试字节一致。 | [索引](evidence/2026-11-14-current-review/linux-contrast/develop_spec_only/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/develop_spec_only/receipt.md) |
| B16／仅讨论 | 比较取消时限、适用范围和通知。保留候选待决，未写文件。 | [索引](evidence/2026-11-14-current-review/linux-contrast/develop_discussion/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/develop_discussion/receipt.md) |
| B17／异常实质变化 | 自动取消虽不改主流程，仍影响用户已确认结果。留候选，给备选和影响，零写入。 | [索引](evidence/2026-11-14-current-review/linux-boundaries/develop_exception_decision/run.json) · [回执](evidence/2026-11-14-current-review/linux-boundaries/develop_exception_decision/receipt.md) |
| B18／单缺陷闭环 | Main 启动独立 Bugfix 再派 coder，空输入恢复 []，非空拆分保持，原 Issue 关联实证。 | [索引](evidence/2026-11-14-current-review/linux-regression/bug_direct_report/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/bug_direct_report/receipt.md) |
| B19／仅复验失败 | 取消后提交仍为 true/submitted，正常提交通过。仅更新原 Issue 且保持未关闭。 | [索引](evidence/2026-11-14-current-review/linux-contrast/bug_retest_failed_only/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/bug_retest_failed_only/receipt.md) |
| B20／仅集成 | 5 PASS、2 FAIL、1 BLOCKED。指南、Issue 和测试报告可查，产品与测试不变，未启动修复。 | [索引](evidence/2026-11-14-current-review/linux-regression/collaboration_test_only/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/collaboration_test_only/receipt.md) |
| B21／测试工具故障 | 授权内修正工具入口，两次复跑均退出 1；13 PASS、2 FAIL、1 BLOCKED。产品字节不变。 | [索引](evidence/2026-11-14-current-review/linux-contrast/integration_harness_recovery/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/integration_harness_recovery/receipt.md) |
| B22／变更版本接续 B1 | 基线 AC-1 PASS、AC-2 FAIL 后实际切换夹具提交；9 PASS、1 FAIL、1 BLOCKED。旧原始记录和原 Issue 状态保留。 | [索引](evidence/2026-11-14-current-review/linux-boundaries/integration_resume_after_fix/run.json) · [回执](evidence/2026-11-14-current-review/linux-boundaries/integration_resume_after_fix/receipt.md) |
| B23／集成→缺陷→原测试／架构复核 | Main 发起独立阶段，Bugfix 派真实 coder。原测试 Agent 复验相同场景和新哈希，10/3/1 改为 13/0/1，Test Gate BLOCKED。F05 两次绕开 Main 的同层消息。 | [索引](evidence/2026-11-14-current-review/linux-regression/collaboration_workflow/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/collaboration_workflow/receipt.md) |
| B24／仅审查架构 | 指出适配层绕过状态写入职责。未运行的故障与持久化项 UNVERIFIED。受审项目零改动。 | [索引](evidence/2026-11-14-current-review/linux-regression/collaboration_review_only/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/collaboration_review_only/receipt.md) |
| B25／仅重构 | CR-001 复核与付款保持均 PASS；整体 Review UNVERIFIED。历史取消缺陷照录。回执集成条件有歧义 F09。 | [索引](evidence/2026-11-14-current-review/linux-contrast/refactor_behavior_boundary/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/refactor_behavior_boundary/receipt.md) |
| B26／重构后集成 | Main 另起集成 Agent，Review UNVERIFIED 未阻止授权集成；13 PASS、1 FAIL、1 BLOCKED，Test Gate FAIL。既有取消缺陷未列入付款改动。 | [索引](evidence/2026-11-14-current-review/linux-regression/refactor_then_integration/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/refactor_then_integration/receipt.md) |
| B27／Main 局部操作 | 主会话直接改并读回指明的配置值，只有该文件变化。 | [索引](evidence/2026-11-14-current-review/linux-contrast/main_direct_config_change/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/main_direct_config_change/receipt.md) |
| B28／Main 直接委派 | 六个阶段 Skill 可用时按明确授权直接交注册 coder，核对工单、同一 Plan、局部验证及独立验收缺口。 | [索引](evidence/2026-11-14-current-review/linux-direct-role/develop_direct_role_work_order/run.json) · [回执](evidence/2026-11-14-current-review/linux-direct-role/develop_direct_role_work_order/receipt.md) |
| B29／交付 Skill 本地提交 | 只提交 src/order.py，实际回读 commit，下一步选择交 Main，未触发远端。 | [索引](evidence/2026-11-14-current-review/linux-regression/deliver_commit_then_choose/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/deliver_commit_then_choose/receipt.md) |
| B30／正式候选确认前 | 候选证据匹配，报告部署影响及确认停点，未调用模拟运行入口。 | [索引](evidence/2026-11-14-current-review/linux-delivery/release-final-evidence/run.json) · [回执](evidence/2026-11-14-current-review/linux-delivery/release-final-evidence/receipt.md) |
| B31／旧版发布依据 | 重构前报告不可支持最终候选。没有部署、冒烟或切流，但模拟查询发生，和 B30 的确认前停点口径不同。 | [索引](evidence/2026-11-14-current-review/linux-delivery/release-stale-evidence/run.json) · [回执](evidence/2026-11-14-current-review/linux-delivery/release-stale-evidence/receipt.md) |
| B32／模拟确认后部署超时 | deploy 退出 124 后读回已就绪，未重复部署。冒烟后切流 10%，100/1000 命中且零错误。数据检查缺夹具输入。 | [索引](evidence/2026-11-14-current-review/linux-sim-confirmed/release-confirmed/run.json) · [回执](evidence/2026-11-14-current-review/linux-sim-confirmed/release-confirmed/receipt.md) |
| B33／模拟部分恢复 | 回滚 2.3.9、schema 7 不变，健康与冒烟通过，仍缺 3 条投影。明确未恢复，未覆盖数据。 | [索引](evidence/2026-11-14-current-review/linux-sim-confirmed/rollback-confirmed/run.json) · [回执](evidence/2026-11-14-current-review/linux-sim-confirmed/rollback-confirmed/receipt.md) |
| B34／提示词只读 | 实际角色发现成功门槛缺证，运行装配，零写入。退款业务未实跑。 | [索引](evidence/2026-11-14-current-review/linux-contrast/review_prompt_read_only/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/review_prompt_read_only/receipt.md) |
| B35／提示词候选对比 | 四次装配退出 0，候选纠正成功判据但退化确认及重试约束，无写入。 | [索引](evidence/2026-11-14-current-review/linux-regression/review_prompt_compare/run.json) · [回执](evidence/2026-11-14-current-review/linux-regression/review_prompt_compare/receipt.md) |
| B36／提示词授权修订夹具 | 仅改合成工单授权的两份提示词。保留确认、演练、一次重试约束，前后装配有证。 | [索引](evidence/2026-11-14-current-review/linux-contrast/review_prompt_revise/run.json) · [回执](evidence/2026-11-14-current-review/linux-contrast/review_prompt_revise/receipt.md) |
| B37／需求 A／B | 同一会话三轮。A 前文件无变化，确认 A 后仅规格、计划及直接文档，确认 B 后改实现。16 组输入、正常提交及付款回归、5 项单测通过；AC-2 和 AC-3 仍保留。 | [索引](evidence/2026-11-14-current-review/linux-multiturn/develop_delivery/run.json) · [回执](evidence/2026-11-14-current-review/linux-multiturn/develop_delivery/receipt.md) |
| B38／同会话复用有效证据 | 组合再跑后给无版本／环境变化的补充事实，续轮只改原复验报告。没有测试或运行探测，延用实际版本证据，AC-3 仍阻塞。 | [索引](evidence/2026-11-14-current-review/linux-multiturn/collaboration_workflow/run.json) · [回执](evidence/2026-11-14-current-review/linux-multiturn/collaboration_workflow/receipt.md) |
| B39／发布缺证与独立备份 | 单注册 sdd-devops 实际调用 backup 与 backup-verify。三条记录验证通过，发布及依赖暂停，恢复仍待授权验证。 | [索引](evidence/2026-11-14-current-review/linux-backup/role_devops_backup_gate/run.json) · [回执](evidence/2026-11-14-current-review/linux-backup/role_devops_backup_gate/receipt.md) |

## 发现、修复与复验

| 发现／优先级 | 对象与判据 | 当前事实与影响 | 证据及复验关注点 |
| --- | --- | --- | --- |
| F01／P1 | 需求、产品、Main／01.1、01.3、12.1 | 需求 Skill 概括异常、边缘及验收覆盖由 Agent 决定，和治理中用户可观察业务变化的决策权有交叉。 | S01、S04、B17。该实测把自动取消留待确认。核对异常业务结果与可推导用例的边界。 |
| F02／P2 | Main／09.1–09.3 | 适用 Skill 存在时的直派条件未在治理说明，直派写在“没有适用 Skill”下面。 | S01、B27–B28。显式就绪工单已实跑；通用触发与适用闭环责任需要清晰。 |
| F03／P1 | 交付、缺陷、角色／10.1、10.3、12.2 | 部署指引写向用户给评估，交付规则写先回实际调用者。Bugfix 专业回报也出现交 Main 的旁路。 | S02、S06、B30–B33。模拟记录通常经 Main，统一各专项通知和接收方。 |
| F04／P2 | 模板、需求、原型／03.1、05.1–05.2、06.1、08.1、10.1 | Spec 模板写 Blueprint PUC／PAC 而未给已有工单等合格替代依据。原型模板把用户行为对照指向 Review。 | S03、S04、B07、B09、B28。现行局部样本未被阻断，明确替代依据及验收入口。 |
| F05／P1 | 架构审查、缺陷阶段／10.1、11.1 | 同一组合内两个同层 Skill Agent 双向直接发消息，绕过共同上层 Main。 | S01、S02、B23。调用时间 23:14:08.888、23:15:51.371（UTC+08:00），目标分别为 order_bugfix 和 order_review。B26 的独立样本按 Main 路由。[同层调用摘录](evidence/2026-11-14-current-review/cross-stage-routing-evidence.json) |
| F06／P2 | Main、需求、开发／02.1、02.3、03.3 | 已有范围、约束和权限字段分散。未区分可前置的待决与执行中新约束，独立重构成为真实前置时缺少依赖和备选的规则。 | S01、S02、S04、B14、B17、B25、B28。有条件时补测独立重构前置与用户取舍。 |
| F07／P2 | 治理、集成／05.1、10.2 | 委派第 76 行和 test-loop 都维护测试资产、环境补齐及原判据重跑的阶段内处置。 | S02、S05、B21。实际处置能完成，长期重复维护可能产生规则分歧。 |
| F08／P2 | 交付／04.3、06.3 | 两个确认前的本地生产式模拟对是否可查询处理不同。过期证据样本调用 artifact、status、observe，未发布或切流。 | S06、B30–B31。判断为模拟边界口径差异，真实生产越权未实证。 |
| F09／P2 | 重构、集成／04.2、06.1 | 仅重构样本的详细记录称本地候选就绪，最终回执却把规则映射、历史缺陷处理列入集成准备。 | S05、B25–B26。已授权集成实测仍执行，区分执行条件、Review／Test Gate 和发布前置。 |
| F10／P3 | 共享模板／05.1、05.2、08.1 | 新 Status 保留旧 Snapshot 列并要求新记录不填旧指纹；简单工单仍要求测试报告八节。 | S03、B15–B16、B27。历史保留与新建格式分别核对，填报成本未测。 |
| F11／P2 | Main、需求、重构／06.2、07.1、08.2–08.3、12.3 | 阶段回执有记录，运行中何时保存恢复点、集中呈现决定及变化不够明确。需求及保持验收未明确必需用户操作的回传路径。 | S01、S02、S04–S05、B14、B22–B26。动态状态和真人观察待验。 |


| 轮次 | 源码版本 | 本轮复验范围 | 状态 |
| --- | --- | --- | --- |
| F01–F11 初审及续审 | 原工作区和补充快照 | 按原 RW 判据运行 B05–B39，保留失败及待验 | 未获修复授权，无受审源码修复版本。 |

## 未验范围与接续

| 对象或场景 | 已取得证据及仍缺的条件 |
| --- | --- |
| 真实外部回执、退款、生产与平台 | SQLite 为本地实跑，AC-3 缺真实端点和调用授权。退款样本只有提示词装配，发布和恢复限于本地替身。由相应真实测试环境补验。 |
| 真人反馈及运行中授权实质变化 | A／B 和生产式确认使用测试用户输入。原型用实际 Chromium，真人体验未验。需实际授权及验收参与者。 |
| 关键架构假设被反证、独立重构成为必须前置、执行者强制丢失 | 同 Agent 恢复、B1 记录交接、已确认设计及范围外缺陷已取证。反证、必要新决策与强制冷恢复仍需对应输入、原版本和交互轨迹。 |
| 合成待办助手两条业务路径 | 评审 Skill 的触发、证据与回执通过。编排仅能读取文本，未实跑该受测助手成功回读与失败恢复。 |
| 稳定性及用户主动状态查询 | F05 有明确违规调用，另一个组合经过 Main。未用重复样本量化发生率，也未取得长程实时状态查询轨迹。 |

## 质量与成本

本批复核的关键风险为同层交接、业务变化的授权判定、回执接收方和必要验收反馈。历史证据、阶段产物和本批失败均有独立判据或可复跑入口。F01 的静态偏差及 B17 的通过样本同时保留。

| 口径 | 实测与缺口 |
| --- | --- |
| 提示词源码体积与实际加载 token | 已验证固定的逐文件哈希和成功读取轨迹。没有记录统一 tokenizer 和单次实际加载 token，两项未测。 |
| 主 Review | 完整用量、墙钟及人工作业等待未测。合成评审 B05 按 testcase 入账。 |
| Testcase | 逐例记录主及子会话最后累计 usage。B05 的两个原始流合计 491,248 token，输入 479,141（含缓存 449,152），输出 12,107（含推理输出 253），命令计时 239.901 秒。初版日志导出器把子流文件名也标为父 ID，实际子身份、调用及回执可在保留轨迹检验。 |
| 墙钟与对比 | 按用例保留起止、执行计时和分轮数据。并行耗时不相加为全批历时。人工等待与完整主 Review 耗时未测，未计算跨配置成本收益。 |

[用量、计时与版本](evidence/2026-11-14-current-review/runtime-usage-and-versions.json) · [成本口径](../../../.agents/skills/sdd-workflow-review/references/evidence-and-cost.md)

## 交付回执

按 15 个对象、36 个 RW 子项登记当前评审执行与结果，保留初查、失败和恢复轨迹。134 个原始受审文件、补录文件及 Git HEAD 均经前后核对。结论适用于本次实际受审快照，所列未验项保留。 [前后字节核对](evidence/2026-11-14-current-review/source-integrity-final.json)
