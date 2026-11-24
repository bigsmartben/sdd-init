---
name: sdd-init
description: 为 Codex Desktop 或 GitHub Copilot App 的当前 Git 仓库首次接入、更新或补接 Agent 协作环境。按仓库接入工单处理根 AGENTS.md、六个原生角色及本地和 CI 验收。
---

# sdd-init

在当前宿主中执行[仓库接入工单](references/repository-onboarding.md)。按预览原地更新当前 Main 管理块。用户决定未标记规则的合并或替换方式及目标仓库的 CI 接入。使用内置脚本预览、写入和检查，运行期路由交 Main，业务工作交对应角色。

从此 Skill 所在目录定位 `scripts/repository.py`，不要从目标仓库推断 Skill 路径。命令形如 `uv run --script "<Skill 目录>/scripts/repository.py" plan --repo "<仓库根目录>" --harness codex`。GitHub Copilot App 使用 `--harness copilot`。用当前会话和客户端提供的证据识别宿主，机器上有某个可执行文件或仓库已有某种配置只能用于盘点。宿主或目标无法确定时，向用户确认。
