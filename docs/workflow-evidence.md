# 工作流分发实施证据

## 2026-11-04 uv 用户级安装入口

按本轮用户确认的一条 uvx 命令安装方式实现；使用入口与更新操作见[安装说明](installation.md)。Python CLI／用户级安装逻辑位于 `src/sdd_init/`，`setup.py` 调用既有构建器将完整资源放入 wheel，`MANIFEST.in` 保证源码包具备重建输入。项目载荷继续保留为 ZIP，不注册成多个用户级 Skills。

| 验证场景 | 本地结果 |
|---|---|
| 仓库测试 | `python -B -m unittest discover -s tests -v`：25/25 通过，含首次安装、重复、更新、定制／缺失／额外文件保护、损坏载荷零写入、并发拒绝与替换失败恢复 |
| 原安装器回归 | 临时构建后的 `scripts/test_govern.py`：39/39 通过 |
| 源码包到 wheel | `uv build --out-dir .build/dist` 成功，从源码包重建 wheel，资源包含在包内 |
| wheel 与源码实际执行 | 分别运行 `scripts/smoke_package.py --from .build/dist/sdd_init-0.1.0-py3-none-any.whl` 与 `--from .`：成功；临时用户目录仅一个 Skill，目标项目五 Skills／五角色，重复执行稳定，用户级重装不改已有项目 |
| Git 来源 | 临时 Git 仓库的 `git+file:///…` 测试被 uv 0.11.20 Windows 内部 URL 解析崩溃阻断；未将该项标为通过 |
| CI | 增加 Ubuntu／Windows 矩阵、包构建及 wheel 冒烟步骤；尚未在远端运行 |

全部安装使用隔离的临时目录，未修改真实用户级安装、其他项目或用户运行配置。未提交或推送，本轮需求尚未写入远端 Issue；GitHub HTTPS 安装须在版本推送后验证。Codex 实际加载与交互调用未人工验收，客户端 `/sdd-init` 快捷入口不可由 Python 包保证，官方 CLI 入口为 `$sdd-init`／`/skills`。本地结果不能替代这些未验证项。

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
