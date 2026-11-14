# 工作流分发实施证据

## 2026-11-14 缺陷修复与定向复验技能

按 [Spec FR-021／AC-021](../specs/platform-independent-sdd/spec.md#范围与需求) 核对 [sdd-bugfix](../source/project/.agents/skills/sdd-bugfix/SKILL.md)。四个隔离案例使用同一候选技能正文，SHA-256 为 `3ad6dbc9b918df872b17c49c34955f300b931b39c8e8f1afb38da1a1592d3989`。Codex CLI 0.169.0 在 WSL 实际读取并执行该候选，由 Main 直接承接。行为记录含实际调用、文件变更及评估端复跑。

| 场景 | 实测结果 |
| --- | --- |
| 直接报告 | 原 `parse('')` 返回 `None`，修复后返回 `[]`；三项非空场景通过。登记并关闭 BUG-001，同记录保留 T001、修复前失败及实际工作树版本。评估端复跑原场景和逗号拆分通过。 |
| 只复验且失败 | SQLite 上 AC-2 仍返回 true，重开后为 submitted；AC-1 正常提交通过。只更新原 ISS-001，保留未关闭；实现、测试及运行配置哈希未变，评估端复跑结果一致。 |
| 接续修复并消除回归 | 首次定向复验 AC-2 通过、AC-1 失败。保留前批证据并接续原 Plan 的 T001，修复后复跑 AC-2、AC-1 和四项局部单测通过，按证据关闭 ISS-001；ISS-003 缺授权端点及真实回执，保留阻塞。评估端复跑两个 SQLite 场景通过。 |
| 只准备性能工单 | 从公开 `parse` 入口复现 NFR-001，复跑五次的最大值为 60.109906 ms，超出 30 ms；输出结果正确。只更新 ISS-005 的归因、原测量口径和可复跑方案，源码未改、实施未启动。 |

行为和客户端发现记录见 `.build/bugfix-mwg6ftok/final/`。该批次未接入时只发现 sdd-init，接入后发现 sdd-init 及七个工作流入口；客户端读取的 Bugfix 正文与该批次行为候选一致。随后并行治理工作将跨阶段接续统一引用到「阶段授权与推进」；归因、修复、复验及关单步骤保持一致。对含此治理改动的工作树快照运行 67 项仓库测试、22 项构建后初始化器测试及隔离 wheel 安装、接入和重复执行冒烟，均通过。wheel 的 87 个资源与构建清单逐项匹配；Bugfix 正文 SHA-256 为 `5f2c9963293a5932e166b43255d79d9608ca02444d0a616adbb64d32b7162135`，见 `.build/bugfix-mwg6ftok/workspace-check/`。

未实跑 Bugfix 的专职角色委派与独立复验、需用户实际操作的反馈、发布后的真实环境以及外部服务回执。集成证据复用、跨阶段停点及人工作业按规则核对；四例均未启动全产品集成或操作远端。本仓采用源码维护模式。

### 人工确认精简复验

候选 Bugfix 正文 SHA-256 为 `5521944d1e9d7c9f939b8b1846d1d4a4b1e81c93910b30479f6b4dc32fffa603`。隔离运行中，直接报告完成修复、定向复验并关闭 BUG-001。只复验案例在两个原判据通过后只更新并关闭 ISS-004。两例均在单轮内完成，评估端重跑公开入口检查均通过。外部回执案例未获得原判据所需的真实证据，只更新 ISS-003 为阻塞并记录恢复条件。三个案例均未追加人工批准。实质业务歧义、扩围决策和用户亲自取证的分支按条款核对，本轮未交互实跑。

原始调用、产物和回执见 `.build/bugfix-confirmation-mwgairkv/behavior/`。技能校验、文档校验、5 项行为夹具准备测试和 22 项构建后初始化器测试通过，构建载荷中的 Skill 和 Issue 模板与源码字节一致。

## 2026-11-14 需求到实现技能

依据 [Spec](../specs/platform-independent-sdd/spec.md) FR-029／AC-029 及 FR-027／FR-031 核对 [sdd-develop](../source/project/.agents/skills/sdd-develop/SKILL.md)。行为实跑候选基于 `1eae8b5` 和当时的工作树，技能正文 SHA-256 为 `7a9c259371a9218fb622f96109a1c74f212b9b872f043ab4e1a7eb52a99b0d7d`。此后调整表达并补上只读审查的直接引用，A／B 和交付路径沿用实跑规则。修改后的分发候选另验证了启动发现及暂缓实施。

| 范围 | 实际结果 |
| --- | --- |
| 两个确认与实施 | WSL 中 Codex CLI 0.169.0 读取隔离项目的候选技能。评估端按实际回复提供 A 和 B 的模拟用户确认。三轮复验沿用同一会话。A 前文件快照相同。A 后归并 Spec、适用契约及交付计划。B 前产品代码、测试及运行配置哈希一致，B 后开始实施并验收。 |
| 点对点验收 | 同一会话中，真实 SQLite 上从公开新建入口验证 AC-4，定向测试在旧实现出现五组预期失败，实施后四项单测及 AC-1 正常提交通过。另一次按保留的 A／B 对话接续，对 AC-4、AC-5 的 11 个输入取证，并记录 AC-2 取消后仍可提交的既有失败及影响。 |
| 接续与范围限制 | 既有 A/B 确认场景沿用原工单及 T001／T002，AC-4 七例、四项单测及 AC-1 通过。只写规格场景仅修改 Spec。只讨论场景返回候选及待决项，文件快照一致。暂缓实施场景交付 Spec 和工单验收计划，产品文件保持基线，B 留待接续。 |
| 分发 | 67 项仓库回归、22 项初始化器回归及 wheel 安装冒烟通过。覆盖旧受管入口替换、重复初始化、同名保护以及缺失新正文或元数据的写入前拒绝。客户端在临时未接入项目只发现 sdd-init，在接入项目发现 sdd-init 及七个工作流入口。包含并行架构重构入口的候选也发现了 sdd-develop 与 sdd-refactor。 |

实际源码候选、逐轮回复、文件快照及实测记录见 `.build/develop-verify-2f557f14/`。组合候选回归日志见 `.build/develop-combined-3b8de9d2/`。后续工作树复跑 67 项回归也通过。最终分发复验见 `.build/develop-package-fb952779/`，源码构建和 wheel 的 86 项载荷逐字节一致，清单 SHA-256 为 `6f219f82dd47535db36e1874531a2a1acdc10dd8a3fbde1eb8a18a31becd5271`。Windows 上的客户端入口发现通过，Windows 模型执行受本机 shell 策略阻断，行为实跑使用 WSL。实跑采用 Main 直接承接，按能力委派和独立角色验收只做了源码核对。原型协作、环境排障及外部系统取证仍待实跑。本次验证范围为隔离候选及订单夹具。

## 2026-11-14 提示词审查与行为验证技能

按 [Spec](../specs/platform-independent-sdd/spec.md) FR-028／AC-028 核对 [sdd-review-prompt](../source/project/.agents/skills/sdd-review-prompt/SKILL.md)。在 WSL 的隔离工作区运行 Codex CLI 0.169.0，使用 gpt-6.1-sol、medium、同一工具和工作区写权限；每例从相同夹具和新配置开始，项目仅提供被测审查入口及共享资源，未注册专职角色。原版取自 `1eae8b5`，该批次技能正文 SHA-256 为 `c2fed8110cc7dfa2873e611869dee38ffe2b8ba9f300585ae2c53ed1cf7103a1`。

| 场景 | 实测结果 |
| --- | --- |
| 只审查、候选对比 | 前后版都沿装配入口区分现行与历史指令，识别原版允许缺证时报成功、候选版放宽免确认例外并丢失重试前状态查询。两类请求的文件哈希均无变化，回执区分静态判断与待跑的业务行为。 |
| 授权修订与复验 | 首批原版及初稿虽修订了正确的提示词，仍额外写入了报告、证据和索引。收紧落盘边界后，同一输入复跑两次，均只改 `base.md` 与 `apply.md`。两次均运行修改前后的本地装配；静态核对确认新版指令保留预览禁写、逐笔确认及本地演练例外、失败查询与重试限制，成功判据改为凭证和状态读回同时满足。措辞有差异，写入范围与关键规则一致。 |
| 权威依据冲突 | 最终版指出应急补偿免确认与原逐笔确认规则冲突，未选择业务特例或修改权威文件，继续预览去重、修正成功判据并验证装配；回执提出待决条件。 |
| 未发起审查 | 两版均只修改历史提示词的指定标题。调用记录没有读取审查 Skill 正文或运行装配对比。 |
| 分发与导航 | 67 项仓库回归、22 项初始化器回归及隔离 wheel 安装冒烟通过。缺少回执模板时写入前拒绝。客户端在未接入项目只发现 sdd-init，接入后发现 sdd-review-prompt 和其余工作流，读取新版元数据；托管导航和分发后的链接通过严格检查。技能、元数据和模板三份文件的分发字节与源码一致。 |

配对执行轨迹、装配输出、修改文件及快照见 `.build/20261114-prompt-review/verified/runs/`，首批探针见同一批次外层的 `runs/`，客户端发现见 `verified/client-discovery.json`。实跑覆盖审查 Agent 的读取、决策与本地写入。退款夹具只装配指令，退款模型行为、真实后端副作用、受控运行其他 Skill 及专职角色调度尚未实跑；补验分别需要等价的模型与退款替身、被测 Skill 隔离环境和相应执行者。

现行 Skill 的交接表述随后与共享治理对齐，以上行为结论对应本节列出的实跑版本。

## 2026-11-13 五项提示词整改复验

以 `e1d6186` 为整改前基线，从同一提交建立隔离候选并应用本轮五项修订。隔离候选分发清单 SHA-256 为 `92a998a7b0450790e6eadbef17ce38816c6322bde9573cad78c07016a824607e`。运行日志、模型前置检查及手工复验记录位于 `.build/prompt-review-retest-d26e8f2f873b462ab963161d9d836370/`。

| 原检查项及依据 | 场景依赖与停止条件 | 复验结果 |
| --- | --- | --- |
| 合并排队的接续，FR-003／AC-003 | `deliver` 回读排队状态 → 按 Git 合并指引继续查询 → 平台确认并核验实际提交 → 部署对应版本 → 检查就绪。需要外部审批或达到等待退出条件时保留恢复入口。 | 入口和 Git 指引的停止条件一致，夹具要求继续查询。手工按原 `deliver_merge_then_deploy` 的平台替身响应复演，排队时暂停部署，取得 `merge-a` 后以该版本演练部署及就绪回读。 |
| 四个英文锚点，文档校验 CLI | `--read` 解析模板锚点 → 定位标题 → 提取同一章节。 | `document-and-artifact-locations`、`authoritative-documents`、`testing-scope-constraints` 和 `prototype-scope` 均从退出码 2 变为 0，返回内容与中文标题选择器一致。纯 Issue 的三个选择器仍可读取。 |
| 非代码 Issue 回交，FR-021／AC-021 | 处理者交回原 Issue 的处理结果 → 原验收执行者按判据核验 → 文档维护者据证关单。只验收沿用本轮授权。 | 复跑原订单夹具，前后均为 AC-1 通过、AC-2 已知失败、AC-3 缺授权端点阻塞。在隔离的文档矛盾分支中，修订指南后 ISS-DOC-001 仍待核验，复跑 AC-1 并核对文档与实际结果后更新同一 Issue。 |
| 根目录共享导航，FR-027／AC-027 | 从项目共享入口运行 `doc_check.py --root . AGENTS.md` → 校验共享根内目标及锚点。 | 隔离候选与当前工作区源码构建的候选均为 0 诊断。实际工作区连接的旧共享副本仍对并行迁移新增的 `#文档交接` 报 `DOC008`，该锚点在当前源码候选已通过。 |
| 根目录意图确认，FR-025 | 读取单条确认指令 → 共享资源可用时读共享规则，缺失时读仓库源码细则。 | 根 `AGENTS.md` 只出现一次意图确认规则。通过临时 junction 与仓库源码入口均实际读取到「意图对齐」章节。 |

隔离候选仓库回归 60/60，当前工作区回归 61/61，两份构建后的初始化器回归均为 22/22。隔离候选 35 份分发 Markdown 校验通过。原 ISS-004 的空输入和非空回归通过。需求接续、只写规格、只评估、只审、混合验收、本地提交等分支做了规则对照及夹具准备。

使用 Codex CLI `0.167.0-alpha.4.1`、`gpt-6.1-sol`、相同只读配置分别检查 `deliver_merge_then_deploy` 与 `collaboration_test_only` 的整改前后工作区。四次均在 PowerShell 读取 `TASK.txt` 和 Skill 的前置阶段被 Windows 执行策略拒绝，成功读取命令数为 0。模型的加载、合并轮询与部署接续、非代码 Issue 核验回交，以及其他原场景的端到端角色行为仍为 UNVERIFIED。手工复演只用于核对场景依赖与可观察结果。本轮的候选验证使用隔离目录，现有用户级安装未更新。

## 2026-11-13 四项 Review 整改复核

整改前、后分发清单 SHA-256 分别为 `8ab4c57b85b524cf8ca8675521026d810d803d5ff19cfcc444b4654f25824e94` 和 `ac37ca343430dd8c1847cbbec538169b380bc47d9bc6ae72301d0b6c2f0f3b86`。隔离证据位于 `.build/review-fix-290d51c5893f49cd9838bc5b8a555da3/`。

| 原发现 | 整改后复核 |
| --- | --- |
| 单独局部复验没有执行入口 | 按原 ISS-004 在修复版本 `c9b5bb7` 运行公开入口，空输入和非空回归均通过。原 Issue 关闭并链接复验报告；未修改实现或测试，未启动实施或集成 Test Gate。 |
| 根导航仍指向退役入口 | 候选包在隔离项目中生成的导航与根目录 `AGENTS.md` 逐字节一致。三个新 Skill 链接可达，两个退役路径不存在。现有用户级安装未变更。 |
| 性能缺陷工单遗漏测量口径 | 原 ISS-005 在同一进程预热后，对公开入口计时五次，按最大值与 30 ms 比较，并保留拆分回归。未修复版本 `28ff909` 的测量复现超限；验收步骤保留在 Issue，实际归因结果另记。没有启动实施。 |
| 历史评测候选被写成当前工作区 | 两个历史清单的实际哈希与下方历史记录一致；历史复跑清单与本轮整改前、后候选分别相差 7、11 个分发文件。历史结果保留原快照范围。 |

仓库回归 59/59、构建后初始化器回归 22/22。CLI 同配置的前后对跑均遇到 Windows 执行策略拦截，未完成模型行为 A/B；两个行为场景改由执行者在隔离候选中实际运行并归并记录。未据此声称完整的模型行为等价或稳定性通过。

## 2026-11-13 三份上游工单的实施后验证

沿用 WO-ORDER-001、ISS-001 与 CHK-001，在 `.build/upstream-follow-through/` 的三个隔离副本分别记录 Plan、实施与实际取证。保留各自的派单前快照。当前任务在 Windows、Python 3.14.6 与文件 SQLite 3.50.4 上执行验证。每个副本的 `implementation-evidence/candidate.json` 记录运行文件与日志哈希。

| 工单 | 实际结果 |
| --- | --- |
| WO-ORDER-001 | Quickstart 的 AC-4、AC-5、取消观察点以及 AC-1 通过。AC-2 取消后再提交与派单前基线同样失败，由 ISS-001 在另一个副本验证。订单号工单范围通过。 |
| ISS-001 | AC-2 返回 `false`，重开后仍为 `cancelled`，原探针只捕获到查询。AC-1 正常提交回归通过。隔离副本中的原 Issue 已复验关闭。 |
| CHK-001 | 用户确认缺失订单沿用契约抛出 `ValueError`，并选择在当前任务内验证。原探针捕获 `set_status` 执行更新和提交，公开调用后第二连接读到 `paid`。缺失订单与数据库异常传播用例通过。原检查项记录为已修改待原审查者复核。 |

本批次共通过 10 项局部单测，8 份隔离验收文档的结构、链接与编码核对无诊断。上述结果对应三个独立候选，真实外部回执 AC-3 未纳入本轮。

## 2026-11-13 三个上游工单的派单前验收

按 [FR-005／FR-020／FR-021／FR-029 与 AC-004／AC-020／AC-021／AC-029](../specs/platform-independent-sdd/spec.md) 核对当前分发源码。三个独立任务分别补齐派单前验收要求和适用模板。隔离订单项目、验收方案、回执、基线命令和快照保存在本地 `.build/upstream-acceptance/`。

| 上游 | 交付与实际验证 |
| --- | --- |
| sdd-spec | `spec/handoff.md` 引用 WO-ORDER-001、稳定 AC 和可复跑 Quickstart。基线确认三种全空白输入被错误创建；合法订单、正常提交和单独取消通过。取消后仍可提交的既有失败单列。 |
| sdd-bugfix | `bugfix/bug_attribution_counterevidence/handoff.md` 引用原 ISS-001、归因证据及修复验收。实际重开数据库确认提交前为 `cancelled`，随后 `submit_order` 将状态更新为 `submitted`。复验方案规定 AC-2 返回 `false`、无状态写入、重开后仍为 `cancelled`，并保留 AC-1 正常提交回归。 |
| sdd-review-code | `review-code/handoff-receipt.md` 引用原 CHK-001，包含复核条件、路径、取证方法及判据。实际初审捕获 UI 直接执行 `UPDATE` 和 `COMMIT`，未调用服务写入入口。公开调用后第二连接读到 `paid`，单独记录为行为基线。 |

已核对三份上游交付、隔离产物链接与仓库回归 59/59。三个任务停在工单可交接，尚无本批次的 sdd-imp 执行、修复后用户验收或架构复核结果。

## 2026-11-13 工单验收与实施完成条件

依据 [FR-005／FR-020／FR-021／FR-026／FR-029](../specs/platform-independent-sdd/spec.md)，原位更新 Spec、执行入口与模板。用户侧验收从操作或调用入口取证，架构整改由 Review 在原检查项定义并复核。Plan 引用上游方案，记录 Task 局部证据及待验判据。

首轮评测使用以 `e598274` 为基线构建的历史快照，分发清单位于 `.build/imp-acceptance-eval/release/build-manifest.json`，SHA-256 为 `7d481b65333dd6aa6a7c58b1e1e6eb2bec8004f65650d1a004420b9d9151670a`。同一隔离批次目录保存 CLI JSONL、运行回复和评测项目。使用 Codex CLI 0.167.0-alpha.4.1 与 Windows 工作区写入沙箱。初始尝试因命令运行器与临时目录权限失败，移到仓库忽略的独立评测目录后复跑。

| 核对 | 实际结果 |
| --- | --- |
| 机械检查 | 修改涉及的 14 份 Markdown、5 个 Skill 的结构检查通过。仓库回归 59/59，构建后初始化器回归 22/22。6 个隔离评测输入准备成功。 |
| 简单实施与需求交接 | `collaboration_simple_imp` 在 `8946848` 加工作树改动上运行 4 项单测，证明空白订单号被拒、合法编号可用。没有追加集成 Test 或架构 Review。轨迹未呈现完整的单项 Plan。另一个需求场景 `spec_delivery` 先归并 AC-4 和验收指南，再实施。新增场景从失败变为通过，原 AC-2 在前后均失败。 |
| 外部证据缺失 | `bug_retest_missing_evidence` 在夹具版本 `0549588` 运行 AC-3，返回 `BLOCKED` 和退出码 3。原 Issue 保留待复验，记录修复版本和获授权端点等恢复条件。 |
| 架构整改与复核 | `collaboration_review_check_items` 在 `8c2b1df` 加工作树改动上记录原检查项、整改 Task 及实际 SQLite 复核结果。本地检查通过，外部环境证据缺失。复跑同时验证了调用路径测试在整改前失败、整改后通过。 |
| 同一工单的两类验收 | `collaboration_mixed_acceptance` 在 `23f0395` 加工作树改动上实测公开入口。两次运行的 10 次调用最大值分别为 3.2986 ms 和 4.2895 ms，均低于 250 ms。两次重开 SQLite 后 10 笔均为 `paid`。架构记录单独复核 `mark_paid` 经服务层写入并提交的路径。 |

根据简单实施的首轮轨迹，在 imp 步骤中明确开工前输出单项 Task。该次复跑的分发清单位于 `.build/imp-acceptance-eval/release-final/build-manifest.json`，SHA-256 为 `7fb79df24c85852d82515dda0777912fa61be2dc57516b7c143e64077a9e1085`。评测项目仍以 `8946848` 为基线，轨迹在首次改动前给出单项任务目标、完成判据和局部检查入口，定向回归修复前失败、修复后通过。该快照的 14 项构建与分发回归通过。复跑日志见同批次的 `final-cases/`。

架构和混合案例的实际轨迹由同一执行者完成各阶段，未观察到独立角色之间的完整派单和交回。保留行为用例的 `UNVERIFIED`。本节结果只证明各自快照和场景中的行为；例如，简单实施的轨迹可作为开工前展示单项 Task 的历史回归基线。后续候选只有在实际加载的规则、依赖、环境和判据均仍适用时才能复用相应证据；变动所影响的路径须单独取证。

## 2026-11-13 Git 交付与部署入口合并

依据 [FR-003／FR-022／FR-027](../specs/platform-independent-sdd/spec.md)，分发源码改用 [sdd-deliver](../source/project/.agents/skills/sdd-deliver/SKILL.md)。Git 和部署指引按请求加载，远端平台指引迁入统一入口。

| 检查 | 实际结果 |
| --- | --- |
| 分发与初始化 | 仓库回归 59/59、构建后初始化器回归 22/22；源码包和 wheel 构建成功，wheel 的隔离安装和重跑冒烟通过。 |
| 已接入项目升级 | 在临时目录从 `59e5c09` 构建旧版并升级。Codex 的 `skills/list` 发现八个项目工作流 Skill，两个旧入口已从共享包移除。一次 init 更新托管导航，项目自有正文及角色配置字节一致，重复 init 无差异。 |
| 规则与引用 | Skill 结构、源码文档、安装导航和共享指引检查通过。安装后实际执行纯 Issue 的条款读取命令，三个选择器均可解析。 |
| 行为夹具 | 四个隔离场景准备成功，覆盖未指定后续路径、已指定推送与部署、合并后部署、独立重启。模型行为保持 UNVERIFIED。 |

验证使用临时安装与项目。未升级真实用户级安装或其他项目，未执行真实 GitHub／GitLab 写入或环境部署。

## 2026-11-13 Bug 归因、实施与复验交接

依据 [FR-005／FR-021、AC-004／AC-021](../specs/platform-independent-sdd/spec.md)，在已有未提交工作区同步三个 Skill、角色与治理交接、导航、模板和评测预期。构建与初始化回归沿用既有分发入口。

| 核对方式 | 实际结果 |
| --- | --- |
| 指令走查 | 对照需求实施、直接报 Bug、验收发现 Bug、只验收、只评估、归因缺证及反证、复验缺证和关单路径核对输入、权限、证据与结果归属；未发现初版由 bugfix 修复或复验的冲突表述。 |
| 隔离夹具 | 准备 10 个案例。实际运行订单夹具：AC-1 通过，AC-2 失败（取消后仍提交），AC-3 因无授权端点阻塞；重开 SQLite 后确认提交前状态为 cancelled，反驳「取消状态未持久化」的旧归因。 |
| 机械检查 | 三个 Skill 格式通过；仓库 unittest 59/59 通过，本地候选构建及构建后初始化器回归 22/22 通过，覆盖分发资源、导航及五个角色。 |

本轮仅验证指令内容、机械分发和夹具前提，未执行新版的真实 Agent 行为评测；案例状态保持 UNVERIFIED。未修改用户级安装、其他项目或远端。

## 2026-11-12 用户级共享工作流

验证范围对应 [FR-027／AC-027](../specs/platform-independent-sdd/spec.md)。Windows 上使用 Codex CLI 0.154.0 和隔离用户目录。`skills/list` 在未初始化仓库发现 `sdd-init`，在已初始化仓库额外发现六个工作流 Skill。`config/read` 对应返回零条与五条 SDD 角色引用。

- 59 项仓库回归与 22 项构建后初始化器回归通过。两个仓库、新 worktree 和新克隆均接入同一共享目录。Git 排除本机链接，用户级升级后已连接项目读到新版。中断恢复测试确认只回收新建链接和引用。源码包、wheel 构建及 wheel 安装冒烟通过。
- 首轮使用 CLI `0.154.0` 验收分发默认模型。`sdd-designer` 正常返回，其余四个角色收到 `gpt-6.1-sol` 或 `gpt-6.1-terra` 不可用的报错。隔离目录改用 `gpt-6-astra` 后，五个角色均启动并返回各自名称。
- 使用桌面版自带的 Codex CLI `0.167.0-alpha.4.1` 在隔离仓库按分发默认模型复验，五个角色均返回各自的 `SDD_ROLE_OK` 标记。逐个核对子会话回复所在轮次的模型，`sdd-designer` 使用 `gpt-6-astra`，`sdd-coder` 使用 `gpt-6.1-sol`，`sdd-documenter`、`sdd-validator` 和 `sdd-delivery` 均使用 `gpt-6.1-terra`。

## 2026-11-04 用户级 sdd-init 实际升级

按本次用户明确授权，将当前仓库来源构建并安装到 `C:/Users/24598/.agents/skills/sdd-init`，载荷包含 [Spec FR-003／AC-003](../specs/platform-independent-sdd/spec.md) 的双平台交付与推送前同步规则。构建入口为 `python -B scripts/build_release.py --output .build/user-install-sync-20261104/sdd-init`，使用现有用户级 installer.install 执行安装，未修改安装器逻辑。

| 核对项 | 实际结果 |
|---|---|
| 旧安装保护 | 49 个受管文件与旧清单全部一致；额外 4 个文件均为 scripts/__pycache__ 内的 Python 缓存，直接升级会被完整性保护拒绝。核对差异后，将旧目录完整迁出 Skills 搜索目录，再按正常安装入口安装新包，未绕过校验 |
| 旧版保全 | 完整目录及缓存保留于 `C:/Users/24598/.agents/backups/sdd-init-20261104-before-platform-sync-c8852404`，迁移前后全部文件哈希一致 |
| 新包与安装 | 53 个受管文件及 66 个 ZIP 载荷文件；清单哈希与 ZIP CRC 通过，已安装目录与构建包清单一致；重复安装返回 Already current |
| 需求资源 | 内置 sdd-commit/SKILL.md 与 references/git-remote.md 均与当前来源逐字节一致；实际安装器在临时项目展开后的两份资源仍与来源及内置 ZIP 一致 |
| 实际安装器冒烟 | 从用户级已安装脚本对临时项目执行 init：六个项目 Skills、五个角色；再次执行后全项目文件哈希不变。展开的两份 commit Markdown 为 0 错误、0 警告，冒烟后用户级安装清单仍有效 |
| 升级保护回归 | `python -B -m unittest discover -s tests -p test_user_install.py -v`，5/5 通过；覆盖隔离升级、定制／缺失／额外文件保护、损坏包、并发锁及失败回滚 |
| 其他范围 | 其他用户级 Skills 的文件哈希及用户配置哈希不变；未初始化或升级当前仓库及任何真实项目，未执行远端交付 |

构建后入口与 prompting 的文档检查通过。实际安装与冒烟详情另生成于 `.build/user-install-sync-20261104/install-audit.json`；本次结果证明用户级入口及分发载荷已更新，不替代真实 GitHub／GitLab 交付或模型行为评测。历史未安装记录保留原有版本归属。

## 2026-11-04 sdd-commit 推送前远端同步补齐

依据 [Spec FR-003／AC-003](../specs/platform-independent-sdd/spec.md)，本轮修正此前仅检查仓库定位和合并前状态、未明确 push 前同步的缺口。更新当时的 Skill 和平台指引，要求远端交付分支创建前及每次 push 前刷新实际引用，分别比较任务与远端同名分支、任务与集成目标；落后或分叉先安全整合并完成受影响检查。固定维护基线沿用既有约定，获取失败或冲突未解不继续推送，保留无关未提交及预暂存内容。普通必要同步沿用终点授权，不增加逐步确认。[现行远端同步检查](../source/project/.agents/skills/sdd-deliver/references/git-remote.md#远端同步检查)

| 检查 | 实际步骤／范围 | 结果与边界 |
|---|---|---|
| 首次推送的旧 main | 临时 bare 仓库及两个 clone；本地从旧 main 建任务分支，另一 clone 更新 main；先读取旧 tracking，再 fetch、以 rev-list／merge-base 比较，merge 最新目标后首次普通 push | 通过；刷新前 tracking 看似已包含目标，刷新后识别双方各 1 个独有提交；整合后包含最新目标 |
| 远端任务分支分叉 | 两个 clone 分别提交同一任务分支；fetch 后比较、保留双方历史 merge，再普通 push | 通过；比较为双方各 1 个独有提交，整合后同时包含远端任务及目标提交 |
| 并发更新及脏工作区 | 查询后另一 clone 推进任务分支；本地普通 push 被拒绝；保留一项暂存及一项未暂存修改再 fetch；另向不存在的临时仓库 fetch | 通过；非快进拒绝未覆盖远端提交，fetch 前后两类 diff 相同；失败 fetch 返回非零，未更改远端；不据此证明 Agent 已自动执行恢复 |
| Skill／文档 | quick_validate.py；doc_check.py 检查 Spec、Skill、平台指引、夹具说明及本记录；git diff --check | Skill 通过；5 个 Markdown 为 0 错误、0 警告；差异格式通过，部分既有文件有换行规范化提示 |
| 定向分发回归 | unittest 的 test_build.py，选择 payload_and_shared_resources、build_is_reproducible、distribution_is_generic、generated_installer_is_idempotent 四项 | 4/4 通过；来源／载荷一致、可重建、引用、新装及幂等检查，均在临时目录执行 |
| 行为夹具 | 新增首次 push 旧 main、远端分叉与脏工作区、刷新竞态、固定维护基线 4 例 | JSON 及唯一编号校验通过；新增及既有场景保持模型执行 UNVERIFIED |

Git 实验只操作临时本地仓库，使用显式 fetch、提交关系比较、fast-forward／merge 与普通 push，验证所选同步方法的 Git 行为；未执行真实 GitHub／GitLab 写入，未验证模型会遵循新增规则。未修改本仓库工作分支或远端引用，未升级已安装副本。本轮只运行上述定向回归；此前 36／40 项结果仍属于此前快照。

## 2026-11-04 sdd-commit 双平台职责扩展

依据 [Spec FR-003／AC-003](../specs/platform-independent-sdd/spec.md)，本轮更新 sdd-commit、原位平台指引、仓库治理、delivery 角色与交接、安装导航及行为评测夹具。采用主 Agent 内容自查；既有未提交修改保留，未更改安装器逻辑、用户级安装或其他项目。

| 场景 | 本轮落点与核对结果 |
|---|---|
| 用户指定交付终点 | Skill 区分本地提交、创建分支、推送、Issue、PR／MR、合并；自主完成必要步骤，保留只建分支及只建 Issue 的停止点，不逐项要求用户操作；无新改动仍可继续远端交付 |
| GitHub／GitLab 适配 | 沿用 git-remote.md，补充主机／仓库定位、企业／自托管、subgroup 与 fork、连接工具／gh／glab／API 路由、查重及平台对象回读；需求与报告权威保持原位 |
| 合并及失败恢复 | 核对最新 head、目标及检查／审批／保护规则，使用预期 SHA 条件；排队与已合并区分，超时先查询，认证缺口只交回必要动作；不附带强推、删除或绕过保护 |
| 行为评测准备 | 新增 7 例：只建分支、GitHub fork PR、GitLab 自托管 MR 续交、只建 Issue、head／排队状态变化、超时恢复、认证缺口；17 例 JSON 解析、编号唯一性及 delivery TOML 解析通过，模型执行均保持 UNVERIFIED |

| 检查 | 命令／范围 | 实际结果 |
|---|---|---|
| Skill 结构 | skill-creator 的 quick_validate.py 检查 sdd-commit | 通过 |
| 文档 | doc_check.py 检查 Spec、Skill、平台指引、治理、交接、夹具说明及本记录；另检查构建后的 SKILL.md 与 assets/prompting.md | 来源 7 个及构建后 2 个 Markdown，均为 0 错误、0 警告；不据此推定行为通过 |
| 仓库回归 | `python -B -m unittest discover -s tests -v` | 36/36 通过；覆盖来源／载荷一致性、可重建、隔离安装与升级、导航及角色配置保护 |
| 构建 | `python -B scripts/build_release.py --output .build/platform-delivery-20261104/sdd-init` | 成功，未覆盖旧构建目录 |
| 安装器回归 | `python -B .build/platform-delivery-20261104/sdd-init/scripts/test_govern.py` | 40/40 通过；全部使用临时项目 |
| 引用与差异 | `python -B scripts/skill_context_stats.py`、`git diff --check` | 六个 Skill 的直接引用均存在；差异格式通过，部分现有 CRLF 文件有 Git 换行规范化提示 |

平台参数已对照指引中链接的官方文档核对，但未执行真实 GitHub／GitLab 交付或真实模型评测；安装与打包测试不证明平台认证、权限、CI、审批及合并链路已实测。未执行本仓库 commit、push、远端 Issue／PR 更新或 merge，未安装到用户级或其他项目。

## 2026-11-04 全仓指令精简复核

依据 [Spec FR-017／AC-017](../specs/platform-independent-sdd/spec.md)，本轮按语义盘点现行仓库治理、通用约束及五项专项架构 Rule、观测与提示词规范、六个 Skill 入口、五个角色、九份输出模板、初始化片段、项目索引、工具输出及行为评测夹具。执行者为本次主 Agent，采用内容自查；未启动独立角色或真实模型行为评测。

| 对象 | 本轮处理 |
|---|---|
| 通用提醒 | 删除重复的如实报告、不虚构、不夸大、证据不足不判通过、局部成功不等于整体成功等外围声明；删除提示词参考中的通用“事实真实性”条目，未搬移到其他规则正文 |
| 生成文本与相应检查 | 精简安装成功输出和两处蓝图占位告警，保留告警触发条件；行为夹具移除未测退款不得标通过的泛化禁止项，保留取消后仍提交的失败场景及修复交接；现有回归不绑定已删提醒，无需增加字符串断言 |
| SDD 专有约束 | 保留 Spec／Blueprint／报告权威、角色及写入分工、授权、独立审查、人工确认、版本追溯、Review 同一快照全部适用项与 Test 全部目标 AC 及组合行为的 Gate 判据；工具机械检查边界保留 |
| 系统技术约束 | 保留持久化回执、业务与观测隔离、媒体拒收、正式与测试资产及装配隔离；保留并发写入的业务实体落库、观测状态快照及直接／间接依赖约束；业务模型提示词的输入、权限和生命周期契约保留 |
| 历史与已有修改 | 保留 baselines、既有执行记录及观测示例的失败／UNVERIFIED 状态；沿用 FR-017／AC-017，不增加精简需求编号，保留其他未提交及并发修改 |

被测版本为 `f83f76092d5f46e5c5ad8ba119e63053185ec886` 加本次工作区未提交改动。Windows／PowerShell；安装回归使用隔离临时项目和临时用户目录。构建目录为 `.build/generic-guidance-audit-20261104/sdd-init`，载荷 SHA256 为 `bd51bbebc892427b9df8bf2f461b59aa6c27fff371bb8fea11d630c41a0ab733`。

| 检查 | 命令或证据入口 | 结果与覆盖 |
|---|---|---|
| 源文档检查 | `python -B source/project/.agents/sdd/scripts/doc_check.py --root . AGENTS.md README.md docs specs source/project tests/fixtures` | 36 个 Markdown，0 错误、0 警告；覆盖现行分发、维护说明、Spec 和夹具说明 |
| 投影入口检查 | `python -B source/project/.agents/sdd/scripts/doc_check.py --root .build/generic-guidance-audit-20261104/sdd-init SKILL.md assets/prompting.md` | 2 个 Markdown，0 错误、0 警告；初始化器共享引用按构建后的真实位置解析；托管片段的安装后链接由安装回归覆盖 |
| 仓库回归 | `python -B -m unittest discover -s tests -v` | 36/36 通过；分发、可重建、新装／升级／幂等、既有内容及配置保护、文档 CLI、隔离用户安装及回滚 |
| 构建 | `python -B scripts/build_release.py --output .build/generic-guidance-audit-20261104/sdd-init` | 成功；从现行来源重建 |
| 安装器回归 | `python -B .build/generic-guidance-audit-20261104/sdd-init/scripts/test_govern.py` | 40/40 通过；安装保护、链接、存量状态及 Gate 证据检查 |
| 产物完整性 | 构建清单、ZIP CRC、载荷及初始化器／共享投影与来源逐字节核对 | 52 个清单文件哈希、63 个载荷文件及全部来源投影一致 |
| 入口引用与格式 | `python -B scripts/skill_context_stats.py`、`git diff --check` | 六个 Skill 直接引用均存在；差异格式通过，Git 提示部分 CRLF 文件后续规范化为 LF |

遗留验证范围：真实模型行为评测仍为 UNVERIFIED；观测多语言完整基线及共享栈当前运行状态未验证，Java 历史媒体示例冲突保留且未执行。本轮未执行包发布、真实用户安装、其他项目升级、产品部署、commit、push 或 merge；既有历史记录保持原有版本归属。

## 2026-11-04 仓库治理与六类架构 Rule 复核

依据 [Spec FR-012／FR-014、AC-012／AC-014](../specs/platform-independent-sdd/spec.md)，对仓库治理、架构规范、观测基线、候选目录、蓝图／契约／时序模板、原型、角色交接、文档写入及实施／审查／验收入口进行职责与语义核对。执行者为本次主 Agent，属于内容自查，不声明独立架构审查或产品验收。

本轮修正：候选目录明确六类 Rule 已生效；媒体保存禁令显式覆盖链路载荷；观测示例中的范围和历史保留策略与现行规则分开；实施、文档写入和治理审查入口承接六类 Rule；治理中的断言技术要求改为引用架构规范。保留基线稳定编号、业务／测试音频例外、瞬时处理例外、观测故障隔离和业务反向依赖禁令，未新增技术选型。复核后，在上述范围未发现剩余职责混放、重复权威正文或已确认约束遗漏；模板必要字段提示及指向正文的摘要属于使用入口，不另立规则。

被测版本为 `f83f76092d5f46e5c5ad8ba119e63053185ec886` 加本次工作区未提交改动（含此前协同、模板、文档 CLI 和本轮规范变更）；Windows／PowerShell 环境，测试使用隔离临时项目及临时用户目录。实际载荷 SHA256：`e92b6bb97ade8dfaf5c68dd1598ca06e9e01750de1d9e9a5b102b86cecf532b2`。

| 检查 | 命令或证据入口 | 结果 |
|---|---|---|
| 文档机械检查 | `python -B source/project/.agents/sdd/scripts/doc_check.py --root . source/project/.agents/sdd source/project/.agents/skills specs/platform-independent-sdd/spec.md` | 27 文件，0 错误、0 警告 |
| 仓库回归 | `python -B -m unittest discover -s tests -v` | 36/36 通过；含构建可复现、分发一致、新装、更新、定制保护、用户安装回滚和隔离 |
| 构建 | `python -B scripts/build_release.py --output .build/governance-architecture-audit-20261104/sdd-init` | 成功 |
| 构建后安装器回归 | `python -B .build/governance-architecture-audit-20261104/sdd-init/scripts/test_govern.py` | 40/40 通过；含安装导航、幂等、既有正文和运行配置保护、缺失资源拒绝及存量工具 |
| 产物完整性 | 构建目录 `build-manifest.json`、`assets/repo-payload.zip` 与 `source/project/` 逐字节核对 | 52 个清单文件哈希、63 个载荷文件及 ZIP CRC 全部通过 |
| 差异格式 | `git diff --check` | 通过；Git 提示 README 和测试文件后续规范化 CRLF 为 LF |

未修改真实用户级安装或其他项目，未执行推送、产品部署及人工验收。观测多语言示例的 full_baseline 仍为 UNVERIFIED，Java 历史媒体示例冲突仍保留且未执行，共享栈当前状态未验证；这些实现缺口不由文档或安装测试通过来消除。

## 2026-11-04 默认分支安装验证

[PR #2](https://github.com/bigsmartben/sdd-init/pull/2) 已合并至 main，合并提交 `8c5ed74949ac3e2a6d8b60f6c913654026aaa867`。执行 `python -B scripts/smoke_package.py --from git+https://github.com/bigsmartben/sdd-init.git` 通过：从 GitHub 解析默认分支、构建并安装用户级 Skill、重复安装、初始化临时项目、核对五 Skills／五角色、确认用户级重装不修改项目以及项目重复初始化稳定。实际使用入口见[安装说明](installation.md)。测试未改动真实用户级安装；Codex UI 加载与调用仍未人工验收。

以下为合并前的分支验证记录。

## 2026-11-04 uv 用户级安装入口

按本轮用户确认的一条 uvx 命令安装方式实现；使用入口与更新操作见[安装说明](installation.md)。Python CLI／用户级安装逻辑位于 `src/sdd_init/`，`setup.py` 调用既有构建器将完整资源放入 wheel，`MANIFEST.in` 保证源码包具备重建输入。项目载荷继续保留为 ZIP，不注册成多个用户级 Skills。

| 验证场景 | 本地结果 |
|---|---|
| 仓库测试 | `python -B -m unittest discover -s tests -v`：25/25 通过，含首次安装、重复、更新、定制／缺失／额外文件保护、损坏载荷零写入、并发拒绝与替换失败恢复 |
| 原安装器回归 | 临时构建后的 `scripts/test_govern.py`：39/39 通过 |
| 源码包到 wheel | `uv build --out-dir .build/dist` 成功，从源码包重建 wheel，资源包含在包内 |
| wheel 与源码实际执行 | 分别运行 `scripts/smoke_package.py --from .build/dist/sdd_init-0.1.0-py3-none-any.whl` 与 `--from .`：成功；临时用户目录仅一个 Skill，目标项目五 Skills／五角色，重复执行稳定，用户级重装不改已有项目 |
| Git 来源 | GitHub HTTPS 分支入口已通过 `scripts/smoke_package.py` 完整验证，解析提交 `fb65a977ab871ccbe1d747bcbb3c399912cf3989`；此前 Windows 本地 `git+file` 的 uv 崩溃不影响此 HTTPS 路径 |
| CI | [提交 fb65a97 的远端 CI](https://github.com/bigsmartben/sdd-init/actions/runs/41777671560)：Ubuntu／Windows 两端全部通过，包含仓库测试、39 项安装器回归、源码包／wheel 构建及 wheel 冒烟 |

全部安装使用隔离的临时目录，未修改真实用户级安装、其他项目或用户运行配置。实现已提交并推送至 `codex/workflow-contract-plan`，GitHub HTTPS 分支安装与临时项目初始化全流程已通过；当前可用命令见安装说明。未合并至 main，不带版本的默认分支命令尚不可用；本轮需求未写入远端 Issue。Codex 实际加载与交互调用未人工验收，客户端 `/sdd-init` 快捷入口不可由 Python 包保证，官方 CLI 入口为 `$sdd-init`／`/skills`。本地结果不能替代这些未验证项。

## 2026-11-04 独立沟通规范分发验证

最终源码完整回归：`python -B -m unittest discover -s tests -v` 通过 20/20；`python -B scripts/build_release.py --output .build/final-communication-20261104/sdd-init` 构建成功；`python -B .build/final-communication-20261104/sdd-init/scripts/test_govern.py` 通过 39/39。检查构建清单哈希、ZIP CRC 和载荷与源码逐字节一致，并确认分发入口及规范正文包含可视化对齐与结论先行两条原则。临时项目测试覆盖新装、上一版升级、原正文保护和重复执行；升级须显式使用 `--update-skills`。未修改用户级安装或其他实际项目；测试不证明真实 Agent 每次运行均遵循规范。

“结论先行、分层确认”补充复核：将推荐结论限定于方案选择，Review／验收先给实际结果；决策必需细节简要呈现，详细材料作为可选入口，授权内细节自主推进。合并重复执行表述，仓库与分发首部入口保持一致。新增 `test_conclusion_first_rule_new_install_and_previous_version_upgrade`，验证新装、旧版入口及规范资源显式升级、正文保留和重复执行；连同现有沟通迁移、分发链接、可复现构建测试，本轮定向 4/4 通过。规范链接、锚点及 `git diff --check` 通过；全部构建及安装使用临时目录。本轮未更改安装器逻辑，未重跑完整 39 项存量工具回归；以下全量结果属于此前快照。

复核修复：新增回归先复现 UTF-8 BOM 被移入正文、资源父目录被普通文件占用时 AGENTS 已被写入的问题；修复后 BOM 保留文件首部，父路径冲突在任何写入前报告。规范进一步区分产品交互与其他产品判断、原型审阅与实际集成验收，明确确认不自动授权落盘，已有视图按需复用；架构文档规范仅在实际编写对应文档时适用。

| 修复后验证 | 实际结果 |
|---|---|
| `python -B -m unittest discover -s tests -v` | 19/19 通过；新增 BOM／混合换行的新装升级幂等、资源父路径冲突的零写入保护 |
| `python -B scripts/build_release.py --output .build/visual-governance-reviewed-20261104/sdd-init` | 构建成功；清单哈希、ZIP CRC、载荷及安装器与维护源字节一致 |
| `python -B .build/visual-governance-reviewed-20261104/sdd-init/scripts/test_govern.py` | 39/39 通过 |

以下为首次实现记录；本节修复后验证对应当前源码。

依据本轮用户确认的实施计划，当前仓库与项目默认分发共同引用[可视化沟通与确认规范](../source/project/.agents/sdd/references/visual-confirmation.md)。独立沟通原则管理块置于 AGENTS 首部，流程导航独立管理；安装器已补齐规范的允许路径与必需文件校验。规范不以前置启动 Skill、角色或业务工作流为条件。

| 验证 | 实际结果 |
|---|---|
| `python -B -m unittest discover -s tests -v` | 17/17 通过；含构建一致性、中文 LF／CRLF 正文保留、新装、旧片段升级、原则块移至首部及重复执行的逐字节一致性 |
| `python -B scripts/build_release.py --output .build/visual-governance-20261104/sdd-init` | 构建成功；规范正文和独立沟通原则模板随包分发 |
| `python -B .build/visual-governance-20261104/sdd-init/scripts/test_govern.py` | 39/39 通过；安装、已有正文／配置保护及存量工具回归 |
| 失败保护 | 缺失必需规范、非法载荷、缺失／重复／嵌套管理标记及 override 遮蔽均在写入前失败；临时目标快照不变 |

验证仅使用隔离临时项目与本地构建产物；用户级安装及其他实际项目未修改，未提交、推送或发布。上述结果证明默认分发与安装行为，不证明真实客户端中的 Agent 每次执行均遵循沟通要求。

## 2026-11-03 当前本地分发验证

本节记录本次用户指定以 hanxue-live 已安装的项目 Skill、Agent 为来源、恢复五 Skill 与五角色并去除项目专属映射后的实际结果；不是另一份需求或 Plan。[Issue #1](https://github.com/bigsmartben/sdd-init/issues/1) 和 [Draft PR #2](https://github.com/bigsmartben/sdd-init/pull/2) 仍保留此前四 Skill／七角色方案，本轮未修改远端正文。以下当前结果取代旧方案的现行分发描述，后文旧验证仅用于追溯。

- 当前项目 Skill 为 sdd-doc、sdd-imp、sdd-test-loop、sdd-review-loop、sdd-commit；角色为 sdd-designer、sdd-coder、sdd-documenter、sdd-validator、sdd-delivery。个人级 sdd-init 仍只分发项目资源。
- 初始化器、托管导航、元数据与回归检查按上述清单适配；增加 module-design、sequence-flows 模板的载荷许可及必需性检查。旧 sdd-accept 和被替代角色在任何写入前报告冲突，即使显式升级也不静默删除。
- 清除来源项目的专属需求路径、课堂映射、架构链接和 ARC 编号；由目标项目 docs/index.md 解析实际需求、蓝图和契约，模板不预设独立 Spec 已退役。模板与 Skill 的可复用职责保留，默认目录按项目治理规则定位。
- 模型默认值沿用五角色来源：designer 使用 gpt-6-astra，coder 使用 gpt-6.1-sol，documenter／validator／delivery 使用 gpt-6.1-terra；不设角色推理强度，不改用户运行配置，保护同名定制及既有文档。

| 检查 | 本次结果 |
| --- | --- |
| `python -B -X utf8 -m unittest discover -s tests -v` | 12/12 通过；覆盖可复现构建、幂等、定制及既有实体保护、五角色模型、非法载荷拒绝、旧入口迁移保护、新模板必需性和通用资源链接 |
| `python -B -X utf8 scripts/build_release.py --output .build/five-skills-five-agents-verified/sdd-init` | 构建成功，产物仅在仓库本地生成 |
| `python -B -X utf8 .build/five-skills-five-agents-verified/sdd-init/scripts/test_govern.py` | 39/39 通过；新安装、重复执行、显式升级、配置保留、相对文件链接和存量状态／快照／提交边界 |
| 产物独立核对 | 清单的 51 个文件 SHA-256 全部一致，ZIP 的 63 个文件与维护源逐字节一致；清单为五项目 Skill、五 Agent，无额外入口；ZIP CRC 正常 |
| 通用性与格式 | 构建及安装后的 Markdown 不含来源项目名、专属需求路径、课堂映射、固定 ARC 映射及失效架构路径；分发文档／角色／元数据 UTF-8 解码通过，`git diff --check` 通过 |

以上为隔离临时项目及本地构建验证，不表示用户级安装、hanxue-live 或其他项目已升级，也不证明真实客户端加载、指定模型运行或产品人工验收。未执行远端更新、提交或推送。存量状态工具仍读取本地 Spec/Status，不能自动解析 Issue 或项目自定义需求映射；使用前核对实际能力，未做批量迁移。

## 此前四 Skill／七角色方案的历史实施记录

以下为此前实际实施与验证记录，不作为当前分发清单。

2026-11-02。本地分支 codex/workflow-contract-plan，起点 60c6bef；2026-11-03 按用户确认将七角色模型建议调整为 TOML 默认模型；需求与实施安排分别引用 [Issue #1](https://github.com/bigsmartben/sdd-init/issues/1) 和 [Draft PR #2](https://github.com/bigsmartben/sdd-init/pull/2)。本文件记录实际结果，不维护另一份需求或 Plan。

## 实际交付

- 更新 sdd-doc、sdd-imp，引入 sdd-accept，撤下 sdd-test-loop 与 sdd-review-loop 的分发入口；保留初始化和 Git 交付配套职责。元数据允许按明确自然语言意图选择，不绑定模型或强制委派。
- 共享说明与入口统一实体归属；提供 Issue、Blueprint、Draft PR 通用模板、六类场景提示、原型引用和人工验收操作模板。原型说明覆盖产品代码隔离、候选操作、固定版本引用和用户确认。
- 初始化只安装资源与导航，不创建 Blueprint／Spec／Status、不回填存量状态、不改用户配置。退役 Skill 冲突在写入前拒绝，不静默删除用户副本；含旧入口的项目升级仍需单独处理。
- 存量状态工具保留原有记录语义并标明适用边界；项目侧撤下不可用的安装入口。观测资源保留为按项目决定采用的参考，不预填项目架构或采纳结果。
- 根据后续确认增加七个项目角色，源位于 source/project/.codex/agents/，通过同一载荷安装。角色包含名称、场景说明、默认 model 和职责指令；模型映射与优先级见执行协作说明，不设置角色推理强度或修改用户运行配置。

## 本地验证

| 检查 | 结果与覆盖 |
| --- | --- |
| python -B -m unittest discover -s tests -v | 2026-11-03 重跑 11/11；载荷一致、可复现、幂等及既有正文保护、新安装实体边界、退役入口拒绝、缺失新模板拒绝；覆盖七角色默认模型、同名模型定制保护、旧无模型角色显式升级、非法或缺失模型及固定强度载荷在写入前拒绝、运行配置保护 |
| python -B scripts/build_release.py --output .build/role-model-defaults/sdd-init | 2026-11-03 构建成功；仅生成本地候选 |
| python -B .build/role-model-defaults/sdd-init/scripts/test_govern.py | 2026-11-03 重跑 39/39；安装后七角色模型映射与无推理强度字段、升级保护、用户配置保留、链接、调用策略及存量记录／快照／提交边界 |
| skill-creator quick_validate.py | 2026-11-02 的 5/5 静态格式检查；本次未重跑，Skill frontmatter 未变 |
| 文档检查 | 2026-11-03：源文件 UTF-8、30 个 Markdown 文件的 39 个相对文件链接及 git diff --check 通过；产物内链接随回归检查，托管片段按安装后位置解析 |
| 导入追溯 | 初始提交 e6bf191 的 50/50 文件哈希与 import-manifest 相符；本次维护源变化不改写历史哈希 |

CI 增加构建产物回归命令；以上是本地结果，远端执行状态以 PR 检查为准。现有回归中旧状态测试使用显式存量夹具，新初始化器不再替测试生成业务实体。旧精确口令断言改为当前调用策略检查，缺失角色引用随通用模型绑定说明撤下；本轮新增的七角色为明确确认的新职责配置。

角色测试初次将所有 TOML 都当角色，误计入既有 Rust Cargo.toml；已将检查限定为角色文件及安装位置，重新运行 10/10 通过。

## 职责语义核对

按入口和共享说明走查代表性表达：“讨论这个方案”仅讨论；“对”仅确认；“对，把结论更新到 Issue”进入固化；“按方案开始实现”进入实施及局部自验；“把版本 X 部署到环境 Y 供我验收”准备环境和操作文档；验收反馈先进入讨论，有明确修复要求再实施。“落地”仅在上下文确实不足时澄清。

这属于指令内容核对与静态检查，没有独立模型行为测试或真实部署证据，不宣称每次运行行为已获保证。

## 剩余事项与限制

- AC-003 的入口、说明与模板已在本地实现；AC-007 的相称本地检查通过，尚未进行用户人工验收。
- AC-004 已提供不依赖平台的说明与模板；目录、托管平台和访问方式待实际项目确定，没有生成并发布具体原型，不算完整原型交付验收。
- AC-005／006 原重型目标移出本轮，不计完成。存量工具仍有全能力检查及 Status 重建语义，不支持 Issue 新工作流，也未进行批量迁移。
- AC-008 的七角色配置与分发已实现并通过本地检查；未在真实目标项目加载角色或开展独立模型行为测试。角色文本边界不等于硬性权限隔离。
- 没有安装到用户级或其他项目，没有产品部署、人工验收、合并或关闭 Issue。此前精简工作流代码与说明已同步 Draft PR；2026-11-03 的默认模型调整尚未提交或推送，远端代码与 CI 不包含该调整。提交与 CI 回执以 PR 为准，不表示其他项目升级完成。


## 2026-11-04 压缩规范复核与安装验证

依据 [Spec FR-019 / AC-019](../specs/platform-independent-sdd/spec.md)，对照压缩前快照复核治理、文档写入规则和观测基线，并核对架构规范、协作、原型、Skills 及模板。当前工作区基于 `f83f76092d5f46e5c5ad8ba119e63053185ec886`，包含未提交修改；本轮由同一执行者复核，不声明独立审查。

| 核对对象 | 结果 |
|---|---|
| 职责与权威 | 治理承载授权、资产及完成条件；架构承载技术约束；doc 归并文档；Review 检查架构实现，Test 检查需求行为；未发现压缩导致的职责混淆 |
| 约束承接 | 授权沿用、例外、实现完成、独立复核、人工确认、版本归属、正式／测试隔离、落库判据、观测非阻塞及媒体边界均有正文或有效引用承接；未发现遗漏，原标题及显式锚点保留 |
| 源文档 | 文档 CLI 检查共享资源、Skills、初始化提示、README、安装说明及 Spec，共 30 份，零错误／警告 |
| 构建 | `python -B scripts/build_release.py --output .build/compression-review-20261104/sdd-init` 成功 |
| 分发回归 | `python -B -m unittest discover -s tests -v`，36/36 通过，包含临时目录中的用户安装、升级保护与回滚检查 |
| 产物安装回归 | `python -B .build/compression-review-20261104/sdd-init/scripts/test_govern.py`，40/40 通过 |
| 隔离新安装 | 在 `.build/compression-review-20261104/installed-project` 执行产物安装器 `init` 成功；安装后的 AGENTS、索引、共享资源及 Skills 共 28 份 Markdown 检查通过；构建后初始化 SKILL 的链接检查通过 |
| 载荷一致性 | ZIP CRC 正常，63 个载荷文件与当前项目源及隔离安装结果逐字节一致；52 项构建清单哈希一致 |

载荷 SHA-256：`9b8d1d3bffc2f686f72717f8e9c65f359280ef2e539d2d35a58e2d0c3b88fded`。

初次将初始化入口和托管片段按源码位置检查，出现 13 个目标缺失；这些引用按构建／安装位置解析后全部通过。隔离新安装首次因目标目录尚未创建而拒绝，创建目录后成功。未修改真实用户级安装或其他项目，未执行产品部署或目标项目验收；本轮未新增或修改规范条款。

## 2026-11-04 测试 Issue 清单与复验闭环

依据 [Spec FR-021／AC-021](../specs/platform-independent-sdd/spec.md)，更新测试报告模板、test／doc／imp、文档写入规则、治理、场景提示及项目索引。验证对象为基于 `f83f76092d5f46e5c5ad8ba119e63053185ec886` 的当前未提交工作区；本节记录文档维护检查，不代表真实目标项目的 Test Gate 或独立模型行为测试。

| 检查 | 结果与范围 |
|---|---|
| 条款与场景走查 | 无 Issue 时记无；多场景关联同一 Issue；修复与局部自验完成后待复验；复验失败沿用编号并保留历史；需人工确认时保持待确认；证据／文档／需求问题分别归位；非代码问题按处理结果核验关闭；Review 沿用专用 gap |
| 源文档与技能 | 本轮修改及直接关联的 12 份 Markdown（含本记录）检查通过，零错误／警告；test、doc、imp 三个技能的 quick_validate.py 检查通过；本轮 10 份修改文件的 UTF-8 与差异空白检查通过 |
| 现有回归 | `python -B -X utf8 -m unittest discover -s tests -v`，36/36 通过，覆盖构建、安装保护、载荷一致性及文档 CLI |
| 最终隔离构建与安装 | 临时目录内构建并执行 `init` 成功；ZIP CRC 正常，64 个载荷文件与项目源及安装结果逐字节一致；安装后 29 份 Markdown 检查通过，零错误／警告 |

最终载荷 SHA-256：`929e5e73bebcbc8e4d77e481f72ef0344c141e2c2be7a5a4cb38bca6b2f75bcc`。本轮 Issue：无。检查产物位于临时目录并随验证清理；未修改用户级安装或其他项目，未执行提交、推送或历史报告迁移。

## 2026-11-04 sdd-deploy 技能与安装分发

依据 [Spec FR-022／AC-022](../specs/platform-independent-sdd/spec.md)，新增当时的 `sdd-deploy` 及 UI 元数据，同步六个技能的安装清单、README、安装说明、托管导航、治理、协作与项目索引；保留五个角色。检查对象为当前未提交工作区，未修改用户级安装或其他项目。[现行部署指引](../source/project/.agents/skills/sdd-deliver/references/deployment.md)

| 检查 | 结果与范围 |
|---|---|
| 语义走查 | 对照已确认意图，默认 dev 并支持指定环境；按请求触发，不随代码修改自动运行、不增设审批；环境准备与修复、首次部署、既有服务更新重启、重复调用复用及冲突诊断均有执行路径；运行就绪与业务验收分开 |
| 技能及源文档 | quick_validate.py 通过；本轮 7 份源 Markdown 零错误／警告；本记录另行执行文档校验 |
| 分发与仓库回归 | unittest discover 首次 36/37 通过，唯一失败为上下文统计仍预期旧技能数；改为包含初始化器的 7 个入口后，该测试文件 2/2 通过。新增部署技能升级与缺失载荷保护测试通过 |
| 构建后安装器回归 | test_govern.py 首次 39/40 通过，唯一失败为载荷仍预期 5 个项目技能；更新为 6 后，对应测试 1/1 通过 |
| 隔离构建与安装 | 临时目录内构建和 init 成功；构建后的初始化入口 1 份、安装后的共享资源／技能／导航 30 份 Markdown 检查均为零错误／警告 |
| 差异检查 | git diff --check 无空白错误；Git 提示部分文件后续将按仓库规则由 CRLF 转 LF |

以上为规则语义走查及工具、安装验证；未进行独立模型行为评测或真实环境部署。构建与安装检查产物随临时目录清理，未执行提交或推送。

## 2026-11-04 部署环境规范通用化

依据 [Spec FR-022／AC-022](../specs/platform-independent-sdd/spec.md) 的补充确认，将用户级 local-base-environment 中的通用环境探测、准备修复、挂载验证与资源隔离要求融入 sdd-deploy。保留项目既定部署规范优先及 dev 优先 Compose，不引入平台发行版、固定路径、个人仓库或特定工具栈，不修改用户级技能。

本轮仅更新技能正文、对应 Spec 与本记录。语义核对覆盖先探测再落地、本地与远端状态区分、服务复用、共享依赖与持久化数据隔离，沿用按请求触发和不增设审批的约定。技能同口径非空白字符由 1415 降至 1197（减少约 15.4%），无新增参考文件或脚本。quick_validate.py 通过；技能与 Spec 两份 Markdown 检查零错误／警告；隔离构建及 init 成功，载荷和安装后的技能与源文件逐字节一致，安装后技能文档检查通过。本记录另行执行文档校验。

未执行真实环境部署或独立模型行为评测；本轮无工具代码变更，未重复运行全套回归。临时构建与安装目录已随检查清理。

## 2026-11-04 imp 上游任务交付与 Review 架构职责分离

依据 [Spec FR-005／FR-012／FR-020 与 AC-004](../specs/platform-independent-sdd/spec.md)，按用户最新确认将 imp 定位为明确上游任务的交付者，覆盖需求、Bug 与 Review issue。T001 确认内容归并、T002 技能／角色／治理／模板同步、T003 局部检查均完成；检查对象为当前未提交工作区。

语义核对覆盖无 Blueprint 的明确任务、普通 Bug、Review 整改交接、重构代码执行与架构判断分离；同步清理原型资源的间接架构约束。新增两个行为用例，模型执行仍为 UNVERIFIED，未将人工语义走查当作模型评测或独立架构 Review。

`python -B -X utf8 -m unittest discover -s tests -v`：49/49 通过，覆盖构建、安装保护、角色与文档工具。修改的 10 份 Markdown 机械检查零错误／警告；本记录另行检查。`git diff --check` 无空白错误。保留原有 AGENTS.md 和未跟踪项目资源，未安装升级用户级或项目副本，未提交或推送。
