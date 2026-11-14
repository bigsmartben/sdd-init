# BUG-001 归因与修复定向复验

## 范围与依据

执行者：Bugfix 技能 Agent `/root/bugfix`，2026-11-15；实施与局部自验：`/root/bugfix/coder`。按 [BUG-001 验收计划与方案](../../issues/BUG-001.md) 对原场景及必要回归取证；[实施任务](../../issues/BUG-001-plan.md) 维护局部检查。此报告不判定整产品 Test Gate 或架构 Review。

环境为本地隔离项目、Python 3.12.3、SQLite 3.45.1，每个场景使用真实临时文件 SQLite，关闭重开确认持久化，临时目录在退出时删除。无网络调用，无模拟数据库，无人工体验判断要求。源文件标识取 SHA-256，不执行 Git 操作。

## 批次 D1：修复前归因

- 实际版本见 [初始 runtime](bugfix-initial-runtime.json)，service 哈希 `96844b5faba169a28c5f4cfb877a9644b83e81f0e63f5b726de525294a69f6de`。
- 命令 `python -B checks/acceptance.py --scenario AC-2` 退出 1；[失败结果](bugfix-diagnosis.json)：accepted=true，persisted_status=submitted。
- 候选根因是 `submit_order` 无条件覆盖状态。观测预测：调用路径读到 cancelled 后仍调用 submitted 写入；如果状态判断已阻止写入，则该归因应被排除。核对源代码实际读取后忽略状态，无条件 `set_status`，而文件库重开仍 submitted，故根因成立。不是临时内存状态或仅返回值错误。
- 结果：1 项 Fail，事实保留；新增回归先失败、再修复的局部证据归原 Plan。

## 批次 R1：修复版本定向复验

实际候选见 [src/checks/runtime manifest](bugfix-candidate.json)，标识 `sha256:7d4083da88ed6593bc2039b890b0026681f522ac7b53d7aa8c8dcde4cb269fea`；运行环境见 [修复 runtime 与完整源文件哈希](bugfix-fixed-runtime.json)。service SHA-256 为 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；其他 src 文件哈希与 D1 一致。仅产品 service 的 cancelled 分支新增 false 返回，函数签名保持。

| 检查 | 实际步骤及结果 | 判定与证据 |
| --- | --- | --- |
| 原场景 AC-2 | `python -B checks/acceptance.py --scenario AC-2`，退出 0；false，重开后 cancelled | Pass；[JSON](bugfix-retest-ac2.json) |
| 必要回归 AC-1 | `python -B checks/acceptance.py --scenario AC-1`，退出 0；true，重开后 submitted | Pass；[JSON](bugfix-retest-ac1.json) |
| 拒绝写入、正常路径、paid、缺失订单 | `python -B -m unittest discover -s tests -p test_order.py -v`，退出 0；4 tests / OK。核对测试断言包括 SQL 跟踪仅 SELECT、total_changes 不变、重开文件库、submit 缺失订单 ValueError | Pass；[原始输出](bugfix-retest-unittest.txt)、[测试实现](../../../tests/test_order.py) |

R1 两项验收场景及一组 4 项定向单测全部通过，无未完成的 BUG-001 关闭判据；执行者与产品实施者不同。用真实文件 SQLite 公开函数入口复现原场景，无场景替换。此批次未执行全产品集成测试或 AC-3，不据此计算整产品通过率。

## 结论及后续条件

BUG-001 达到关闭条件：原取消覆盖故障恢复，必要正常提交、paid 持久化及 submit 错误传播回归通过，取消分支确无写入。无需人工体验反馈。原 Issue 更新为 Closed after retest。

实施者全 discovery 曾遇到独立 `mark_paid(MISSING)` 不抛异常，事实及初始/修复后结果保留于 [Plan](../../issues/BUG-001-plan.md)，未改 ui；Main 已安排独立集成取证并预留 BUG-002。该缺口不影响 BUG-001 特定恢复目标，但不能声称整体产品通过。

候选已具备 Main 组织集成及架构检查的本地条件：上述源文件 manifest、公开验收入口、原测试与修复回归均可运行。AC-3 端点为 null、调用未授权且本轮无网络；必须保持阻塞，需有权人员提供授权真实端点和网络条件后另行接续。UI 直接 SQL 架构偏差交 Main 后续 Review，不属于本次产品修复。
