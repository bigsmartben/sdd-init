本工单完成只读静态审查，无源码写入、无实跑、无子 Agent。未发现足以新增为“存在偏差”的确定性缺陷。五个对象的职责、终点、授权、失败恢复及证据边界在当前正文中闭合。`review-prompt` 当前模型配置缺少同配置行为证据，须单独保留。

**逐对象结果**

| 对象 | 静态结论及精确依据 | 专业独立执行／交付终点 |
|---|---|---|
| `source/project/.agents/skills/sdd-deliver/SKILL.md` | 符合。10–16 行定义独立和组合终点、就绪与复验；20–24 行沿调用链处理评估、确认及提交后选择；28 行向 Main 回执并交回跨阶段事项。 | 阶段只组织自身交付；未要求其他 Skill 先运行。 |
| `source/project/.codex/agents/sdd-coder.toml` | 符合。5 行直达独立执行和实施依据；8 行自主调查、实施、失败修正，保留测试限定授权；11–18 行给出输入、同一 Plan、版本与局部证据。 | 不以完整 Blueprint 为前置；共享 `implementation.md:7,11–19` 明确工单直接引用、原判据、自验覆盖及缺项回执。 |
| `source/project/.codex/agents/sdd-devops.toml` | 符合。5 行按共享指引独立接单；8 行自主制定专业方案、操作与复验；11–17 行输入、实际状态、模板和回执完整。 | 发布、备份、排障等按自身前置；无自行启动集成阶段或指挥其他角色的路径。 |
| `source/project/.codex/agents/sdd-doc-consistency.toml` | 符合。5 行排除运行时指令；7–9 行按同对象、条件、版本取证；11 行删除建议须检查承接、独有条件和历史用途；13 行只读交回实际调用者。 | 只交发现、建议及待裁决事项；实际只读会话由 `delegation.md:43` 保证，不把角色自述当权限证明。 |
| `source/initializer/assets/user-agents/review-prompt.toml` | 静态符合；当前配置行为证据不足。6–10 行按工单和实际加载路径取证，默认只读，授权修订限定对象；12 行区分装配与行为证据；14 行报告只在授权范围写入并回实际调用者。 | 不依赖 SDD 安装；独立专项产物归调用方。当前 `model`／强度是 `gpt-6-astra`／`high`（2–3 行）。 |

**全部 RW 子项静态覆盖**

C＝在本对象及其适用共享契约内静态符合；N＝不适用。每格按 `.1/.2/.3` 顺序列出。此表不声称行为通过。

| RW | deliver | coder | devops | doc-consistency | review-prompt |
|---|---|---|---|---|---|
| 01 | C/C/C | C/C/C | C/C/C | N/N/C | C/C/C |
| 02 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 03 | N/N/N | C/C/C | N/N/N | N/N/N | N/N/N |
| 04 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 05 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 06 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 07 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 08 | C/C/C | C/N/N | C/N/N | C/N/N | C/N/N |
| 09 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 10 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 11 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |
| 12 | C/C/C | C/C/C | C/C/C | C/C/C | C/C/C |

N 的理由：

- RW-03：需求交付与技术重构的独立分流不是交付、运维、只读文档或通用提示词专项的本职阶段；范围外发现和授权边界另按 RW-04、12 检查。coder 承接实施和重构，全部适用。
- doc 的 01.1／01.2：只读取证不组织用户需求与方案确认；需裁决内容回调用方。
- 角色的 08.2／08.3：面向用户的长程通知、状态查询由 Main 组织；角色须按原调用链提供状态和缺口，已在 RW-07、12 检查。
- RW-09～12 的 C 表示本对象未建立强制逐层、同层调用或倒置路径；整版调用关系仍由 Main 横向归并。

共同依据：

