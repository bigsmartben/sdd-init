# 流量治理

按[交付与运行规则](delivery.md)确定的终点处理灰度、切流、恢复和路由排障。沿用项目既有的路由管理入口与观察判据，按授权限定环境、请求范围、目标版本及比例。

1. 定位集群、context、namespace、入口和实际生效的路由。核对主机、路径或其他匹配条件、当前目的地与权重、目标版本和就绪状态及声明式配置来源。复用项目的控制器、GitOps 或平台流程，检查叠加规则及并发变更。
2. 切流前留存原权重、路由修订和指标基线。按已约定的步长、观察窗口和成功／停止条件调整授权范围内的路由。判据或恢复动作影响范围无法从现有约定确定时，在回执中列明缺项。
3. 回读控制面配置和实际生效的代理或网关路由。以授权范围内的真实入口探测或生产观测验证请求命中、实际流量分布、命中目标版本及错误率或延迟等约定指标。记录时间窗与样本范围；证据不足时保持未证实状态，暂停依赖该结果的下一步。
4. 异常、超时或并发变更时先回读当前路由、分发状态、服务和指标，再决定继续观察、重试或按项目策略恢复。恢复前核对原路由及目的地仍可用、范围与当前版本无冲突，且恢复已获授权；恢复后重新验证实际分布和服务状态。路由排障沿用上述定位和观察，写入按其各自授权执行。

## Istio

按实例实际资源和 API 版本定位路由。使用 VirtualService 时核对 hosts、gateways、匹配规则及目的地；路由指向 subset 时核对 DestinationRule、标签和后端实例。项目使用 Kubernetes Gateway API 时检查实际管理该流量的路由及网关状态。配置权重表达分配意图，应结合实际请求和指标验证结果。参考 [Istio 切流](https://istio.io/latest/docs/tasks/traffic-management/traffic-shifting/)、[VirtualService 配置](https://istio.io/latest/docs/reference/config/networking/virtual-service/) 和 [Istio 指标查询](https://istio.io/latest/docs/tasks/observability/metrics/querying-metrics/)。

回执包括环境与路由标识、范围、变更前后权重、实际命中的版本、观测窗口与证据入口、异常或恢复结果及待处理项。
