# 安装与恢复

## 用户级入口和共享载荷

使用已选定来源的 `sdd-init` CLI。远端分发可用 `uvx --from <已确认的分发地址> sdd-init <命令>`，版本可用已确认的标签、提交或制品固定。

| 命令 | 行为 |
| --- | --- |
| `sdd-init inspect` | 只读检查候选及已安装版本、位置、完整性和待恢复状态 |
| `sdd-init install` | 校验并发布用户级入口、共享资源及通用角色 `review-prompt`，必要时先恢复 |
| `sdd-init recover` | 以原 Skill 和角色路径恢复未完成安装 |

三条命令均可指定 `--skills-dir <目录>` 和 `--agents-dir <目录>`，隔离验证须同时指定。默认初始化入口为 `~/.agents/skills/sdd-init`，共享目录与 Skill 搜索根同级。用户角色默认发布到 `$CODEX_HOME/agents/`，未设置时使用 `~/.codex/agents/`。Codex 新会话自动发现独立角色 TOML。共享更新作用于链接到该目录的项目。只有指定工作区执行 `init` 时才刷新该项目的托管文件和项目角色。

## 指定项目

`python -B <已安装的-sdd-init>/scripts/govern.py --root <目标仓库> <命令>`

| 命令 | 行为 |
| --- | --- |
| `inspect` | 只读核对版本、链接、配置、入口冲突及待写项 |
| `init` | 首次接入、升级或重连，必要时先恢复 |
| `recover` | 恢复未完成的项目操作 |

`init` 将六个技能分别链接到 `.agents/skills/<技能名>/`，例如 `.agents/skills/sdd-bugfix/SKILL.md`，不复制技能正文。共享包链接位于扫描目录外的 `.agents/sdd-workflow/`，角色使用相对路径引用。Windows 使用 junction，其他平台使用目录符号链接。重新 `init` 自动迁出指向同一共享目录的标准旧 `.agents/skills/sdd-workflow` 链接，同名实体目录或非标准链接保留并报冲突。安装元数据记录实际共享版本和托管片段哈希，版本识别以回执中的 SHA-256 为准。重复 `inspect` 可核对剩余写入和版本差异。客户端打开已信任的目标项目后刷新 Skill 与角色配置。

共享更新移除原受管 `sdd-review-prompt` 及其回执模板。已链接项目运行新版 `init` 刷新托管导航。项目自有链接由项目维护。

## 冲突处理

- 保留同名或遮蔽项。审阅后，按用户决定迁出冲突副本，或在托管块外保留定制内容，再刷新标准托管块。
- 用户级安装按角色路径和哈希保护已安装角色，遇到同名自有角色、缺失或修改冲突时报告实际路径。
- 项目恢复记录位于 `.sdd-init-recovery/journal.json`。用户级恢复记录位于 Skill 目录相邻的 `.<Skill目录名>-sdd-init-install-recovery/journal.json`，角色暂存在用户角色目录内。恢复阻塞时，保留记录、暂存和外部编辑副本，核对回执中的路径、预检值和实际内容，解除冲突后重试对应的 `recover`。
- 旧版用户级安装器异常退出可能留下空的 `.sdd-init-install.lock` 和 `.sdd-init-backup-*`。先确认旧进程已退出、目录归属及备份内容，从可靠备份恢复后再重试。损坏的恢复记录应保留并和备份对照。
