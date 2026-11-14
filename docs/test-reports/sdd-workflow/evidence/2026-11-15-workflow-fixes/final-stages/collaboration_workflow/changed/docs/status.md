# 订单本地回归与修复状态

## 当前工单与授权

依据 [TASK](../TASK.txt) 和本轮用户确认，范围为新建、取消、提交、公开付款及 AC-3；环境为当前隔离项目的本地 Python 与文件 SQLite。阶段为初始全功能集成回归、证据支持的本地缺陷修复、修复后集成复验和相关架构检查。保持现有行为、接口与架构决定。禁止原仓、已安装工作流、外部平台、网络和真实部署；不执行提交或其他 Git 写操作。

## 当前进展

- 起始提交：`89df9f629407a6b572c6f65c87fc9768e0f52f5d`，分支 `main`，起始工作区干净。实际源码快照由阶段报告记录哈希，不以未变的 HEAD 代替修复版本。
- Main `/root` 调度；集成阶段 Agent `/root/order_integration` 已完成[初始回归](test-reports/order/initial.md)和[修复后复验](test-reports/order/fixed.md)。架构 Agent `/root/order_architecture_check` 已完成[初审和修复复核](test-reports/order/architecture-review.md)。
- 初始回归：20 项，17 PASS、2 FAIL、1 BLOCKED；原始证据在初始报告中逐项引用。
- Bugfix Agent `/root/order_bugfix` 已修复 [ORDER-001](issues/ORDER-001.md) 和 [ORDER-002](issues/ORDER-002.md)，[Plan](../specs/order/plan.md) 与[定向复验](test-reports/order/bugfix.md)记录根因、局部自验及独立定向检查。
- Main 已将实际源码哈希和 Task/证据交回原集成及架构执行者；[修复后全量复验](test-reports/order/fixed.md)已完成，20项中19 PASS、0 FAIL、0未测、1 BLOCKED，8项单元测试通过。两个原 Issue 已依据独立整轮证据关闭；初始失败和历次处理保留。原架构执行者已完成33项运行复核（33 PASS）及原检查项记录收尾，CHK-001/005 已关闭，CHK-002/003/004/007 通过。修复版 order_service SHA256 `3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb`；ui SHA256 `4a03e8d39ef106a5037404562a931aad9009a1bb579304daa15f820983de6909`；未创建Git提交。
- 行为与接口依据：[Spec](../specs/order/spec.md)、[契约](contracts/order.md)；架构依据：[Blueprint](blueprint.md)、[Code Review Rules](code-review-rules.md)。
- 初始 Test Gate：FAIL；初始 Review Gate：FAIL，详见原报告。
- 修复后 Test Gate：BLOCKED，仅 AC-3 未取得真实外部回执；[逐项证据与报告](test-reports/order/fixed.md)。
- 修复后 Review Gate：UNVERIFIED，原实现偏差已消除，CHK-006 规则映射待查；[架构审查与复核](test-reports/order/architecture-review.md)。两个 Gate 均未宣告全范围通过。

## 阻塞与恢复

AC-3 所需外部端点与权限暂缺。保持阻塞；恢复需有权人员提供真实测试服务端点、调用权限并另行授权外部执行。本地通过不能代替 AC-3。

架构 CHK-006 的取消语义规则映射待查，详见[审查记录](test-reports/order/architecture-review.md)。恢复需有权方确认项目规则适用性，或决定是否及何时维护规则；本轮不自行改写 Code Review Rules。其他事项按实际证据补记；只暂停受影响项，继续其余已就绪的授权工作。

## 交付与接续

本轮全部可执行本地场景已完成；仅修改工单相关源码、测试资产和文档，未改需求/契约/Blueprint/Code Review Rules/runtime，未执行网络或Git写操作。修复实际版本仍为原HEAD加本地未提交改动，哈希见上述报告。复跑入口及清理说明见[Quickstart](../specs/order/quickstart.md)。

后续仅在外部端点与权限/执行授权、真实调用入口齐备时恢复 AC-3；在项目规则适用性获确认或有权方决定规则维护并交付映射时恢复 CHK-006。不需要重新执行已被当前快照充分证明且未受影响的本地场景。

Main 最终核对：源码差异限于两项根因修复，测试资产与两轮哈希一致；修改及直接受影响的10份Markdown机械校验为0错误、0警告，`git diff --check`通过。语义核对确认报告、Issue关闭依据、实际版本和两项剩余条件相符；机械检查不替代实测及Gate判定。
