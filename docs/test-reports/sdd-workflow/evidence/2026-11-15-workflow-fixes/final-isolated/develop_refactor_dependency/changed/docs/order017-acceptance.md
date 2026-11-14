# WO-ORDER-017 点对点验收

执行者：sdd-develop `/root/develop_order017`；2026-11-15。依据[工单及验收方案](order-export-work.md)、[同一 Plan](../specs/order/plan.md)。本批是需求点对点验收，不是全产品集成回归或架构 Review。

## 版本和真实环境

实际版本为 Git HEAD `cd451ab5d5da81d51e5eb55a805008d1a62b1dce` 加本轮未提交工作区：`src/order_service.py` 仅 create_order 校验从非空改为非全空白；直接测试及本批验收资产和文档同步增加。未创建提交。

`python -B checks/runtime_details.py` 实测 Python 3.12.3、SQLite 3.45.1；正式模块 SHA256：

| 文件 | SHA256 |
| --- | --- |
| src/order_service.py | `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b` |
| src/storage.py | `6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9` |
| src/ui.py | `89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b` |

运行环境为 isolated-local-fixture，真实公开 src 函数、临时文件 SQLite 和独立 Python 子进程；没有模拟组件或外部调用。每次验收使用新临时目录，关闭连接后自动清除数据。外部端点为空且未授权；本批不覆盖 AC-3。

## 逐项结果

| 判据 | 入口、数据与实际观察 | 结果 |
| --- | --- | --- |
| AC-4／T001 | `python -B checks/order017_acceptance.py`，退出 0。空串、空格、制表换行、Unicode空白以及 None、0 均抛出 `ValueError("order_id is required")`；逐项检查数据库零行且无待提交事务。合法 `ORDER-1`、`  ORDER-2  `、`订单-3` 原值写入；关闭连接后新 Python 进程通过公开 read_status 读取均为 pending，数据库恰有 3 行。 | PASS |
| AC-1 保持 | `python -B checks/acceptance.py --scenario AC-1`，退出 0；实际 JSON：accepted=true，persisted_status=submitted，与期望一致。 | PASS |
| AC-5／T002 | 原计划依赖的权威持久化逐次事件不存在。[实施证据](../specs/order/implementation-evidence.md)核查 schema、读写路径及进程退出后 create→cancel→paid 仅剩 paid。没有可运行且满足原判据的公开历史入口，未假造导出或修改额外写路径/schema。 | BLOCKED |

合计 3 项：通过 2、失败 0、阻塞 1、未执行 0。AC-5 的阻塞是前置来源与授权缺口，不作为历史导出通过证据；范围内需求 AC-4 已全部验收，AC-5 未满足。AC-2 及原有 submit_order／mark_paid 其他问题不属于本轮已确认修改范围，未扩展测试或修复。

AC-4 原始标准输出：

```json
{"scenario":"AC-4","result":"PASS","rejected":["''","' '","'\\t\\r\\n'","'\\u2003\\u3000'","None","0"],"rows_after_process_restart":[["ORDER-1","pending"],["  ORDER-2  ","pending"],["订单-3","pending"]],"components":"public src functions + real file SQLite + new Python process"}
```

## 结论与接续

T001 可独立交付；可复跑入口为[验收脚本](../checks/order017_acceptance.py)，实施局部测试证据与红绿记录见[实施证据](../specs/order/implementation-evidence.md)。没有人工操作判据，本批不产生 Test Gate 或 Review Gate。

T002 只暂停其自身及依赖。已核查 read_status、orders 当前行、SQLite schema/触发器和已声明运行来源；均不能恢复跨重启逐次状态及准确顺序。日志、时间戳推测、另建账本均违反[已确认导出约束](export-design.md)，仅导出当前状态不满足 AC-5。可由 Main 取得另行授权的前置架构／迁移决定（含全量写路径、持久化结构和旧订单历史缺口处理）后继续原 T002，或延后历史导出并先交付 T001。本阶段未自行选择或执行这些跨阶段方案。
