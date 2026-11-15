# 订单验收指南

## 1. 验收目标与范围

依据：[订单 Spec](spec.md)、[订单契约](../../docs/contracts/order.md)、[蓝图](../../docs/blueprint.md)。本指南覆盖已确认提交、取消、支付、外部回执及其缺失订单和数据库异常路径。无 UI，不需要 HTML 原型或人工视觉确认；没有已确认的性能阈值。

## 2. 版本、准备与入口

在当前生成的隔离项目根目录运行，基线 Git HEAD 为 `2518bb5a4654cb1c606dd724bf0ad35ef1da643e`，含本轮 `checks/`、`tests/` 测试资产修正。产品 `src/` 与 `runtime.json` 保持基线；实际文件哈希和测试工具版本见[报告](../../docs/test-reports/order/2026-11-14-integration.md)。用 `git rev-parse HEAD`、`git status --short`、`python -B checks/runtime_details.py` 核对实际版本，不能只凭 HEAD 忽略工作区改动。

Python 3.11+、标准库 SQLite，无需安装依赖。环境是 `isolated-local-fixture`；每个本地场景独立临时目录和 SQLite 文件，订单 ORDER-1。操作前不存在该库；场景内新建数据，结束时关闭连接、删除目录，异常时也执行清理。缺失订单和只读 SQLite 是从已确认契约推导的常规边界，不新增业务规则。

CI 与本地完整集成使用同一真实入口：

```bash
python -B checks/integration_runner.py
python -B checks/integration_runner.py
```

每次输出逐场景 JSON。退出码 0 表示全部通过，1 表示至少一项失败（即使同时阻塞），3 表示无失败但有阻塞。非零业务结果必须保留，不能改为成功。完整命令可连续复跑，无需人工清库。单项定位使用 `python -B checks/acceptance.py --scenario 场景ID`；直接完整入口为 `python -B checks/acceptance.py`。工具回归入口 `python -B -m unittest discover -s tests -v` 不替代集成验收。

## 3. 场景覆盖与步骤

以下每个 ID 均可代入单项命令；观察 JSON 的预期、实际、中间状态与结果，并关联运行版本留存输出。

| 功能 / 场景 | 前置与操作 | 通过判据 / 观察 |
| --- | --- | --- |
| AC-1 提交 | 新建 ORDER-1，提交，关闭并重开库 | 提交 true，重开后 submitted |
| AC-2 取消后提交 | 新建、取消、提交，重开库 | 取消中间状态 cancelled；提交 false，重开仍 cancelled |
| AC-3 外部回执 | 读取 runtime.json 的端点、权限与网络授权事实 | 必须在获授权的真实外部服务核验；当前无条件时 BLOCKED，禁止以本地结果或模拟回执替代 |
| STATE-1 新建持久化 | 新建，关闭并重开库 | pending |
| STATE-2 取消持久化 | 新建、取消，关闭并重开库 | cancelled |
| PAY-1 支付持久化 | 新建现存订单，调用 ui.mark_paid，关闭并重开库 | paid |
| ERR-2-READ 缺失读取 | 空库读取 MISSING | ValueError |
| ERR-2-SET 缺失状态写入 | 空库对 MISSING 调用 set_status | ValueError |
| ERR-2-CANCEL 缺失取消 | 空库取消 MISSING | ValueError |
| ERR-2-SUBMIT 缺失提交 | 空库提交 MISSING | ValueError，不能报成功 |
| ERR-2-PAY 缺失支付 | 空库 mark_paid MISSING | 契约要求 ValueError |
| ERR-3-CREATE 写异常 | 文件库启用 SQLite query_only，尝试新建 | OperationalError 向上传播，未写入 |
| ERR-3-SET 写异常 | 先新建，启用 query_only，set_status paid | OperationalError 向上传播，状态保持 pending |
| ERR-3-CANCEL 写异常 | 先新建，启用 query_only，取消 | OperationalError 向上传播，状态保持 pending |
| ERR-3-SUBMIT 写异常 | 先新建，启用 query_only，提交 | OperationalError 向上传播，不能返回成功，状态保持 pending |
| ERR-3-PAY 写异常 | 先新建，启用 query_only，mark_paid | OperationalError 向上传播，状态保持 pending |

真实组件为 src 服务、ui 适配器与文件 SQLite；query_only 是对真实数据库施加写失败条件，没有替代产品模块。证据至少包括各项预期与实际、异常类型、中间状态、关闭重开后的状态（写异常项以独立新连接核对）和退出码；工具异常不能遮蔽其余场景。

## 4. 失败与恢复

本轮禁止外网、外部平台与真实部署，产品实现冻结。AC-3 当前端点 null、权限 false、网络 false；运行器仅报告阻塞，不进行网络请求。未来须由有权人员提供获授权真实测试服务端点和调用权限，并另行授权网络验证后恢复；当前夹具不包含真实外部调用适配，单改配置也不能取得真实回执证据。

本地失败保留原判据、输出与 Issue；产品修复必须由 Main 协调另行授权。无需人工复位：每次新建独立临时库，连接和目录由上下文清理。不得用修改预期、跳过失败或重复覆盖首次输出使 Gate 通过。

## 5. 结果入口

[本轮 Test Report](../../docs/test-reports/order/2026-11-14-integration.md) 记录实际版本、首次工具失败、修正复跑、逐项业务结果、人工待验情况及 Test Gate；[ORD-001](../../docs/issues/ORD-001.md) 记录取消覆盖缺陷，[ORD-002](../../docs/issues/ORD-002.md) 记录缺失订单支付异常。自动结果与人工反馈分别记录。
