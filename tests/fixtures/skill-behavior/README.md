# Skill 行为评测

cases.json 的 files 是最小输入夹具，input 是交给执行者的请求；expected 和 forbidden 只供评估者判定，不传给执行者。每例在独立临时目录中准备当前分发 Skill、Agent 与夹具。commit_scope 需先创建本地基线提交，再施加题设的两处修改；不配置远端。init 用构建后的安装器，只操作临时项目。

记录执行者读取、工具调用、文件差异与回复，按语义逐项核对预期及禁止行为。

commit 平台场景的 `evidence/*.json` 描述评测所需的仓库／平台状态，不是实际远端回执。执行评测时将这些状态配置到隔离的 Git 仓库及连接工具／CLI／API 测试替身，由替身返回查询与写入结果并记录调用；不得访问真实平台写入。`commit_github_pr` 需先暂存无关文档再施加订单修复；`commit_merge_head_change` 依次模拟 head 变化、检查 pending／通过、排队与最终合并，核对每一步动作及返回状态。只将 input 和所需原始输入交给执行者，预期与禁止项留给评估者；未配置替身或未实际运行时保持 UNVERIFIED。

验证分三类：机械测试验证安装、打包及工具不变量；维护者语义核对检查指令与场景的职责对应；真实模型评测必须保存实际执行轨迹及结果。当前 cases.json 的 UNVERIFIED 表示尚未执行真实模型评测。机械测试通过不得将其改为 PASS。

远端同步场景使用状态中的 graph 准备对应提交关系；`commit_first_push_stale_main` 保留过期 tracking，只有实际 fetch 才刷新；`commit_remote_diverged_dirty` 准备双方分叉及无关暂存／未暂存修改；`commit_remote_refresh_race` 按查询阶段推进远端 SHA，并模拟非快进拒绝和获取失败；`commit_pinned_release_base` 以维护分支而非 main 作为已确认目标。判定读取了哪些实际引用、两组比较及同步是否在 push 前完成，不以输出了 fetch／pull 字样代替行为证明。

统计命令：python -B scripts/skill_context_stats.py。输出字符量而非 token；描述已包含在入口字符量中，参考文件按整文件列出，实际读取范围由任务决定。
