# 订单集成验收指南

## 1. 目标与范围

依据 [Spec](spec.md) 的 AC-1、AC-2、AC-3 与 paid 保持要求，以及[订单契约](../../docs/contracts/order.md)。覆盖提交、取消后提交、支付、外部回执及输入和数据库异常；边界场景由契约“非空字符串”“不存在订单抛 ValueError”“数据库异常向上传播”推导。没有图形界面或人工视觉判据。

## 2. 版本、环境与入口

在当前隔离项目根目录执行。产品基线为 `67e0283f880b4995f5df4d58f2c2b6a3ca8b2003`，测试资产为当前工作区的 `checks/acceptance.py` 与 `checks/integration_runner.py`；实际文件哈希见[本轮证据](../../docs/test-reports/order/evidence/ci-reruns.json)。不要仅按 HEAD 假定包含测试工具修正。

使用 Python 3.11+、标准库 SQLite，无需安装依赖。实际配置取自 [runtime.json](../../runtime.json)。每个本地场景自动创建独立临时 SQLite 文件，关闭、重开观察持久化后删除，不共享测试数据；整数边界先创建合法字符串订单 `"42"`，再传整数 `42`，检查拒绝和原数据保护。

```bash
git rev-parse HEAD
git status --short
python -B checks/runtime_details.py
python -B checks/integration_runner.py
```

CI 命令完成输出全量 JSON。退出码：0 全部 PASS；1 至少一项 FAIL；3 没有 FAIL 但存在 BLOCKED。非零结果要检查逐项证据，不能直接解释为入口损坏。单项入口如下；`--scenario` 接受下表全部展开 ID。

```bash
python -B checks/acceptance.py --scenario AC-2
python -B checks/acceptance.py --scenario PAY-1
python -B checks/acceptance.py --scenario ID-submit-integer
```

## 3. 场景、步骤和判据

每行使用上述单项入口（替换 ID）或执行全量 CI。观察 JSON 的 `states`、`accepted`、`persisted_status`、`observed_error`、`result`；`states.reopened` 是关闭原连接后重新打开文件数据库的内容。

| 场景 | 前置与操作 | 期望及证据 |
|---|---|---|
| AC-1 | 新建 ORDER-1，提交，关闭重开 | created 为 pending；accepted=true；after_submit 与 reopened 均 submitted |
| AC-2 | 新建 ORDER-1，取消，提交，关闭重开 | cancelled 中间态存在；accepted=false；after_submit 与 reopened 均 cancelled |
| AC-3 | 读取实际端点、授权、网络条件 | 真实服务回执才可满足；未就绪输出 BLOCKED，external_call_performed=false |
| PAY-1 | 新建，提交，再调用 ui.mark_paid，关闭重开 | 提交 true、submitted 中间态，after_paid 与 reopened 均 paid |
| PAY-2 | 空库调用 ui.mark_paid(MISSING) | ValueError，重开仍空库 |
| ID-{create,submit,cancel,set_status,mark_paid}-{empty,none,integer} | 15项组合；传空串、None、42，整数项预存字符串订单 "42" | ValueError；重开与 before_operation 相同，不能影响原订单 |
| MISSING-{submit,cancel,set_status} | 3项；空库操作 MISSING | ValueError，重开仍空库 |
| DB-{create,submit,cancel,set_status,mark_paid} | 5项；新建 ORDER-1 后关闭连接，再执行操作 | sqlite3.Error 向上传播，重开 ORDER-1 仍 pending |

这些准备与顺序来自现有判据，不增加新业务状态、并发或性能门槛。现有单元测试 `python -B -m unittest discover -s tests -v` 可作辅助检查，不能替代集成入口。

## 4. 异常与恢复

本地复跑无需手工清库，每次使用新临时目录并在结束时清理。当前命令不访问网络，也不把本地状态当作外部回执。AC-3 的恢复条件是有权人员提供真实测试端点、调用授权、可联网环境，并在另行获授权后使用真实外部验收入口；本地运行器即使配置变化仍不会调用外部服务。

## 5. 结果与接续

本指南只给操作与判据。实际逐项结果、缺陷、版本和 Test Gate 见[集成报告](../../docs/test-reports/order/2026-11-15-integration.md)，接续入口见[状态](../../docs/status.md)。
