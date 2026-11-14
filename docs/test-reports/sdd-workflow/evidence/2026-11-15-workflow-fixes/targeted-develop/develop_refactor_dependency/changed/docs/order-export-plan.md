# Plan — WO-ORDER-017

## 1. Goal and Basis

- 依据：[工单与 AC-4／AC-5](order-export-work.md)、[已确认设计](export-design.md)、[订单需求](../specs/order/spec.md)、[函数契约](contracts/order.md)。实际调用者与回执方为 `/root/develop_order_017`；A/B 确认及本轮实施授权沿用工单。
- 范围：仅修改 `src/order_service.py` 的创建输入校验、直接相关测试和本 Plan；不修改 schema、storage、UI、其他写路径、工单、Spec 或 quickstart，不提交 Git。
- 当前实现：创建只拒绝空字符串和非字符串；文件 SQLite 仅定义 `orders(order_id, status)`；服务和 UI 的状态写入覆盖同一行。历史来源需查证后才能作为实现依据。
- 起始版本：`162bdaf0aff7bebeb747ca1f3cdffea7ef8674e1`，接单时工作树干净。

## 2. Task List

### T001: 拒绝全空白订单号并保持合法编号原样

- **Basis**：工单 AC-4；契约 `create_order` 的 pending、commit 和输入要求。
- **Change scope**：`src/order_service.py:create_order`；新增 `tests/test_order_validation.py`。
- **Implementation**：以 `isinstance(order_id, str)` 与 `order_id.strip()` 的非空性校验入口，只用于判断，不替换原始编号。先写失败测试证明全空白输入缺口，再修改校验。
- **Dependencies**：无；不依赖 T002。
- **Completion criteria and local verification**：空串、空格、tab、newline、Unicode 空白、非字符串均抛出原有 `ValueError`，不执行 SQL 或 commit，数据库行和写计数不变；合法编号（含边缘空白）原样创建并跨连接持久化。运行直接测试、现有单元测试和 AC-1 定向保持检查。
- **Status**：Complete（实施及局部自验）。
- **Results and evidence**：修复前 `python -B -m unittest discover -s tests -p test_order_validation.py -v` 退出 1，`Ran 3 tests` / `FAILED (failures=15)`：两组全空白子场景未抛出 ValueError，重开数据库发现 7 条多余 pending 行；完整失败输出位于本次隔离工作区 scratch 的 `order-validation-before.log`，该日志是临时取证而非项目交付资产。修复后 `python -B -m unittest discover -s tests -v` 退出 0，`Ran 5 tests` / `OK`（含原有提交与付款测试）。`python -B checks/acceptance.py --scenario AC-1` 退出 0，输出 `result=PASS, accepted=true, persisted_status=submitted`。AC-4 覆盖 14 个无效输入的拒绝／无连接调用／无数据库写入，以及 3 个合法编号原样持久化。

### T002: 查证跨进程逐次历史的权威持久化来源

- **Basis**：工单 AC-5 与已确认设计；含取消、付款的逐次状态及准确顺序，禁止当前状态冒充历史。
- **Change scope**：只读核查现有源码、测试和临时 SQLite；仅在存在合法来源且授权边界足够时新增只读入口及直接测试。
- **Implementation**：检索权威持久化事件、表、触发器、其他持久化文件与公开读入口；用跨进程临时文件数据库实验检查状态覆盖。缺失历史来源时不实现伪历史，记录依赖及已检查替代，交调用者处理跨职责架构／迁移决定。
- **Dependencies**：无 Task 前置；实施前置为权威已有持久化逐次历史来源。该前置不满足时标记 Blocked。
- **Completion criteria and local verification**：若来源存在，以进程重启后含取消／付款顺序的直接测试验证只读导出；若缺失，交付可复查源码与 SQLite 证据、替代来源排查、影响和恢复条件，AC-5 保持未完成。
- **Status**：Blocked（AC-5 未完成，来源核查已完成）。
- **Results and evidence**：`rg --files` 及 `rg -n -i 'history|event|audit|trigger|journal|sqlite|status|UPDATE|INSERT' src tests README.md runtime.json checks` 未发现权威历史资产或历史读入口。源证据：[storage.py:7](../src/storage.py) 只创建 orders 当前状态表；[order_service.py:18-25](../src/order_service.py) 更新并覆盖当前状态，取消通过同一路径；[ui.py:4-6](../src/ui.py) 付款直接覆盖为 paid。独立 writer/reader 子进程实验（Python 3.12.3 / SQLite 3.45.1）退出 0：两条路径 `create_order → cancel_order → mark_paid` 与 `create_order → mark_paid` 分别关闭 writer、在新进程打开同一文件，均得到 `rows=[["ORDER-1", "paid"]]`、`status=paid`；两者查询内容相等。`sqlite_master` 均只有 `sqlite_autoindex_orders_1` 与 `orders`（SQL 为 `CREATE TABLE orders (order_id TEXT PRIMARY KEY, status TEXT NOT NULL)`），无事件表或 trigger；`PRAGMA journal_mode` 为 `delete`，关闭后临时目录只剩两份数据库文件。准确历史与顺序已无法从当前公开权威读接口恢复。