- `delegation.md:15–18,29–31,35–43,47–66`：实际调用者、角色独立、只读权限、缺项及确认回传。
- `sdd-repository-governance.md:7–9,21–29,47,51–61,80–100,158–160,186`：关键决定、直接角色路径、持续执行、状态接续、验收及证据边界。
- `document-writing.md:3–11,15,25–31`：唯一正文、条件例外、直接引用、写后检查及局部证据。
- `delivery.md:21–31,35–49`：生产实时源与间接触发、告知后接续、先回读再重试、独立项继续。
- `release-evidence.md:3–5`：最终候选、适用 Gate、发布缺证暂停但独立备份等可继续。
- `git-delivery.md:14–16,20–30`，`git-remote.md:32–48,74–84`：范围外暂存保护、远端同步、最新 head、合并与不明结果回读。
- `deployment.md:7–16,30–34`，`traffic.md:5–8`，`recovery.md:7–18`：源／制品／运行关联、控制面与数据面、部分恢复、备份与可恢复区别。

**已有行为证据适用性**

对 `2026-11-15-workflow-fixes/final-v2-manifest.json` 做只读哈希核对：

- 当前 deliver、coder、devops、doc-consistency 正文均与 `final-v2` 相同。
- 清单内全部共享 references／assets 与当前字节相同；因此这批已有证据可按场景复用，不能把 11 月 14 日初审 F03/F08 继续认作当前未修复缺陷。
- `final-isolated/role_coder/run.json`：实际注册 `sdd-coder`，只改原 Plan、实现和指定测试，定向与单测结果在回执中，独立验收仍待输入。
- `final-isolated/role_devops/run.json`：实际注册 `sdd-devops`，本地提交 `221c879bb01417295359bab5e3201f484561b271` 只含 `ops/rollout.txt`，保护暂存 `notes.txt`。
- `final-isolated/role_doc_consistency/run.json` 与 `role_doc_runtime_boundary/run.json`：加载角色 hash `7e063245…`，模型 `gpt-6.1-terra`，`changed=[]`；覆盖冲突、重复、断链、错版证据和提示词排除。
- `final-delivery/release-confirmed/run.json`：实际层级 Main → `/root/deliver` → `sdd-devops`。部署超时后回读就绪，再冒烟与切流；数据完整性缺证未宣称通过。
- `final-delivery/role_devops_backup_gate`：实际 devops 在发布阻塞时完成独立三条记录备份；明确还原可恢复性未验。
- 同批 `release-final-evidence`／`release-stale-evidence`／`release-missing-evidence`／`release-query-only`／`rollback-partial`／`rollback-confirmed` 及 `delivery-audit.json` 支持授权停点、仅查询、旧证据和部分恢复的限定结论。

**唯一新增版本证据缺口**

`review-prompt` 当前 SHA-256 为 `8b3e90566f44aec2dad068b67211746b32169a643fd9c30d59f5b80ad614b824`；`final-v2` 为 `87112509fc93378290b3797beb14b7b122ea0852e596ea8346278ca412e08777`。

对归档 `before-sources.zip` 与当前做只读逐行比较，唯一正文差异是当前新增第 2–3 行模型和推理强度，`developer_instructions` 完全一致。历史三个 `final-isolated/review_prompt_{read_only,compare,revise}/run.json` 实际模型均为 `gpt-6.1-sol`，加载 hash 均为旧值。因此：

- 可复用为同指令正文的只读、候选比较、授权修订与回执边界证据。
- 不支持“现行 astra/high 配置行为通过”。
- 建议将现行配置的独立调用、授权写入和缺证回执标为证据不足；后续若授权行为取证，复用原三类最小隔离工单即可。真实退款行为仍不在原夹具覆盖内。

**六个遗留入口**

`source/project/.agents/skills/` 中 `sdd-commit`、`sdd-deploy`、`sdd-doc`、`sdd-spec`、`sdd-review-code`、`sdd-review-prompt` 均无任何实际文件，仅有空目录或空 `agents/`、`references/` 子目录。无 `SKILL.md`、元数据或可加载提示词。`rg --files` 只列六个当前分发 Skill。

结论：未构成实际遗留入口或当前执行歧义，不应将空目录误报为仍分发旧 Skill。清理属于可选工作区整洁事项，本轮不修复。
