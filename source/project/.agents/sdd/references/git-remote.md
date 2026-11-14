# 仓库平台适配与远端操作

## 选择平台与执行通道

从用户给定的对象链接、选定 remote 的 fetch／push 地址、分支 tracking、项目配置及平台元数据确定主机、平台、完整仓库路径、默认分支与写入权限。支持 HTTPS、SSH 及 SSH 别名；GitLab 保留完整 group/subgroup/project 路径，不按路径段数或自定义域名猜平台。fork 场景分别定位可推送的源仓库与接收 PR／MR 的目标仓库，不把 origin 或 main 当固定答案；多个候选无法消歧时只问该选择。

优先使用项目既有且可访问目标实例的工具；不足时使用本机 `git` 配合成熟的平台 CLI、连接工具或对应平台 API。显式指定主机／组织／仓库及对象编号，避免工具按默认登录写错实例。先检查可用通道与已有认证，只有用户必须完成登录、授权或开放权限时才交回该最小动作。

使用已有凭据通道，不读取或展示令牌，不将凭据写入文档、正文或命令记录。执行前按本机版本的 `--help` 或目标实例文档核对参数及 API 能力；下表是操作映射，不要求一次执行全部动作。

| 目的 | GitHub | GitLab | 关键输入／回读 |
|---|---|---|---|
| 仓库定位 | `gh repo view` 或仓库 API | `glab repo view` 或项目 API | 主机、完整路径／项目 ID、默认分支及权限 |
| Issue 查重／读写 | `gh issue list/view/create/edit` 或 Issues API | `glab issue list/view/create/update` 或 Issues API | 仓库内编号、URL、摘要、状态与本任务关联 |
| 请求查重／读写 | `gh pr list/view/create/edit` 或 Pull requests API | `glab mr list/view/create/update` 或 Merge requests API | 源仓库／分支、目标仓库／分支、草稿状态、head SHA、URL |
| 检查与审批 | PR checks、reviews、保护规则 | MR pipeline、approvals、合并规则 | 检查对应的提交、必需项及阻塞，不拿其他分支的绿色状态代替 |
| 合并及回读 | `gh pr merge/view` 或合并 API | `glab mr merge/view` 或合并 API | 预期 head、允许策略、实际合并状态、合并／squash 提交及目标分支 |

