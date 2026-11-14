# 订单验收指南

## 1. 验收目标与范围

依据：[Spec](spec.md) AC-1、AC-2、AC-3 与[函数契约](../../docs/contracts/order.md)。覆盖新建、取消、提交、公开 `ui.mark_paid`，以及持久化、输入边界、缺失订单、数据库异常和多订单隔离。无 UI，无人工视觉验收。对已确认判据取证，未定义的 paid 后提交、重复提交等状态规则不另行设定。

## 2. 版本、环境与入口

在当前生成的隔离项目根目录执行，Python 3.11+ 与标准库 SQLite，无需安装依赖。当前及修复后工作区均用相同资产复跑；实际版本取 `git rev-parse HEAD`、`git status --short` 和 `python -B checks/runtime_details.py`，报告保存源码 SHA-256。初始版本与修复后实测版本分别见[初始报告](../../docs/test-reports/order/initial.md)及[修复后报告](../../docs/test-reports/order/fixed.md)，HEAD 相同但源码有修改时必须同时记录实际源码哈希。

```sh
python -B checks/runtime_details.py
python -B checks/order_integration.py
```

脚本从本目录正式 `src` 模块公开调用入口驱动真实文件 SQLite，不替换产品组件。每个场景独立临时目录和数据库，订单使用 ORDER-1 等常规非空字符串；用第二订单验证隔离。输入边界 `''`、`None`、`1` 由非空字符串规则推导；关闭连接用于验证数据库异常传播。输出 JSON 含逐项操作、预期、实际、版本、源码及测试资产哈希。退出码 0 为全部通过，1 为存在失败，3 为无失败但有阻塞。

## 3. 路径与判断点

下表各项由上面的完整入口执行，稳定用例编号与原始逐项结果一并输出。

| 功能 / 场景依据 | 数据和步骤 | 预期与关键观察 |
|---|---|---|
| 新建 / 函数契约 | 创建 ORDER-1，关闭重开数据库 | pending 持久化 |
| AC-1 | 创建、提交，关闭重开 | 返回 true，submitted 持久化 |
| AC-2 | 创建、取消、读取、提交，关闭重开 | 中间 cancelled；返回 false，重开仍 cancelled |
| mark_paid / 函数契约 | 创建、公开 ui.mark_paid，关闭重开 | paid 持久化 |
| 非法编号 / Spec | 分别用空串、None、整数新建 | ValueError 且没有写入订单 |
| 缺失订单 / 函数契约 | 对不存在编号调用 read_status、cancel_order、submit_order、set_status、ui.mark_paid | 每个入口抛 ValueError，无新增订单 |
| 数据库异常 / 函数契约 | 用已关闭连接调用各写入口 | SQLite 异常向上传播，不转成功 |
| 多订单协同 | 同库创建不同编号，分别提交、取消、标记 paid | 独立状态互不覆盖，重开仍一致 |
| AC-3 | 只读 runtime.json 的配置和授权事实 | 缺端点或权限为 BLOCKED，本轮不访问网络 |

原有验收入口仍可单独运行：`python -B checks/acceptance.py --scenario AC-1`、`--scenario AC-2`、`--scenario AC-3`；无参数执行三项并输出 JSON，退出码同上。`python -B -m unittest discover -s tests -v` 为已有局部检查，不能代替完整集成覆盖。

## 4. 复位、失败与恢复

每项结束关闭连接并删除临时目录，不写入产品配置或保留测试订单。失败原样记录，不通过修改断言消除。AC-3 恢复须由有权人员提供获授权的真实测试服务端点、调用权限和运行网络许可，并由 Main 重新确认该外部环境和真实回执调用路径；当前本地 fixture 不执行外部调用，补齐配置本身不能证明通过。不得自行获取凭据、配置外部服务或部署。其余本地项可独立完成。

## 5. 结果入口

[初始全功能集成报告](../../docs/test-reports/order/initial.md)、[修复后全功能集成报告](../../docs/test-reports/order/fixed.md)、[ORDER-001](../../docs/issues/ORDER-001.md)、[ORDER-002](../../docs/issues/ORDER-002.md)。实际执行与 Gate 归报告，修复方案和局部自验归后续 Bugfix 工单。
