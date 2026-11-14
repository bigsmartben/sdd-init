# 订单验收指南

## 1. 目标与范围

依据：[Spec](spec.md) 与[订单接口契约](../../docs/contracts/order.md)。覆盖新建、提交、取消后的再次提交、状态写入、mark_paid、错误传播、输入边界和多订单协同，以及真实外部回执 AC-3。验收对象为 Main 指定的本次取消后仍提交缺陷修复候选；实际源文件哈希与运行环境归本轮 [Test Report](../../docs/test-reports/order/integration.md)。候选交付前只准备资产，不据初始版本判定 Gate。

本项目为无图形 UI 的 CLI／库夹具，不需人工视觉验收。纯内部职责、依赖和架构符合性归独立 Review，不作为本指南功能判据。

## 2. 环境与入口

从本隔离项目根目录执行，使用 Python 3.11+ 和标准库 SQLite，无需安装依赖。配置事实见 [runtime.json](../../runtime.json)。每个本地测试创建独立临时 SQLite 文件，真实调用 `src.order_service`、`src.ui`、`src.storage`，关闭连接后重开检查持久化；测试退出清理临时目录。不使用内存数据库、替代服务或外部回执模拟。

先核对 Main 指定候选与实际源文件哈希：

```bash
python -B checks/runtime_details.py
```

主要验收入口（逐场景 JSON；退出 0=全通过、1=有失败、3=无失败但阻塞）：

```bash
python -B checks/acceptance.py
```

补充公开函数全功能集成场景：

```bash
python -B -m unittest discover -s tests -p test_order_integration.py -v
```

既有单元回归另跑 `python -B -m unittest discover -s tests -p test_order.py -v`，不以其替代公开验收。单独复跑某个主要场景可用 `python -B checks/acceptance.py --scenario AC-1`，将编号替换为 AC-2 或 AC-3。

## 3. 场景与通过判据

以下常规数据、重复提交和异常覆盖由执行者依据 Spec／契约推导，不增加状态转换语义。I01～I08 对应集成脚本 `test_I01`～`test_I08` 方法名前缀；测试失败会打印具体子场景。

| 场景 / 依据 | 前置与操作 | 观察与通过判据 | 证据 |
|---|---|---|---|
| I01 / 新建契约 | 新临时库；用非空中文编号 `订单-1` 新建 | 新连接读回 pending | 集成测试输出 |
| I02 / AC-1 | 新建 ORDER-1，再提交；关闭连接并重开 | 返回严格 true，读回 submitted | 集成输出及主要验收 AC-1 JSON |
| I03 / AC-2 | 新建 ORDER-1、取消，连续提交两次；关闭连接并重开 | 取消先持久化 cancelled；每次返回严格 false，最终仍 cancelled | 集成输出及主要验收 AC-2 JSON |
| I04 / set_status、mark_paid | 新建 SERVICE、ADAPTER；分别 set_status(paid)、mark_paid；关闭重开 | 两个订单均 paid | 集成测试输出 |
| I05 / 不存在订单异常 | 无 missing 订单；分别读、取消、提交、set_status(paid)、mark_paid | 每个入口均抛 ValueError，不能报告成功 | 集成输出，失败列具体入口 |
| I06 / 编号边界 | 空库；分别用空字符串、None、整数新建 | 均抛 ValueError，库中仍无订单 | 集成测试输出 |
| I07 / 数据库异常 | 关闭真实连接后调用新建、读、取消、提交、set_status、mark_paid | 各入口传播 sqlite3.Error | 集成测试输出 |
| I08 / 跨入口协同 | 同一文件库分别新建 CANCEL、SUBMIT、PAY；取消并提交首单、提交次单、mark_paid 第三单 | 返回 false／true；关闭重开分别 cancelled／submitted／paid，互不覆盖 | 集成测试输出 |
| E03 / AC-3 | 检查端点与授权；真实外部服务核验回执 | 仅真实已授权端点回执能通过；缺失时 BLOCKED，不以本地结果替代 | 主要验收 AC-3 JSON 与 runtime 事实 |

## 4. 异常与恢复

每次复跑使用新临时文件，退出自动关闭连接并删除临时目录；不触碰业务数据。产品行为不符时保留原始输出及实际哈希并登记或引用原 Issue，不改断言迁就实现。数据库异常测试故意关闭连接，不依赖人工复位。

当前 AC-3 缺少端点和权限、禁止网络调用；`checks/acceptance.py` 只读记录 BLOCKED，从不发送请求。恢复需要有权人员提供真实测试端点、调用权限和网络授权，并安排能实际调用该端点的验收入口；即使配置变更，当前脚本也不会核验外部回执。外部凭据、服务配置和部署不在本轮修改授权内。

## 5. 结果引用

实际候选、逐项结果、缺陷、统计与 Test Gate 见 [Test Report](../../docs/test-reports/order/integration.md)。只有范围内全部功能通过、证据完整时才能 PASS；外部阻塞也会使整体 Gate 未通过。人工操作／视觉反馈不适用。
