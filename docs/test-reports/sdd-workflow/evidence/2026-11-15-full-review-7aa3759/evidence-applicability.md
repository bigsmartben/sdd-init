# 既有行为证据适用性核对

核对对象为 [2026-11-15 修复与最终回归报告](../../2026-11-15-workflow-fixes.md)及其 [原始证据目录](../2026-11-15-workflow-fixes/)，与本轮冻结输入 [before-manifest.json](before-manifest.json)，HEAD `7aa37597ad00b9eb09a890a6d3d1be230dc9f750`。本记录为只读核对，不含本轮新增模型执行；旧证据只支持原场景、原环境和实际观测，不能代替本轮静态逐项审查。

## 输入字节对照

以 Python 标准库读取旧 [final-v2-manifest.json](../2026-11-15-workflow-fixes/final-v2-manifest.json) 的 `files` 字典及本轮清单 `files` 数组，按相对路径逐一比较 SHA-256，再以 `hashlib.sha256(Path(path).read_bytes())` 核对本轮工作区。旧清单 158 项，本轮 156 项；共同 156 项中 **146 项相同、10 项不同**；旧清单独有 2 项，本轮独有 0 项。本轮 156 个文件与冻结清单全部相同，`git rev-parse HEAD` 返回上述提交。

不同的 10 项：

| 路径 | final-v2 SHA-256 | 本轮 SHA-256 |
| --- | --- | --- |
| `.agents/skills/sdd-workflow-review/SKILL.md` | `d7e2c20f2ac93415db526e33fccdf8f62d9bd9c7a8349c2d2e85ba396dc1458c` | `f3d64daea4350f1783598c08eefbb386a8a9a617b328bfccdf27848e87b749f2` |
| `.agents/skills/sdd-workflow-review/assets/review-report-template.md` | `233736f843a45207c89715d44248423fb471a16844cefc7cd3c1a930bbaaff7d` | `3f9f70186391e68cdfd0fc52791cfc3bb3e2c2afe4804b5e0bae57c6f79ab1d3` |
| `.agents/skills/sdd-workflow-review/references/evidence-and-cost.md` | `fc7d2c15e6f665c6db8b3b2f459ae73ca5f4c2ac6614cc09bd3ef2270d7dd617` | `a102a84b412ffd139a998e65f15d2cfc7c334f39409ae7508e5d63c440942f2f` |
| `.agents/skills/sdd-workflow-review/references/review-criteria.md` | `7a6d787a47ccca7f479a7198fd27a93e601efab2bc00d4e43719ad435480a15a` | `36deb5a1965974a376161850bcef79b9ed78dd4d0983a2d3d3cf67baac7ac056` |
| `docs/workflow-evidence.md` | `71134873eca4e4f2ff5d9edd6b323af54beeda635d828734e61e58e1e8a1c285` | `80c595f2bad765dffdb65d4017fb2493ed61d232bde2c4f4f6801c253ac56712` |
| `source/initializer/assets/user-agents/review-prompt.toml` | `87112509fc93378290b3797beb14b7b122ea0852e596ea8346278ca412e08777` | `8b3e90566f44aec2dad068b67211746b32169a643fd9c30d59f5b80ad614b824` |
| `specs/platform-independent-sdd/spec.md` | `22f4ff868a3db084e996b1f2c87c29362ccaeba687a4f6c8738386aa16db235d` | `70d73ff25b06abdd9e257ffae48ed741a6516078a9c4b17bdd2560163568858e` |
| `tests/fixtures/skill-behavior/README.md` | `f50266e127f6468d43f719f3d72295a3ab2ab0515d0dd3de0431df531531dee7` | `cc73cbd50e6a7653c585984ce775b889ebec27e0a99538f997a5c58f0456ad89` |
| `tests/fixtures/skill-behavior/cases.json` | `2a7629aea4bba95dd7e6b37d3d321bd69fc54fc7075e0972c2610cd6151566b6` | `e7050095e8f50c71ffd74f3cc5dc7373f82ca576b847d7fb9d78672978fc2649` |
| `tests/test_skill_context_stats.py` | `57874d514e079a283e9cec4560eb241f70756117063dc0734b5ff6798cb739a5` | `19bf266b43d9b18f031c60498c0abf7cb50c49e5cd2b0b9f7debed1cba0b9a80` |

