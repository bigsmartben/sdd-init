# Plan — BUG-001 取消提交恢复

## 目标与依据

恢复 [BUG-001](BUG-001.md) 记录的取消后不提交行为；上游验收计划及步骤见原 Issue。保持函数接口、正常提交、paid 持久化和错误传播；不处理 UI 架构偏差、不改变外部配置。

## 任务

### T001: 恢复取消分支并添加定向回归

- 依据：[BUG-001 根因与验收方案](BUG-001.md)。归因已由实际 AC-2 失败与无条件写入路径验证。
- 范围：`src/order_service.py`、`tests/test_order.py`，实施者维护本 Plan 的任务实施与局部结果；其他文件归阶段调度方。
- 实施：在已存在的读取结果上判断 cancelled，返回 false 且不写库；其余分支保持。补取消后提交拒绝及重开持久化、无写入、不存在订单异常覆盖；不规定未确认的新状态规则。
- 依赖：无；工单就绪、修复已授权。
- 完成条件：AC-2 返回 false 且 cancelled 不被改写；AC-1、paid 回归通过；不存在订单仍 ValueError；公开接口不变。
- 局部命令：`python -B -m unittest discover -s tests -p test_order.py -v`；原全 discovery 命令包含其他执行者的集成测试，结果另列；原 Issue 定向入口为 `python -B checks/acceptance.py --scenario AC-1` 及 `--scenario AC-2`。
- 状态：Complete；2026-11-15 由 `/root/bugfix/coder` 完成授权修复及局部自验，阶段独立复验待 `/root/bugfix` 执行。
- 实际修改：`submit_order` 读取 cancelled 时立即返回 false，其他逻辑及函数签名保持。`tests/test_order.py` 新增取消后拒绝、SQL 跟踪仅 SELECT、累计写入次数不变、关闭重开 cancelled 和不存在订单 ValueError 检查；正常提交增加关闭重开 submitted 检查；原 paid 测试保持。
- 实际版本：`src/order_service.py` SHA-256 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；`tests/test_order.py` SHA-256 `a438c19810b3a10ad713090330d14496ea11bd7fd43a0c79d953fb695c4d631e`。本地临时文件 SQLite；Python 3.12.3 / SQLite 3.45.1。未执行 Git 操作。
- 归因独立核验：修复前初始服务哈希与原 Issue 一致；AC-2 命令退出 1，accepted=true、persisted_status=submitted。新增单测在修复前失败于 `assertFalse`，实测返回 True，支持取消后仍无条件写入的归因。
- 局部结果：上述限定 `test_order.py` 命令退出 0，4 tests / OK，覆盖 AC-2 无写入及重开持久化、AC-1 重开持久化、paid 持久化和 submit 不存在订单异常。AC-1、AC-2 验收命令分别退出 0，分别为 true/submitted 和 false/cancelled。用 `inspect.signature` 核对 create_order、read_status、cancel_order、submit_order 均为 `(connection, order_id)`，set_status 为 `(connection, order_id, status)`，与修复前定义一致。
- 范围外失败证据：修复前 `python -B -m unittest discover -s tests -v` 为 12 tests / 4 failures，其中本地取消回归和集成 I03、I08 体现同一提交缺陷；集成 I05 的 mark_paid(MISSING) 另有未抛 ValueError。修复后该全 discovery 命令退出 1，12 tests / 1 failure，仅余 `test_I05_missing_order_errors (operation='mark_paid')` 的 `AssertionError: ValueError not raised`，位置 `tests/test_order_integration.py:64`。未修改 ui 或该集成资产；已交调用者转 Main 协调，不能据此声称整产品测试通过。

## 交付检查

本轮仅 BUG-001 实施及局部自验，T001 授权判据已覆盖。原 Issue 所列阶段独立复验仍由 `/root/bugfix` 在上述实际版本执行；其结果和 Issue 状态由阶段调度方维护。范围外 I05 失败和后续整产品集成及架构检查交 Main 协调。调用者转交 Main 确认：集成资产仍由 `/root/integration` 准备，正式集成待本阶段候选；缺失订单问题预留 BUG-002，由集成阶段正式取证登记，本 Plan 不充当该缺陷的正式结论。外部 AC-3 需端点、权限与网络条件；本轮未外调，不能用本地 PASS 替代。本任务未发起网络、Git、部署或共享工作流修改。

文档检查入口：`python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/issues/BUG-001-plan.md`，退出 0，1 文件、0 errors、0 warnings。读回核对本 Plan 与原 Issue 的稳定编号、范围、版本、局部覆盖及待阶段复验含义一致；机械检查不代表整产品测试通过。

阶段接续结果：`/root/bugfix` 已在上述实际修复版本完成 [R1 定向复验](../test-reports/order/bugfix-001.md)，原 Issue 已关闭；以上局部自验完成时的待验状态作为历史保留。
