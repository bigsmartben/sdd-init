# 安装和使用

本入口需要 uv、Git，以及 Python 3.11+（uv 可按配置自动下载 Python）。私有 GitHub 仓库还需要本机 Git 已具备读取权限；安装器不接收或保存访问令牌。

## 首次安装

默认安装命令（已合并至 main，并通过 GitHub HTTPS 安装验证）：

```powershell
uvx --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

默认安装到 `~/.agents/skills/sdd-init/`，Windows 中 `~` 为用户主目录。目录中包含 SKILL.md、脚本、说明、模板和 `assets/repo-payload.zip`；只有 sdd-init 注册为用户级 Skill。安装完成后不依赖 uv 缓存保存资源，运行项目初始化脚本仍需要 Python。

在需要的仓库中打开 Codex，选择 sdd-init（支持该快捷入口的客户端可输入 `/sdd-init`）。CLI／IDE 可输入 `$sdd-init` 或通过 `/skills` 选择；也可明确要求“使用 sdd-init 初始化当前仓库”。未发现新 Skill 时重启 Codex。安装器不修改客户端命令注册或用户配置。[Codex 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)

只有此时才将五个项目 Skills、五个角色和共享资源展开到目标仓库。初始化与项目升级继续使用现有 Skill 的冲突保护规则。

## 更新与冲突

```powershell
uvx --refresh --from git+https://github.com/bigsmartben/sdd-init.git sdd-init install
```

uv 默认可能复用缓存；`--refresh` 用于重新解析远端。需要固定版本时，将 Git URL 写成 `git+https://github.com/bigsmartben/sdd-init.git@<tag-or-commit>`。[uv 工具说明](https://docs.astral.sh/uv/guides/tools/)

更新只替换用户级 sdd-init 及其内置资源，既有项目保持原状；新项目使用新载荷，旧项目须明确要求升级。相同内容重复执行不产生变更。安装器核对完整文件清单与哈希；发现定制、缺失、额外文件或无清单的旧版时停止，不提供自动强制覆盖。应先备份并审阅旧目录，再人工迁出冲突目录后重装。旧用户级入口的迁移不自动执行。

安装先在同目录暂存并验证，再替换；替换失败会尝试恢复旧目录。并发安装以锁文件拒绝；进程异常中断后，应检查 `.sdd-init-install.lock` 和 `.sdd-init-backup-*`，确认没有安装进程、旧文件已保全，再人工恢复。哈希用于完整性和定制检查，不是签名验证。

## 开发验证

```powershell
uv build --out-dir .build/dist
python -B -m unittest discover -s tests -v
python -B scripts/smoke_package.py --from .build/dist/sdd_init-0.1.0-py3-none-any.whl
```

`src/sdd_init/cli.py` 定义命令入口，`installer.py` 负责用户级安装；`setup.py` 在构建时调用 `scripts/build_release.py`，从 `source/` 生成内置资源。源码包包含构建所需输入，wheel 不要求访问原仓库。不要编辑 wheel、build 或 `.build` 内的资源。测试通过 `--skills-dir` 隔离安装位置；自定义位置只有位于客户端搜索范围时才可被发现。
