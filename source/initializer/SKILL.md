---
name: sdd-init
description: 用户要求安装或升级项目 SDD 工作流时使用；安装四个项目 Skill、七个独立角色、共享模板和导航，保留既有正文及用户运行配置。
---

# SDD 初始化与升级

明确自然语言安装或升级意图即可使用，无需精确口令。仅安装资源与导航，不启动设计、实施、部署验收或 Git 交付。

1. 核对目标仓库、现有 AGENTS、Issue／架构／PR 入口及实际安装范围。仅维护本 Skill 时不初始化当前仓库。
2. 使用构建产物中的脚本，路径以实际安装位置为准：

   `python <sdd-init>/scripts/govern.py --root <repo> inspect`

   `python <sdd-init>/scripts/govern.py --root <repo> init`

   明确升级时使用 `init --update-skills`，沿用已有授权，不重复索取口令。
3. 安装载荷中的 sdd-doc、sdd-imp、sdd-accept、sdd-commit、七个项目角色及共享资源，只合并 AGENTS 托管片段，保留其他内容。角色定义在项目 .codex/agents/；职责与模型建议见[执行协作](references/delegation.md)。不创建独立 Spec、Status 或架构正文，不固定模型和推理强度，不改 .codex/config.toml 或用户级配置。
4. 修改过的同名资源、遮蔽入口或退役 Skill 会在写入前报告。旧 sdd-test-loop／sdd-review-loop 不随升级静默删除；有这些入口的存量项目需先按单独明确范围处理，再安装新入口，避免两套流程并存。
5. 核对安装内容、导航、重复执行与保护行为；报告新增、更新、保留和阻塞。安装不代表方案确认、实现完成或人工验收通过，不升级其他项目。

共享约定见 [governance](references/governance.md)，模板在 assets；项目载荷为 `assets/repo-payload.zip`，不展开到用户级 Skills 或 Agent 目录。[托管片段](assets/agents-fragment.md)提供项目导航。已有文档只在明确的文档任务中按实际来源归并，不用模板覆盖。

业务确有模型提示词需求时可参考 [prompting](assets/prompting.md)，沿用项目已有规范；仅开发工具使用 AI 不构成创建业务规范的理由。观测样例按实际项目需要使用，不由初始化确认架构选型。

旧状态命令与模板仅保留给既有 Spec/Status 记录，不作为新工作流门禁，不自动迁移或回填历史事实。
