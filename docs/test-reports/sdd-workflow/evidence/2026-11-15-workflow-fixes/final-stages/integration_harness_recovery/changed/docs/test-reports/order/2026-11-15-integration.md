# Test Report — 订单集成回归 2026-11-15

## 1. 目标与依据

批次：2026-11-15-integration；类型：完整功能集成回归；执行者 `/root/integration_test`，实际调用者 Main `/root`。工具修正由独立专业角色 `/root/integration_test/test_tools` 完成，本执行者在修正后独立执行两次。实测 UTC 时间以[证据时间戳](evidence/ci-reruns.json)为准（本地时区 Asia/Shanghai 为 2026-11-15）。

依据：[Spec](../../../specs/order/spec.md)、[契约](../../contracts/order.md)、[本轮指南](../../../specs/order/quickstart.md)。目标是在冻结产品实现的当前隔离环境，覆盖提交、取消、支付和真实外部回执路径，确认给定 CI 入口可复跑。

## 2. 范围、计划与确认

沿用用户经 Main 交办的明确确认：仅当前隔离项目，目标为当前 HEAD 加实际工作区，环境为当前隔离订单环境，主要路径为提交、取消、支付、外部回执；允许修正测试工具、补测和写文档，产品冻结，禁止外网、外部平台和真实部署。不存在待确认的本地业务判据。

覆盖 AC-1/2/3、paid 保持与适用输入、缺失订单、数据库异常契约。常规空串、None、整数及关闭连接由既有契约推导，不增加业务含义。无并发、性能指标、UI 或人工视觉要求，不进行架构符合性 Review。完成标准是逐项完整留证；只有所有适用项满足、证据齐备才可 PASS。

## 3. 实际版本与环境

- 产品版本 `67e0283f880b4995f5df4d58f2c2b6a3ca8b2003`，分支 main；初始工作区干净。运行时 `git diff HEAD -- src runtime.json` 输出为空，产品源文件未改。
- 测试资产包含未提交修正 `checks/integration_runner.py` 和 `checks/acceptance.py`，不能只用 HEAD 标识复跑版本；各文件 SHA256、完整命令和工作目录见[实测清单](evidence/ci-reruns.json)。文档更新不影响被测产品。
- Python 3.12.3，SQLite 3.45.1；[环境事实](evidence/preparation.json)来自实际命令；[runtime.json](../../../runtime.json) 为 isolated-local-fixture，外部端点 null、调用授权 false、网络 false。
- 真实组件：src 正式服务、UI 库适配函数和标准 SQLite 文件数据库；通过公开函数组合执行。无外部替身、无外部真实回执证据；本地成功不能证明 AC-3。

## 4. 准备与数据

每个本地场景使用新临时目录文件数据库，订单 ORDER-1；整数边界使用合法字符串订单 "42"，再传非法整数 42。记录操作前、中间步骤及关闭重开后的状态；上下文结束关闭连接并删除临时目录，两次全量运行互不共享数据库。数据恢复由测试工具自动执行，无需改产品或配置。

准备缺口仅 AC-3：真实端点、权限、联网条件均不具备。本轮不尝试获取凭据或配置外部服务。恢复需要有权人员提供真实环境及授权并另外允许真实调用；本地运行器不会访问网络，不能单靠填配置完成该 AC。

## 5. 执行与覆盖统计

1. 原 CI 入口因拼写 `run_acceptence` 引发 NameError，退出1，没有业务场景结果。保留[工具执行者原始回执](evidence/runner-initial-failure.json)。本轮授权内只修正入口和补充测试，不改变断言标准或 src。
2. 独立初步验收 AC-1 PASS、AC-2 FAIL、AC-3 BLOCKED；现有2个单元测试 PASS；见[准备执行记录](evidence/preparation.json)。单元测试未覆盖取消保护，不能代替全量结果。
3. 修正后从项目根两次执行 `python -B checks/integration_runner.py`，均正常输出28项JSON，退出1；业务结果稳定一致。该退出码表示存在已证实业务失败，入口已恢复可复跑。

计数按场景每批只计一次：总28，PASS19，FAIL8，Not run0，BLOCKED1；第二次为复跑证据，不计为56项。通过率19/28；本地可执行27项全部执行。功能覆盖：AC-1、AC-2、AC-3均建立结果，paid 场景及契约边界全覆盖；AC-3仅环境阻塞判断，真实业务回执尚未验证。未以覆盖映射代替通过。

## 6. 逐项结果

下表命令均为 `python -B checks/acceptance.py` 加所列参数；实际批次使用全量 CI 连续两次覆盖每项。两次产品/工具文件相同，以[SHA256](evidence/ci-reruns.json)关联版本。具体输入、中间态、错误原文、重开状态均见同一JSON的两次 `runs[].results`。

