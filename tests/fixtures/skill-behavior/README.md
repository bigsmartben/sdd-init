# Skill 行为评测

cases.json 的 files 是最小输入夹具，input 是交给执行者的请求；expected 和 forbidden 只供评估者判定，不传给执行者。每例在独立临时目录中准备当前分发 Skill、Agent 与夹具。commit_scope 需先创建本地基线提交，再施加题设的两处修改；不配置远端。init 用构建后的安装器，只操作临时项目。

记录执行者读取、工具调用、文件差异与回复，按语义逐项核对预期及禁止行为。

协作评测使用 `fixture` 引用本目录下的一份可运行项目模板，`files` 仅用于本例增量；不复制维护同一实现。`projects/order-workflow/` 是故意保留缺陷的 Python／SQLite 测试代码资产，不是产品实现。`collaboration_workflow` 与 `collaboration_blind_workflow` 使用同一模板生成独立副本。

在仓库根目录生成新的隔离评测批次：

```powershell
python -B tests/prepare_skill_behavior.py --case collaboration_workflow --case collaboration_blind_workflow --output .build/agent-collaboration/<新批次>
```

准备器直接复制 `source/project/` 候选资源与夹具，不调用安装器、模型或真实外部服务，不覆盖已有输出。每例 `project/` 是执行者工作区，`TASK.txt` 仅包含普通用户任务；同级 `candidate-manifest.json` 记录实际候选源字节哈希，`evaluation.json` 保留评估者判断点，两者均在执行者工作区外。不要把本目录 cases.json、evaluation.json、已知缺陷位置或整改路线传给盲评执行者；评估者另行核对其实际调用轨迹、角色身份及执行先后。目录隔离不是操作系统访问控制，真实评测还须约束执行者仅访问其工作区。

准备及保护单测入口是 `python -B -m unittest discover -s tests -p test_skill_behavior.py -v`。这些检查只能证明隔离准备、输入分流及来源字节，不能证明真实角色调用或将模型状态更新为 PASS。候选规则变化后重新生成新批次，保留旧目录，不静默替换正在评测的快照。角色会话仍须实际读取并执行该候选指令；复制 TOML 不代表运行平台已重新加载角色。

共同机制按场景检查：复杂 imp 的实际委派与同一 Plan 持续推进；Bug 经评估归因和 imp 修复后，doc 据满足原 Issue 判据的局部或集成证据更新原 Issue；review 以检查项承载审查、Task 交接及原审查者复核。核对阻塞隔离、缺失验证代码和证据补查分流、增量交接与有效证据复用。简单局部、只验收、只评估、只审不修和能力受限作为边界例，不要求每例全角色轮转。实际评测结果和候选快照引用归报告；夹具定义保持可重复使用，不能覆盖历史失败。

需求交付案例 `spec_delivery` 核对确认后的 Spec／AC 能否直接接续实施。`spec_only` 和 `spec_pending_criteria` 分别核对只写规格与需求尚待确认时的停止条件。

Bug 定向案例可用同一命令准备：`bug_direct_report` 验证直接报告的缺陷能以原场景及必要回归的局部证据关闭原 Issue；`bug_assess_only` 检查归因结果与授权边界；`bug_diagnosis_missing_evidence` 检查已授权修复但归因缺证时是否停在取证；`bug_attribution_counterevidence` 检查当前版本反驳旧归因时是否先回退再接续；`bug_retest_missing_evidence` 检查外部原场景无法复验时是否保留原 Issue 和恢复条件。集成发现和只验收分别由 `collaboration_workflow` 和 `collaboration_test_only` 覆盖。只验收例还检查缺少可执行指南时能否生成验收文档。核对实际操作、阶段交接、文件差异及报告中的版本和覆盖。夹具中的旧观察是任务输入，仅本轮实际运行可作为本轮证据。

`collaboration_review_check_items` 复用订单模板，只增加本轮架构检查范围输入。评估每个检查项的依据、初审、imp Task、状态与复核证据：符合项直接通过，多个检查项可共用整改 Task 并分别复核，复杂整改也可关联多个 Task；不另建独立 gap 台账。外部环境及依赖项受阻时，本地独立项仍继续。此例不重新验收取消需求、不重跑完整 imp／test 评测；修复者只实现明确目标，方案仍只在 imp Plan。使用同一准备命令，将 `--case` 改为 `collaboration_review_check_items` 并选择新批次；现行案例术语更新不改历史执行记录。

`collaboration_mixed_acceptance` 复用订单夹具。评测输入给出同一整改的公开调用性能判据及架构规则，核对实际测量条件、结果与版本，以及原审查者对状态写入路径的复核。两类结果分别取证，同一个 Task 可以引用两者。

`bug_local_retest_only` 在修复已提交的隔离仓库核对仅复验请求：检查原场景和必要回归、复验版本与原 Issue 关单依据。`bug_performance_acceptance` 核对 Bug 工单直接在原 Issue 编写验收方案时，是否保留已确认的计时条件、统计口径及阈值。两例先提交夹具基线，再将 `TASK.txt` 的内容交给执行者。

commit 平台场景的 `evidence/*.json` 描述评测所需的仓库／平台状态，不是实际远端回执。执行评测时将这些状态配置到隔离的 Git 仓库及连接工具／CLI／API 测试替身，由替身返回查询与写入结果并记录调用；不得访问真实平台写入。`commit_github_pr` 需先暂存无关文档再施加订单修复；`commit_merge_head_change` 依次模拟 head 变化、检查 pending／通过、排队与最终合并，核对每一步动作及返回状态。只将 input 和所需原始输入交给执行者，预期与禁止项留给评估者；未配置替身或未实际运行时保持 UNVERIFIED。

验证分三类：机械测试验证安装、打包及工具不变量；维护者语义核对检查指令与场景的职责对应；真实模型评测必须保存实际执行轨迹及结果。cases.json 中的 UNVERIFIED 是案例准备时的默认状态。已运行批次按实际轨迹在实施证据中记录通过项、失败和未验证项。机械测试通过不得视为行为评测通过。

远端同步场景使用状态中的 graph 准备对应提交关系；`commit_first_push_stale_main` 保留过期 tracking，只有实际 fetch 才刷新；`commit_remote_diverged_dirty` 准备双方分叉及无关暂存／未暂存修改；`commit_remote_refresh_race` 按查询阶段推进远端 SHA，并模拟非快进拒绝和获取失败；`commit_pinned_release_base` 以维护分支而非 main 作为已确认目标。判定读取了哪些实际引用、两组比较及同步是否在 push 前完成，不以输出了 fetch／pull 字样代替行为证明。

交付组合场景用隔离 Git 仓库和平台、部署测试替身记录变更顺序与版本。提交场景准备基线及题设差异；`deliver_merge_then_deploy` 按查询阶段返回排队和已合并状态，部署替身记录实际版本。仅配置本轮所需状态，真实平台与运行环境不参与这些案例。

统计命令：python -B scripts/skill_context_stats.py。输出字符量而非 token；描述已包含在入口字符量中，参考文件按整文件列出，实际读取范围由任务决定。
