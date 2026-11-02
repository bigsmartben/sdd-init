# 平台操作

先确认选定 remote 对应的 host、owner/namespace 和 repo/project，区分 fork 源仓库与 PR/MR 接收仓库；GitLab 子组路径不能按固定两段截断。自托管主机不由域名猜测，结合已认证工具或用户配置核实。缺少认证时提示所需连接，不读取或展示 token。

## GitHub

优先已有 GitHub 连接；不足时使用 `gh`，显式指定仓库与 base/head。`gh pr create` 在分支未发布时可能提示推送或 fork，必须先取得对应授权并明确 head，不能让创建 PR 隐式扩大授权。先查同一源/目标的现有 PR。

多行正文保存 UTF-8 文件，通过 `--body-file` 提交，保留真实换行。使用 API 时传结构化正文。创建成功后，若客户端提供 PR 附件工具，将真实 URL 附加到当前聊天。

`gh pr create --dry-run` 仍可能 push，不能把它当作未获授权时的只读预览；在本地准备标题和正文即可。

合并前读取最新 head、目标分支、检查、审批与保护要求；CLI 可用 `--match-head-commit` 绑定已批准 head。不要使用 `--admin` 绕过要求或自动附加 `--delete-branch`。merge queue / auto-merge 是等待中的动作，读平台状态确认最终结果。

官方命令：
- https://cli.github.com/manual/gh_pr_create
- https://cli.github.com/manual/gh_pr_merge

## GitLab

使用覆盖所需操作的已连接工具，或认证到正确 host 的 `glab`。明确项目、source branch、target branch 与 draft 状态；创建前按项目和源/目标查询现有 MR。`glab mr create` 的 `--push` / `--create-source-branch` 会引入额外变更；只有用户已明确授权这些动作才可使用，不能用 `--fill` 的便利行为绕过确认。

多行描述优先结构化 API 参数；CLI 先读取当前版本 `glab mr create --help`，选择其实际支持的文件/stdin/description 输入，不凭空使用 GitHub 的 `--body-file` 参数。

当前官方 CLI 支持 `--description-file` 和 merge 的 `--sha`；实际执行仍核对已安装版本。读取 MR 与项目的源分支清理设置；用户未授权清理时显式关闭删除源分支，避免平台默认设置在 merge 后代为删除。

合并前读取最新 head SHA、diff、pipeline、approvals、讨论和保护规则。使用当前 CLI 支持的 SHA 校验参数，或 GitLab merge API 的 `sha` 参数绑定已批准 head。先确认当前版本命令的自动合并/等待行为；不得用跳过检查或删除源分支的选项冒充普通 merge。回读 `merged` 状态及 merge commit；等待 pipeline/自动合并只能报告 pending。

官方命令与 API：
- https://docs.gitlab.com/cli/mr/create/
- https://docs.gitlab.com/cli/mr/merge/
- https://docs.gitlab.com/api/merge_requests/#merge-a-merge-request

## 重试与外部结果

网络中断或超时后先查远端分支、对应 PR/MR 和 head。已完成则记录成功；未完成且原授权仍适用才重试。认证/权限错误或同一失败在核实后仍重复时停止，交付明确阻塞，避免无界重试。除 user 明确要求外，不改仓库权限、保护规则或 CI 策略。
