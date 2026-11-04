# 工作流分发实施证据

## 2026-11-04 用户级 sdd-init 实际升级

按本次用户明确授权，将当前仓库来源构建并安装到 `C:/Users/24598/.agents/skills/sdd-init`，载荷包含 [Spec FR-003／AC-003](../specs/platform-independent-sdd/spec.md) 的双平台交付与推送前同步规则。构建入口为 `python -B scripts/build_release.py --output .build/user-install-sync-20261104/sdd-init`，使用现有用户级 installer.install 执行安装，未修改安装器逻辑。

| 核对项 | 实际结果 |
|---|---|
| 旧安装保护 | 49 个受管文件与旧清单全部一致；额外 4 个文件均为 scripts/__pycache__ 内的 Python 缓存，直接升级会被完整性保护拒绝。核对差异后，将旧目录完整迁出 Skills 搜索目录，再按正常安装入口安装新包，未绕过校验 |
| 旧版保全 | 完整目录及缓存保留于 `C:/Users/24598/.agents/backups/sdd-init-20261104-before-platform-sync-c8852404`，迁移前后全部文件哈希一致 |
| 新包与安装 | 53 个受管文件及 66 个 ZIP 载荷文件；清单哈希与 ZIP CRC 通过，已安装目录与构建包清单一致；重复安装返回 Already current |
| 需求资源 | 内置 sdd-commit/SKILL.md 与 references/git-remote.md 均与当前来源逐字节一致；实际安装器在临时项目展开后的两份资源仍与来源及内置 ZIP 一致 |
| 实际安装器冒烟 | 从用户级已安装脚本对临时项目执行 init：六个项目 Skills、五个角色；再次执行后全项目文件哈希不变。展开的两份 commit Markdown 为 0 错误、0 警告，冒烟后用户级安装清单仍有效 |
| 升级保护回归 | `python -B -m unittest discover -s tests -p test_user_install.py -v`，5/5 通过；覆盖隔离升级、定制／缺失／额外文件保护、损坏包、并发锁及失败回滚 |
| 其他范围 | 其他用户级 Skills 的文件哈希及用户配置哈希不变；未初始化或升级当前仓库及任何真实项目，未执行远端交付 |

构建后入口与 prompting 的文档检查通过。实际安装与冒烟详情另生成于 `.build/user-install-sync-20261104/install-audit.json`；本次结果证明用户级入口及分发载荷已更新，不替代真实 GitHub／GitLab 交付或模型行为评测。历史未安装记录保留原有版本归属。

## 2026-11-04 sdd-commit 推送前远端同步补齐

