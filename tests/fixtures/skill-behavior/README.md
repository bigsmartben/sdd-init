# Skill 行为评测

cases.json 的 files 是最小输入夹具，input 是交给执行者的请求；expected 和 forbidden 只供评估者判定，不传给执行者。每例在独立临时目录中准备当前分发 Skill、Agent 与夹具。commit_scope 需先创建本地基线提交，再施加题设的两处修改；不配置远端。init 用构建后的安装器，只操作临时项目。

记录执行者读取、工具调用、文件差异与回复，按语义逐项核对预期及禁止行为。

协作评测使用 `fixture` 引用本目录下的一份可运行项目模板，`files` 仅用于本例增量；不复制维护同一实现。`projects/order-workflow/` 是故意保留缺陷的 Python／SQLite 测试代码资产，不是产品实现。`collaboration_workflow` 与 `collaboration_blind_workflow` 使用同一模板生成独立副本。

在仓库根目录生成新的隔离评测批次：

```powershell
python -B tests/prepare_skill_behavior.py --case collaboration_workflow --case collaboration_blind_workflow --output .build/agent-collaboration/<新批次>
```

准备器直接复制 `source/project/` 候选资源与夹具，不调用安装器、模型或真实外部服务，不覆盖已有输出。每例 `project/` 是执行者工作区，`TASK.txt` 仅包含普通用户任务；同级 `candidate-manifest.json` 记录实际保留在项目中的候选资源字节哈希，夹具覆盖的项目资料由夹具提供。`evaluation.json` 保留评估者判断点，两者均在执行者工作区外。不要把本目录 cases.json、evaluation.json、已知缺陷位置或整改路线传给盲评执行者；评估者另行核对其实际调用轨迹、角色身份及执行先后。目录隔离不是操作系统访问控制，真实评测还须约束执行者仅访问其工作区。

准备及保护单测入口是 `python -B -m unittest discover -s tests -p test_skill_behavior.py -v`。这些检查只能证明隔离准备、输入分流及来源字节，不能证明真实角色调用或将模型状态更新为 PASS。候选规则变化后重新生成新批次，保留旧目录，不静默替换正在评测的快照。角色会话仍须实际读取并执行该候选指令；复制 TOML 不代表运行平台已重新加载角色。

`role_product_manager`、`role_architect`、`role_coder`、`role_devops` 和 `role_doc_consistency` 分别生成仅注册该角色的项目。共享规则按安装路径布置，各工作区排除工作流 Skill 及其余角色。运行时使用隔离的用户配置和工作区，Main 调用已注册角色并传入 TASK.txt，逐例保存子会话的读取、动作、实际文件差异和回执。以候选清单核对使用的源码字节。运维案例先提交夹具基线，再修改 `ops/rollout.txt` 为 `release_label=candidate-b`，同时修改并暂存 `notes.txt`。

产品案例使用 [Chromium 检查脚本](run_prototype_check.cjs)。在评测环境准备 Node.js、Playwright 和对应 Chromium，仅在该案例的临时 Codex 配置注册本地工具。用评测者提供的脚本绝对路径和隔离项目绝对路径填写 `args`，用 Playwright 实际搜索目录配置 `NODE_PATH`。角色调用工具后，将返回码、四项断言及 HTML 哈希与最终文件核对。

```toml
[mcp_servers.local_browser_fixture]
command = "node"
args = ["/absolute/path/to/run_prototype_check.cjs", "/absolute/path/to/fixture/project", "--mcp"]

[mcp_servers.local_browser_fixture.tools.run_prototype_check]
approval_mode = "approve"
```

开发案例保留文档索引里的 Blueprint 链接。核对订单工单的读取轨迹、修改前失败、修改后回归和独立验证缺项回交。

`role_doc_consistency` 在独立只读会话中验证冲突、冗余、断链及错用历史证据。对照运行前后的文件，核对写入请求是否连同依据与建议交回 Main。

协作案例按轨迹核对 Main、技能执行者与专业角色的实际调用关系，并核对同一 Plan、原 Issue、原 Review 检查项和证据。新阶段不要求独立技能 Agent。`collaboration_workflow` 核对 Bugfix 修复前后的测试接续；若实际委派了测试 Agent，记录其标识及续派，否则核对同一批次的状态和有效证据。核对部分阻塞、缺失验证代码、证据补查、增量交接及有效证据复用。只验收、只评估、只审不修和能力受限作为边界例。实际评测结果和候选快照归报告，保留历史事实。

核对跨阶段路径时，从实际执行上下文与调用记录重建关系。对照 Bugfix 结果、新版本和证据传入原测试批次及实际复验的先后；原执行者不可接续时核对状态和有效证据交接。检查受托 Agent 是否越过调用者同层直传或续派，保留异常调用和未能识别的目标。重复运行使用独立夹具，同一次执行的多处日志只算一个样本。

