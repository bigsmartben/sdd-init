# 安装和使用

本入口需要 uv、Git，以及 Python 3.11+（uv 可按配置自动下载 Python）。私有 GitHub 仓库还需要本机 Git 已具备读取权限；安装器不接收或保存访问令牌。

## 首次安装

从 GitHub 默认分支安装：

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

默认在 `~/.agents/skills/sdd-init/` 安装初始化入口，在相邻的 `~/.agents/skills-sdd-init-shared/` 安装工作流 Skill、角色和通用资源。Windows 的 `~` 为用户主目录。只有 sdd-init 进入用户级 Skill 扫描范围。

在需要的仓库中打开 Codex，选择 sdd-init（支持该快捷入口的客户端可输入 `/sdd-init`）。CLI／IDE 可输入 `$sdd-init` 或通过 `/skills` 选择；也可明确要求“使用 sdd-init 初始化当前仓库”。未发现新 Skill 时重启 Codex。安装器不修改客户端命令注册或用户配置。[Codex 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)

初始化在项目内创建 `.agents/skills/sdd-workflow` 目录链接。Windows 使用 junction，其他平台使用目录符号链接。安装器合并 `AGENTS.md` 导航与 `.codex/config.toml` 中的角色引用，并在 `.gitignore` 排除本机链接和安装元数据。角色的项目配置在 Codex 信任该仓库后加载。需要文档归并时，可直接要求 Codex 委派 `sdd-documenter`。换机、克隆或新建 worktree 后重新运行 sdd-init 以接上本机共享目录。

## 更新与冲突

```powershell
uvx --refresh --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

uv 默认可能复用缓存；`--refresh` 用于重新解析远端。需要固定版本时，将 Git URL 写成 `git+https://github.com/bigsmartben/sdd-init.git@<tag-or-commit>`。[uv 工具说明](https://docs.astral.sh/uv/guides/tools/)

更新替换用户级入口和同一位置的共享资源。已链接项目重新加载后使用新版。相同内容重复执行不产生变更。安装器核对文件清单与哈希，校验已安装目录时跳过清单内 Python 源文件对应的未登记 `__pycache__` 字节码。发现定制、缺失、其他额外文件或无清单的旧版时停止，不提供自动强制覆盖。应先备份并审阅旧目录，再人工迁出冲突目录后重装。完整且与旧清单相符的用户级入口可直接更新。

目标项目自行处理遗留文件。清理后，在目标仓库调用一次 `sdd-init` 即可接入共享模式。脚本统一使用 `init`，同步 `AGENTS.md` 和 `.codex/config.toml` 中的 SDD 托管块，保留项目正文、主模型、MCP 和其他配置。安装器报告与当前工作流的同名冲突。项目自有文档及其中的链接由项目维护。

共享包更新将原受管 `sdd-spec` 替换为 `sdd-develop`。旧受管 `sdd-imp` 的实施规则归入[共享实施规则](../source/project/.agents/sdd/references/implementation.md)。共享包同时移除旧受管技能 `sdd-doc`、`sdd-commit` 和 `sdd-deploy`。文档归并使用 [sdd-documenter](../source/project/.codex/agents/sdd-documenter.toml)，交付使用 [sdd-deliver](../source/project/.agents/skills/sdd-deliver/SKILL.md)。在已接入的项目中运行一次 `sdd-init` 刷新托管导航，再重新加载项目。

安装先暂存并验证入口及共享目录，再分别发布。替换失败时恢复旧目录。进程异常中断后，检查 Skill 搜索目录中的 `.sdd-init-install.lock` 及其父目录中的 `.sdd-init-backup-*`，确认安装进程已退出、旧文件已保全，再人工恢复。哈希用于完整性和定制检查。

## 项目安装恢复与旧命令退役

项目 `init` 在目标根目录的 `.sdd-init.lock` 上获取操作系统文件锁，同项目并发安装直接拒绝。该一字节文件持久保留，不能用文件存在判断进程活跃，也不要在安装期间删除或替换它；进程退出由操作系统释放锁。inspect 不创建锁。锁与恢复记录是本地运行元数据，不应提交到版本库。

写入前的资源冲突只产生锁元数据。安装先持久化 `.sdd-init-recovery/journal.json`，保存受影响文件的原始字节、目标字节、权限、新增目录及新链接的目标。备份字节以 Base64 编码保存。逐文件替换使用同一恢复目录的暂存文件，成功后标记 committed 并清理恢复目录。进程中断后可按恢复记录续接。

普通写入失败自动恢复本次文件和链接；异常终止后，重新执行相同 init 命令会先处理恢复记录，再做新安装。恢复期间已恢复的文件可以重复检查；恢复成功只清理本次新建且仍为空的目录。安装及恢复都会比对文件内容，发现外部修改时保留文件并阻止覆盖。

若提示 `Recovery blocked`，先保留错误中列出的文件和 `.sdd-init-recovery/`，根据 `journal.json` 的 path／before／after 核对受影响内容，保存外部编辑副本并解除文件占用、权限或内容冲突，再重试同一命令。记录损坏时保留恢复记录，并从可靠备份核对恢复。

旧 start、record、attest、check、finish、commit 已移除，无兼容入口或自动迁移。初始化器保留 inspect／init，项目共享 govern.py 仅保留 inspect；文档检查使用 doc_check.py，Git 交付使用 sdd-deliver。已接入的项目通过用户级更新取得新版工具，历史 Spec、Status 和证据由项目维护。

## 开发验证

在本仓库根目录构建并运行回归检查。安装冒烟测试将当前构建的 wheel 安装到临时 Skill 目录，并在独立的临时项目中验证接入。

```powershell
uv build --out-dir .build/dist
python -B -m unittest discover -s tests -v
python -B scripts/smoke_package.py --from .build/dist/sdd_init-0.6.0-py3-none-any.whl
```

`src/sdd_init/cli.py` 定义命令入口，`installer.py` 负责用户级安装；`setup.py` 在构建时调用 `scripts/build_release.py`，从 `source/` 生成内置资源。源码包包含构建所需输入，wheel 不要求访问原仓库。不要编辑 wheel、build 或 `.build` 内的资源。测试通过 `--skills-dir` 隔离安装位置；自定义 Skill 目录只有位于客户端搜索范围时才可被发现，共享目录与该目录同级。