云效 Codeup 使用目标实例的仓库及合并请求接口，核对组织、仓库 ID 或完整路径、MR 编号、源／目标、校验与合并限制。议题按项目已接入的系统操作。验证实例实际支持的合并条件与权限，沿用[合并检查](#合并检查)。参考 [Codeup 仓库查询](https://www.alibabacloud.com/help/en/yunxiao/developer-reference/getrepository-query-the-code-base)、[MR 查询](https://www.alibabacloud.com/help/en/yunxiao/developer-reference/getchangerequest-query-merge-request)、[自动化检查](https://www.alibabacloud.com/help/en/yunxiao/user-guide/automated-checks-settings)及[合并接口](https://www.alibabacloud.com/help/en/yunxiao/developer-reference/mergechangerequest-merge-merge-request)。

## 仓库集成与流水线

1. 从项目配置和实例定位仓库、所接工具、流水线及其触发条件。读取当前绑定、触发事件或检查门禁，确认变更影响的仓库、分支、环境和权限。配置集成时查重并复用现有连接，仅按本轮授权更新绑定、事件或检查；受保护设置沿用项目权限规则。
2. 触发已有流水线前核对源仓库、目标分支／标签及对应 SHA、流水线参数及连带效果。会触发部署或生产操作时，先按[执行前确认与部署评估](delivery.md#执行前确认与部署评估)落实适用的前置条件。先查对应版本是否已有自动触发或手动运行，按授权复用或触发单次运行。指定 SHA 无法直接传入时，核对所选引用及实际运行解析出的源提交，错配的运行不可作为本轮证据。
3. 查运行编号、源 SHA、阶段状态、必需检查、审批及实际制品。已有运行和触发后结果不明的情况先回读，确认还需执行才按授权重试。仅触发任务返回已核实的运行，要求跟进检查时继续到所需结果或明确阻塞。回执提供实际关联、链接、版本和状态。
4. 维护 CI/CD 或排障时，从失败步骤、日志、触发配置与依赖定位原因。在授权的 CI/CD 配置、环境或运维脚本范围内修复并复跑受影响检查，记录实际运行提交、状态和制品。回执附产品实现或全产品验收缺口及证据。

云效 Codeup 仓库按实例实际配置使用开放集成或关联 Flow。已有流水线的手动触发与运行状态使用目标实例提供的 Flow 通道，MR 门禁读取该请求关联的自动化检查。参考 [Codeup 开放集成](https://www.alibabacloud.com/help/en/yunxiao/user-guide/open-integration/)、[关联 Flow 流水线](https://www.alibabacloud.com/help/en/yunxiao/user-guide/how-to-associate-flow-pipeline)、[Flow 触发](https://www.alibabacloud.com/help/en/yunxiao/developer-reference/createpipelinerun)、[Flow 运行查询](https://www.alibabacloud.com/help/en/yunxiao/developer-reference/getpipelinerun)及 [MR 检查查询](https://www.alibabacloud.com/help/en/yunxiao/developer-reference/listchangerequestcichicklist-query-merge-request-ci-automated-check-list)。

## 远端同步检查

新建用于远端交付的任务分支前及每次 push 前执行本节；本地提交、明确指定当前提交起点的本地建分支、纯 Issue 操作不因此扩大为远端交付。先明确推送目的地和集成目标（如 upstream/main 或 develop），已有 PR／MR 以实际目标为准；普通任务按项目约定或仓库默认分支确定目标，不能把任务分支的 tracking 当成 main 的最新状态。明确固定版本、发布维护基线等例外沿用已确认约定并报告与主线的差异，不擅自迁到 main。

1. 记录当前 HEAD、分支、工作区／暂存区归属及远端地址，向实际源仓库和目标仓库 fetch 所需引用。fetch／push URL 不同时也要核实实际推送目的地的引用；显式覆盖目标分支和已存在的远端任务分支，不能假定默认 refspec 会取回全部所需分支。查询远端是否存在同名分支；不存在视为首次推送，不用旧 tracking 代替实际结果。fetch 失败、目标已删除或不可访问时暂停该次远端交付。
2. 用更新后的引用分别比较两组提交关系：任务 HEAD 与远端同名分支、任务 HEAD 与最新目标分支。可用 `git rev-list --left-right --count HEAD...<已获取引用>` 区分领先／落后，结合 `git merge-base --is-ancestor <已获取引用> HEAD` 判断是否已包含该基线；两组结果分别记录 SHA。没有 upstream、没有远端同名分支、工作区干净或本地 main 未变化都不证明目标基线最新。浅克隆或历史不完整时补取所需历史；无法判断则保留阻塞，不把“无共同祖先”直接判为无需同步。
3. 按下表处理。同步前保留无关未提交及预暂存内容，禁止用自动 stash、reset 或整仓 commit 清场。可安全隔离时在授权内自主处理。普通交付授权包含必要的 fetch、快进及不改写历史的同步 merge。无法安全隔离、需新增历史改写授权或出现跨职责冲突时，只暂停受影响操作，在回执中记录具体缺口、冲突位置和恢复条件，解决后再 push。

| 比较对象及结果 | 行为 |
|---|---|
| 新任务分支，无远端同名分支 | 从已获取的最新目标基线准备分支；已存在本地任务提交时先整合目标，不能仅因首次 push 会成功而跳过 |
| 远端同名分支是本地祖先 | 允许普通快进 push，仍须完成目标分支比较 |
| 本地落后远端同名分支，且可快进 | 快进到远端最新提交；不得以本地旧提交覆盖远端 |
| 本地与远端同名分支已分叉 | 先检查双方差异归属，再按项目策略整合，默认保留提交历史；出现无关改动或范围不明先解决归属 |
| 最新目标分支不是任务 HEAD 的祖先 | 除已确认固定基线例外外，将目标更新快进或 merge 到任务分支，按影响补做检查；只 pull 任务分支不能代替此步骤 |
| 两组均已包含所需提交 | 继续核对本次提交范围并推送；仍遵守目标分支保护 |

4. 整合后检查冲突标记、差异归属及合并结果，按受影响范围执行必要局部验证；同步改变 HEAD 后，旧 SHA 的检查不直接作为新 SHA 的检查结果。push 前再次核对实际远端任务引用和目标引用是否仍是本轮已检查的 SHA；变化则重新 fetch、比较及整合。使用明确源／目标 ref 的普通 push，非快进拒绝后返回同步步骤，不改用强推。持续并发变化或状态不可核实时报告阻塞，避免无限重试。
5. push 后回读远端任务 SHA 和目标引用，确认本次提交已到达；目标又前进时记录该差异并按本节继续同步或报告待同步，不能称已基于最新 main。后续合并仍执行[合并检查](#合并检查)的最新状态核对，push 前检查不消除并发更新窗口。

同步完成的判据是明确远端提交已按项目策略纳入本次基线，并非机械执行一次 `git pull`。需要 pull 时显式指定 remote、分支和整合策略；可使用 fetch 后明确 fast-forward／merge，避免受本机默认 pull／rebase 配置影响。Git 行为依据：[fetch](https://git-scm.com/docs/git-fetch)、[pull](https://git-scm.com/docs/git-pull)、[提交关系判定](https://git-scm.com/docs/git-merge-base)、[push](https://git-scm.com/docs/git-push)。

## 分支、Issue 与请求

### 分支准备

分支按任务终点准备，并执行[远端同步检查](#远端同步检查)：复用合适的任务分支，否则按项目约定从正确起点新建，操作前检查是否会覆盖或混入工作区／暂存区差异。只推送本次范围的分支及提交，不默认直推受保护目标分支；不修改已有 remote 指向，也不自动 fork。

### 平台议题与请求

创建前按本任务引用及仓库内对象查询：Issue 核对内容关联，不能只凭同名合并无关议题；PR／MR 核对源仓库、源分支及目标仓库、目标分支。发现匹配对象则在授权范围内复用或更新，保留他人维护的内容；已关闭或已合并对象先判断任务是否已完成，不自动重开或重复创建。

沿用项目已有 Issue／PR／MR 模板，填写任务摘要、Spec／报告引用、实际变更、验证与未完成项。跨本地与平台的引用应能被仓库读者定位，不把本机绝对路径当远端链接。平台编号和独立 Issue 编号分别关联；普通关联使用引用，关闭已获授权且已有符合原 Issue 关闭条件的验证证据时，才设置 `Closes`／`Fixes` 等自动关闭关系。

多行正文用结构化参数，或写入 UTF-8 文件并传路径。CLI 提供文件参数时使用它，例如 `--body-file` 或帮助中列出的 `--description-file`。Windows `.cmd`／`.bat` 入口不得内联多行正文；没有文件参数时换可保留换行的接口。保留实际换行，避免 shell 插值。明确源／目标和标题正文，避免交互向导让用户代操作。使用目标平台可解析的正文链接，GitLab 的文件引用保留 `/-/blob/`。

### 请求准备

预先完成并核验授权 push，再创建请求，防止 CLI 隐式推送或 fork。请求是否草稿按任务和项目约定确定，不用草稿掩盖已知未完成项。参数依据：[GitHub PR 创建](https://cli.github.com/manual/gh_pr_create)、[GitLab MR 创建](https://docs.gitlab.com/cli/mr/create/)。实例版本能力以实际查询为准。

## 合并与恢复

### 合并检查

合并前重新查询请求状态、源 head、目标最新提交、差异及适用检查／审批／保护规则，确认仍属本次范围。head 或目标变化时核对差异与已有检查的适用性，必要时等待检查刷新或交回修复。授权、检查及适用的[执行前确认与部署评估](delivery.md#执行前确认与部署评估)仍覆盖当前操作时直接继续。冲突修复沿用上述交接，更新请求后重新核对受影响检查。

按已确认约定或仓库允许的默认策略合并；有实质策略歧义才询问。将预期 head 传入平台支持的合并条件，防止回读后被并发替换：GitHub CLI 使用 `--match-head-commit`，GitLab CLI 使用 `--sha`，API 使用对应 SHA 条件。当前工具无法约束 head 时换用可用 API；无法满足必要约束则报告阻塞。普通合并不改写源分支历史，不使用 admin／skip 等绕过检查的选项，不修改保护规则，也不附带删除源分支；核对平台自动删除设置是否与授权冲突。

检查失败、缺少审批或保护阻塞时返回具体阻塞及链接，不自行批准代替所需审查。队列／自动合并返回的是等待状态，回读到平台已合并及目标提交后才报告完成；squash／rebase 合并结果不能只用“源 SHA 是目标祖先”判断，应结合平台合并记录及实际目标提交核验。已授权合并且仍在执行中时继续跟进，需外部审批或超出当前可等待范围时返回等待项和恢复入口，不擅自注册定时任务。

参数依据：[GitHub 合并](https://cli.github.com/manual/gh_pr_merge)、[GitLab 合并](https://docs.gitlab.com/cli/mr/merge/)。实例版本能力以实际查询为准。

### 失败恢复

网络中断、超时或非零退出后，先查询分支引用、Issue、PR／MR 及合并状态；已完成则记录回执，仅确定未完成且原授权仍适用才重试。无法查明时报告结果待核实；认证、权限或重复失败时停止盲目重试。只建 Issue 或 PR／MR 时到该终点结束。