| 场景 / 判据 | 前置 / 数据 | 操作 | 预期 | 实际 | 结论 | 证据 / 版本 | Issue |
|---|---|---|---|---|---|---|---|
| AC-1 / Spec AC-1 | 指南对应场景，独立临时库 | `--scenario AC-1`；全量两次 | true；重开 submitted | accepted=true；重开 submitted | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| AC-2 / Spec AC-2 | 指南对应场景，独立临时库 | `--scenario AC-2`；全量两次 | false；重开 cancelled | accepted=true；重开 submitted | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-001](../../issues/ORDER-001.md) |
| AC-3 / Spec AC-3 | 指南对应场景，独立临时库 | `--scenario AC-3`；全量两次 | 真实授权外部服务回执 | 未配置端点、未授权、无网络；未调用外部服务 | BLOCKED | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| PAY-1 / Spec paid / 契约 | 指南对应场景，独立临时库 | `--scenario PAY-1`；全量两次 | 提交后 paid 持久化 | accepted=true；重开 paid | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| PAY-2 / 订单契约 | 指南对应场景，独立临时库 | `--scenario PAY-2`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-002](../../issues/ORDER-002.md) |
| ID-create-empty / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-create-empty`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-create-none / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-create-none`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-create-integer / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-create-integer`；全量两次 | ValueError；原数据保持 | ValueError；重开 {"42": "pending"} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-submit-empty / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-submit-empty`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-submit-none / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-submit-none`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-submit-integer / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-submit-integer`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {"42": "submitted"} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-003](../../issues/ORDER-003.md) |
| ID-cancel-empty / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-cancel-empty`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-cancel-none / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-cancel-none`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-cancel-integer / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-cancel-integer`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {"42": "cancelled"} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-003](../../issues/ORDER-003.md) |
| ID-set_status-empty / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-set_status-empty`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-set_status-none / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-set_status-none`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| ID-set_status-integer / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-set_status-integer`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {"42": "paid"} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-003](../../issues/ORDER-003.md) |
| ID-mark_paid-empty / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-mark_paid-empty`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-002](../../issues/ORDER-002.md) |
| ID-mark_paid-none / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-mark_paid-none`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-002](../../issues/ORDER-002.md) |
| ID-mark_paid-integer / 订单契约 | 指南对应场景，独立临时库 | `--scenario ID-mark_paid-integer`；全量两次 | ValueError；原数据保持 | 未抛异常；重开 {"42": "paid"} | FAIL | [两次逐项证据](evidence/ci-reruns.json) | [ORDER-002](../../issues/ORDER-002.md) |
| MISSING-submit / 订单契约 | 指南对应场景，独立临时库 | `--scenario MISSING-submit`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| MISSING-cancel / 订单契约 | 指南对应场景，独立临时库 | `--scenario MISSING-cancel`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| MISSING-set_status / 订单契约 | 指南对应场景，独立临时库 | `--scenario MISSING-set_status`；全量两次 | ValueError；原数据保持 | ValueError；重开 {} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| DB-create / 订单契约 | 指南对应场景，独立临时库 | `--scenario DB-create`；全量两次 | sqlite3.Error；原 pending 持久化 | ProgrammingError；重开 {"ORDER-1": "pending"} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| DB-submit / 订单契约 | 指南对应场景，独立临时库 | `--scenario DB-submit`；全量两次 | sqlite3.Error；原 pending 持久化 | ProgrammingError；重开 {"ORDER-1": "pending"} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| DB-cancel / 订单契约 | 指南对应场景，独立临时库 | `--scenario DB-cancel`；全量两次 | sqlite3.Error；原 pending 持久化 | ProgrammingError；重开 {"ORDER-1": "pending"} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| DB-set_status / 订单契约 | 指南对应场景，独立临时库 | `--scenario DB-set_status`；全量两次 | sqlite3.Error；原 pending 持久化 | ProgrammingError；重开 {"ORDER-1": "pending"} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |
| DB-mark_paid / 订单契约 | 指南对应场景，独立临时库 | `--scenario DB-mark_paid`；全量两次 | sqlite3.Error；原 pending 持久化 | ProgrammingError；重开 {"ORDER-1": "pending"} | PASS | [两次逐项证据](evidence/ci-reruns.json) | 无 |

## 7. 问题及影响

| Issue | 关联场景 | 影响 |
|---|---|---|
| [ORDER-001](../../issues/ORDER-001.md) | AC-2 | 取消状态被提交覆盖，违反明确 AC |
| [ORDER-002](../../issues/ORDER-002.md) | PAY-2、ID-mark_paid 三项 | 缺失/非法ID未抛错，整数还误写已有订单 |
| [ORDER-003](../../issues/ORDER-003.md) | ID-submit/cancel/set_status 的 integer 项 | 非法整数误改合法字符串订单 |

上述均为实测产品偏差，产品冻结下仅登记，不归因或修复。原入口 NameError 为已修正的测试侧问题，保留失败与修正后两次结果。AC-3 环境缺口为 BLOCKED，未当作产品缺陷。

## 8. 结论、人工反馈与 Gate

**Test Gate：FAIL。** 适用当前产品基线及所列测试资产、isolated-local-fixture。给定 CI 入口已恢复且可稳定复跑；8项业务失败和1项外部阻塞阻止整体通过。不存在未执行且仍可在当前授权下执行的既定场景。

人工确认：该无UI本地产品没有必需的人工视觉/体验验收；没有把自动结果记成人工反馈。用户授权来自 Main 交办，未另取人工业务验收意见。外部路径需真实服务证据，不以模拟或人工推测替代。

接续：Main 按另行授权安排上述产品缺陷处理，将明确修复版本及影响范围回交原 Agent `/root/integration_test`，复验同编号及完整回归；AC-3 另需真实端点、权限、网络及真实验收入口。文档写后检查范围为本轮修改的7个Markdown（指南、索引、状态、报告及3个Issue），`doc_check.py --root .` 返回0错误0警告；`git diff --check` 通过。语义核对确认：判据来自原Spec/契约，8项失败归3个产品Issue，外部阻塞与本地失败分别保留，入口恢复与Gate明确区分，链接和稳定ID一致；未验证远程服务或架构符合性。机械检查不证明业务通过，执行回执见[最终检查](evidence/final-validation.json)。本轮不提交、不部署、不修改产品或共享规则。[状态入口](../../status.md)。