依据 [Spec FR-003／AC-003](../specs/platform-independent-sdd/spec.md)，本轮修正此前仅检查仓库定位和合并前状态、未明确 push 前同步的缺口。更新 Skill 及原位[远端同步检查](../source/project/.agents/skills/sdd-commit/references/git-remote.md#远端同步检查)，要求远端交付分支创建前及每次 push 前刷新实际引用，分别比较任务与远端同名分支、任务与集成目标；落后或分叉先安全整合并完成受影响检查。固定维护基线沿用既有约定，获取失败或冲突未解不继续推送，保留无关未提交及预暂存内容。普通必要同步沿用终点授权，不增加逐步确认。

| 检查 | 实际步骤／范围 | 结果与边界 |
|---|---|---|
| 首次推送的旧 main | 临时 bare 仓库及两个 clone；本地从旧 main 建任务分支，另一 clone 更新 main；先读取旧 tracking，再 fetch、以 rev-list／merge-base 比较，merge 最新目标后首次普通 push | 通过；刷新前 tracking 看似已包含目标，刷新后识别双方各 1 个独有提交；整合后包含最新目标 |
| 远端任务分支分叉 | 两个 clone 分别提交同一任务分支；fetch 后比较、保留双方历史 merge，再普通 push | 通过；比较为双方各 1 个独有提交，整合后同时包含远端任务及目标提交 |
| 并发更新及脏工作区 | 查询后另一 clone 推进任务分支；本地普通 push 被拒绝；保留一项暂存及一项未暂存修改再 fetch；另向不存在的临时仓库 fetch | 通过；非快进拒绝未覆盖远端提交，fetch 前后两类 diff 相同；失败 fetch 返回非零，未更改远端；不据此证明 Agent 已自动执行恢复 |
| Skill／文档 | quick_validate.py；doc_check.py 检查 Spec、Skill、平台指引、夹具说明及本记录；git diff --check | Skill 通过；5 个 Markdown 为 0 错误、0 警告；差异格式通过，部分既有文件有换行规范化提示 |
| 定向分发回归 | unittest 的 test_build.py，选择 payload_and_shared_resources、build_is_reproducible、distribution_is_generic、generated_installer_is_idempotent 四项 | 4/4 通过；来源／载荷一致、可重建、引用、新装及幂等检查，均在临时目录执行 |
| 行为夹具 | 新增首次 push 旧 main、远端分叉与脏工作区、刷新竞态、固定维护基线 4 例 | JSON 及唯一编号校验通过；新增及既有场景保持模型执行 UNVERIFIED |

Git 实验只操作临时本地仓库，使用显式 fetch、提交关系比较、fast-forward／merge 与普通 push，验证所选同步方法的 Git 行为；未执行真实 GitHub／GitLab 写入，未验证模型会遵循新增规则。未修改本仓库工作分支或远端引用，未升级已安装副本。本轮只运行上述定向回归；此前 36／40 项结果仍属于此前快照。

## 2026-11-04 sdd-commit 双平台职责扩展

依据 [Spec FR-003／AC-003](../specs/platform-independent-sdd/spec.md)，本轮更新 sdd-commit、原位平台指引、仓库治理、delivery 角色与交接、安装导航及行为评测夹具。采用主 Agent 内容自查；既有未提交修改保留，未更改安装器逻辑、用户级安装或其他项目。

| 场景 | 本轮落点与核对结果 |
|---|---|
| 用户指定交付终点 | Skill 区分本地提交、创建分支、推送、Issue、PR／MR、合并；自主完成必要步骤，保留只建分支及只建 Issue 的停止点，不逐项要求用户操作；无新改动仍可继续远端交付 |
| GitHub／GitLab 适配 | 沿用 git-remote.md，补充主机／仓库定位、企业／自托管、subgroup 与 fork、连接工具／gh／glab／API 路由、查重及平台对象回读；需求与报告权威保持原位 |
| 合并及失败恢复 | 核对最新 head、目标及检查／审批／保护规则，使用预期 SHA 条件；排队与已合并区分，超时先查询，认证缺口只交回必要动作；不附带强推、删除或绕过保护 |
| 行为评测准备 | 新增 7 例：只建分支、GitHub fork PR、GitLab 自托管 MR 续交、只建 Issue、head／排队状态变化、超时恢复、认证缺口；17 例 JSON 解析、编号唯一性及 delivery TOML 解析通过，模型执行均保持 UNVERIFIED |

| 检查 | 命令／范围 | 实际结果 |
|---|---|---|
| Skill 结构 | skill-creator 的 quick_validate.py 检查 sdd-commit | 通过 |
| 文档 | doc_check.py 检查 Spec、Skill、平台指引、治理、交接、夹具说明及本记录；另检查构建后的 SKILL.md 与 assets/prompting.md | 来源 7 个及构建后 2 个 Markdown，均为 0 错误、0 警告；不据此推定行为通过 |
| 仓库回归 | `python -B -m unittest discover -s tests -v` | 36/36 通过；覆盖来源／载荷一致性、可重建、隔离安装与升级、导航及角色配置保护 |
| 构建 | `python -B scripts/build_release.py --output .build/platform-delivery-20261104/sdd-init` | 成功，未覆盖旧构建目录 |
| 安装器回归 | `python -B .build/platform-delivery-20261104/sdd-init/scripts/test_govern.py` | 40/40 通过；全部使用临时项目 |
| 引用与差异 | `python -B scripts/skill_context_stats.py`、`git diff --check` | 六个 Skill 的直接引用均存在；差异格式通过，部分现有 CRLF 文件有 Git 换行规范化提示 |

平台参数已对照指引中链接的官方文档核对，但未执行真实 GitHub／GitLab 交付或真实模型评测；安装与打包测试不证明平台认证、权限、CI、审批及合并链路已实测。未执行本仓库 commit、push、远端 Issue／PR 更新或 merge，未安装到用户级或其他项目。

## 2026-11-04 全仓指令精简复核

依据 [Spec FR-017／AC-017](../specs/platform-independent-sdd/spec.md)，本轮按语义盘点现行仓库治理、通用约束及五项专项架构 Rule、观测与提示词规范、六个 Skill 入口、五个角色、九份输出模板、初始化片段、项目索引、工具输出及行为评测夹具。执行者为本次主 Agent，采用内容自查；未启动独立角色或真实模型行为评测。

| 对象 | 本轮处理 |
|---|---|
| 通用提醒 | 删除重复的如实报告、不虚构、不夸大、证据不足不判通过、局部成功不等于整体成功等外围声明；删除提示词参考中的通用“事实真实性”条目，未搬移到其他规则正文 |
| 生成文本与相应检查 | 精简安装成功输出和两处蓝图占位告警，保留告警触发条件；行为夹具移除未测退款不得标通过的泛化禁止项，保留取消后仍提交的失败场景及修复交接；现有回归不绑定已删提醒，无需增加字符串断言 |
| SDD 专有约束 | 保留 Spec／Blueprint／报告权威、角色及写入分工、授权、独立审查、人工确认、版本追溯、Review 同一快照全部适用项与 Test 全部目标 AC 及组合行为的 Gate 判据；工具机械检查边界保留 |
| 系统技术约束 | 保留持久化回执、业务与观测隔离、媒体拒收、正式与测试资产及装配隔离；保留并发写入的业务实体落库、观测状态快照及直接／间接依赖约束；业务模型提示词的输入、权限和生命周期契约保留 |
| 历史与已有修改 | 保留 baselines、既有执行记录及观测示例的失败／UNVERIFIED 状态；沿用 FR-017／AC-017，不增加精简需求编号，保留其他未提交及并发修改 |

被测版本为 `f83f76092d5f46e5c5ad8ba119e63053185ec886` 加本次工作区未提交改动。Windows／PowerShell；安装回归使用隔离临时项目和临时用户目录。构建目录为 `.build/generic-guidance-audit-20261104/sdd-init`，载荷 SHA256 为 `bd51bbebc892427b9df8bf2f461b59aa6c27fff371bb8fea11d630c41a0ab733`。

| 检查 | 命令或证据入口 | 结果与覆盖 |
|---|---|---|
| 源文档检查 | `python -B source/project/.agents/sdd/scripts/doc_check.py --root . AGENTS.md README.md docs specs source/project tests/fixtures` | 36 个 Markdown，0 错误、0 警告；覆盖现行分发、维护说明、Spec 和夹具说明 |
| 投影入口检查 | `python -B source/project/.agents/sdd/scripts/doc_check.py --root .build/generic-guidance-audit-20261104/sdd-init SKILL.md assets/prompting.md` | 2 个 Markdown，0 错误、0 警告；初始化器共享引用按构建后的真实位置解析；托管片段的安装后链接由安装回归覆盖 |
| 仓库回归 | `python -B -m unittest discover -s tests -v` | 36/36 通过；分发、可重建、新装／升级／幂等、既有内容及配置保护、文档 CLI、隔离用户安装及回滚 |
| 构建 | `python -B scripts/build_release.py --output .build/generic-guidance-audit-20261104/sdd-init` | 成功；从现行来源重建 |
| 安装器回归 | `python -B .build/generic-guidance-audit-20261104/sdd-init/scripts/test_govern.py` | 40/40 通过；安装保护、链接、存量状态及 Gate 证据检查 |
| 产物完整性 | 构建清单、ZIP CRC、载荷及初始化器／共享投影与来源逐字节核对 | 52 个清单文件哈希、63 个载荷文件及全部来源投影一致 |
| 入口引用与格式 | `python -B scripts/skill_context_stats.py`、`git diff --check` | 六个 Skill 直接引用均存在；差异格式通过，Git 提示部分 CRLF 文件后续规范化为 LF |

遗留验证范围：真实模型行为评测仍为 UNVERIFIED；观测多语言完整基线及共享栈当前运行状态未验证，Java 历史媒体示例冲突保留且未执行。本轮未执行包发布、真实用户安装、其他项目升级、产品部署、commit、push 或 merge；既有历史记录保持原有版本归属。

## 2026-11-04 仓库治理与六类架构 Rule 复核

依据 [Spec FR-012／FR-014、AC-012／AC-014](../specs/platform-independent-sdd/spec.md)，对仓库治理、架构规范、观测基线、候选目录、蓝图／契约／时序模板、原型、角色交接、文档写入及实施／审查／验收入口进行职责与语义核对。执行者为本次主 Agent，属于内容自查，不声明独立架构审查或产品验收。

本轮修正：候选目录明确六类 Rule 已生效；媒体保存禁令显式覆盖链路载荷；观测示例中的范围和历史保留策略与现行规则分开；实施、文档写入和治理审查入口承接六类 Rule；治理中的断言技术要求改为引用架构规范。保留基线稳定编号、业务／测试音频例外、瞬时处理例外、观测故障隔离和业务反向依赖禁令，未新增技术选型。复核后，在上述范围未发现剩余职责混放、重复权威正文或已确认约束遗漏；模板必要字段提示及指向正文的摘要属于使用入口，不另立规则。

被测版本为 `f83f76092d5f46e5c5ad8ba119e63053185ec886` 加本次工作区未提交改动（含此前协同、模板、文档 CLI 和本轮规范变更）；Windows／PowerShell 环境，测试使用隔离临时项目及临时用户目录。实际载荷 SHA256：`e92b6bb97ade8dfaf5c68dd1598ca06e9e01750de1d9e9a5b102b86cecf532b2`。

| 检查 | 命令或证据入口 | 结果 |
|---|---|---|
| 文档机械检查 | `python -B source/project/.agents/sdd/scripts/doc_check.py --root . source/project/.agents/sdd source/project/.agents/skills specs/platform-independent-sdd/spec.md` | 27 文件，0 错误、0 警告 |
| 仓库回归 | `python -B -m unittest discover -s tests -v` | 36/36 通过；含构建可复现、分发一致、新装、更新、定制保护、用户安装回滚和隔离 |
| 构建 | `python -B scripts/build_release.py --output .build/governance-architecture-audit-20261104/sdd-init` | 成功 |
| 构建后安装器回归 | `python -B .build/governance-architecture-audit-20261104/sdd-init/scripts/test_govern.py` | 40/40 通过；含安装导航、幂等、既有正文和运行配置保护、缺失资源拒绝及存量工具 |
| 产物完整性 | 构建目录 `build-manifest.json`、`assets/repo-payload.zip` 与 `source/project/` 逐字节核对 | 52 个清单文件哈希、63 个载荷文件及 ZIP CRC 全部通过 |
| 差异格式 | `git diff --check` | 通过；Git 提示 README 和测试文件后续规范化 CRLF 为 LF |

未修改真实用户级安装或其他项目，未执行推送、产品部署及人工验收。观测多语言示例的 full_baseline 仍为 UNVERIFIED，Java 历史媒体示例冲突仍保留且未执行，共享栈当前状态未验证；这些实现缺口不由文档或安装测试通过来消除。

## 2026-11-04 默认分支安装验证

[PR #2](https://github.com/bigsmartben/sdd-init/pull/2) 已合并至 main，合并提交 `8c5ed74949ac3e2a6d8b60f6c913654026aaa867`。执行 `python -B scripts/smoke_package.py --from git+https://github.com/bigsmartben/sdd-init.git` 通过：从 GitHub 解析默认分支、构建并安装用户级 Skill、重复安装、初始化临时项目、核对五 Skills／五角色、确认用户级重装不修改项目以及项目重复初始化稳定。实际使用入口见[安装说明](installation.md)。测试未改动真实用户级安装；Codex UI 加载与调用仍未人工验收。

以下为合并前的分支验证记录。

## 2026-11-04 uv 用户级安装入口

按本轮用户确认的一条 uvx 命令安装方式实现；使用入口与更新操作见[安装说明](installation.md)。Python CLI／用户级安装逻辑位于 `src/sdd_init/`，`setup.py` 调用既有构建器将完整资源放入 wheel，`MANIFEST.in` 保证源码包具备重建输入。项目载荷继续保留为 ZIP，不注册成多个用户级 Skills。

| 验证场景 | 本地结果 |
|---|---|
| 仓库测试 | `python -B -m unittest discover -s tests -v`：25/25 通过，含首次安装、重复、更新、定制／缺失／额外文件保护、损坏载荷零写入、并发拒绝与替换失败恢复 |
| 原安装器回归 | 临时构建后的 `scripts/test_govern.py`：39/39 通过 |
| 源码包到 wheel | `uv build --out-dir .build/dist` 成功，从源码包重建 wheel，资源包含在包内 |
| wheel 与源码实际执行 | 分别运行 `scripts/smoke_package.py --from .build/dist/sdd_init-0.1.0-py3-none-any.whl` 与 `--from .`：成功；临时用户目录仅一个 Skill，目标项目五 Skills／五角色，重复执行稳定，用户级重装不改已有项目 |
| Git 来源 | GitHub HTTPS 分支入口已通过 `scripts/smoke_package.py` 完整验证，解析提交 `fb65a977ab871ccbe1d747bcbb3c399912cf3989`；此前 Windows 本地 `git+file` 的 uv 崩溃不影响此 HTTPS 路径 |
| CI | [提交 fb65a97 的远端 CI](https://github.com/bigsmartben/sdd-init/actions/runs/41777671560)：Ubuntu／Windows 两端全部通过，包含仓库测试、39 项安装器回归、源码包／wheel 构建及 wheel 冒烟 |

全部安装使用隔离的临时目录，未修改真实用户级安装、其他项目或用户运行配置。实现已提交并推送至 `codex/workflow-contract-plan`，GitHub HTTPS 分支安装与临时项目初始化全流程已通过；当前可用命令见安装说明。未合并至 main，不带版本的默认分支命令尚不可用；本轮需求未写入远端 Issue。Codex 实际加载与交互调用未人工验收，客户端 `/sdd-init` 快捷入口不可由 Python 包保证，官方 CLI 入口为 `$sdd-init`／`/skills`。本地结果不能替代这些未验证项。

## 2026-11-04 独立沟通规范分发验证

最终源码完整回归：`python -B -m unittest discover -s tests -v` 通过 20/20；`python -B scripts/build_release.py --output .build/final-communication-20261104/sdd-init` 构建成功；`python -B .build/final-communication-20261104/sdd-init/scripts/test_govern.py` 通过 39/39。检查构建清单哈希、ZIP CRC 和载荷与源码逐字节一致，并确认分发入口及规范正文包含可视化对齐与结论先行两条原则。临时项目测试覆盖新装、上一版升级、原正文保护和重复执行；升级须显式使用 `--update-skills`。未修改用户级安装或其他实际项目；测试不证明真实 Agent 每次运行均遵循规范。

“结论先行、分层确认”补充复核：将推荐结论限定于方案选择，Review／验收先给实际结果；决策必需细节简要呈现，详细材料作为可选入口，授权内细节自主推进。合并重复执行表述，仓库与分发首部入口保持一致。新增 `test_conclusion_first_rule_new_install_and_previous_version_upgrade`，验证新装、旧版入口及规范资源显式升级、正文保留和重复执行；连同现有沟通迁移、分发链接、可复现构建测试，本轮定向 4/4 通过。规范链接、锚点及 `git diff --check` 通过；全部构建及安装使用临时目录。本轮未更改安装器逻辑，未重跑完整 39 项存量工具回归；以下全量结果属于此前快照。

复核修复：新增回归先复现 UTF-8 BOM 被移入正文、资源父目录被普通文件占用时 AGENTS 已被写入的问题；修复后 BOM 保留文件首部，父路径冲突在任何写入前报告。规范进一步区分产品交互与其他产品判断、原型审阅与实际集成验收，明确确认不自动授权落盘，已有视图按需复用；架构文档规范仅在实际编写对应文档时适用。

| 修复后验证 | 实际结果 |
|---|---|
| `python -B -m unittest discover -s tests -v` | 19/19 通过；新增 BOM／混合换行的新装升级幂等、资源父路径冲突的零写入保护 |
| `python -B scripts/build_release.py --output .build/visual-governance-reviewed-20261104/sdd-init` | 构建成功；清单哈希、ZIP CRC、载荷及安装器与维护源字节一致 |
| `python -B .build/visual-governance-reviewed-20261104/sdd-init/scripts/test_govern.py` | 39/39 通过 |

以下为首次实现记录；本节修复后验证对应当前源码。

依据本轮用户确认的实施计划，当前仓库与项目默认分发共同引用[可视化沟通与确认规范](../source/project/.agents/sdd/references/visual-confirmation.md)。独立沟通原则管理块置于 AGENTS 首部，流程导航独立管理；安装器已补齐规范的允许路径与必需文件校验。规范不以前置启动 Skill、角色或业务工作流为条件。

| 验证 | 实际结果 |
|---|---|
| `python -B -m unittest discover -s tests -v` | 17/17 通过；含构建一致性、中文 LF／CRLF 正文保留、新装、旧片段升级、原则块移至首部及重复执行的逐字节一致性 |
| `python -B scripts/build_release.py --output .build/visual-governance-20261104/sdd-init` | 构建成功；规范正文和独立沟通原则模板随包分发 |
| `python -B .build/visual-governance-20261104/sdd-init/scripts/test_govern.py` | 39/39 通过；安装、已有正文／配置保护及存量工具回归 |
| 失败保护 | 缺失必需规范、非法载荷、缺失／重复／嵌套管理标记及 override 遮蔽均在写入前失败；临时目标快照不变 |

验证仅使用隔离临时项目与本地构建产物；用户级安装及其他实际项目未修改，未提交、推送或发布。上述结果证明默认分发与安装行为，不证明真实客户端中的 Agent 每次执行均遵循沟通要求。

## 2026-11-03 当前本地分发验证

本节记录本次用户指定以 hanxue-live 已安装的项目 Skill、Agent 为来源、恢复五 Skill 与五角色并去除项目专属映射后的实际结果；不是另一份需求或 Plan。[Issue #1](https://github.com/bigsmartben/sdd-init/issues/1) 和 [Draft PR #2](https://github.com/bigsmartben/sdd-init/pull/2) 仍保留此前四 Skill／七角色方案，本轮未修改远端正文。以下当前结果取代旧方案的现行分发描述，后文旧验证仅用于追溯。

- 当前项目 Skill 为 sdd-doc、sdd-imp、sdd-test-loop、sdd-review-loop、sdd-commit；角色为 sdd-designer、sdd-coder、sdd-documenter、sdd-validator、sdd-delivery。个人级 sdd-init 仍只分发项目资源。
- 初始化器、托管导航、元数据与回归检查按上述清单适配；增加 module-design、sequence-flows 模板的载荷许可及必需性检查。旧 sdd-accept 和被替代角色在任何写入前报告冲突，即使显式升级也不静默删除。
- 清除来源项目的专属需求路径、课堂映射、架构链接和 ARC 编号；由目标项目 docs/index.md 解析实际需求、蓝图和契约，模板不预设独立 Spec 已退役。模板与 Skill 的可复用职责保留，默认目录按项目治理规则定位。
- 模型默认值沿用五角色来源：designer 使用 gpt-6-astra，coder 使用 gpt-6.1-sol，documenter／validator／delivery 使用 gpt-6.1-terra；不设角色推理强度，不改用户运行配置，保护同名定制及既有文档。

| 检查 | 本次结果 |
| --- | --- |
| `python -B -X utf8 -m unittest discover -s tests -v` | 12/12 通过；覆盖可复现构建、幂等、定制及既有实体保护、五角色模型、非法载荷拒绝、旧入口迁移保护、新模板必需性和通用资源链接 |
| `python -B -X utf8 scripts/build_release.py --output .build/five-skills-five-agents-verified/sdd-init` | 构建成功，产物仅在仓库本地生成 |
| `python -B -X utf8 .build/five-skills-five-agents-verified/sdd-init/scripts/test_govern.py` | 39/39 通过；新安装、重复执行、显式升级、配置保留、相对文件链接和存量状态／快照／提交边界 |
| 产物独立核对 | 清单的 51 个文件 SHA-256 全部一致，ZIP 的 63 个文件与维护源逐字节一致；清单为五项目 Skill、五 Agent，无额外入口；ZIP CRC 正常 |
| 通用性与格式 | 构建及安装后的 Markdown 不含来源项目名、专属需求路径、课堂映射、固定 ARC 映射及失效架构路径；分发文档／角色／元数据 UTF-8 解码通过，`git diff --check` 通过 |

以上为隔离临时项目及本地构建验证，不表示用户级安装、hanxue-live 或其他项目已升级，也不证明真实客户端加载、指定模型运行或产品人工验收。未执行远端更新、提交或推送。存量状态工具仍读取本地 Spec/Status，不能自动解析 Issue 或项目自定义需求映射；使用前核对实际能力，未做批量迁移。

## 此前四 Skill／七角色方案的历史实施记录

以下为此前实际实施与验证记录，不作为当前分发清单。

2026-11-02。本地分支 codex/workflow-contract-plan，起点 60c6bef；2026-11-03 按用户确认将七角色模型建议调整为 TOML 默认模型；需求与实施安排分别引用 [Issue #1](https://github.com/bigsmartben/sdd-init/issues/1) 和 [Draft PR #2](https://github.com/bigsmartben/sdd-init/pull/2)。本文件记录实际结果，不维护另一份需求或 Plan。

## 实际交付

- 更新 sdd-doc、sdd-imp，引入 sdd-accept，撤下 sdd-test-loop 与 sdd-review-loop 的分发入口；保留初始化和 Git 交付配套职责。元数据允许按明确自然语言意图选择，不绑定模型或强制委派。
- 共享说明与入口统一实体归属；提供 Issue、Blueprint、Draft PR 通用模板、六类场景提示、原型引用和人工验收操作模板。原型说明覆盖产品代码隔离、候选操作、固定版本引用和用户确认。
- 初始化只安装资源与导航，不创建 Blueprint／Spec／Status、不回填存量状态、不改用户配置。退役 Skill 冲突在写入前拒绝，不静默删除用户副本；含旧入口的项目升级仍需单独处理。
- 存量状态工具保留原有记录语义并标明适用边界；项目侧撤下不可用的安装入口。观测资源保留为按项目决定采用的参考，不预填项目架构或采纳结果。
- 根据后续确认增加七个项目角色，源位于 source/project/.codex/agents/，通过同一载荷安装。角色包含名称、场景说明、默认 model 和职责指令；模型映射与优先级见执行协作说明，不设置角色推理强度或修改用户运行配置。

## 本地验证

| 检查 | 结果与覆盖 |
| --- | --- |
| python -B -m unittest discover -s tests -v | 2026-11-03 重跑 11/11；载荷一致、可复现、幂等及既有正文保护、新安装实体边界、退役入口拒绝、缺失新模板拒绝；覆盖七角色默认模型、同名模型定制保护、旧无模型角色显式升级、非法或缺失模型及固定强度载荷在写入前拒绝、运行配置保护 |
| python -B scripts/build_release.py --output .build/role-model-defaults/sdd-init | 2026-11-03 构建成功；仅生成本地候选 |
| python -B .build/role-model-defaults/sdd-init/scripts/test_govern.py | 2026-11-03 重跑 39/39；安装后七角色模型映射与无推理强度字段、升级保护、用户配置保留、链接、调用策略及存量记录／快照／提交边界 |
| skill-creator quick_validate.py | 2026-11-02 的 5/5 静态格式检查；本次未重跑，Skill frontmatter 未变 |
| 文档检查 | 2026-11-03：源文件 UTF-8、30 个 Markdown 文件的 39 个相对文件链接及 git diff --check 通过；产物内链接随回归检查，托管片段按安装后位置解析 |
| 导入追溯 | 初始提交 e6bf191 的 50/50 文件哈希与 import-manifest 相符；本次维护源变化不改写历史哈希 |

CI 增加构建产物回归命令；以上是本地结果，远端执行状态以 PR 检查为准。现有回归中旧状态测试使用显式存量夹具，新初始化器不再替测试生成业务实体。旧精确口令断言改为当前调用策略检查，缺失角色引用随通用模型绑定说明撤下；本轮新增的七角色为明确确认的新职责配置。

角色测试初次将所有 TOML 都当角色，误计入既有 Rust Cargo.toml；已将检查限定为角色文件及安装位置，重新运行 10/10 通过。

## 职责语义核对

按入口和共享说明走查代表性表达：“讨论这个方案”仅讨论；“对”仅确认；“对，把结论更新到 Issue”进入固化；“按方案开始实现”进入实施及局部自验；“把版本 X 部署到环境 Y 供我验收”准备环境和操作文档；验收反馈先进入讨论，有明确修复要求再实施。“落地”仅在上下文确实不足时澄清。

这属于指令内容核对与静态检查，没有独立模型行为测试或真实部署证据，不宣称每次运行行为已获保证。

## 剩余事项与限制

- AC-003 的入口、说明与模板已在本地实现；AC-007 的相称本地检查通过，尚未进行用户人工验收。
- AC-004 已提供不依赖平台的说明与模板；目录、托管平台和访问方式待实际项目确定，没有生成并发布具体原型，不算完整原型交付验收。
- AC-005／006 原重型目标移出本轮，不计完成。存量工具仍有全能力检查及 Status 重建语义，不支持 Issue 新工作流，也未进行批量迁移。
- AC-008 的七角色配置与分发已实现并通过本地检查；未在真实目标项目加载角色或开展独立模型行为测试。角色文本边界不等于硬性权限隔离。
- 没有安装到用户级或其他项目，没有产品部署、人工验收、合并或关闭 Issue。此前精简工作流代码与说明已同步 Draft PR；2026-11-03 的默认模型调整尚未提交或推送，远端代码与 CI 不包含该调整。提交与 CI 回执以 PR 为准，不表示其他项目升级完成。


## 2026-11-04 压缩规范复核与安装验证

依据 [Spec FR-019 / AC-019](../specs/platform-independent-sdd/spec.md)，对照压缩前快照复核治理、文档写入规则和观测基线，并核对架构规范、协作、原型、Skills 及模板。当前工作区基于 `f83f76092d5f46e5c5ad8ba119e63053185ec886`，包含未提交修改；本轮由同一执行者复核，不声明独立审查。

| 核对对象 | 结果 |
|---|---|
| 职责与权威 | 治理承载授权、资产及完成条件；架构承载技术约束；doc 归并文档；Review 检查架构实现，Test 检查需求行为；未发现压缩导致的职责混淆 |
| 约束承接 | 授权沿用、例外、实现完成、独立复核、人工确认、版本归属、正式／测试隔离、落库判据、观测非阻塞及媒体边界均有正文或有效引用承接；未发现遗漏，原标题及显式锚点保留 |
| 源文档 | 文档 CLI 检查共享资源、Skills、初始化提示、README、安装说明及 Spec，共 30 份，零错误／警告 |
| 构建 | `python -B scripts/build_release.py --output .build/compression-review-20261104/sdd-init` 成功 |
| 分发回归 | `python -B -m unittest discover -s tests -v`，36/36 通过，包含临时目录中的用户安装、升级保护与回滚检查 |
| 产物安装回归 | `python -B .build/compression-review-20261104/sdd-init/scripts/test_govern.py`，40/40 通过 |
| 隔离新安装 | 在 `.build/compression-review-20261104/installed-project` 执行产物安装器 `init` 成功；安装后的 AGENTS、索引、共享资源及 Skills 共 28 份 Markdown 检查通过；构建后初始化 SKILL 的链接检查通过 |
| 载荷一致性 | ZIP CRC 正常，63 个载荷文件与当前项目源及隔离安装结果逐字节一致；52 项构建清单哈希一致 |

载荷 SHA-256：`9b8d1d3bffc2f686f72717f8e9c65f359280ef2e539d2d35a58e2d0c3b88fded`。

初次将初始化入口和托管片段按源码位置检查，出现 13 个目标缺失；这些引用按构建／安装位置解析后全部通过。隔离新安装首次因目标目录尚未创建而拒绝，创建目录后成功。未修改真实用户级安装或其他项目，未执行产品部署或目标项目验收；本轮未新增或修改规范条款。

## 2026-11-04 测试 Issue 清单与复验闭环

依据 [Spec FR-021／AC-021](../specs/platform-independent-sdd/spec.md)，更新测试报告模板、test／doc／imp、文档写入规则、治理、场景提示及项目索引。验证对象为基于 `f83f76092d5f46e5c5ad8ba119e63053185ec886` 的当前未提交工作区；本节记录文档维护检查，不代表真实目标项目的 Test Gate 或独立模型行为测试。

| 检查 | 结果与范围 |
|---|---|
| 条款与场景走查 | 无 Issue 时记无；多场景关联同一 Issue；修复与局部自验完成后待复验；复验失败沿用编号并保留历史；需人工确认时保持待确认；证据／文档／需求问题分别归位；非代码问题按处理结果核验关闭；Review 沿用专用 gap |
| 源文档与技能 | 本轮修改及直接关联的 12 份 Markdown（含本记录）检查通过，零错误／警告；test、doc、imp 三个技能的 quick_validate.py 检查通过；本轮 10 份修改文件的 UTF-8 与差异空白检查通过 |
| 现有回归 | `python -B -X utf8 -m unittest discover -s tests -v`，36/36 通过，覆盖构建、安装保护、载荷一致性及文档 CLI |
| 最终隔离构建与安装 | 临时目录内构建并执行 `init` 成功；ZIP CRC 正常，64 个载荷文件与项目源及安装结果逐字节一致；安装后 29 份 Markdown 检查通过，零错误／警告 |

最终载荷 SHA-256：`929e5e73bebcbc8e4d77e481f72ef0344c141e2c2be7a5a4cb38bca6b2f75bcc`。本轮 Issue：无。检查产物位于临时目录并随验证清理；未修改用户级安装或其他项目，未执行提交、推送或历史报告迁移。

## 2026-11-04 sdd-deploy 技能与安装分发

依据 [Spec FR-022／AC-022](../specs/platform-independent-sdd/spec.md)，新增 [sdd-deploy](../source/project/.agents/skills/sdd-deploy/SKILL.md) 及 UI 元数据，同步六个技能的安装清单、README、安装说明、托管导航、治理、协作与项目索引；保留五个角色。检查对象为当前未提交工作区，未修改用户级安装或其他项目。

| 检查 | 结果与范围 |
|---|---|
| 语义走查 | 对照已确认意图，默认 dev 并支持指定环境；按请求触发，不随代码修改自动运行、不增设审批；环境准备与修复、首次部署、既有服务更新重启、重复调用复用及冲突诊断均有执行路径；运行就绪与业务验收分开 |
| 技能及源文档 | quick_validate.py 通过；本轮 7 份源 Markdown 零错误／警告；本记录另行执行文档校验 |
| 分发与仓库回归 | unittest discover 首次 36/37 通过，唯一失败为上下文统计仍预期旧技能数；改为包含初始化器的 7 个入口后，该测试文件 2/2 通过。新增部署技能升级与缺失载荷保护测试通过 |
| 构建后安装器回归 | test_govern.py 首次 39/40 通过，唯一失败为载荷仍预期 5 个项目技能；更新为 6 后，对应测试 1/1 通过 |
| 隔离构建与安装 | 临时目录内构建和 init 成功；构建后的初始化入口 1 份、安装后的共享资源／技能／导航 30 份 Markdown 检查均为零错误／警告 |
| 差异检查 | git diff --check 无空白错误；Git 提示部分文件后续将按仓库规则由 CRLF 转 LF |

以上为规则语义走查及工具、安装验证；未进行独立模型行为评测或真实环境部署。构建与安装检查产物随临时目录清理，未执行提交或推送。

## 2026-11-04 部署环境规范通用化

依据 [Spec FR-022／AC-022](../specs/platform-independent-sdd/spec.md) 的补充确认，将用户级 local-base-environment 中的通用环境探测、准备修复、挂载验证与资源隔离要求融入 sdd-deploy。保留项目既定部署规范优先及 dev 优先 Compose，不引入平台发行版、固定路径、个人仓库或特定工具栈，不修改用户级技能。

本轮仅更新技能正文、对应 Spec 与本记录。语义核对覆盖先探测再落地、本地与远端状态区分、服务复用、共享依赖与持久化数据隔离，沿用按请求触发和不增设审批的约定。技能同口径非空白字符由 1415 降至 1197（减少约 15.4%），无新增参考文件或脚本。quick_validate.py 通过；技能与 Spec 两份 Markdown 检查零错误／警告；隔离构建及 init 成功，载荷和安装后的技能与源文件逐字节一致，安装后技能文档检查通过。本记录另行执行文档校验。

未执行真实环境部署或独立模型行为评测；本轮无工具代码变更，未重复运行全套回归。临时构建与安装目录已随检查清理。