旧清单独有 `MANIFEST.in` 和 `docs/test-reports/sdd-workflow/2026-11-14-whitepaper-assessment-archive.md`；此比较不表示它们必然从仓库删除，只说明未列于本轮清单。共同输入中项目工作流 Skill、五个项目角色、共享规则和白皮书字节一致；通用 `review-prompt` 角色新增 `model = "gpt-6-astra"` 和 `model_reasoning_effort = "high"`。旧归档对应字节可从 [before-sources.zip](../2026-11-15-workflow-fixes/before-sources.zip) 或 [fixed-sources.zip](../2026-11-15-workflow-fixes/fixed-sources.zip) 按清单哈希定位。

判据差异集中于评审过程：现行 Spec FR/AC-033、034 及 Skill 明确静态先行、并行发现归并、按关键疑点选择最小实跑、需要比较目标才做 A/B、分阶段报告及成本记录。RW 子项主体未改变，但评审 Skill 行为和适用专项判据已变。旧 `workflow_review_explicit` 的 [run.json](../2026-11-15-workflow-fixes/final-isolated/workflow_review_explicit/run.json) 实际固定旧 Skill、旧判据和旧角色哈希，不能证明新增过程。

## 案例复用台账

[final-behavior-index.json](../2026-11-15-workflow-fixes/final-behavior-index.json) 登记 53 次路径级尝试，按末级用例名去重为 **48 个独立案例**；五次为重试。49 条路径具有 `run.json` 和 `receipt.md`；四条状态查询、冷接续记录使用专用状态／交接 JSON，不应仅因没有顶层 receipt 判定缺证。`evaluation.json` 的 `model_execution: UNVERIFIED` 是夹具定义字段，不能当作实际结果；应查看运行事件、会话、变更产物和专用审计。

| 适用范围 | 独立案例数 | 原始位置和边界 |
| --- | ---: | --- |
| 原场景观察可作本轮行为证据 | 43 | 索引中的 R01–R07、R09–R18 全部独立案例，以及 R08 的 `role_doc_runtime_boundary`。逐例引用索引所列路径，沿用其原输入、可观察行为及失败和未验范围。R13、R16–R18 各有重试，计一次独立案例。 |
| 仅复用旧版普通维护未触发的观察 | 1 | R08 `final-isolated/workflow_review_not_requested`；旧请求是配置值 30→60，其会话和产物支持当次未进入评审。由于 Skill 已变，不单凭它断言现行 Skill 在所有普通维护场景均不会触发。 |
| 仅作历史依据，不能支持现行受变更对象通过 | 4 | R08 `workflow_review_explicit` 受 Skill、判据、模板变化影响；`review_prompt_read_only`、`review_prompt_compare`、`review_prompt_revise` 受角色模型配置变化影响。旧轨迹仍可证明当时观察，不能代表新配置行为。 |

43 项的复用是对现行未变源码对应的原始场景证据的适用判断，并非 43 项覆盖所有现行验收条件或当前环境下重新实跑。具体结论以对应 `run.json`、`request.txt`、`events.jsonl`、`sessions/`、`receipt.md` 和 `changed/` 为准；不得把执行退出码、角色注册或摘要当作所有业务判据通过。旧批环境为 Ubuntu WSL2、Codex CLI 0.169.0、Python 3.12.3，主受测模型 `gpt-6.1-sol`／`medium`，隔离配置、夹具和文件型替身；各角色模型及加载见各自会话。它不是当前不同模型或真实生产环境的可比实测。

