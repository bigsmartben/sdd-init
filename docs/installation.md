# 安装与验证

## 初始化用户级 Skill

需要 Git、uv 与 Python 3.11 或更新版本。从本仓源码目录运行以下命令。使用已发布的 wheel 或固定 Git 提交时，将 `--from .` 换成对应发行源。

```powershell
uvx --from . sdd-init inspect
uvx --from . sdd-init install
```

默认安装到 `~/.agents/skills/sdd-init/`。`--home` 可指定隔离用户目录，`--skills-dir` 可指定 Skill 的父目录。已有同名资源内容不同时，安装在写入前报告冲突并保留现有文件。

## 接入目标仓库

在 Codex Desktop 或 GitHub Copilot App 打开目标 Git 仓库，开始新会话并调用 `sdd-init`。技能按[仓库接入工单](../source/initializer/references/repository-onboarding.md)盘点当前宿主、展示差异、执行接入并给出验收回执。

| 宿主 | 仓库规则 | 原生角色配置 |
| --- | --- | --- |
| Codex Desktop | 根目录 `AGENTS.md` | `.codex/agents/<角色>.toml`，按 `name` 发现 |
| GitHub Copilot App | 根目录 `AGENTS.md` | `.github/agents/<角色>.agent.md`，使用 YAML 前置属性与 Markdown 正文 |

六个逻辑角色共用同一份职责源码。构建器从 TOML 生成 Copilot 配置。Codex 子 Agent 继承父会话的实际权限。Copilot 的 architect 和 analyst 配置读取与搜索工具。实际可调用能力由对应宿主、会话权限和组织配置决定。[Codex 子 Agent](https://developers.openai.com/codex/subagents) · [Copilot App 自定义](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app) · [Copilot 角色格式](https://docs.github.com/en/copilot/reference/custom-agents-configuration) · [Copilot 项目角色路径](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents)

同一仓库补接另一端时，使用同一根规则和该端原生角色目录。首次创建使用 Main 模板。使用当前标记的 Main 管理块按预览原地更新，块外项目内容原样保留。未标记的已有规则需要更新时，先审阅差异，再选择合并或整文件替换。管理块格式异常或与项目条款存在冲突时，可提供包含当前管理块的完整合并候选供用户审阅。

## 命令与 CI

在目标仓库执行，`发行源` 指与初始化相同的包或固定源码版本。`--repo` 和 `--harness` 分别指定目标及宿主。以下以 Codex 为例。

```powershell
uvx --from '<发行源>' sdd-init project plan --repo . --harness codex
uvx --from '<发行源>' sdd-init project apply --repo . --harness codex --expect '<已审阅的 Plan 值>'
uvx --from '<发行源>' sdd-init project check --repo . --harness codex
```

用户选定 `--upgrade merge`、`--upgrade replace`、`--merged-file`、`--reuse-role` 或 `--ci-source` 时，应用使用生成预览的同一组参数。`apply` 重新计算预览指纹，已审阅的文件或候选变更后重新预览。中断时根据输出检查已写文件，再预览剩余改动。安装后的 Skill 也可用 `uv run --script "<Skill 目录>/scripts/repository.py"` 执行相同的 `plan`、`apply`、`check` 子命令。

`check` 在配置缺失、规则不符或角色解析失败时返回非零退出码。本地与 CI 使用同一个入口。若用户选择注册 GitHub Actions，在预览和应用中加 `--ci-source "<wheel HTTPS URL 或固定完整提交的 git+https URL>"`，将看到目标宿主对应的 `.github/workflows/sdd-init-<宿主>.yml`。同名工作流已有定制时，审阅差异后按用户决定合入项目现有 CI。其他 CI 平台使用上述 `check` 命令。

## 开发验证与桌面验收

在本仓源码目录运行。构建输出放在新建隔离目录。

```powershell
uv run --no-project --with 'PyYAML>=6.0.2,<7' python -B -m unittest discover -s tests -v
$distCandidate = Join-Path ([IO.Path]::GetTempPath()) ('sdd-init-dist-' + [guid]::NewGuid().ToString('N'))
uv build --out-dir $distCandidate
$wheelCandidate = Get-ChildItem -LiteralPath $distCandidate -Filter '*.whl' | Select-Object -First 1
python -B scripts/smoke_package.py --from $wheelCandidate.FullName
```

冒烟检查在临时用户目录与临时 Git 仓库验证 UVX 初始化、Skill 内置命令、两端配置及重复接入。两端桌面验收按工单的[宿主验收](../source/initializer/references/repository-onboarding.md#宿主验收)执行。在受控用户环境中记录实际客户端版本、根规则加载、六个角色发现与具名调用证据。配置校验和原生调用分别记录。[本轮验证证据](workflow-evidence.md#2026-11-24-仓库接入)