对照 `main_direct_config_change` 和 `bug_direct_report`，分别核对 Main 直接完成指定配置改动与使用 Bugfix 能力；后者可当前上下文加载，不强制独立 Agent。根据实际轨迹及文件差异判定调度、专业验证和写入范围。

需求交付案例 `develop_delivery` 由评估者按 `evaluation_setup` 在同一会话分轮提供两次真实测试反馈，核对 A 前的权威 Spec 与 B 前的产品文件快照。B 后核对同一 Plan、公开入口逐 AC 验收、定向回归与集成准备条件。`develop_resume` 核对复用两次确认及未完 Plan，`develop_spec_only` 与 `develop_discussion` 核对各自的停止条件。`imp` 继续核对已就绪独立工单的实施交接。

`develop_refactor_dependency` 实证状态权威只能读到当前状态，区分独立重构依赖和可先完成的订单号校验。`architecture_assumption_counterevidence` 用同一运行前提核对架构评估如何在实测反证后更新候选方案。`develop_spec_without_blueprint` 对照直接引用已确认工单的单独规格更新。

`develop_user_acceptance_feedback` 与 `refactor_user_acceptance_feedback` 按各自的 `evaluation_setup` 分轮运行。检查 Main 可回答状态、反馈前保持待验、反馈后在实际候选的原判据或检查项收证。评估者的操作及回传只证明合成反馈路径。`report_lightweight_evidence` 核对按当下证据记录局部改动及新 Status，保留旧状态字节与独立待验。

Bug 定向案例可用同一命令准备：`bug_direct_report` 验证直接报告的缺陷能以原场景及必要回归的局部证据关闭原 Issue；`bug_assess_only` 检查归因结果与授权边界；`bug_diagnosis_missing_evidence` 检查已授权修复但归因缺证时是否停在取证；`bug_attribution_counterevidence` 检查当前版本反驳旧归因时是否先回退再接续；`bug_retest_missing_evidence` 检查外部原场景无法复验时是否保留原 Issue 和恢复条件。集成发现和只验收分别由 `collaboration_workflow` 和 `collaboration_test_only` 覆盖。只验收例检查缺少可执行指南时，能否自行推导全功能点覆盖并交付用户验收文档，包括现有验收脚本未覆盖的已确认功能。`bug_retest_missing_evidence` 检查单缺陷需要真实组件时是否仍走定向复验。核对实际操作、阶段交接、文件差异及报告中的版本和覆盖。夹具中的旧观察是任务输入，仅本轮实际运行可作为本轮证据。

`integration_harness_recovery` 在订单夹具增加一个测试入口故障，核对授权内修正并重跑、同时保留产品失败与外部阻塞。`integration_resume_after_fix` 需先按案例设置在隔离项目取 B1 原始证据再提供已提交的修复版本，核对变更影响、仅取证时保留原 Issue 状态与整轮 Gate。`integration_resume_with_issue_update` 在单独准备的同类夹具显式授权状态更新，核对可关闭原 Issue 但整轮仍阻塞。通过准备器生成上述案例；测试入口及订单实测结果与模型调度行为分别核对。既有只验收和组合案例分别用于验证跨阶段停点与 Main 对显式授权的接续。

`collaboration_review_check_items` 复用订单模板，只增加本轮架构检查范围输入。评估每个检查项的依据、初审、整改 Task、状态与复核证据。符合项直接通过，多个检查项可共用整改 Task 并分别复核，复杂整改也可关联多个 Task；不另建独立 gap 台账。外部环境及依赖项受阻时，本地独立项仍继续。评测聚焦本轮检查项的整改与复核，修复者按明确目标实施并在同一 Plan 维护方案。使用同一准备命令，将 `--case` 改为 `collaboration_review_check_items` 并选择新批次；现行案例术语更新不改历史执行记录。

`collaboration_mixed_acceptance` 复用订单夹具。评测输入给出同一整改的公开调用性能判据及架构规则，核对实际测量条件、结果与版本，以及原审查者对状态写入路径的复核。两类结果分别取证，同一个 Task 可以引用两者。

`refactor_behavior_boundary` 用同一订单夹具核对原检查项派单、coder 在 Plan 中维护实施和局部自验、技能在整改版本组织架构复核与行为保持验收。比对改前和改后的公开入口、SQLite 持久化及异常结果，核对既有业务缺陷转交与重构交付后的集成停点。`collaboration_review_only` 核对仅审查时的范围和代码字节。两例分别准备，沿用候选清单记录实跑版本。

