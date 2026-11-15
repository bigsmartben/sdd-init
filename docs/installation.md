# 安装和使用

本入口需要 uv、Git，以及 Python 3.11+（uv 可按配置自动下载 Python）。私有 GitHub 仓库还需要本机 Git 已具备读取权限；安装器不接收或保存访问令牌。

## 首次安装

从 GitHub 默认分支安装：

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

默认在 `~/.agents/skills/sdd-init/` 安装初始化入口，在相邻的 `~/.agents/skills-sdd-init-shared/` 安装项目工作流。通用 `review-prompt` 以独立 TOML 安装到 `$CODEX_HOME/agents/`，未设置 `CODEX_HOME` 时使用 `~/.codex/agents/`。Windows 的 `~` 为用户主目录。Codex 新会话可发现用户级角色，适用于未接入 SDD 的项目。[Codex 自定义角色](https://developers.openai.com/codex/subagents#custom-agents)

在需要的仓库中打开 Codex，选择 sdd-init（支持该快捷入口的客户端可输入 `/sdd-init`）。CLI／IDE 可输入 `$sdd-init` 或通过 `/skills` 选择，也可明确要求“使用 sdd-init 初始化当前仓库”。未发现新 Skill 时重启 Codex。专项审查可请求“把这份提示词交给 review-prompt，只做审查”，附实际对象和预期依据。角色依赖客户端的用户级发现能力。用户 `config.toml` 由用户维护。[Codex Skill 文档](https://learn.chatgpt.com/docs/build-skills)

初始化在项目内创建 `.agents/skills/sdd-workflow` 目录链接。Windows 使用 junction，其他平台使用目录符号链接。安装器合并 `AGENTS.md` 导航与 `.codex/config.toml` 中的角色引用，并在 `.gitignore` 排除本机链接和安装元数据。托管导航指向[主任务职责](../source/project/.agents/sdd/references/sdd-repository-governance.md#职责与交接)和[阶段授权与推进](../source/project/.agents/sdd/references/sdd-repository-governance.md#阶段授权与推进)。角色的项目配置在 Codex 信任该仓库后加载。换机、克隆或新建 worktree 后重新运行 sdd-init 以接上本机共享目录。

主任务启动技能 Agent，技能 Agent 可调用所需专业角色。项目限制 Codex 委派深度时，这条路径需要允许两级委派。安装器沿用项目已有设置。启动和能力不足时的处理见[技能 Agent 的启动与接续](../source/project/.agents/sdd/references/delegation.md#技能-agent-的启动与接续)。

## 只读检查

使用与预定安装相同的分发来源检查共享版本和影响范围。项目检查用实际安装的脚本，返回共享版本、项目登记版本、链接、角色注册、待写项及阻塞原因。

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init inspect
python -B "$env:USERPROFILE/.agents/skills/sdd-init/scripts/govern.py" --root . inspect
```

用户级 CLI 的 `inspect`、`install` 和 `recover` 均接受 `--skills-dir` 和 `--agents-dir`。隔离验证时同时指定两处临时目录，自定义安装的后续操作沿用原路径。项目检查可通过 `--root` 明确工作区。回执显示实际角色路径，两个 SHA-256 分别标识分发内容和项目共享内容。项目本机 `.sdd-init-state.json` 记录上次接入时的共享版本和已安装片段哈希。

## 更新与冲突

```powershell
uvx --refresh --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

uv 默认可能复用缓存；`--refresh` 用于重新解析远端。需要固定版本时，将 Git URL 写成 `git+https://github.com/bigsmartben/sdd-init.git@<tag-or-commit>`。[uv 工具说明](https://docs.astral.sh/uv/guides/tools/)

更新替换用户级入口和同一位置的共享资源。所有已有链接指向同一位置的项目都会使用新版。更新前核对影响范围；指定项目的托管导航和角色引用在该工作区运行 `init` 时刷新。相同内容重复执行保持文件内容稳定。安装器核对清单及哈希；已安装目录中由清单内 Python 源文件生成的字节码可保留。发现定制、缺失、额外文件或无清单时，保留原目录并报告冲突。完整且符合旧清单的安装可直接升级。

用户角色以已安装清单的路径和哈希判定归属。存在同名自有角色，或受管角色缺失、被修改时，保留现有文件和配置，处理冲突后重试。项目 `init` 只维护项目受管角色。角色目录须支持同文件系统硬链接，安装器用它发布完整文件并在冲突时保护既有目标。

目标项目自行处理遗留文件。清理后，在目标仓库调用一次 `sdd-init` 即可接入共享模式。脚本统一使用 `init`，同步 `AGENTS.md` 和 `.codex/config.toml` 中的 SDD 托管块，保留项目正文、主模型、MCP 和其他配置。安装器报告与当前工作流的同名冲突。项目自有文档及其中的链接由项目维护。

共享包更新将原受管 `sdd-spec` 替换为 `sdd-develop`，并移除旧受管技能 `sdd-doc`、`sdd-imp`、`sdd-commit` 和 `sdd-deploy`。已接入项目随后运行一次 `sdd-init` 并重新加载项目。初始化器用[现行五个角色](../source/project/.agents/sdd/references/delegation.md)刷新托管引用和导航，迁出标准旧托管角色 `sdd-delivery`、`sdd-designer`、`sdd-documenter` 和 `sdd-validator`。旧托管引用已定制，或项目自有角色与新版同名时，保留原配置并报告冲突。

同一共享包更新也将原受管 `sdd-review-code` 替换为 [sdd-refactor](../source/project/.agents/skills/sdd-refactor/SKILL.md)。原共享链接直接指向更新后的资源，项目 `init` 刷新托管导航。若项目仍有独立的 `.agents/skills/sdd-review-code/SKILL.md`，`init` 会保留该文件并报告冲突。先将旧副本迁出 Skill 发现范围，再运行 `init`。历史记录及托管块外的项目文档仍由项目维护。

共享包升级会移除原受管 `sdd-review-prompt` 和它的回执模板。已链接项目在运行新版 `init` 后移除托管导航中的旧入口，随后重新加载项目。升级共享包到刷新项目之间，旧导航链接会暂时失效。独立旧副本按上述冲突策略处理，托管块外的链接由项目自行核对。

项目托管块按其内容及来源识别。标准片段和已知旧引用自动刷新。定制导航、定制角色引用、同名资源或来源不明时，保留路径及原内容，由用户选择保留、迁移或替换。托管块外可保存项目自有规则。重新执行 `inspect` 核对此前冲突和变更计划。

## 项目安装恢复与旧命令退役

项目 `init` 在目标根目录的 `.sdd-init.lock` 上获取操作系统文件锁，同项目并发安装直接拒绝。该一字节文件持久保留，不能用文件存在判断进程活跃，也不要在安装期间删除或替换它；进程退出由操作系统释放锁。inspect 不创建锁。锁与恢复记录是本地运行元数据，不应提交到版本库。

写入前的资源冲突只产生锁元数据。安装先持久化 `.sdd-init-recovery/journal.json`，保存受影响文件的原始字节、目标字节、权限、新增目录及新链接的目标。备份字节以 Base64 编码保存。逐文件替换使用同一恢复目录的暂存文件，成功后标记 committed 并清理恢复目录。进程中断后可按恢复记录续接。

普通写入失败自动恢复本次文件和链接；异常终止后，重新执行相同 init 命令会先处理恢复记录，再做新安装。恢复期间已恢复的文件可以重复检查；恢复成功只清理本次新建且仍为空的目录。安装及恢复都会比对文件内容，发现外部修改时保留文件并阻止覆盖。

只恢复时运行 `govern.py --root <项目> recover`。若提示 `Recovery blocked`，保留错误中列出的文件和 `.sdd-init-recovery/`，根据 `journal.json` 的 path／before／after 核对受影响内容，保存外部编辑副本并解除文件占用、权限或内容冲突，再重试。记录损坏时保留恢复记录，并从可靠备份核对恢复。

已接入的项目通过用户级更新取得新版工具。现行入口和历史记录的处理方式见[旧治理命令退役边界](blueprint.md#旧治理命令退役边界)。

## 用户级安装恢复

用户级安装分别锁定 Skill 和角色目录，锁文件为持久元数据。恢复日志在 Skill 目录相邻的 `.<Skill目录名>-sdd-init-install-recovery/`，角色暂存和备份在用户角色目录的 `.sdd-init-review-prompt-recovery-*`。两处数据属于同一事务。异常中断后使用原 Skill 和角色目录运行 `sdd-init recover`，或重跑安装。出现外部修改、损坏记录或 I/O 失败时保留记录、暂存和备份，按回执核对后重试。已有旧版未完成事务使用其原目录恢复。

旧版可能留下空的 `.sdd-init-install.lock` 和父目录中的 `.sdd-init-backup-*`。确认旧进程退出并核对备份归属和内容，按旧版本的实际记录人工恢复，再使用现行安装器。

## 开发验证

在本仓库根目录构建并运行回归检查。安装冒烟测试将当前 wheel 安装到临时 Skill 和角色目录，并在独立的临时项目中验证接入。

```powershell
uv build --out-dir .build/dist
python -B -m unittest discover -s tests -v
python -B scripts/smoke_package.py --from .build/dist/sdd_init-0.7.0-py3-none-any.whl
```

`src/sdd_init/cli.py` 定义命令入口，`installer.py` 负责用户级安装。构建器汇集 `source/` 的分发资源，并将 `src/sdd_init/release.py` 投影为初始化器使用的清单校验模块。源码包包含构建所需输入，wheel 可独立安装。客户端发现验证使用隔离的用户配置路径和搜索根，角色目录采用该临时 Codex 配置下的 `agents`。

本仓采用源码维护模式。五份角色定义统一维护在 [项目分发源码](../source/project/.codex/agents/)，角色注册与接入在隔离项目验证。独立角色的实际运行案例见[行为夹具](../tests/fixtures/skill-behavior/README.md)。
