---
name: sdd-doc
description: 将已确认对话结论和执行证据归并到对应文档，完成写入一致性检查；纯讨论不触发。
---

# 对话结论落盘

输入：已确认结论或真实执行证据、授权写入范围。按需归并上游工单提供或集成验收时准备的验收文档，按原判据和实际覆盖更新 Issue 状态。用户要求记录 Technical Research and Selection Report 时，按对应对象行归并调研材料、证据和确认状态。新建或需定位正文时查[文档与产物落点](../../sdd/references/sdd-repository-governance.md#文档与产物落点)。

按[权威实体](../../sdd/references/sdd-repository-governance.md#权威实体)定位正文，执行[文档写入规则](../../sdd/references/document-writing.md)的通用步骤及输出要求；只读取[本轮对象](../../sdd/references/document-writing.md#按对象读取与语义核对)对应行和语义影响涉及的上游、模板。

在项目根目录使用以下命令取得所需片段。示例为 documenter 交接 Test Report，按实际对象替换表格首列名称，直接写入任务省略交接片段。

```powershell
python -B -X utf8 .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root .agents/skills/sdd-workflow --read 'sdd/references/sdd-repository-governance.md#权威实体' 'sdd/references/document-writing.md#文档写入规则' 'sdd/references/document-writing.md#按对象读取与语义核对:Test Report' 'sdd/references/delegation.md#最小交接:documenter'
```

共享规则按同一方式取用相应锚点。写后用同一脚本以项目根目录为 `--root`，传入修改及直接受影响的 Markdown。

用户明确要求生成或更新 Code Review Rules 时，读取[目标仓库的 Code Review Rules](../../sdd/references/sdd-repository-governance.md#目标仓库的-code-review-rules)的决策边界，并按默认落点或项目映射定位正文。依据已确认的 Blueprint、契约与实际运行路径选用[架构规范](../../sdd/references/architecture-rules.md)中的适用约束，按[Code Review Rules](../../sdd/assets/code-review-rules_template.md)写成针对本项目入口和职责的可检查规则。同义规则原位归并，保留稳定标识；逐项核对受影响条款，明确撤销的约束从现行规则中移除。缺乏设计依据的归属或冲突列为待决。仅维护规则内容，执行证据归 Review。

角色交接只读取[最小交接](../../sdd/references/delegation.md#最小交接)的共同要求及相关角色行；决定执行者或独立性时再读取[执行协作](../../sdd/references/delegation.md)的对应规则。普通写入不加载实施、验收或交付流程。

例：正文已有“在线请求超时 5 秒，离线任务不受此限”，对话确认在线超时改为 10 秒。原位更新为 10 秒，保留离线例外，同步引用该限制的关联条款，不追加第二份规则。
