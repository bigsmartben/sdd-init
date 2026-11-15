# 白皮书与 Review 分工维护验证

日期：2026-11-14（Asia/Shanghai）。本批次是已确认分工的文档与 Skill 维护，不是用户显式启动的真实全量工作流评审。本轮未安装、发布、推送或修改安装器。

## 版本与范围

等待前一任务 `01a1da3f-d425-7de2-93c4-71c5acc1a6ae` 的轮次 `01a1da50-b4d9-7e51-874f-4a51ca20cabf` 完成后才写入；以当时工作区（包含已有未提交改动）为基线。既有修改保留。本轮改动范围及字节核对结果见[验证数据](evidence/2026-11-14-artifact-division/validation.json)。

原白皮书 SHA-256：`d277c42ba0914ff2d60c66541850bb69aa1a51e8bfa7121494e036e8b696af8c`；[原文快照](evidence/2026-11-14-artifact-division/whitepaper-before.txt)保留迁移前判据、成本口径与版本摘要。迁出的摘要见[历史附录](2026-11-14-whitepaper-assessment-archive.md)，它不覆盖原报告后续补齐的发现和矩阵。

适用依据为本轮确认的产物分工，以及更新后的 Spec FR-033／AC-033、FR-034／AC-034。具体产物见[Skill](../../../.agents/skills/sdd-workflow-review/SKILL.md)、[白皮书](../../sdd-workflow-whitepaper.md)、[白皮书模板](../../../.agents/skills/sdd-workflow-review/assets/whitepaper-template.md)、[报告模板](../../../.agents/skills/sdd-workflow-review/assets/review-report-template.md)。

## 静态与维护验证

| 检查 | 结果与证据 | 限制 |
| --- | --- | --- |
| 判据和设计迁移 | 对迁移前快照逐行比较：36 个 RW 子项、S1～S8 和 I1～I3 共 11 条设计表格行原文一致；RW-09～RW-12 补充 Spec 追溯 | 编号与字节检查不替代语义判断 |
| 产物归属与一致性 | 白皮书保留设计，判据与成本规则归 Skill 参考文件，版本摘要归历史附录；Spec 编号沿用，README、索引与蓝图同步 | 没有裁定原版本发现已修复 |
| 流程与显式边界 | 核对普通维护不启动；审查不授权修复；可沿用有效修复授权；设计变化须有决定；修复后沿原判据复验关联路径；保留失败和未验；openai.yaml 的显式策略未改 | 本轮为语义检查，未重跑模型自动选择或修复行为 |
| 报告表达能力 | 模板分列逐对象、逐 RW 子项、静态／行为证据、发现和修复复验链、未验与接续；体积、加载、运行 token 与两类任务时长分开 | 表格完整不等于实际覆盖完成 |
| 历史保护 | 基线中的 83 个既有报告及证据文件 SHA-256 均不变；另存原白皮书全文 | 历史结论仍按原版本解释 |
| Skill 验证器 | `python -B -X utf8 C:/Users/24598/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/sdd-workflow-review`：通过 | 首次默认 GBK 解码失败；指定 UTF-8 后通过，未改变验证器 |
| 文档机械检查 | doc_check 检查本轮 Markdown 与直接引用，0 错误、0 警告 | 只证明所支持的链接、编码及结构 |
| 准备器回归 | `python -B -m unittest discover -s tests -p test_skill_behavior.py -v`：5 项通过 | 仅验证隔离准备器，非模型行为 |

语义核对还确认：通用 review-prompt 仅提供提示词专项证据，整体覆盖与结论归 Skill；白皮书只读引用不妨碍取得新决定后更新设计。FR-028 的通用角色职责、FR-031 的调度边界与本轮分工一致。未修改目标项目分发规则或安装实现。

## 隔离模板与报告落点试填

通过现有准备器生成 `workflow_review_explicit` 和 `workflow_review_not_requested` 两个临时项目，未调用模型。候选 Skill 的模板和参考文件随隔离副本读取；夹具白皮书与合成判据分离，显式案例工单指定缩小矩阵，不误认真实工作流全覆盖。

在显式夹具运行 `checks/load_guidance.py`，退出 0，输出见[装配记录](evidence/2026-11-14-artifact-division/fixture-loading.txt)。该脚本只读取提示词，不执行待办业务行为。随后把报告模板实例化到 `docs/test-reports/sdd-workflow/template-smoke.md`，白皮书模板实例化到 `docs/whitepaper-template-smoke.md`，按实际落点重定向相对链接。两份实例 doc_check 均为 0 错误、0 警告；15 个原有夹具文件哈希不变。临时目录见验证数据。

实际白皮书本身是白皮书模板的完整实例。报告试填用于核对结构与输出路径，未填充的实测数据保持未测，不作为正式 Review 交付。只审查／获授权修复／复验失败／缺证四种情形均可在模板中分别记录，不要求覆盖原始记录。

## 失败、修正与未验范围

初次文档检查发现迁移附录中沿用的旧锚点不存在、夹具 Spec 相对路径多一层，以及两个标题层级警告。修正路径、标题层级，并在附录显式说明旧锚点缺失，再运行检查通过。原始历史报告未改写。

本轮未执行真实全量评审、模型触发选择、提示词角色调用、真实多阶段修复复验或性能比较；前一任务已有模型验证不能当作本次候选版本的行为通过。review 与 testcase 的模型 token、实际加载 token、运行成本及可比节省比例均未测。本轮局部命令时间不是被评估工作流的质量成本数据。

若后续显式启动全面评审，应固定新的源码与判据快照，按报告模板展开完整对象与 36 个子项，并在获相应授权的隔离环境采集行为及成本证据。
