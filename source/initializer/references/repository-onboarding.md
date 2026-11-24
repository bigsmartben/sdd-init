# 仓库接入工单

目标是在〈目标仓库根目录〉完成〈当前 harness 及版本〉接入，使仓库规则生效、自定义 Agent 可由当前宿主识别和调用。记录本次模式〈首次接入／已有接入更新／另一宿主补接〉。

1. **识别与盘点。** 定位仓库根目录、当前 harness、已有 AGENTS.md、Main 模板版本、现有角色配置、另一宿主已有适配和 CI 入口。记录判断依据。无法确定目标时先向用户澄清。
2. **向用户介绍工单。** 用目标仓库术语说明当前 harness、接入目标、执行顺序、预计读写的文件、各角色接入位置、用户决定点和验证方式。
3. **更新 Main 入口和规则。** 根目录 AGENTS.md 指向主会话读取的 `.agents/sdd-init/main.md`。按预览创建入口和规则文件，或更新当前管理内容，保留块外项目指令。未标记的现有入口需要更新时，展示合并和整文件替换的差异，按用户选择写入。冲突条款由用户决定，整文件替换列明覆盖的项目专属内容。文件变更后重新核对。
4. **适配当前宿主。** 按该宿主实际支持的原生入口适配 architect、analyst、implementer、tester、devops、uat-observer。逐项记录逻辑角色名、宿主入口、配置来源与发现或加载方式。优先复用已有有效配置。有用户定制冲突时展示差异并保留待决项。补接另一端时复用仓库规则，保留既有适配。
5. **执行可复跑检查。** 提供可在本地和 CI 运行的同一检查入口，记录命令与退出结果。检查 AGENTS.md 入口、主会话规则文件、合并或替换结果、角色格式、角色名与路由以及必要引用。用隔离副本核对重复接入。注册目标仓库 CI 前展示改动并取得用户选择。
6. **当前 harness 验收。** 按该端实际加载机制读取仓库规则、核对角色发现结果，并以最小只读任务验证角色调用。按角色记录可追溯的识别和调用证据。如需新会话或用户现场操作，说明步骤并记录待验证项。配置检查结果与宿主实测结果分别记录。
7. **回执。** 报告仓库、宿主、模板版本、规则写入方式及确认记录、变更文件、每个角色的配置／发现／调用状态、检查命令与结果、CI 接入选择、冲突和恢复条件。依据实测逐项标为通过、失败或待验证。完整接入以规则及角色在该端通过约定验收为准。

## 执行命令

以下命令中的 `<执行入口>` 用 `uv run --script "<Skill 目录>/scripts/repository.py"` 替换。分发包也提供等效的 `uvx --from "<同一发行源>" sdd-init project`。

- 先运行 `<执行入口> plan --repo "<仓库根目录>" --harness <codex|copilot>`。预览打印模板 SHA-256、变更和待决项。等待选择时保留现场。
- 用户选择合并或替换后，以 `--upgrade merge` 或 `--upgrade replace` 重新预览。合并模式保留块外原有内容。遇到重复或冲突的既有规则，先准备包含当前模板管理块的完整候选文件，通过 `--upgrade merge --merged-file "<候选文件>"` 预览并让用户核对差异。现有角色配置经核对有效且获准保留后，按角色加 `--reuse-role <角色名>`。
- 用户选定 GitHub Actions 时，传 `--ci-source "<对应版本的 wheel HTTPS URL 或固定完整提交 SHA 的 git+https URL>"` 预览专用工作流。其余 CI 平台按项目实际入口接入同一检查命令，用户选定并审阅修改后执行。现有工作流冲突时按同样方式确认合并。
- 使用同一组选项运行 `apply`，加 `--expect <已审阅预览中的 Plan 值>`。如果文件变更、写入中断或计划已过期，检查已落盘文件和剩余差异，生成新的预览后继续。核对 Git diff 或读回新增文件，确认合并保留或替换结果与审阅内容相符。
- 运行 `check --repo "<仓库根目录>" --harness <codex|copilot>`。如果本轮选择了 GitHub Actions，再带原 `--ci-source` 核对生成的入口。目标项目启用 `/speckit.*` 时，另核对适用命令契约和 `.specify/memory/constitution.md`。

## 宿主验收

| 宿主 | 仓库角色入口 | 验收操作 |
| --- | --- | --- |
| Codex Desktop | `.codex/agents/<角色>.toml`，按 TOML 的 `name` 选择 | 开启受信的新会话，由 Main 读取规则并关闭历史继承后逐个具名派发。记录实际多 Agent 后端和工具。V1 核对有效 `agents.max_depth = 1` 时子角色的委派工具，V2 按实际工具和调用结果验收。 |
| GitHub Copilot App | `.github/agents/<角色>.agent.md`，按文件对应的角色标识选择 | 在本地新会话由 Main 逐个具名派发，核对角色加载、仓库指令继承与有效工具清单。 |

用临时仓库和最小只读工单检查 Main 的具名调用。核对子角色实际输入是否含完整路由、角色目录或父会话的测试标记。检查有效工具中是否仍有代理调用、角色发现或同级通信入口。这类工具仍暴露时记录名字和有效权限，具备受控探针时核对实际响应。分别记录角色通过读文件访问共享规则和配置的情况。回执附宿主版本、配置来源和原生调用证据。缺少上下文、工具记录或具名入口时，记录暴露面及复验条件。

参考 [Codex 仓库指令](https://developers.openai.com/codex/guides/agents-md)、[Codex 子 Agent](https://developers.openai.com/codex/subagents)、[GitHub Copilot App 自定义](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app)和[GitHub Copilot Agent 配置](https://docs.github.com/en/copilot/reference/custom-agents-configuration)。