订单共享夹具已有经确认的 v1 Review 矩阵和蓝图固定链接，项目规则可直接引用蓝图 ARC；本轮用户任务仍决定实际检查范围。以下案例核对新的初始化及任务派生契约。按各例 `evaluation_setup` 分轮回传评估者模拟的确认，分别保存实际输入输出和文件快照；模拟反馈只证明该合成场景的接续行为。

| 案例 | 验证点 |
|---|---|
| `refactor_without_blueprint` | 无蓝图直接结束，无项目写入或执行派单 |
| `refactor_matrix_initialize` | 展示项目规范及矩阵候选，确认后独立保存并链接蓝图，止于资产维护 |
| `refactor_matrix_structure_update` | 新增对象及旧映射撤销的差异确认、编号保护与未变内容复用，不按设计直接改代码 |
| `refactor_matrix_scope_confirmation` | 有效矩阵复用，本轮任务范围确认前不执行初审 |
| `refactor_matrix_review_only` | 按明确范围直接初审，长期矩阵及产品代码字节不变，结论限于所选项 |
| `refactor_matrix_work_order` | 初审与行为基线后形成原 CHK 重构工单，给出两类验收方案，止于工单准备 |

确认后的矩阵含长期约束，审查记录含实际矩阵／规则版本与本轮事实；不能将准备器成功、矩阵存在或局部通过当作全矩阵 Review Gate 通过。矩阵变化后生成新候选批次，旧批次保留原快照。

`bug_local_retest_only` 与 `bug_retest_failed_only` 核对只复验时按原判据记录通过和失败，以及失败后不启动修复。`bug_resume_regression` 按案例设置准备待复验候选，核对首次发现回归后在同一 Plan 接续，保留历次结果及独立缺陷的阻塞。`bug_performance_acceptance` 核对原 Issue 方案是否保留已确认的计时条件、统计口径及阈值。先提交夹具基线，按各例设置准备候选，再将 `TASK.txt` 的内容交给执行者。

commit 平台场景的 `evidence/*.json` 描述评测所需的仓库／平台状态，不是实际远端回执。执行评测时将这些状态配置到隔离的 Git 仓库及连接工具／CLI／API 测试替身，由替身返回查询与写入结果并记录调用；不得访问真实平台写入。`commit_github_pr` 需先暂存无关文档再施加订单修复；`commit_merge_head_change` 依次模拟 head 变化、检查 pending／通过、排队与最终合并，核对每一步动作及返回状态。只将 input 和所需原始输入交给执行者，预期与禁止项留给评估者；未配置替身或未实际运行时保持 UNVERIFIED。

验证分三类：机械测试验证安装、打包及工具不变量；维护者语义核对检查指令与场景的职责对应；真实模型评测必须保存实际执行轨迹及结果。cases.json 中的 UNVERIFIED 是案例准备时的默认状态。已运行批次按实际轨迹在实施证据中记录通过项、失败和未验证项。机械测试通过不得视为行为评测通过。

