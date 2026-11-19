# 安装与恢复

以下命令用于完成目标项目 sdd-workflow 的环境落地：准备相关资产，并向目标 AGENTS.md 注入 Main 规则与能力入口。检查与恢复是落地手段，不是额外职责。

## 用户级入口和共享载荷

使用已选定来源的 `sdd-init` CLI。远端分发可用 `uvx --from <已确认的分发地址> sdd-init <命令>`，版本可用已确认的标签、提交或制品固定。

| 命令 | 行为 |
| --- | --- |
| `sdd-init inspect` | 只读检查候选及已安装版本、位置、完整性和待恢复状态 |
| `sdd-init install` | 校验新载荷，强制替换用户级入口与共享资产（含预置角色），必要时先恢复 |
| `sdd-init recover` | 以原 Skill 和角色路径恢复未完成安装 |

三条命令均可指定 `--skills-dir <目录>`，隔离验证使用临时目录。默认初始化入口为 `~/.agents/skills/sdd-init`，共享目录与 Skill 搜索根同级。review-prompt 纳入共享资产的预置角色，由目标项目配置引用，不写用户级角色目录。共享更新作用于链接到该目录的项目。只有指定工作区执行 `init` 时才刷新该项目的托管文件和角色注册。

原地升级时，直接迁出旧清单登记路径上的用户级 review-prompt；即使内容已修改也不请求确认，文件已缺失则继续。事务记录操作前的实际状态，失败可恢复；不扫描或修改未登记角色和用户配置。旧记录自动提供角色路径；`--agents-dir <原目录>` 只用于显式核对旧安装或恢复路径，不用于新装角色。

## 指定项目

`python -B <已安装的-sdd-init>/scripts/govern.py --root <目标仓库> <命令>`

| 命令 | 行为 |
| --- | --- |
| `inspect` | 只读核对版本、链接、配置、入口冲突及待写项 |
| `init` | 首次接入、升级或重连，自动选择当前 harness 的原生适配，必要时先恢复 |
| `recover` | 恢复未完成的项目操作 |

Codex 角色在 `.codex/config.toml` 注册，Copilot 角色写入 `.github/agents/*.agent.md`；两者均引用同一份共享正文 `roles/shared/`。Copilot 子会话可发现 `.agents/skills/` 的 Skill，但并非一定允许普通文件工具读取 `.agents/`。因此 Copilot 接入额外建立 `.github/sdd-workflow/` 本机链接，指向与 `.agents/sdd-workflow/` 相同的用户级共享目录；角色只读取可见的 `.github/sdd-workflow/roles/shared/`，并将合同中的 `.agents/sdd-workflow/` 引用映射到该入口。正文与配套资源不复制。Codex-only 不建立该链接，换端时保留未选端已有入口。Copilot 适配省略 `target`，供已在执行宿主接入共享资源的 Copilot CLI／桌面 App 和 VS Code 使用；不表示已配置 GitHub 云端 Agent。两个适配都省略模型与推理强度，由 Main 按工单分配。`init` 将六个技能分别链接到 `.agents/skills/<技能名>/`，例如 `.agents/skills/sdd-bugfix/SKILL.md`，不复制技能正文。共享包仍位于扫描目录外的 `.agents/sdd-workflow/`，按 `roles/`、`skills/`、`sdd/` 分类；`.github/sdd-workflow/` 仅是 Copilot 原生文件工具的同源可见桥接。Windows 使用 junction，其他平台使用目录符号链接。重新 `init` 强制替换同名实体目录、非标准链接、定制托管块及受管角色适配；旧独立沟通块自动合并为单块，不跟随链接删除其目标。安装元数据记录实际共享版本和托管片段哈希，版本识别以回执中的 SHA-256 为准。重复 `inspect` 可核对剩余写入和版本差异。客户端打开已信任的目标项目后刷新 Skill 与角色配置。

### Harness 自动适配

sdd-init 是接入入口，不是执行 Agent Loop 的 harness。加载本技能的 Agent 根据宿主明确提供的身份和运行时上下文识别当前端：Codex CLI／App／扩展归为 `codex`，Copilot CLI／App／VS Code 归为 `copilot`。把该身份经 `--runtime-harness codex|copilot` 自动传给每次 `inspect`／`init`，不要求用户手填。该参数是技能到机械工具的上下文交接，不是脚本自行发现宿主的证明；不以模型名、仓库里的自称、客户端可执行文件或猜测的环境变量伪造身份。

