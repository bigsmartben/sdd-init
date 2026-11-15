# 订单号校验实施计划

A、B 已确认；T001 实施和局部自验完成。全空白编号已按空字符串拒绝；合法原值与非字符串处理保持，AC-4、AC-5、AC-1 及现有单测通过。技能 Agent 点对点验收通过，见[验收报告](../../docs/test-reports/order/validation.md)。

## 依据、范围与授权

原需求及 A 来源见 [Spec](spec.md#确认与授权)，通过判据为该文档 AC-4、AC-5，验收责任、前提、数据、步骤及判据见[验收方案](quickstart.md#本轮订单号校验验收)。函数及异常语义见[契约](../../docs/contracts/order.md)。

本轮只收紧新建订单号校验，保留合法编号原值、函数接口、既有非字符串处理及其他订单行为。适用[蓝图](../../docs/blueprint.md) ARC-1（服务写入入口）、ARC-2（文件 SQLite 与 commit）、ARC-3（验证资产只调用正式模块）、ARC-4（无网络）。不更改状态流转、UI、存储结构或架构，不处理历史独立偏差。

用户已确认 B，授权当前隔离项目的产品与测试代码、本计划及临时 SQLite 验证。临时目录以 TMPDIR 指向获授权 scratch；禁止修改原仓和工作流，不包含 Git 写入、外部平台、发布、部署及外部服务。

实施前只读源码调查：`src/order_service.py` 的 `create_order` 当时仅通过字符串类型和真值拒绝输入，随后 INSERT/commit，故全空白字符串可通过。`tests/test_order.py` 尚无编号校验覆盖。以上为实施前静态事实。技能 Agent 完成方案准备后交独立 sdd-coder 接续本计划，不另建副本。

## Task

### T001: 拒绝全空白订单号并保留合法订单行为

- 依据：Spec AC-4、AC-5 及上文验收方案；保持 AC-1 和 mark_paid 可观察结果。
- 文件归属：实施执行者负责 `src/order_service.py` 中 `create_order`、`tests/test_order.py` 的输入校验测试、`checks/acceptance.py` 的 AC-4/AC-5 验收分支与场景入口；实施执行者同时维护本计划 T001 及实际实施状态；技能 Agent 负责 Spec、Quickstart、契约与点对点验收报告。所有执行者保留其他人的修改，不触碰范围外逻辑。
- 方案：在现有类型检查短路之后，用字符串的 `strip()` 结果判断是否包含非空白字符；仍使用原始 `order_id` 插入，不把裁剪值赋回编号。保留现有 ValueError 类型、消息和 INSERT/commit。输入拒绝必须发生在数据库写操作之前。该调整承接已有服务边界，不需要新增依赖或表结构。
- 测试与验收入口：按验收方案补齐拒绝、合法原值、类型保持、当前连接及文件重开检查；验收入口输出逐输入结果，任何不满足均返回失败。增加 AC-4/AC-5 场景选项及默认运行覆盖，保留既有场景语义和退出码。
- 依赖：无其他 Task；B 确认及交办授权已满足。
- 完成条件与局部自验：定向单元测试覆盖全部输入类别，AC-4、AC-5、AC-1 检查通过，现有单元测试通过；错误输入不执行新增写入，合法编号精确保存。保留取消提交、UI 和外部配置现状。执行者回传实际改动、版本、命令及逐项结果；技能 Agent 再按同一验收方案逐 AC 验收，可复用仍适用的局部证据。
- 状态：完成（实施与局部自验）；技能 Agent 点对点验收通过，见[验收报告](../../docs/test-reports/order/validation.md)。
- 实际改动：`create_order` 在 INSERT 前用 `not order_id.strip()` 拒绝全空白，INSERT 保留原始值；新增 3 个输入类别单测，验收入口新增 AC-4/AC-5 的逐输入结果、当前行与重开行比较，默认入口覆盖 AC-1 至 AC-5。
- 结果与证据：见下文局部自验。现有取消提交及 UI 写入边界的历史偏差已交 Main，不作为本 Task 修复要求；本轮没有确认其恢复，也没有架构 Review 结论。

### 局部自验版本与执行证据

执行日期 2026-11-14，隔离项目根目录；Python 3.12.3、SQLite 3.45.1，标准库，无网络。Git 基线只读识别为 `83a8ad12ca4c60ba9bcaf37ec891db0e6a35c046`，未提交的实际执行版本由以下 SHA-256 标识：

| 文件 | SHA-256 |
|---|---|
| `src/order_service.py` | `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b` |
| `tests/test_order.py` | `be2169dc8e58cfea45a484c2beb562fcf1a64f75b6f51496cdf1577482f6d5ec` |
| `checks/acceptance.py` | `810313fa38ad965777d9d655750d46432d5616286367dae05a8c3569b9103f1d` |

所有写库命令均以前缀 `TMPDIR=/tmp/sdd-review-execution-ykzxy2w_/develop_delivery-zwof9g4j/scratch` 执行。每个输入独立文件库，基准为唯一 `BASELINE/pending` 行，当前连接和关闭重开均核对全表；临时库在执行后清理。

| 命令（省略上述 TMPDIR 前缀） | 实测与退出码 |
|---|---|
| `python -B -m unittest discover -s tests -v`（实现前、补测试后） | 退出 1；5 个测试中 7 个全空白子输入失败，均为 `ValueError not raised`。空字符串、合法原值、非字符串与原有回归通过，证明测试捕获本次缺口。 |
| `python -B -m unittest discover -s tests -v`（实现后） | 退出 0，5/5 测试通过；新测试覆盖 16 个输入，含重开检查；原有 submit 与 mark_paid 均通过。 |
| `python -B checks/acceptance.py --scenario AC-4` | 退出 0，8/8 输入 PASS。 |
| `python -B checks/acceptance.py --scenario AC-5` | 退出 0，8/8 输入 PASS。 |
| `python -B checks/acceptance.py --scenario AC-1` | 退出 0，提交返回 true，重开后 submitted，PASS。 |
| `python -B checks/acceptance.py` | 退出 1；顺序为 AC-1 PASS、AC-2 FAIL、AC-3 BLOCKED、AC-4 PASS、AC-5 PASS。确认新增编号加入默认入口并保留既有退出码优先级。AC-2 实际 true/submitted 与预期 false/cancelled 不符，属于已知历史偏差；AC-3 无端点或权限，未访问网络。 |
| `python -B checks/runtime_details.py` | 退出 0，取得上述运行环境与源哈希；runtime 外部端点 null、授权 false、网络 false。 |
| `git diff --check` | 退出 0，无空白错误。 |

逐输入原始 JSON 位于获授权 scratch：`/tmp/sdd-review-execution-ykzxy2w_/develop_delivery-zwof9g4j/scratch/coder-AC-4.json`、`coder-AC-5.json`、`coder-AC-1.json`、`coder-all.json`。本计划保留可复跑命令与结果，正式点对点验收报告由技能 Agent 维护于 [验收报告](../../docs/test-reports/order/validation.md)，已回收通过。

| 判据 | 已实测输入（转义形式） | 逐输入结果与观察 |
|---|---|---|
| AC-4 | `""`、`" "`、`"   "`、`"\t"`、`"\n"`、`" \t\r\n "`、`"\u3000"`、`"\u00a0"` | 每个均 PASS：ValueError，消息精确为 `order_id is required`；当前及重开全表均为原基准行。 |
| AC-5 合法 | `"ORDER-1"`、`" ORDER-1 "`、`"\tORDER-1\n"` | 每个均 PASS：当前及重开均恰好多出原输入的 pending 行，基准未变；含首尾空白的两项均无裁剪替代行。 |
| AC-5 类型 | `None`、`0`、`False`、`[]`、`{}` | 每个均 PASS：异常类型、消息及当前/重开全表不变均满足 AC-4 同一判据。 |

## 交付核对与恢复条件

T001 已覆盖本轮需求及直接回归，无本轮未解决失败或实施阻塞。技能 Agent 已按同一验收方案独立复跑 AC-4、AC-5、AC-1 和现有单测，18 个本轮验收案例通过；mark_paid 保持证据已回收，详见上述验收报告。历史 AC-2、UI 写入边界未修复，AC-3 未执行外部调用；本轮局部通过不代表全产品通过。本轮不触发其他技能阶段或 Git／外部操作。
