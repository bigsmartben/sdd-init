---
name: sdd-init
description: 用户要求安装或升级项目 SDD 工作流时使用；安装六个项目 Skill、五个独立角色、共享模板和导航，保留既有正文及用户运行配置。
---

# SDD 初始化与升级

明确自然语言安装或升级意图即可使用，无需精确口令。仅安装资源与导航，不启动设计、实施、部署验收或 Git 交付。

1. 核对目标仓库、现有 AGENTS、Spec／架构／计划入口及实际安装范围。仅维护本 Skill 时不初始化当前仓库。
2. 使用构建产物中的脚本，路径以实际安装位置为准：

   `python <sdd-init>/scripts/govern.py --root <repo> inspect`

   `python <sdd-init>/scripts/govern.py --root <repo> init`

   明确升级时使用 `init --update-skills`，沿用已有授权，不重复索取口令。
3. 安装载荷中的 sdd-doc、sdd-imp、sdd-test-loop、sdd-review-loop、sdd-commit、sdd-deploy、五个项目角色及共享资源，将独立沟通原则托管块置于 AGENTS 首部，流程导航单独合并，保留管理块外的正文及原有换行。角色定义在项目 .codex/agents/；需要了解角色分工时读取[执行协作](references/delegation.md)。不创建独立 Spec、Status 或架构正文，角色包含默认模型，不设置推理强度，不改 .codex/config.toml 或用户级配置。
4. 修改过的同名资源、遮蔽入口或退役 Skill 会在写入前报告。冲突入口按明确范围处理后再安装，避免多套流程并存。
5. 同一项目安装互斥；普通写入失败恢复本次文件，异常终止后的下次 init 先恢复未完成操作。恢复记录位于目标仓库 `.sdd-init-recovery/`；遇到外部修改或恢复失败时保留记录并报告路径，解除冲突后重新执行同一安装命令，不删除记录后强制覆盖。核对安装内容、导航、重复执行与保护行为；报告新增、更新、保留和阻塞。

初始化器只提供 inspect／init。旧 start、record、attest、check、finish、commit 命令已退役，不保留兼容入口；历史文档不迁移，项目工作由现行 Skills 承担，文档机械检查使用 doc_check.py。

默认目录和工程资产规则随包安装至项目 `.agents/sdd/references/sdd-repository-governance.md`，`docs/index.md` 与该项目规则只在缺失时初始化。已有项目查其路径映射，按需归并后续规则。安装和升级分发项目规则模板。需要解释生成或更新条件时查[目标仓库的 Code Review Rules](references/sdd-repository-governance.md#目标仓库的-code-review-rules)。

需要解释项目流程时查[流程与产物索引](references/sdd-repository-governance.md#skill-场景与对象分工)，模板在 assets。项目载荷为 `assets/repo-payload.zip`，不展开到用户级 Skills 或 Agent 目录。核对安装入口时读取[独立沟通原则片段](assets/communication-fragment.md)与[流程导航片段](assets/agents-fragment.md)。已有文档只在明确的文档任务中按实际来源归并，不用模板覆盖。

业务确有模型提示词需求时可参考 [prompting](assets/prompting.md)，沿用项目已有规范；仅开发工具使用 AI 不构成创建业务规范的理由。观测样例按实际项目需要使用，不由初始化确认架构选型。

例：对空项目执行 init 后，核对六个 Skill、五个角色和导航，再次执行应无新增变更；同名资源存在冲突时报告路径并停止。
