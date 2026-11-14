# Test Report — 订单缺陷定向复验

## 1. 目标、依据与执行者

本批仅恢复 [ORDER-001](../../issues/ORDER-001.md) 与 [ORDER-002](../../issues/ORDER-002.md) 的原契约，依据原 Issue 验收计划与方案；不代替全产品集成 Gate。实施与局部自验执行者 `/root/order_bugfix/implement`，定向复验执行者 `/root/order_bugfix`。接口与数据依据 [订单契约](../../contracts/order.md)，实施方案归 [同一 Plan](../../plans/order-bugfix.md)。

## 2. 实际版本与环境

HEAD `fc366da8aff900abc000129676514d994ca5c671` 加未提交产品修复，实际运行 Python 3.12.3 / SQLite 3.45.1，本地真实临时文件 SQLite；无外部调用。完整产品和测试入口指纹见 [局部版本](evidence/bugfix-local-version.json)，复验前核对一致见 [定向原始证据](evidence/bugfix-retest.json)。

| 产品文件 | SHA256 |
|---|---|
| src/order_service.py | 3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb |
| src/ui.py | 4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909 |

## 3. 归因与修复

ORDER-001：提交函数无条件写 submitted，与首轮取消后 true/submitted 相符；修复为读到 cancelled 立即 false。ORDER-002：UI 直接 UPDATE 缺失行后正常返回，与首轮 O-14 exception=null 相符；改用既有服务 set_status 恢复存在性检查和唯一业务写入口。签名、现存订单付款持久化、返回 None、错误向上传播及无网络行为保持。原始失败分别保留于 [首轮 CLI](evidence/initial-acceptance.json) 和 [首轮补充](evidence/initial-regression.json)。

## 4. 逐项证据与结果

| 范围 | 操作与观察 / 通过判据 | 实际结果 | 证据 |
|---|---|---|---|
| ORDER-001 原场景 AC-2 | 新建、取消、提交、关闭重开，false/cancelled | PASS，false/cancelled | [Skill 原场景复验](evidence/bugfix-retest.json) |
| 取消不写入 | 相同公开调用，SQLite trace 仅 SELECT，无 UPDATE/COMMIT，不开启事务 | PASS，仅 SELECT；重开 cancelled | [Skill trace](evidence/bugfix-retest.json) |
| ORDER-002 原场景 O-14 | 缺失对象 mark_paid 抛 ValueError，原有行与重开数据不变 | PASS，ValueError，pending 行不变 | [Skill 原场景复验](evidence/bugfix-retest.json) |
| 付款返回与持久化 | cancelled 的现有订单付款，返回 None，关闭重开 paid | PASS | [Skill 保持检查](evidence/bugfix-retest.json) |
| 正常提交 AC-1 | pending 提交为 true/submitted，关闭重开 | PASS | [局部 CLI](evidence/bugfix-local-ac1.json) |
| O-07～O-20 必要回归 | 原运行器 14 项：付款三种状态、缺失对象、真实 query_only 错误与 commit 读锁错误传播 | 14 PASS | [局部回归](evidence/bugfix-local-regression.json) |
| 既有局部单测 | 正常提交、付款持久化 | 2 PASS | [单测](evidence/bugfix-local-unittest.json) |

局部回归与定向复验产品指纹一致，判据及真实文件数据库环境匹配，可复用必要回归证据。SQL trace 是公开取消提交场景的补充观测，不替代文件数据库关闭重开结果。数据均为临时目录，连接关闭后清理；测试资产未修改。

## 5. 结论与后续

两个原 Issue 均有原故障恢复与必要回归证据，按本轮状态写入授权关闭。本批定向复验 PASS；无人工视觉或体验反馈项。原测试 Agent 已在相同冻结快照完成[独立全产品集成复验](retest.md)：23 场景 22 PASS、0 FAIL、1 BLOCKED（仅 AC-3），另 2 单测 PASS；[前后指纹](evidence/retest-version-after.json) 证实产品及验证资产未变。两个原 Issue 保持关闭，新增独立关闭依据已归并原记录。相关架构检查由 Main 另行组织。AC-3 不在本地修复目标内，仍因缺真实外部端点、调用权限、网络及真实协议/回执判据阻塞，不能以本批结果替代。
