# 安装和使用

本入口需要 uv、Git，以及 Python 3.11+（uv 可按配置自动下载 Python）。私有 GitHub 仓库还需要本机 Git 已具备读取权限；安装器不接收或保存访问令牌。

[sdd-init Skill](../source/initializer/SKILL.md)只负责目标项目 sdd-workflow 的环境落地：一是准备所需资产及其链接与角色配置，二是向目标 AGENTS.md 注入 Main 规则与能力入口。首次接入、更新、重连、检查和恢复都是实现这一职责的操作，不承担接入后的项目任务调度与业务交付。

## 首次安装

从 GitHub 默认分支安装：

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

默认在 `~/.agents/skills/sdd-init/` 安装初始化入口，在相邻的 `~/.agents/skills-sdd-init-shared/` 安装项目工作流资产。`review-prompt` 与其余预置专业角色统一位于共享资产中，由目标项目接入时注册，不再独立安装到用户级角色目录。Windows 的 `~` 为用户主目录。[Codex 自定义角色](https://developers.openai.com/codex/subagents#custom-agents)

在需要的仓库中打开 Codex，选择 sdd-init（支持该快捷入口的客户端可输入 `/sdd-init`）。CLI／IDE 可输入 `$sdd-init` 或通过 `/skills` 选择，也可明确要求“使用 sdd-init 初始化当前仓库”。未发现新 Skill 时重启 Codex。接入后可请求“把这份提示词交给 review-prompt，只做审查”，附实际对象和预期依据。角色依赖客户端加载可信项目的角色配置；未接入项目不默认提供该角色。用户 `config.toml` 由用户维护。[Codex Skill 文档](https://learn.chatgpt.com/docs/build-skills)

初始化将六个技能分别链接到项目的 `.agents/skills/<技能名>/`，例如 `.agents/skills/sdd-bugfix/SKILL.md`；不复制技能正文。共享包链接位于扫描目录外的 `.agents/sdd-workflow/`，供共享规则、模板和角色引用。Windows 使用 junction，其他平台使用目录符号链接。安装器合并 `AGENTS.md` 导航与 `.codex/config.toml` 中的角色引用，并在 `.gitignore` 排除本机链接和安装元数据。托管导航指向[主任务职责](../source/project/.agents/sdd/references/sdd-repository-governance.md#职责与交接)和[阶段授权与推进](../source/project/.agents/sdd/references/sdd-repository-governance.md#阶段授权与推进)。角色的项目配置在 Codex 信任该仓库后加载。换机、克隆或新建 worktree 后重新运行 sdd-init 以接上本机共享目录。

sdd-init 统一组装和写入单个 Main 托管指令块，源为 [agents-fragment.md](../source/initializer/assets/agents-fragment.md)。Align 意图对齐、探索调度、授权边界、任务交接及目标验收统一归 Main 规则，由核心指令和按需引用的详细条款承载，不另写独立沟通块。专业执行规则由对应执行者遵循，不因引用而交给 Main 代做。Harness 加载项目指令，Main 按目标直接执行、加载 Skill 或委派专业能力，不要求固定两级委派。安装器保留项目自有正文和配置；专业能力的启动和限制见[执行协作](../source/project/.agents/sdd/references/delegation.md#技能-agent-的启动与接续)。

## 只读检查

使用与预定安装相同的分发来源检查共享版本和影响范围。项目检查用实际安装的脚本，返回共享版本、项目登记版本、链接、角色注册、待写项及阻塞原因。

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init inspect
python -B "$env:USERPROFILE/.agents/skills/sdd-init/scripts/govern.py" --root . inspect
```

用户级 CLI 的 `inspect`、`install` 和 `recover` 均接受 `--skills-dir`。隔离验证指定临时目录，自定义安装的后续操作沿用原路径。旧版用户角色的实际路径从原清单或恢复记录读取；`--agents-dir` 仅用于核对该历史路径，不是新装目标。项目检查可通过 `--root` 明确工作区。两个 SHA-256 分别标识分发内容和项目共享内容。项目本机 `.sdd-init-state.json` 记录上次接入时的共享版本和已安装片段哈希。

## 更新与冲突

```powershell
uvx --refresh --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

uv 默认可能复用缓存；`--refresh` 用于重新解析远端。需要固定版本时，将 Git URL 写成 `git+https://github.com/bigsmartben/sdd-init.git@<tag-or-commit>`。[uv 工具说明](https://docs.astral.sh/uv/guides/tools/)

更新替换用户级入口和同一位置的共享资源。所有已有链接指向同一位置的项目都会使用新版。更新前核对影响范围；指定项目的托管导航和角色引用在该工作区运行 `init` 时刷新。相同内容重复执行保持文件内容稳定。安装器核对清单及哈希；已安装目录中由清单内 Python 源文件生成的字节码可保留。发现定制、缺失、额外文件或无清单时，保留原目录并报告冲突。完整且符合旧清单的安装可直接升级。

`review-prompt` 原地升级为工作流预置角色：更新共享资产后，在指定项目运行 `init`，原五角色注册块会加入该角色。用户级安装直接迁出旧清单登记路径上的原角色，即使文件已修改也不请求确认，文件缺失则继续；不扫描或删除未登记的同名角色，不修改用户配置。事务记录迁出前的实际状态，失败或中断时恢复，事务开始后的外部编辑仍受保护。项目已有同名自有角色或定制注册时，`init` 保留并报告冲突。升级后不再承诺未接入项目的全局可用性。

重新 `init` 会将指向同一共享目录的标准旧 `.agents/skills/sdd-workflow` 链接迁为上述布局，并刷新托管导航、角色引用与忽略项。失败或中断可恢复文件和链接；不递归删除共享内容。同名实体目录、指向其他位置的链接和定制内容保留并报告冲突。其他遗留文件由目标项目自行处理。清理后，在目标仓库调用一次 `sdd-init` 即可接入共享模式。脚本统一使用 `init`，同步 `AGENTS.md` 和 `.codex/config.toml` 中的 SDD 托管块，保留项目正文、主模型、MCP 和其他配置。安装器报告与当前工作流的同名冲突。项目自有文档及其中的链接由项目维护。

共享包更新将原受管 `sdd-spec` 替换为 `sdd-develop`，并移除旧受管技能 `sdd-doc`、`sdd-imp`、`sdd-commit` 和 `sdd-deploy`。已接入项目随后运行一次 `sdd-init` 并重新加载项目。初始化器用[现行六个角色](../source/project/.agents/sdd/references/delegation.md)刷新托管引用和导航，迁出标准旧托管角色 `sdd-delivery`、`sdd-designer`、`sdd-documenter` 和 `sdd-validator`。旧托管引用已定制，或项目自有角色与新版同名时，保留原配置并报告冲突。

同一共享包更新也将原受管 `sdd-review-code` 替换为 [sdd-refactor](../source/project/.agents/skills/sdd-refactor/SKILL.md)。原共享链接直接指向更新后的资源，项目 `init` 刷新托管导航。若项目仍有独立的 `.agents/skills/sdd-review-code/SKILL.md`，`init` 会保留该文件并报告冲突。先将旧副本迁出 Skill 发现范围，再运行 `init`。历史记录及托管块外的项目文档仍由项目维护。

共享包升级会移除原受管 `sdd-review-prompt` 和它的回执模板。已链接项目在运行新版 `init` 后移除托管导航中的旧入口，随后重新加载项目。升级共享包到刷新项目之间，旧导航链接会暂时失效。独立旧副本按上述冲突策略处理，托管块外的链接由项目自行核对。

项目 Main 托管块只接受当前片段或本机有效单块状态所登记的内容，不使用历史片段白名单。旧版独立沟通块、双块状态、定制内容或来源不明时报告冲突，不自动迁移或覆盖；由用户在保护自有内容后处理。托管块外可保存项目自有规则。角色引用及目录链接按各自的安装规则核验。重新执行 `inspect` 核对冲突和变更计划。

## 项目安装恢复与旧命令退役

项目 `init` 在目标根目录的 `.sdd-init.lock` 上获取操作系统文件锁，同项目并发安装直接拒绝。该一字节文件持久保留，不能用文件存在判断进程活跃，也不要在安装期间删除或替换它；进程退出由操作系统释放锁。inspect 不创建锁。锁与恢复记录是本地运行元数据，不应提交到版本库。

写入前的资源冲突只产生锁元数据。安装先持久化 `.sdd-init-recovery/journal.json`，保存受影响文件的原始字节、目标字节、权限、新增目录及各链接的原始状态、目标和操作进度。备份字节以 Base64 编码保存。逐文件替换使用同一恢复目录的暂存文件，成功后标记 committed 并清理恢复目录。进程中断后可按恢复记录续接。

普通写入失败自动恢复本次文件和链接；异常终止后，重新执行相同 init 命令会先处理恢复记录，再做新安装。恢复期间已恢复的文件可以重复检查；恢复成功只清理本次新建且仍为空的目录。安装及恢复都会比对文件内容，发现外部修改时保留文件并阻止覆盖。

只恢复时运行 `govern.py --root <项目> recover`。若提示 `Recovery blocked`，保留错误中列出的文件和 `.sdd-init-recovery/`，根据 `journal.json` 的 path／before／after 核对受影响内容，保存外部编辑副本并解除文件占用、权限或内容冲突，再重试。记录损坏时保留恢复记录，并从可靠备份核对恢复。

已接入的项目通过用户级更新取得新版工具。现行入口和历史记录的处理方式见[旧治理命令退役边界](blueprint.md#旧治理命令退役边界)。

## 用户级安装恢复

用户级安装锁定 Skill 安装目标，锁文件为持久元数据。恢复日志在 Skill 目录相邻的 `.<Skill目录名>-sdd-init-install-recovery/`。新装不创建用户角色目录或角色锁；只有处理旧版用户角色事务或迁出原受管角色时，才按记录锁定其原目录，使用 `.sdd-init-review-prompt-recovery-*` 保存该事务的暂存或备份。异常中断后沿用原 Skill 目录运行 `sdd-init recover`，或重跑安装，旧角色路径自动从记录读取。出现外部修改、损坏记录或 I/O 失败时保留记录、暂存和备份，按回执核对后重试。

旧版可能留下空的 `.sdd-init-install.lock` 和父目录中的 `.sdd-init-backup-*`。确认旧进程退出并核对备份归属和内容，按旧版本的实际记录人工恢复，再使用现行安装器。

## 开发验证

在本仓库根目录构建并运行回归检查。每次使用新的输出目录，避免混入旧 wheel。安装冒烟测试将当前 wheel 安装到临时 Skill 和角色目录，并在独立的临时项目中验证接入。

```powershell
python -B -m unittest discover -s tests -v
$dist = ".build\candidate\dist"
if (Test-Path $dist) { throw "Choose a new output directory: $dist" }
uv build --out-dir $dist
if ($LASTEXITCODE -ne 0) { throw "Package build failed" }
$wheels = @(Get-ChildItem -Path $dist -Filter *.whl -File)
if ($wheels.Count -ne 1) { throw "Expected exactly one wheel in $dist; found $($wheels.Count)" }
python -B scripts\smoke_package.py --from $wheels[0].FullName
```

`src/sdd_init/cli.py` 定义命令入口，`installer.py` 负责用户级安装。构建器汇集 `source/` 的分发资源，并将 `src/sdd_init/release.py` 投影为初始化器使用的清单校验模块。源码包包含构建所需输入，wheel 可独立安装。客户端发现验证使用隔离的用户配置路径、搜索根和目标项目；旧用户角色迁出测试另使用隔离的历史角色目录。

本仓采用源码维护模式。六份角色定义统一维护在 [项目分发源码](../source/project/.codex/agents/)，角色注册与接入在隔离项目验证。独立角色的行为案例及实测边界见[行为夹具](../tests/fixtures/skill-behavior/README.md)。
