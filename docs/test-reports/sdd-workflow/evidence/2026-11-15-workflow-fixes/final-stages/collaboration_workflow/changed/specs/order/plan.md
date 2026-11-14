# Plan — 订单现行缺陷恢复

## 1. 目标与依据

依据 [TASK](../../TASK.txt)、[Spec](spec.md)、[接口契约](../../docs/contracts/order.md) 与原 [ORDER-001](../../docs/issues/ORDER-001.md)、[ORDER-002](../../docs/issues/ORDER-002.md)。恢复取消保护和 missing mark_paid 的 ValueError，保持签名、paid 持久化和非 cancelled 提交既有语义。

Main `/root` 授权独立 Bugfix Agent `/root/order_bugfix` 组织修复；仅本地 Python、文件 SQLite，不访问外部平台、网络，不改配置或 Git。初始提交 `89df9f629407a6b572c6f65c87fc9768e0f52f5d`，独立 [归因证据](../../docs/test-reports/order/evidence/bugfix-diagnosis.json) 保存初始源码哈希、SQL 和结果。已验证直接因果：submit 丢弃读取的状态，随后无条件写 submitted；UI 绕过服务，UPDATE 未找到行仍 commit。

## 2. Task 清单

### T001: 恢复取消保护与 paid 入口契约

- 依据：原 Issue 的点对点判据及上述归因；ARC-1/CR-001 已确认服务负责状态写入，见 [原架构初审 CHK-001/005](../../docs/test-reports/order/architecture-review.md)。
- 范围：仅 `src/order_service.py`、`src/ui.py`、必要 `tests/test_order.py`；不得修改冻结的 `checks/order_integration.py` 或现有验收预期。
- 实施方案：`src/order_service.py` 提交读取 cancelled 时直接 false，不写入/commit；其余已有路径保持。`src/ui.py` 的 mark_paid 委托现有 `order_service.set_status(..., "paid")`，继承 missing 和数据库异常语义。已核对归因，无反证；未引入接口或新状态规则。
- 依赖：无；两个产品模块及回归测试由同一 coder 串行维护。
- 验收计划：真实临时文件 SQLite，原 create→cancel→submit 应 false、立即及重开为 cancelled、无 UPDATE/commit；pending 提交 true 且重开 submitted；missing mark_paid 为 ValueError 且无写入/commit；现存 paid 重开保持、其他订单不变；missing read/cancel/submit/set_status、关闭连接异常仍上抛。局部单测后由 Bugfix Agent 定向复验，整轮集成和架构复核由 Main 另行接续原独立执行者。
- 状态：Complete（实施与局部自验）；Bugfix 独立定向复验已通过；跨阶段检查另行执行。
- 结果及证据：2026-11-15，基础 HEAD `89df9f629407a6b572c6f65c87fc9768e0f52f5d` 加本地工作区改动；`python -B -m unittest discover -s tests -v` 共 8 项通过。新增单测修复前 3 处失败见 [red](../../docs/test-reports/order/evidence/bugfix-coder-red.json)，同一批修复后全通过见 [green](../../docs/test-reports/order/evidence/bugfix-coder-green.json)。覆盖取消无写入/commit、关闭重开 cancelled、正常及 paid/submitted 再提交、paid 关闭重开、missing 各入口无写入/commit、真实 SQLite 写入/commit 故障上抛、关闭连接异常及订单隔离。
- 实际源码 SHA-256：`src/order_service.py` 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；`src/ui.py` 为 `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`。完整 src、单测及冻结集成脚本哈希见 green；冻结集成脚本保持 `496fa99f09e2c5d0796678ac580ffa49553e155f266a68673b68e58e93e1bc99`。
- 待验：Bugfix Agent 已沿原 ORDER-001/002 完成独立定向复验 17/17 PASS（[原始证据](../../docs/test-reports/order/evidence/bugfix-retest.json)、[报告](../../docs/test-reports/order/bugfix.md)）；Main 接续原集成执行者跑既有验收入口并交原架构执行者复核 CHK-001/005 及受影响项。局部证据不代替独立结果；AC-3 与 CHK-006 仍保持原边界。
- 写后核对：已读回对照原 Issue、契约、diff 与上述实测覆盖；状态仅表示本 Task 的实施和局部自验完成。Plan 文档机械检查为 1 文件、0 errors、0 warnings，`git diff --check` 通过，原始输出见 [检查证据](../../docs/test-reports/order/evidence/bugfix-coder-checks.json)。

## 3. 交付检查

完成条件是 T001 实施和局部自验通过、Bugfix 原场景及必要回归通过。Issue 采用“已修复，待独立集成复验”，不以本阶段结果替代整轮 Test Gate。AC-3 的外部端点与权限阻塞不属本次修复；CHK-006 映射缺口仍由 Main 协调，不更新 Code Review Rules。最终报告落点为 [Bugfix 报告](../../docs/test-reports/order/bugfix.md)。