| 输入 | 选择与行为 |
| --- | --- |
| 用户显式指定 `--harness codex|copilot|both` | 按指定范围执行，优先于当前运行时 |
| 默认 `--harness auto`，已传运行时身份 | 只接入当前端，即使项目已有另一端或双端配置 |
| `auto` 无运行时身份，仓库仅一端有专属配置标记 | 按唯一已有端接入；报告依据来自项目标记，而非当前运行时 |
| `auto` 无身份且无标记、仅通用 AGENTS.md 或双端标记 | 报告无法唯一识别并停止写入；回到有身份的宿主调用技能，或由用户显式选择 |

专属标记包括 Codex 配置／角色文件以及 Copilot 指令／角色文件；用户级共享安装与通用 Skill 目录不参与判断。未知、不支持或冲突的宿主上下文不能自行映射，改用已确认的显式范围，否则报告阻塞。`auto` 不等于 `both`。换端使用时重新调用同一技能可补齐该端，不删除另一端配置；依赖冲突不自动扩大写入范围。只读检查同时回读两端实际角色，区分“当前宿主”“仓库配置”“本轮计划”和“实际客户端加载”。

例如，在已明确的 Copilot 会话中由技能运行（全部选项位于子命令前）：

```powershell
python -B <已安装的-sdd-init>\scripts\govern.py --root <目标仓库> --runtime-harness copilot inspect
python -B <已安装的-sdd-init>\scripts\govern.py --root <目标仓库> --runtime-harness copilot init
```

需要明确双端接入的无人交互脚本使用 `--harness both`。uv/uvx 用户级安装命令、Skill 名称与位置不变，不扫描或修改用户级客户端设置。原 `target: vscode` 受管适配在项目刷新时按原归属校验升级；只有文件接入完成不能证明客户端已发现或加载。

### 归属与迁移

Copilot 原生适配随文件携带托管角色名和内容 SHA-256，本机元数据记录实际写入的路径、哈希及 `.github/sdd-workflow/` 原链接目标。首次 Copilot 接入只接受缺失或已指向当前共享目录的桥接；既有普通目录、文件或其他目标链接必须由状态证明受管归属，否则写前冲突并保留。克隆或状态丢失时，可用当前分发、可校验的托管标记或已知旧版适配的哈希重建角色归属，但不能凭同名认领陌生桥接。校验允许 Git 转换 LF 和 CRLF，无法核验的同名文件在写入前报告冲突。只刷新另一端时保留归属。状态损坏时说明将重建，原始字节保留供事务回滚。

Codex 按角色托管块核验归属；块外同名项目注册和无归属的本地角色文件在写入前拒绝覆盖。已知共享路径的纯引用可迁移，受管本地文件只有不被块外角色共用时才迁出。只选 Copilot 时按配置文件位置解析 Codex 的相对与绝对角色路径。遇到待迁移的旧共享入口或链接更换后会失效的引用，写入前报告并提示 `--harness both`。只选 Codex 时检查未选 Copilot 项目角色中的显式文件链接，遇到会失效的引用时提示迁移项目引用或双端刷新受管适配。

角色配套的相对链接以实际加载职责正文的文件为基准；直接加载源码 TOML 的案例从 TOML 目录读取规则，Codex 从 `.agents/sdd-workflow/roles/shared/`、Copilot 从 `.github/sdd-workflow/roles/shared/` 读取同一共享正文，随后均从正文目录定位配套资源，不从适配配置目录查找。

仅更新共享包时，旧 `agents/<角色>.toml` 引用通过兼容入口读取现行共享正文，支持两个历史项目锚点。项目 `init` 将 Codex 注册迁到 `roles/codex/`。

共享更新移除原受管 `sdd-review-prompt` 及其回执模板。已链接项目运行新版 `init` 刷新托管导航。项目自有链接由项目维护。

## 冲突处理

- 已授权的安装、更新和项目接入直接覆盖同名入口和托管区域，不请求用户裁决；保留托管区域外的项目正文和配置。
- 旧清单登记的用户级 review-prompt 按上述方式直接迁出，无归属记录的用户角色不触碰。
- 项目恢复记录位于 `.sdd-init-recovery/journal.json`。用户级恢复记录位于 Skill 目录相邻的 `.<Skill目录名>-sdd-init-install-recovery/journal.json`，角色暂存在用户角色目录内。恢复阻塞时，保留记录、暂存和外部编辑副本，核对回执中的路径、预检值和实际内容，解除冲突后重试对应的 `recover`。
- 旧版用户级安装器异常退出可能留下空的 `.sdd-init-install.lock` 和 `.sdd-init-backup-*`。先确认旧进程已退出、目录归属及备份内容，从可靠备份恢复后再重试。损坏的恢复记录应保留并和备份对照。