#### T002 实验复跑入口

从项目根目录运行以下只使用公开服务／适配写入口的本地实验；所有数据库均为自动清理的临时文件，不修改产品路径或 schema：

```sh
python -B - <<'PY'
import json
from pathlib import Path
import subprocess
import sys
import tempfile

writer = '''from src import storage, order_service, ui
import sys
c = storage.connect(sys.argv[1])
order_service.create_order(c, "ORDER-1")
if sys.argv[2] == "cancelled":
    order_service.cancel_order(c, "ORDER-1")
ui.mark_paid(c, "ORDER-1")
c.close()
'''
reader = '''from src import storage, order_service
import json, sys
c = storage.connect(sys.argv[1])
print(json.dumps({"schema": c.execute("SELECT type, name, sql FROM sqlite_master ORDER BY type, name").fetchall(), "rows": c.execute("SELECT * FROM orders").fetchall(), "status": order_service.read_status(c, "ORDER-1"), "journal_mode": c.execute("PRAGMA journal_mode").fetchone()[0]}))
c.close()
'''
with tempfile.TemporaryDirectory() as directory:
    results = {}
    for route in ("cancelled", "direct"):
        path = str(Path(directory) / (route + ".sqlite"))
        subprocess.run([sys.executable, "-B", "-c", writer, path, route], check=True)
        results[route] = json.loads(subprocess.check_output([sys.executable, "-B", "-c", reader, path], text=True))
    assert results["cancelled"] == results["direct"]
    print(json.dumps({"routes": results, "same_reopened_contents": True, "files": sorted(p.name for p in Path(directory).iterdir())}, ensure_ascii=False, indent=2))
PY
```

已检查替代：当前行不能辨别是否曾取消；内存无法跨重启；未发现持久化事件、触发器或公开历史入口；SQLite 临时 journal 不是应用逐次事件来源且本实验关闭后已不存在；日志／时间推测、外部账本违反已确认设计。故未新增只读导出入口，未将当前状态包装成历史。

### Delivery Batches

| 用户目标 | Task | 可观察结果 | 局部验证 |
| --- | --- | --- | --- |
| AC-4 | T001 | 全空白拒绝且无写入，合法编号原样创建 | `python -B -m unittest discover -s tests -v` |
| AC-5 | T002 | 核实权威历史来源；无来源保留阻塞 | 源码检索、跨进程 SQLite 实验 |

### Execution DAG

T001 与 T002 相互独立，均从已授权工单开始；本轮串行执行以便记录证据。T002 的只读实现另依赖权威历史来源，不能阻断 T001。

## 3. Delivery Checks

- **Goal coverage and completion**：T001 通过局部自验；调用者已独立运行 `checks/order_export_acceptance.py`，正式 AC-4、AC-1 及 5 项单测均通过，见[工单验收状态](order-export-work.md#验收计划与实际状态)与[原始验收证据](order-export-acceptance.json)。T002 来源缺失而阻塞。产品 diff 仅创建校验一行，storage、UI、submit、cancel 均未改变；保持未提交。
- **Blockers and next actions**：T002 若要保留每次变更，需要权威事件数据、全量写路径覆盖与持久化结构，以及既有仅当前状态订单的处理决定；这些属于独立架构／迁移事项，当前授权不允许实施。恢复条件为 Main 取得相应决定、扩展授权并交回可执行工单，或提供实际已有合法权威历史来源及读路径。本轮不改变 schema 或写路径。
- **Coverage gaps and applicable follow-up**：AC-5 未满足，不报告通过；AC-2 的现有取消后提交覆盖行为由调度方确认保留为既存偏差，其正式基线证据由调度方维护，不归因于本轮校验改动；AC-3 外部服务不在本轮范围。
- **Version and hashes**：基于 `162bdaf0aff7bebeb747ca1f3cdffea7ef8674e1` 的未提交工作树；SHA-256：`src/order_service.py=22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`，`tests/test_order_validation.py=dd19542ad768316753a3f6f1c43ac65b25e516ebb3159de670efa106ac237582`；未改 `src/storage.py=6881b113e593125682a4886546497d1f6bd07ae490bb1951df4aedc070b23fa9`、`src/ui.py=89ef1238b40556d5a7b3dc93daeeb1a04b68a600c7c985d648a80a66f84cb25b`。
- **Document checks**：写后逐项对照工单和真实输出检查编号、依赖、授权与未完成判据，语义与工单一致，无越权扩展。`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-export-plan.md` 退出 0，输出 `Checked 1 Markdown files: 0 errors, 0 warnings (mechanical only)`；`git diff --check` 退出 0，无输出。未检查外部链接可达性或执行架构审查。
