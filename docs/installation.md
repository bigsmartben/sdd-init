# 安装和使用

本入口需要 uv、Git，以及 Python 3.11+（uv 可按配置自动下载 Python）。私有 GitHub 仓库还需要本机 Git 已具备读取权限；安装器不接收或保存访问令牌。

[sdd-init Skill](../source/initializer/SKILL.md)只负责目标项目 sdd-workflow 的环境落地：一是准备所需资产及其链接与角色配置，二是向目标 AGENTS.md 注入 Main 规则与能力入口。首次接入、更新、重连、检查和恢复都是实现这一职责的操作，不承担接入后的项目任务调度与业务交付。

## 首次安装

从 GitHub 默认分支安装：

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

默认在 `~/.agents/skills/sdd-init/` 安装初始化入口，在相邻的 `~/.agents/skills-sdd-init-shared/` 安装项目工作流资产。`review-prompt` 与其余预置专业角色统一位于共享资产中，由目标项目接入时注册，不再独立安装到用户级角色目录。Windows 的 `~` 为用户主目录。[Codex 自定义角色](https://developers.openai.com/codex/subagents#custom-agents)

在需要的仓库中打开 Codex、Copilot CLI／桌面 App 或 VS Code Copilot，调用同一个 sdd-init（使用客户端提供的技能选择入口，或明确要求“使用 sdd-init 初始化当前仓库”）。uv/uvx 分发、用户级技能名称和位置不变。未发现新 Skill 时刷新或重启客户端。技能根据宿主明确提供的上下文自动识别 harness，并传递给项目工具，无需用户重复选择。接入后可请求“把这份提示词交给 review-prompt，只做审查”，附实际对象和预期依据。Codex 与 Copilot 的角色适配分别位于 `.codex/config.toml` 和 `.github/agents/*.agent.md`，共同角色正文只维护在共享目录 `roles/shared/`。Copilot 接入建立忽略的 `.github/sdd-workflow/` 本机链接，让普通文件工具访问与 `.agents/sdd-workflow/` 相同的共享正文和配套资源；不复制内容。Copilot 适配省略 `target`，不再限定为 VS Code；要求当前执行宿主已接入共享资源，不承诺仅凭提交这些文件就能在 GitHub 云端使用。两个适配都省略模型与推理强度，由 Main 按工单分配。具体规则见[角色的模型与推理强度](../source/project/.agents/sdd/references/delegation.md#角色的模型与推理强度)。用户级客户端配置由用户维护。[Codex Skill 文档](https://learn.chatgpt.com/docs/build-skills) · [Copilot CLI Skill 路径](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) · [Copilot 角色配置](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

初始化将六个技能分别链接到项目的 `.agents/skills/<技能名>/`，例如 `.agents/skills/sdd-bugfix/SKILL.md`；不复制技能正文。共享包链接位于扫描目录外的 `.agents/sdd-workflow/`，按 `roles/`、`skills/`、`sdd/` 分类；Copilot 接入再建立指向同一目录的 `.github/sdd-workflow/` 桥接，避免普通工具读取 `.agents/` 的宿主权限差异。默认 `--harness auto` 优先采用技能自动传入的 `--runtime-harness codex|copilot`，只配置当前端；无运行时输入时，仅唯一一端的仓库配置标记可确定接入范围。无标记、仅通用 `AGENTS.md` 或双端标记时停止写入，不再默认配置两端。显式 `--harness codex|copilot|both` 优先；需要双端的脚本须明确 `both`，也可先后在两个 harness 中调用同一技能。识别契约和命令见[Harness 自动适配](../source/initializer/assets/install.md#harness-自动适配)。

`inspect` 只读报告运行时输入、项目中的 `.codex/config.toml`、`.codex/agents/*.toml`、`.github/copilot-instructions.md` 和 `.github/agents/*.md` 标记、选择依据、计划以及双端各自已落盘的 SDD 角色；项目标记不证明当前运行时，文件落盘也不证明客户端已加载。Windows 使用 junction，其他平台使用目录符号链接。安装器合并 `AGENTS.md` 导航和所选端原生角色适配，并在 `.gitignore` 排除本机链接和安装元数据；未选端配置保留。托管导航指向[主任务职责](../source/project/.agents/sdd/references/sdd-repository-governance.md#职责与交接)和[阶段授权与推进](../source/project/.agents/sdd/references/sdd-repository-governance.md#阶段授权与推进)。换机、克隆或新建 worktree 后，在实际执行宿主重新运行 sdd-init 以接上其共享目录。

Copilot 原生适配随文件携带托管角色名和内容 SHA-256，本机安装元数据记录实际写入的路径、哈希以及 `.github/sdd-workflow/` 原链接目标。克隆或换机后，本机记录可以从当前分发、可校验的托管标记或已知旧版适配的哈希恢复，包括旧 `target: vscode` 受管适配。校验允许 Git 转换 LF 和 CRLF。项目自有或内容已修改的适配仍按原归属规则处理；桥接的普通目录、文件或其他目标链接不得仅凭同名覆盖，须由状态证明，无法确认归属时 `inspect` 和 `init` 会在写入前报告冲突。仅刷新 Codex 时保留 Copilot 归属记录。

Codex 的 `# sdd-init roles:start`／`end` 块标记受管角色注册；块外的同名项目角色注册在写入前报告冲突，不按名字认领。只有恰好指向已知 SDD 共享角色路径且没有额外配置的注册可直接迁移。待迁出的本地角色文件必须由托管块明确引用，且不能被块外角色共用；其他同名或声明同名的本地文件保留并报告冲突，不删除其指令或链接目标。

角色配套链接以实际加载职责正文的文件为基准。直接使用源码 TOML 的隔离案例从该 TOML 目录读取配套规则；安装后 `review-prompt` 正文与配套目录同属 `roles/shared/`，Codex 和 Copilot 适配先读取该正文，再从正文目录解析链接，不从适配配置目录查找规则。

单端接入预检保护未选端的文件引用。只接入 Copilot 时，按 `.codex/config.toml` 的位置解析相对和绝对 `config_file` 路径。若依赖旧锚点、待迁移的 `agents/` 兼容入口或更换链接后不可达的角色文件，`inspect`／`init` 会在写入前停止并提示 `--harness both`。只接入 Codex 时，检查 Copilot 项目角色中的 Markdown 文件链接和适配入口引用，若迁移会切断依赖，先调整项目引用或双端刷新受管适配。

sdd-init 统一组装和写入单个 Main 托管指令块，源为 [agents-fragment.md](../source/initializer/assets/agents-fragment.md)。Align 意图对齐、探索调度、授权边界、任务交接及目标验收统一归 Main 规则，由核心指令和按需引用的详细条款承载，不另写独立沟通块。专业执行规则由对应执行者遵循，不因引用而交给 Main 代做。Harness 加载项目指令，Main 按目标直接执行、加载 Skill 或委派专业能力，不要求固定两级委派。安装器保留项目自有正文和配置；专业能力的启动和限制见[执行协作](../source/project/.agents/sdd/references/delegation.md#技能-agent-的启动与接续)。

## 只读检查

使用与预定安装相同的分发来源检查共享版本和影响范围。项目检查用实际安装的脚本，返回共享版本、项目登记版本、链接、每端实际落盘的 SDD 角色、Codex 悬空注册、待写项及阻塞原因。角色回读覆盖两端，客户端的实际发现和信任状态在客户端查验。

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init inspect
python -B "$env:USERPROFILE\.agents\skills\sdd-init\scripts\govern.py" --root . --runtime-harness copilot inspect
```

项目检查示例以 Copilot 为当前宿主；技能在 Codex 中自动传 `codex`。普通终端可省略该输入让工具按唯一仓库标记选择，或显式传 `--harness`，不把示例值当作探测结果。用户级 CLI 的 `inspect`、`install` 和 `recover` 均接受 `--skills-dir`。隔离验证指定临时目录，自定义安装的后续操作沿用原路径。旧版用户角色的实际路径从原清单或恢复记录读取；`--agents-dir` 仅用于核对该历史路径，不是新装目标。项目检查可通过 `--root` 明确工作区。两个 SHA-256 分别标识分发内容和项目共享内容。项目本机 `.sdd-init-state.json` 记录上次接入时的共享版本、已安装片段哈希及 Copilot 适配托管路径。

## 更新与冲突

```powershell
uvx --refresh --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

uv 默认可能复用缓存；`--refresh` 用于重新解析远端。需要固定版本时，将 Git URL 写成 `git+https://github.com/bigsmartben/sdd-init.git@<tag-or-commit>`。[uv 工具说明](https://docs.astral.sh/uv/guides/tools/)

更新强制替换用户级入口和同一位置的共享资源，即使旧内容已定制、缺失、包含额外文件或缺少清单，也不请求用户裁决。所有已有链接指向同一位置的项目都会使用新版；指定项目的托管导航和角色引用在该工作区运行 `init` 时刷新。相同内容重复执行保持文件内容稳定；新载荷仍须通过完整性校验。旧清单缺失时无法确定原用户角色路径，未登记的用户角色不受影响。

共享包保留现行角色在旧 `agents/<角色>.toml` 路径的兼容入口，两个历史项目锚点均可加载同一份新版职责正文。仅更新共享包后，旧项目的 Codex 角色引用可继续使用。运行项目 `init` 时注册迁到 `roles/codex/`。

`review-prompt` 原地升级为工作流预置角色：更新共享资产后，在指定项目运行 `init`，原五角色注册块会加入该角色。用户级安装直接迁出旧清单登记路径上的原角色，即使文件已修改也不请求确认，文件缺失则继续；不扫描或删除未登记的同名角色，不修改用户配置。事务记录迁出前的实际状态，失败或中断时恢复，事务开始后的外部编辑仍受保护。项目角色按前述托管归属核对，受管注册可刷新，非受管冲突在写入前拒绝。升级后不再承诺未接入项目的全局可用性。

重新 `init` 会将旧 `.agents/skills/sdd-workflow` 入口迁为上述布局，并强制替换同名实体目录、非标准链接及托管配置；删除链接时不跟随或删除链接目标。失败或中断可恢复文件和链接。脚本同步 `AGENTS.md` 和 `.codex/config.toml` 中的 SDD 托管块，保留范围外的项目正文、主模型、MCP 和其他配置。项目自有文档及其中的链接由项目维护。

共享包更新将原受管 `sdd-spec` 替换为 `sdd-develop`，并移除旧受管技能 `sdd-doc`、`sdd-imp`、`sdd-commit` 和 `sdd-deploy`。已接入项目随后运行一次 `sdd-init` 并重新加载项目。初始化器用[现行六个角色](../source/project/.agents/sdd/references/delegation.md)刷新托管引用和导航，迁出旧托管角色 `sdd-delivery`、`sdd-designer`、`sdd-documenter` 和 `sdd-validator`。角色替换限于可核验的受管注册和文件，不能仅凭同名删除项目角色。

同一共享包更新也将原受管 `sdd-review-code` 替换为 [sdd-refactor](../source/project/.agents/skills/sdd-refactor/SKILL.md)。项目 `init` 刷新托管导航并移除同名旧入口；历史记录及托管块外的项目文档仍由项目维护。

共享包升级会移除原受管 `sdd-review-prompt` 和它的回执模板。已链接项目运行新版 `init` 后移除旧入口，随后重新加载项目。升级共享包到刷新项目之间，旧导航链接会暂时失效；托管块外的链接由项目自行核对。

项目 Main 托管块、旧独立沟通块和双块状态强制迁为新版单块，保留托管块外正文及原换行和 BOM。角色引用和目录入口按同一覆盖原则更新。`inspect` 只读展示变更计划；格式损坏、权限不足或无法安全恢复时报告错误。

## 项目安装恢复与旧命令退役

项目 `init` 在目标根目录的 `.sdd-init.lock` 上获取操作系统文件锁，同项目并发安装直接拒绝。该一字节文件持久保留，不能用文件存在判断进程活跃，也不要在安装期间删除或替换它；进程退出由操作系统释放锁。inspect 不创建锁。锁与恢复记录是本地运行元数据，不应提交到版本库。

新载荷损坏或无法确定托管块边界等写前错误不会覆盖目标。安装先持久化 `.sdd-init-recovery/journal.json`，保存受影响文件的原始字节、目标字节、权限、新增目录及各入口的原始状态、目标和操作进度。文件备份以 Base64 编码保存，待替换目录和链接暂存于恢复目录；逐文件替换使用同目录暂存文件，成功后标记 committed 并清理恢复目录。进程中断后可按恢复记录续接。

项目状态文件不参与项目正文的 UTF-8 合并。状态内容或编码损坏时，`inspect` 只读说明将重建，`init` 在其余前置条件满足后生成新状态；原始状态字节仍进入事务备份，失败时原样恢复。损坏记录不能作为适配归属证明，适配文件须通过上述独立归属核验后才能更新。

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

本仓采用源码维护模式。六份角色定义以 [Codex 角色源码](../source/project/.codex/agents/) 为构建输入，构建器生成共享正文与 Codex／Copilot 适配；项目角色注册与接入在隔离项目验证。独立角色的行为案例及实测边界见[行为夹具](../tests/fixtures/skill-behavior/README.md)。

当前自动适配的隔离回归、分发冒烟及原生客户端未实测边界见[本轮实施证据](workflow-evidence.md#2026-11-19-harness-自动适配)。安装器能正确接收运行时身份不等于已实测技能在每个客户端中的自动识别与加载。