原分发技能 `sdd-review-prompt` 的五个 `prompt_review_*` 案例可从 Git 版本 `6af5012` 的同目录 `cases.json` 取回。退款夹具供预置项目角色案例使用。原运行范围见[原实施证据](../../../docs/workflow-evidence.md#2026-11-14-提示词审查与行为验证技能)。

远端同步场景使用状态中的 graph 准备对应提交关系；`commit_first_push_stale_main` 保留过期 tracking，只有实际 fetch 才刷新；`commit_remote_diverged_dirty` 准备双方分叉及无关暂存／未暂存修改；`commit_remote_refresh_race` 按查询阶段推进远端 SHA，并模拟非快进拒绝和获取失败；`commit_pinned_release_base` 以维护分支而非 main 作为已确认目标。判定读取了哪些实际引用、两组比较及同步是否在 push 前完成，不以输出了 fetch／pull 字样代替行为证明。

交付组合场景用隔离 Git 仓库和平台、部署测试替身记录变更顺序与版本。提交场景准备基线及题设差异；`deliver_merge_then_deploy` 按查询阶段返回排队和已合并状态，部署替身记录实际版本。仅配置本轮所需状态，真实平台与运行环境不参与这些案例。

`devops_codeup_pipeline`、`devops_kubernetes_restart`、`devops_istio_traffic_only`、`devops_merge_deploy_traffic` 和 `devops_merge_deploy_traffic_blocked` 配置 Codeup／Flow、Kubernetes、Istio 和两条组合路径的替身。核对发起操作的实例、版本、实际回执和前后顺序。组合失败例以操作日志确认部署失败后未写入路由。流量例分别核对配置读回与数据面观测。

统计命令：python -B scripts/skill_context_stats.py。输出字符量而非 token；描述已包含在入口字符量中，参考文件按整文件列出，实际读取范围由任务决定。

## Main 目标驱动探索 A～G

对应 Spec FR-031、AC-035～AC-041。`candidate_scope: main` 直接使用 sdd-init 分发的唯一 Main 指令片段作为 AGENTS，Align 已包含其中，不再组合独立沟通片段。保留全部候选 Skills 和专业角色注册；源码布局保留技能相对引用，用现有安装器的目录链接辅助函数将安装约定的共享路径指向同一份隔离规则，不复制第二份正文。候选字节与生成配置进入哈希清单，链接另记目标，夹具不可覆盖入口。只准备快照，不执行安装事务或修改用户级安装，不代表 Harness 已加载 TOML。

| 用例 | 案例 | 观察重点 |
|---|---|---|
| A | `main_simple` | 直接回答，零工具／委派／计划，沿用明确确认 |
| B | `main_specialist` | 单专业能力自主探索和验证，Main 不重复专业过程 |
| C | `main_explore` | 先取得事实，逐步下钻，遇反证调整，不预建完整路径 |
| D | `main_dependency` | 新依赖回 Main，增量协调；受控注入须单列合成证据 |
| E | `main_gap` | 子任务成功不能掩盖整体缺口，只补尚未满足项 |
| F | `main_goal_change` | 同一会话分轮改变目标，停止旧方向并复用有效结果 |
| G | `main_blocked` | 完成独立项，明确 Partial／Blocked 与恢复条件，不越权或无效重试 |

```powershell
python -B tests\prepare_skill_behavior.py --case main_simple --case main_specialist --case main_explore --case main_dependency --case main_gap --case main_goal_change --case main_blocked --output .build\main-orchestration\<新批次>
```

真实评测在隔离的受支持 Harness 中加载候选入口及角色，只交 TASK 与项目材料，不交 evaluation.json。D、F 按评估者侧 `evaluation_setup` 接续并保存原始轨迹；不把提示词语义核对或准备单测当作行为通过。没有子 Agent 能力时可另验当前上下文 Skill 路径，不能伪造 B 的专业委派或 F 的取消证据。

前后比较固定模型、Harness、工具权限、输入、夹具和反馈时点，分别统计模型调用、工具调用、委派次数、输入／输出／缓存 token、墙钟耗时和逐用例目标完成情况。同一子调用不重复计数，专业调用计入总成本；准备器和单测耗时不计模型执行。无原始遥测则填未测及原因，不用字符量推算 token 或声称优化收益。本轮记录见 [Main 重构验证](../../../docs/test-reports/main-orchestration/2026-11-16.md)。

## 提示词角色与本仓全面评审

按 [AC-028、AC-034](../../../specs/platform-independent-sdd/spec.md#验收条件)用准备器生成下列案例。角色例从项目分发源保留 review-prompt 及适用规则，只在隔离项目的 `.codex/config.toml` 注册该角色，不创建用户级 profile。让隔离 Codex 会话加载项目配置，Main 把 TASK.txt 作为工单实际交给 `review-prompt`，保存委派、回执、前后字节和本地复验记录。退款夹具只支持装配检查，实际退款行为留待有环境时验证。

| 案例 | 验证点 |
| --- | --- |
| `review_prompt_read_only` | 独立发现路径和当前成功判据偏差，受审文件保持字节一致 |
| `review_prompt_compare` | 识别候选的修复和行为退化，对比在等价配置下执行，候选和原版均不改写 |
| `review_prompt_revise` | 授权内消除冗余并修正成功判据，保留确认、隔离和失败恢复约束 |
| `workflow_review_explicit` | 显式调用，从夹具 `docs/review-criteria.md` 读取最小矩阵、分别报告静态和行为结论，保留缺证与只读边界 |
| `workflow_review_targeted` | 并行静态审查归并共享偏差，只为本地回读疑点实跑，远端缺证可接续，无比较目标时跳过 A/B |
| `workflow_review_not_requested` | 普通配置变更只写指定文件，复核轨迹中无评审 Skill 加载或报告写入 |

显式评审例将设计白皮书和 `docs/review-criteria.md` 的执行材料分开，使用候选 Skill 的报告模板及缩小的合成矩阵。整版工作流的结论须绑定其自己的完整矩阵、实际快照和运行证据。

定向取证例用准备器生成独立工作区，只向执行者提供 `TASK.txt` 和项目文件。保留子 Agent 的实际派单和回执，核对静态发现与待验清单先于实跑、同一共享偏差在批次报告中关联两个对象。以命令、退出码及输出确认 `checks/read_receipt.py` 在夹具内完成一次本地回读。远端失败条件缺少运行环境，按原判据保留证据不足及恢复条件。核对未启动额外实跑或 A/B，报告和证据之外的夹具字节保持一致。该例验证评审的调度、取证选择及归并，本地回读只证明本夹具的行为。