对案例定义的补核：从 `fixed-sources.zip` 读取 `tests/fixtures/skill-behavior/cases.json`，其 SHA-256 为 `2a7629aea4bba95dd7e6b37d3d321bd69fc54fc7075e0972c2610cd6151566b6`，与 final-v2 清单一致。用 Python `json.loads` 按 `id` 建立字典并比较完整对象：旧版 82 项、当前 83 项，共同 82 项结构和值全部相同，当前新增的唯一 ID 是 `workflow_review_targeted`。43 个可复用案例中，27 个名称在两版 `cases.json` 中直接对应，完整对象均相同；另 16 个名称不在两版 `cases.json` 中，包括由旧执行器组合、覆盖或专用探针产生的场景，其实际输入只能按相应原始 `request.txt`、运行记录和专用审计限定，**没有据此证明这 16 个场景的当前等价输入已逐项核对**。上面的复用结论指原运行观察对未变工作流正文的相关性，并非声称 43 个案例在本轮都具有相同的现成输入。

原始记录抽核及限制：

- R01 的 [组合运行](../2026-11-15-workflow-fixes/final-stages/collaboration_workflow/run.json) 留有实际回合、文件哈希及会话；外部 AC-3 仍阻塞，不能据本地通过数推断全业务通过。
- R05 的 `role_coder`、`role_devops` 已登记角色身份和候选文件，运行出口未直接提取角色提示词正文哈希；不得将注册身份当作已证明实际装配正文。
- R15 的 [delivery-audit.json](../2026-11-15-workflow-fixes/final-delivery/release-confirmed/delivery-audit.json) 记录 `production-sim` 的 deploy 超时（124）及后续 status 回读；这是文件型替身，不是生产发布。
- R17 的 [正式候选报告](../2026-11-15-workflow-fixes/final-formal-ui-retry/formal_ui_acceptance/changed/docs/test-reports/checklist/formal-ui-acceptance.md) 保留 AC-2 失败及 Test Gate FAIL；它支持工作流如实登记失败，不支持候选业务通过。原型和正式候选是不同证据。
- R16 的 [active-status.json](../2026-11-15-workflow-fixes/final-active-status-retry/active_status_query/active-status.json) 显示查询在运行中注入并被接受；首次协议拒绝单独保留。R18 的 [handoff.json](../2026-11-15-workflow-fixes/final-cold-handoff-retry/cold_integration_handoff/handoff.json) 记录旧配置销毁、新会话、同产品版本及 AC-1、AC-2 各一次调用；不证明写入中强制终止恢复。
- 真实外部订单／退款／生产、真人业务验收、写入中强制故障恢复及本地提交后的完整远端选项未获该批行为证据。

现行夹具 `workflow_review_targeted` 标记 `model_execution: UNVERIFIED`，其新目标包括并行静态发现归并、只对本地回执疑点实跑、远端缺证、无比较目标不做 A/B；旧版 `workflow_review_explicit` 不含这些行为的现行版本证据。任何新增执行的结果应另行记录，不能预先记为通过。

## 隔离工具可用性

只读执行 `Get-Command python, node, codex, wsl, git`：Windows 可定位 Python、Node、WSL、Git，PATH 中未找到 `codex`；`wsl --list --quiet` 列出 Ubuntu 等发行版。仓库文件 `.build/prompt-role-workflow-review/client/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex` 存在，但未验证 WSL 内可执行性、认证或权限。`tests/prepare_skill_behavior.py`、`tests/fixtures/skill-behavior/run_prototype_check.cjs` 存在。

旧 [isolation-harness.zip](../2026-11-15-workflow-fixes/isolation-harness.zip) 包含冻结、执行及审计脚本，但旧 `run_review.py` 硬编码旧工作区 vendor、WSL Node／浏览器、认证路径和旧证据目录；`freeze.py` 依赖旧清单、`MANIFEST.in` 及旧 `.build` 模拟器。文件存在不等于现环境可直接运行；应先按当前候选、隔离配置及实际路径核对。以上未调用已安装 Skill、未改用户配置，也未启动模型。
